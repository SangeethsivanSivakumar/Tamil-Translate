# Models

> Complete overview of Sarvam AI's specialized models for Indian languages. Choose the right model for your use case - from speech processing to text generation and translation.

Sarvam AI gives developers a purpose-built stack for building with Indian languages.
From speech-to-text, speech translation, and language translation to high-quality text-to-speech, our models are optimized for India’s multilingual landscape and culturally aligned use cases. With simple, production-ready APIs, developers can quickly build and ship reliable India-first AI experiences without worrying about the underlying complexity.

## Model Selection Guide

<CardGroup cols={3}>
  <Card title="Saarika: Speech to Text" icon="microphone" href="/api-reference-docs/getting-started/models/saarika" />

  <Card title="Saaras: Speech to Text Translate" icon="headphones" href="/api-reference-docs/getting-started/models/saaras" />

  <Card title="Bulbul: Text to Speech" icon="volume-up" href="/api-reference-docs/getting-started/models/bulbul" />

  <Card title="Mayura: Text Translation" icon="language" href="/api-reference-docs/getting-started/models/mayura" />

  <Card title="Sarvam-Translate: Text Translation" icon="globe" href="/api-reference-docs/getting-started/models/sarvam-translate" />

  <Card title="Sarvam-M: Chat & Reasoning" icon="brain" href="/api-reference-docs/getting-started/models/sarvam-m" />
</CardGroup>

## Language Support Overview

### Core Indic Languages

| Language | Code    |   | Language  | Code    |
| -------- | ------- | - | --------- | ------- |
| Hindi    | `hi-IN` |   | Kannada   | `kn-IN` |
| Bengali  | `bn-IN` |   | Malayalam | `ml-IN` |
| Tamil    | `ta-IN` |   | Marathi   | `mr-IN` |
| Telugu   | `te-IN` |   | Punjabi   | `pa-IN` |
| Gujarati | `gu-IN` |   | Odia      | `od-IN` |
| English  | `en-IN` |   |           |         |

### Sarvam Translate: Complete 22 Indian Language Support

In addition to the core Indic languages above, Sarvam Translate supports all 22 official Indian languages including:

| Language | Code     |   | Language | Code     |
| -------- | -------- | - | -------- | -------- |
| Assamese | `as-IN`  |   | Maithili | `mai-IN` |
| Bodo     | `brx-IN` |   | Manipuri | `mni-IN` |
| Dogri    | `doi-IN` |   | Nepali   | `ne-IN`  |
| Kashmiri | `ks-IN`  |   | Sanskrit | `sa-IN`  |
| Konkani  | `kok-IN` |   | Santali  | `sat-IN` |
| Sindhi   | `sd-IN`  |   | Urdu     | `ur-IN`  |

***

## Model Language Support Summary

| Model                                       | Languages            |
| ------------------------------------------- | -------------------- |
| **Saarika Speech-to-Text Model**            | 11 languages support |
| **Saaras Speech-to-Text Translation Model** | 11 languages support |
| **Bulbul Text-to-Speech Model**             | 11 languages support |
| **Mayura Translation Model**                | 11 languages support |
| **Sarvam Translate Model**                  | 22 languages support |

***

## Use Cases

<Tabs>
  <Tab title="Voice Assistant">
    ### Build a multilingual voice assistant

    1. **Speech Input**: Use Saarika to convert user speech to text
    2. **Understanding**: Process with Sarvam-M for intelligent responses
    3. **Speech Output**: Convert responses to speech with Bulbul

    Perfect for customer service, smart home devices, and accessibility applications.

    [Learn how to build a voice agent with LiveKit →](/api-reference-docs/cookbook/integration/build-voice-agent-with-live-kit)
  </Tab>

  <Tab title="Content Localization">
    ### Localize content across Indian languages

    Build end-to-end multilingual experiences from audio to translated speech:

    1. **Transcribe speech**: Use Sarvam Speech-to-Text to accurately convert audio in Indian languages into text.
    2. **Translate at scale**: Convert transcripts across 22 Indian languages with Sarvam Translate.
    3. **Generate localized audio**: Turn translated text into natural, production-ready speech with Bulbul's high-quality voices.

    This gives you a complete pipeline — speech → text → translation → localized audio — enabling developers to deliver fully localized content for apps, videos, learning platforms, and product experiences with minimal engineering effort.
  </Tab>

  <Tab title="Call Center Analytics">
    ### Analyze multilingual customer interactions

    1. **Speech Recognition**: Convert calls to text with Saarika
    2. **Translation**: Standardize to English with Saaras for analysis
    3. **Insights**: Extract patterns and sentiment from conversations

    Essential for customer experience optimization and compliance monitoring.

    [Learn how to analyze calls with our analytics cookbook →](/api-reference-docs/cookbook/example-guides/call-analytics-cookbook)
  </Tab>

  <Tab title="Educational Platform">
    ### Create inclusive learning experiences

    1. **Content Translation**: Make materials accessible in 22 languages
    2. **Audio Learning**: Generate pronunciation guides with Bulbul
    3. **Interactive Chat**: Enable Q\&A with Sarvam-M in native languages

    Perfect for online education, language learning, and skill development platforms.
  </Tab>
</Tabs>