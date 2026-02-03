"""
Translation service using Sarvam AI API.

Handles text chunking, concurrent translation, retry logic, and cost tracking.
Supports two-step translation for improved Tamil quality.
"""

import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Optional

from tamil_translate.config import get_config
from tamil_translate.security import load_api_key_securely

logger = logging.getLogger(__name__)


class TranslationError(Exception):
    """Base exception for translation errors."""

    pass


class APIKeyError(TranslationError):
    """Raised when API key is invalid."""

    pass


class RateLimitError(TranslationError):
    """Raised when API rate limit is hit."""

    pass


class ChunkingError(TranslationError):
    """Raised when text chunking fails validation."""

    pass


@dataclass
class TranslationResult:
    """Result from translating text."""

    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    chunk_count: int
    cost_inr: float
    processing_time: float
    char_count: int

    def __repr__(self) -> str:
        return (
            f"TranslationResult({self.source_lang}→{self.target_lang}, "
            f"chunks={self.chunk_count}, cost=₹{self.cost_inr:.2f}, "
            f"time={self.processing_time:.2f}s)"
        )


@dataclass
class TranslationStats:
    """Aggregate statistics for translation operations."""

    total_chars: int = 0
    total_chunks: int = 0
    total_cost_inr: float = 0.0
    total_time: float = 0.0
    successful_translations: int = 0
    failed_translations: int = 0

    def add_result(self, result: TranslationResult) -> None:
        """Add a translation result to the statistics."""
        self.total_chars += result.char_count
        self.total_chunks += result.chunk_count
        self.total_cost_inr += result.cost_inr
        self.total_time += result.processing_time
        self.successful_translations += 1

    def add_failure(self) -> None:
        """Record a failed translation."""
        self.failed_translations += 1


