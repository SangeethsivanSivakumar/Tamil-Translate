# Translate API Tutorial

# **Translate API using Mayura and Sarvam-Translate Models**

# **Overview**

This tutorial demonstrates how to use the **Sarvam translate API** to translate texts/paragraphs from one language to another. The API supports additional features such as transliteration (a type of conversion of a text from one script to another that involves swapping letters), output\_Script and gender.

## **1. Installation**

Before you begin, ensure you have the necessary Python libraries installed. Run the following commands to install the required packages:

```bash
pip install -Uqq sarvamai
```

```python
from sarvamai import SarvamAI
```

## **2. Authentication**

To use the API, you need an API subscription key. Follow these steps to set up your API key:

1. **Obtain your API key**: If you don’t have an API key, sign up on the [Sarvam AI Dashboard](https://dashboard.sarvam.ai/) to get one.
2. **Replace the placeholder key**: In the code below, replace "YOUR\_SARVAM\_AI\_API\_KEY" with your actual API key.

```python
SARVAM_API_KEY = "YOUR_SARVAM_API_KEY"
```

## **3. Understanding the Parameters**

🔹 The API takes several key parameters:

| **Parameter**          | **Description**                                         | **Mayura:v1**                                                                                | **Sarvam-Translate:v1**                                                                                                         |
| ---------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `input`                | The text to translate (max character limit)             | 1000 characters                                                                              | 2000 characters                                                                                                                 |
| `source_language_code` | Language of the input text                              | Bengali, English, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu | All Mayura:v1 languages + Assamese, Bodo, Dogri, Konkani, Kashmiri, Maithili, Manipuri, Nepali, Sanskrit, Santali, Sindhi, Urdu |
| `target_language_code` | Target language for translation                         | Same as source                                                                               | Same as source                                                                                                                  |
| `speaker_gender`       | Gender of the speaker for better contextual translation | Supported                                                                                    | Supported                                                                                                                       |
| `mode`                 | Tone or style of translation                            | Supports `formal`, `classic-colloquial`, `modern-colloquial`                                 | `formal` supported                                                                                                              |
| `numerals_format`      | Format for numerals in translation                      | `international` (0-9) or `native` (e.g., १-९)                                                | `international` (0-9) or `native` (e.g., १-९)                                                                                   |

**`language_code`** (String) – Newly added languages. Supported values:

* `"as-IN"` (Assamese - India)
* `"brx-IN"` (Bodo- India)
* `"doi-IN"` (Dogri - India)
* `"kok-IN"` (Konkani - India)
* `"ks-IN"` (Kashmiri - India)
* `"mai-IN"` (Maithili - India)
* `"mni-IN"` (Manipuri (Meiteilon) - India)
* `"ne-IN"` (Nepali - India)
* `"sa-IN"` (Sanskrit - India)
* `"sat-IN"` (Santali - India)
* `"sd-IN"` (Sindhi - India)
* `"ur-IN"` (Urdu - India)

## **4. Basic Usage**

### **4.1: Read the Document**

We have two sample documents under the `data` folder:

* [Download sample1.txt](https://github.com/sarvamai/sarvam-ai-cookbook/blob/main/notebooks/translate/data/sample3.txt)
* [Download sample2.txt](https://github.com/sarvamai/sarvam-ai-cookbook/blob/main/notebooks/translate/data/sample4.txt)

```python
def read_file(file_path, lang_name):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            # Read the first 5 lines
            lines = [next(file) for _ in range(5)]
            print(f"=== {lang_name} Text (First Few Lines) ===")
            print("".join(lines))  # Print first few lines

            # Read the remaining content
            remaining_text = file.read()

            # Combine all text
            full_doc = "".join(lines) + remaining_text

            # Count total characters
            total_chars = len(full_doc)
            print(f"\nTotal number of characters in {lang_name} file:", total_chars)

            return full_doc
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")
        return None
```

```python
# Read English and Hindi documents
english_doc = read_file("sample1.txt", "English")
hindi_doc = read_file("sample2.txt", "Hindi")
```

### **4.2: Split the input text into chunks based on model limits**

For Mayura:v1, the API has a maximum chunk size of 1000 characters per request.

For Sarvam-Translate:v1, the API has a maximum chunk size of 2000 characters per request.

we need to split the text accordingly.

```python
def chunk_text(text, max_length=2000):
    """Splits text into chunks of at most max_length characters while preserving word boundaries."""
    chunks = []

    while len(text) > max_length:
        split_index = text.rfind(" ", 0, max_length)  # Find the last space within limit
        if split_index == -1:
            split_index = max_length  # No space found, force split at max_length

        chunks.append(text[:split_index].strip())  # Trim spaces before adding
        text = text[split_index:].lstrip()  # Remove leading spaces for the next chunk

    if text:
        chunks.append(text.strip())  # Add the last chunk

    return chunks
```

```python
# Split the text
english_text_chunks = chunk_text(english_doc)

# Display chunk info
print(f"Total Chunks: {len(english_text_chunks)}")
for i, chunk in enumerate(
    english_text_chunks[:3], 1
):  # Show only first 3 chunks for preview
    print(f"\n=== Chunk {i} (Length: {len(chunk)}) ===\n{chunk}")
```

```python
# Split the text
hindi_text_chunks = chunk_text(hindi_doc)

# Display chunk info
print(f"Total Chunks: {len(hindi_text_chunks)}")
for i, chunk in enumerate(
    hindi_text_chunks[:3], 1
):  # Show only first 3 chunks for preview
    print(f"\n=== Chunk {i} (Length: {len(chunk)}) ===\n{chunk}")
```

### **4.3: Sample Hindi to Sanskrit Translation using Sarvam-Translate:v1**

sarvam-translate:v1: Supports all 22 scheduled languages of India, formal mode only.

```python
# Sample Hindi text (can be up to 2000 characters per chunk for sarvam-translate:v1)
hindi_text = "भारत एक महान देश है। इसकी संस्कृति बहुत पुरानी और समृद्ध है।"

# Simple chunking for demonstration (no chunk exceeds 2000 characters)
hindi_text_chunks = [hindi_text]  # In real cases, you would split longer text here

# Loop through each chunk and translate
for idx, chunk in enumerate(hindi_text_chunks):
    response = client.text.translate(
        input=chunk,
        source_language_code="hi-IN",
        target_language_code="sa-IN",
        speaker_gender="Male",
        mode="formal",
        model="sarvam-translate:v1",
    )

    # Print the translated output
    print(f"Chunk {idx + 1} Translation:\n{response.translated_text}\n")
```

### **4.4: Setting up the API Endpoint using Sarvam-Translate model**

There are three main types of translations we support:

1️⃣ **English to Indic** 🏛 → Translating from **English to Indian languages** (e.g., *"Invoice total is $3,450.75." → "इनवॉइस कुल राशि $3,450.75 है।"*)

2️⃣ **Indic to English** 🌍 → Converting **Indian languages to English** (e.g., *"आपका ऑर्डर सफलतापूर्वक दर्ज किया गया है।" → "Your order has been successfully placed."*)

3️⃣ **Indic to Indic** 🔄 → Translating **between Indian languages** (e.g., *Hindi → Tamil, Bengali → Marathi*).

```python
# Initialize SarvamAI

from sarvamai import SarvamAI

client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
```

### **English to Indic Translation**

```python
translated_texts = []
for idx, chunk in enumerate(english_text_chunks):
    response = client.text.translate(
        input=chunk,
        source_language_code="en-IN",
        target_language_code="sa-IN",
        speaker_gender="Male",
        mode="formal",
        model="sarvam-translate:v1",
    )

    translated_text = response.translated_text
    print(f"\n=== Translated Chunk {idx + 1} ===\n{translated_text}\n")
    translated_texts.append(translated_text)

# Combine all translated chunks
final_translation = "\n".join(translated_texts)
print("\n=== Final Translated Text in Sanskrit ===")
print(final_translation)
```

### **Indic to English Translation**

```python
translated_texts = []
for idx, chunk in enumerate(hindi_text_chunks):
    response = client.text.translate(
        input=chunk,
        source_language_code="hi-IN",
        target_language_code="sd-IN",
        speaker_gender="Male",
        mode="formal",
        model="sarvam-translate:v1",
    )

    translated_text = response.translated_text
    print(f"\n=== Translated Chunk {idx + 1} ===\n{translated_text}\n")
    translated_texts.append(translated_text)

# Combine all translated chunks
final_translation = "\n".join(translated_texts)
print("\n=== Final Translated Text in Sindhi ===")
print(final_translation)
```

### **Indic to Indic Translation**

```python
translated_texts = []
for idx, chunk in enumerate(hindi_text_chunks):
    response = client.text.translate(
        input=chunk,
        source_language_code="hi-IN",
        target_language_code="bn-IN",
        speaker_gender="Male",
        mode="formal",
        model="sarvam-translate:v1",
    )

    translated_text = response.translated_text
    print(f"\n=== Translated Chunk {idx + 1} ===\n{translated_text}\n")
    translated_texts.append(translated_text)

# Combine all translated chunks
final_translation = "\n".join(translated_texts)
print("\n=== Translated Text Chunks in Bengali ===")
print(final_translation)
```

## **5. Advanced Features**

### **5.1: Translation Modes & Differences**

1️⃣ **Formal** – Highly professional, uses **pure Hindi** (e.g., *"कुल राशि", "देय है"*). Suitable for **official documents, legal papers, and corporate communication**.

2️⃣ **Classic-Colloquial** – Balanced mix of **Hindi & English**, slightly informal (e.g., *"कुल जोड़", "देना होगा"*). Ideal for **business emails, customer support, and semi-formal communication**.

3️⃣ **Modern-Colloquial** – **Hinglish, casual, and direct** (e.g., *"Invoice total", "due है", "contact करो"*). Best for **chatbots, social media, and casual conversations**.

**📌 Rule of Thumb:**

* **Use Formal for official content** 🏛
* **Use Classic-Colloquial for general communication** 💬
* **Use Modern-Colloquial for everyday conversations** 🚀

```python
# To highlight the difference between the models lets use the below example.
full_text = (
    "The invoice total is $3,450.75, due by 15th March 2025. Contact us at support@example.com for queries. "
    "Order #987654321 was placed on 02/29/2024. Your tracking ID is TRK12345678."
)
```

### **Formal**

Supported by both Mayura:v1 and Sarvam-Translate:v1.

```python
response = client.text.translate(
    input=full_text,
    source_language_code="en-IN",
    target_language_code="hi-IN",
    speaker_gender="Male",
    mode="formal",
    model="sarvam-translate:v1",
)
translated_text = response.translated_text
print("\n=== Translated Text ===\n", translated_text)
```

### **Classic Colloquial**

Supported only by Mayura:v1 model.

```python
response = client.text.translate(
    input=full_text,
    source_language_code="en-IN",
    target_language_code="hi-IN",
    speaker_gender="Male",
    mode="classic-colloquial",
    model="mayura:v1",
)
translated_text = response.translated_text
print("\n=== Translated Text ===\n", translated_text)
```

### **Modern Colloquial**

Supported only by Mayura:v1 model.

```python
response = client.text.translate(
    input=full_text,
    source_language_code="en-IN",
    target_language_code="hi-IN",
    speaker_gender="Male",
    mode="modern-colloquial",
    model="mayura:v1",
)
translated_text = response.translated_text
print("\n=== Translated Text ===\n", translated_text)
```

### **5.2: Speaker Gender**

The translation model supports **Male** and **Female** speaker options, which impact the tone and style of the output.

1️⃣ **Male Voice** 🔵

2️⃣ **Female Voice** 🔴

### **Female**

```python
response = client.text.translate(
    input=full_text,
    source_language_code="en-IN",
    target_language_code="hi-IN",
    speaker_gender="Female",
    mode="formal",
    model="sarvam-translate:v1",
)
translated_text = response.translated_text
print("\n=== Translated Text ===\n", translated_text)
```

### **Male**

```python
response = client.text.translate(
    input=full_text,
    source_language_code="en-IN",
    target_language_code="hi-IN",
    speaker_gender="Male",
    mode="formal",
    model="sarvam-translate:v1",
)
translated_text = response.translated_text
print("\n=== Translated Text ===\n", translated_text)
```

### **5.3: Numerals Format Feature**

The `numerals_format` parameter controls how numbers appear in the translation. It has two options:

1️⃣ **International (Default)** 🌍 → Uses standard **0-9** numerals.\
✅ Example: *"मेरा phone number है: 9840950950."*\
✅ Best for **universally understood content, technical documents, and modern usage**.

2️⃣ **Native** 🔡 → Uses **language-specific** numerals.\
✅ Example: *"मेरा phone number है: ९८४०९५०९५०."*\
✅ Ideal for **traditional texts, cultural adaptation, and regional content**.

**📌 When to Use What?**

* Use **International** for **wider readability and digital content** 📱
* Use **Native** for **localized, heritage-focused, and print media content** 📖

### **Native**

```python
response = client.text.translate(
    input=full_text,
    source_language_code="en-IN",
    target_language_code="hi-IN",
    speaker_gender="Male",
    mode="formal",
    model="sarvam-translate:v1",
    numerals_format="native",
)
translated_text = response.translated_text
print("\n=== Translated Text ===\n", translated_text)
```

### **International**

```python
response = client.text.translate(
    input=full_text,
    source_language_code="en-IN",
    target_language_code="hi-IN",
    speaker_gender="Male",
    mode="formal",
    model="sarvam-translate:v1",
    numerals_format="international",
)
translated_text = response.translated_text
print("\n=== Translated Text ===\n", translated_text)
```

### **5.4: Numerals Format Feature**

The `output_script` parameter controls how the translated text is **transliterated**, i.e., how it appears in different scripts while keeping pronunciation intact.

### **Transliteration Options for Mayura:**

1️⃣ **Default (null)** – No transliteration applied.\
✅ Example: *"आपका Rs. 3000 का EMI pending है।"*\
✅ Best for **modern, mixed-language content**.

2️⃣ **Roman** – Converts the output into **Romanized Hindi**.\
✅ Example: *"aapka Rs. 3000 ka EMI pending hai."*\
✅ Ideal for **users who can speak but not read native scripts**.

3️⃣ **Fully-Native** – Uses **formal native script transliteration**.\
✅ Example: *"आपका रु. 3000 का ई.एम.ऐ. पेंडिंग है।"*\
✅ Best for **official documents and structured writing**.

4️⃣ **Spoken-Form-in-Native** – Uses **native script but mimics spoken style**.\
✅ Example: *"आपका थ्री थाउजेंड रूपीस का ईएमअइ पेंडिंग है।"*\
✅ Ideal for **voice assistants, conversational AI, and informal speech**.

### **📌 When to Use What?**

* **Default** – For natural, mixed-language modern writing ✍️
* **Roman** – For users unfamiliar with native scripts 🔤
* **Fully-Native** – For formal, structured translations 🏛
* **Spoken-Form-in-Native** – For casual speech and voice applications 🎙

```python
response = client.text.translate(
    input=full_text,
    source_language_code="en-IN",
    target_language_code="hi-IN",
    speaker_gender="Male",
    mode="modern-colloquial",
    model="mayura:v1",
    output_script="roman",
    numerals_format="international",
)
translated_text = response.translated_text
print("\n=== Translated Text ===\n", translated_text)
```

```python
response = client.text.translate(
    input=full_text,
    source_language_code="en-IN",
    target_language_code="hi-IN",
    speaker_gender="Male",
    mode="modern-colloquial",
    model="mayura:v1",
    output_script="spoken-form-in-native",
    numerals_format="international",
)
translated_text = response.translated_text
print("\n=== Translated Text ===\n", translated_text)
```

```python
response = client.text.translate(
    input=full_text,
    source_language_code="en-IN",
    target_language_code="hi-IN",
    speaker_gender="Male",
    mode="modern-colloquial",
    model="mayura:v1",
    output_script="fully-native",
    numerals_format="international",
)
translated_text = response.translated_text
print("\n=== Translated Text ===\n", translated_text)
```

🚫 Note: For sarvam-translate:v1 - Transliteration is not supported

## **6. Error Handling**

You may encounter these errors while using the API:

* **403 Forbidden** (`invalid_api_key_error`)

  * Cause: Invalid API key.
  * Solution: Use a valid API key from the [Sarvam AI Dashboard](https://dashboard.sarvam.ai/).

* **429 Too Many Requests** (`insufficient_quota_error`)

  * Cause: Exceeded API quota.
  * Solution: Check your usage, upgrade if needed, or implement exponential backoff when retrying.

* **500 Internal Server Error** (`internal_server_error`)

  * Cause: Issue on our servers.
  * Solution: Try again later. If persistent, contact support.

* **400 Bad Request** (`invalid_request_error`)
  * Cause: Incorrect request formatting.
  * Solution: Verify your request structure and parameters.

## **7. Additional Resources**

For more details, refer to the our official documentation and we are always there to support and help you on our Discord Server:

* **Documentation**: [docs.sarvam.ai](https://docs.sarvam.ai)
* **Community**: [Join the Discord Community](https://discord.com/invite/5rAsykttcs)

***

## **8. Final Notes**

* Keep your API key secure.
* Use clear audio for best results.
* Explore advanced features like diarization and translation.

**Keep Building!** 🚀