class TranslationService:
    """
    Translation service using Sarvam AI API.

    Features:
    - Word-boundary preserving text chunking
    - ThreadPoolExecutor for concurrent translation
    - Exponential backoff retry logic
    - Two-step Tamil translation for quality
    - Real-time cost tracking
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        max_workers: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        """
        Initialize the translation service.

        Args:
            api_key: Sarvam API key (uses env var if not provided)
            max_workers: Number of concurrent translation workers
            max_retries: Maximum retry attempts for failed requests
        """
        self.config = get_config()
        self.api_key = api_key or load_api_key_securely()
        self.max_workers = max_workers or self.config.MAX_WORKERS
        self.max_retries = max_retries or self.config.MAX_RETRIES

        # Initialize statistics
        self.stats = TranslationStats()

        # Lazy-initialized client
        self._client = None

    def _get_client(self):
        """Lazily initialize the SarvamAI client."""
        if self._client is None:
            try:
                from sarvamai import SarvamAI

                self._client = SarvamAI(api_subscription_key=self.api_key)
                logger.info("SarvamAI client initialized")
            except ImportError as e:
                raise ImportError(
                    "sarvamai not installed. Install with: pip install sarvamai"
                ) from e
        return self._client

    def _detect_and_remove_repetition(
        self,
        text: str,
        min_phrase_length: int = 20,
        max_repetitions: int = 3,
    ) -> str:
        """
        Detect and remove repetitive phrases from translated text.

        The Sarvam API sometimes produces hallucination loops where the same
        phrase is repeated many times. This method detects such patterns and
        removes the repetitions, keeping only the first occurrence.

        Args:
            text: Translated text to check
            min_phrase_length: Minimum phrase length to check for repetition
            max_repetitions: Keep at most this many occurrences (removes if more)

        Returns:
            Text with repetitions removed
        """
        if not text or len(text) < min_phrase_length * 2:
            return text

        original_length = len(text)

        # Pattern: find phrases of min_phrase_length+ chars repeated 4+ times
        # Use word boundaries to avoid partial matches
        pattern = rf'(.{{{min_phrase_length},}}?)\1{{{max_repetitions + 1},}}'

        def replace_repetition(match: re.Match) -> str:
            """Keep first occurrence of the repeated phrase."""
            phrase = match.group(1)
            return phrase

        cleaned_text = re.sub(pattern, replace_repetition, text, flags=re.DOTALL)

        if len(cleaned_text) < original_length:
            removed_chars = original_length - len(cleaned_text)
            logger.warning(
                f"Repetition detected and removed: {removed_chars} chars "
                f"({removed_chars * 100 // original_length}% of output)"
            )

        return cleaned_text

    def chunk_text(self, text: str, max_length: Optional[int] = None) -> List[str]:
        """
        Split text into chunks while preserving word boundaries.

        Based on official Sarvam AI tutorial pattern with validation.

        Args:
            text: Text to split
            max_length: Maximum chunk size (default from config)

        Returns:
            List of text chunks

        Raises:
            ChunkingError: If chunking results in data loss
        """
        max_length = max_length or self.config.MAX_CHUNK_SIZE
        original_text = text
        original_length = len(text.strip())
        chunks = []

        while len(text) > max_length:
            # Find the last space within limit to preserve word boundaries
            split_index = text.rfind(" ", 0, max_length)

            if split_index == -1:
                # No space found, force split at max_length (rare for natural text)
                split_index = max_length
                logger.warning(
                    f"Forced split at position {split_index} (no word boundary found)"
                )

            chunks.append(text[:split_index].strip())
            text = text[split_index:].lstrip()

        if text.strip():
            chunks.append(text.strip())

        # Validate: check for data loss
        reassembled = " ".join(chunks)
        reassembled_length = len(reassembled)

        # Allow 1% variance for whitespace normalization
        loss_percentage = abs(reassembled_length - original_length) / max(original_length, 1)
        if loss_percentage > 0.01 and original_length > 100:
            raise ChunkingError(
                f"Chunking lost {loss_percentage * 100:.2f}% of data: "
                f"{original_length} chars → {reassembled_length} chars"
            )

        logger.debug(f"Split text into {len(chunks)} chunks (max {max_length} chars each)")
        return chunks

    def translate_chunk(
        self,
        chunk: str,
        source_lang: str,
        target_lang: str,
    ) -> str:
        """
        Translate a single chunk with retry logic.

        Args:
            chunk: Text chunk to translate
            source_lang: Source language code (e.g., 'sa-IN')
            target_lang: Target language code (e.g., 'en-IN')

        Returns:
            Translated text (with repetitions removed if detected)

        Raises:
            TranslationError: If translation fails after all retries
        """
        client = self._get_client()

        for attempt in range(self.max_retries):
            try:
                response = client.text.translate(
                    input=chunk,
                    source_language_code=source_lang,
                    target_language_code=target_lang,
                    speaker_gender=self.config.SPEAKER_GENDER,
                    mode=self.config.TRANSLATION_MODE,
                    model=self.config.MODEL,
                    numerals_format=self.config.NUMERALS_FORMAT,
                )
                # Clean output to remove any hallucination loops
                translated = self._detect_and_remove_repetition(response.translated_text)
                return translated

            except Exception as e:
                error_str = str(e).lower()
                status_code = getattr(e, "status_code", None)

                # Handle specific error codes
                if status_code == 403 or "invalid_api_key" in error_str:
                    raise APIKeyError(
                        "Invalid API key. Verify your key at: https://dashboard.sarvam.ai"
                    ) from e

                if status_code == 429 or "quota" in error_str or "rate" in error_str:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2**attempt
                    logger.warning(
                        f"Rate limited (attempt {attempt + 1}/{self.max_retries}), "
                        f"waiting {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue

                if status_code == 500 or "server" in error_str:
                    # Server error: retry with backoff
                    wait_time = 2**attempt
                    logger.warning(
                        f"Server error (attempt {attempt + 1}/{self.max_retries}), "
                        f"waiting {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue

                # Other errors: fail immediately
                raise TranslationError(f"Translation failed: {e}") from e

        raise TranslationError(f"Translation failed after {self.max_retries} retries")

    def translate_batch(
        self,
        chunks: List[str],
        source_lang: str,
        target_lang: str,
    ) -> List[str]:
        """
        Translate multiple chunks concurrently.

        Uses ThreadPoolExecutor for parallel API calls.

        Args:
            chunks: List of text chunks
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            List of translated chunks in same order

        Raises:
            TranslationError: If any chunk translation fails
        """
        if not chunks:
            return []

        if len(chunks) == 1:
            # Single chunk: no need for threading
            return [self.translate_chunk(chunks[0], source_lang, target_lang)]

        results = [None] * len(chunks)
        errors = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all translation tasks
            future_to_index = {
                executor.submit(
                    self.translate_chunk, chunk, source_lang, target_lang
                ): i
                for i, chunk in enumerate(chunks)
            }

            # Collect results
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    errors.append((index, e))
                    logger.error(f"Chunk {index} translation failed: {e}")

        if errors:
            # Report first error but include count of all errors
            first_index, first_error = errors[0]
            raise TranslationError(
                f"Translation failed for {len(errors)} chunks. "
                f"First error (chunk {first_index}): {first_error}"
            )

        return results

    def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> TranslationResult:
        """
        Translate a full text document.

        Handles chunking, concurrent translation, and reassembly.

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'sa-IN' for Sanskrit)
            target_lang: Target language code (e.g., 'en-IN' for English)

        Returns:
            TranslationResult with translated text and metadata
        """
        start_time = time.time()

        # Chunk the text
        chunks = self.chunk_text(text)
        logger.info(f"Translating {len(text)} chars in {len(chunks)} chunks")

        # Translate all chunks
        translated_chunks = self.translate_batch(chunks, source_lang, target_lang)

        # Reassemble
        translated_text = "\n".join(translated_chunks)

        # Calculate cost
        char_count = len(text)
        cost_inr = self.config.calculate_cost(char_count)

        processing_time = time.time() - start_time

        result = TranslationResult(
            source_text=text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            chunk_count=len(chunks),
            cost_inr=cost_inr,
            processing_time=processing_time,
            char_count=char_count,
        )

        # Update statistics
        self.stats.add_result(result)

        return result

    def translate_to_english(self, text: str, source_lang: str = "sa-IN") -> TranslationResult:
        """
        Translate text to English.

        Args:
            text: Text to translate
            source_lang: Source language code (default 'sa-IN' for Sanskrit)

        Returns:
            TranslationResult
        """
        return self.translate_text(text, source_lang, "en-IN")

    def translate_to_tamil(
        self,
        text: str,
        source_lang: str = "sa-IN",
        use_two_step: bool = True,
    ) -> TranslationResult:
        """
        Translate text to Tamil.

        By default uses two-step translation (Sanskrit → English → Tamil)
        for improved quality, as direct Sanskrit→Tamil has low BLEU score (8.03).

        Args:
            text: Text to translate
            source_lang: Source language code (default 'sa-IN' for Sanskrit)
            use_two_step: Use two-step translation via English (default True)

        Returns:
            TranslationResult
        """
        if use_two_step and source_lang != "en-IN":
            return self.translate_two_step(text, source_lang, "en-IN", "ta-IN")
        else:
            return self.translate_text(text, source_lang, "ta-IN")

    def translate_two_step(
        self,
        text: str,
        source_lang: str,
        intermediate_lang: str,
        target_lang: str,
    ) -> TranslationResult:
        """
        Translate through an intermediate language for improved quality.

        Example: Sanskrit → English → Tamil

        Args:
            text: Text to translate
            source_lang: Source language code
            intermediate_lang: Intermediate language code
            target_lang: Target language code

        Returns:
            TranslationResult with combined cost and time
        """
        start_time = time.time()

        # Step 1: Source → Intermediate
        logger.info(f"Step 1: {source_lang} → {intermediate_lang}")
        step1_result = self.translate_text(text, source_lang, intermediate_lang)

        # Step 2: Intermediate → Target
        logger.info(f"Step 2: {intermediate_lang} → {target_lang}")
        step2_result = self.translate_text(
            step1_result.translated_text, intermediate_lang, target_lang
        )

        # Combine results
        total_time = time.time() - start_time
        total_cost = step1_result.cost_inr + step2_result.cost_inr
        total_chunks = step1_result.chunk_count + step2_result.chunk_count

        return TranslationResult(
            source_text=text,
            translated_text=step2_result.translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            chunk_count=total_chunks,
            cost_inr=total_cost,
            processing_time=total_time,
            char_count=len(text) + len(step1_result.translated_text),
        )

    def estimate_cost(self, text: str, include_tamil_two_step: bool = True) -> dict:
        """
        Estimate translation cost without making API calls.

        Args:
            text: Text to estimate cost for
            include_tamil_two_step: Include two-step Tamil translation cost

        Returns:
            Dictionary with cost breakdown
        """
        char_count = len(text)
        english_cost = self.config.calculate_cost(char_count)

        if include_tamil_two_step:
            # Tamil two-step: English intermediate + Tamil final
            tamil_cost = english_cost * 2  # Roughly double for two-step
        else:
            tamil_cost = english_cost

        total_cost = english_cost + tamil_cost

        return {
            "char_count": char_count,
            "english_cost_inr": english_cost,
            "tamil_cost_inr": tamil_cost,
            "total_cost_inr": total_cost,
            "estimated_usd": round(total_cost / 83, 2),
        }

    def get_stats(self) -> dict:
        """
        Get translation statistics.

        Returns:
            Dictionary with aggregate statistics
        """
        return {
            "total_chars": self.stats.total_chars,
            "total_chunks": self.stats.total_chunks,
            "total_cost_inr": round(self.stats.total_cost_inr, 2),
            "total_time_seconds": round(self.stats.total_time, 2),
            "successful_translations": self.stats.successful_translations,
            "failed_translations": self.stats.failed_translations,
            "avg_chars_per_second": round(
                self.stats.total_chars / max(self.stats.total_time, 0.001), 0
            ),
        }


def create_translator(
    api_key: Optional[str] = None,
    max_workers: Optional[int] = None,
) -> TranslationService:
    """
    Factory function to create a translation service.

    Args:
        api_key: Optional API key (uses env var if not provided)
        max_workers: Optional worker count

    Returns:
        Configured TranslationService instance
    """
    return TranslationService(api_key=api_key, max_workers=max_workers)
