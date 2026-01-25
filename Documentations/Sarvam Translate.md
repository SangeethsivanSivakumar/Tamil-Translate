# Sarvam Translate

> Sarvam Translate - Comprehensive translation model supporting all 22 official Indian languages with formal translation style and structured text optimization.

Sarvam Translate enables high-quality translation between English and 22 Indian languages. It provides comprehensive coverage of all scheduled Indian languages with formal translation style, making it ideal for official and professional communication needs.

## Key Features

<CardGroup cols={2}>
  <Card title="Wide Language Support" icon="globe">
    Support for all 22 scheduled Indian languages and English for comprehensive translation coverage.
  </Card>

  <Card title="Formal Style Translation" icon="paragraph">
    Default translation mode is formal to ensure clarity and consistency in professional communications.
  </Card>

  <Card title="Numeral Format Control" icon="calculator">
    Option to choose between international and native numeral systems for culturally appropriate translations.
  </Card>

  <Card title="Comprehensive Coverage" icon="shield-check">
    Complete support for all official Indian languages as per the Constitution of India.
  </Card>

  <Card title="High Quality Translation" icon="star">
    Formal translation style optimized for professional and official communication needs.
  </Card>
</CardGroup>

## Language Support

Sarvam Translate supports all 22 scheduled Indian languages as per the Constitution of India:

| Language  | Code   |
| --------- | ------ |
| Assamese  | as-IN  |
| Bengali   | bn-IN  |
| Bodo      | brx-IN |
| Dogri     | doi-IN |
| English   | en-IN  |
| Gujarati  | gu-IN  |
| Hindi     | hi-IN  |
| Kannada   | kn-IN  |
| Kashmiri  | ks-IN  |
| Konkani   | kok-IN |
| Maithili  | mai-IN |
| Malayalam | ml-IN  |
| Manipuri  | mni-IN |
| Marathi   | mr-IN  |
| Nepali    | ne-IN  |
| Odia      | od-IN  |
| Punjabi   | pa-IN  |
| Sanskrit  | sa-IN  |
| Santali   | sat-IN |
| Sindhi    | sd-IN  |
| Tamil     | ta-IN  |
| Telugu    | te-IN  |
| Urdu      | ur-IN  |

Supports bidirectional translation for all listed languages.

<Note>
  All languages support bidirectional translation. Specify the exact source language code for optimal translation quality.
</Note>

## Corpus BLEU (Bilingual Evaluation Understudy) Benchmark

Corpus BLEU score is a metric that evaluates the overall quality of machine translation by comparing it to reference translations across an entire dataset.
Higher scores (closer to 100) indicate better performance.

<ColumnChartBLEU
  data={[
    { label: "Assamese", value: 29.22 },
    { label: "Bengali", value: 8.10 },
    { label: "Bodo", value: 25.20 },
    { label: "Dogri", value: 18.03 },
    { label: "Gujarati", value: 28.41 },
    { label: "Hindi", value: 32.15 },
    { label: "Kannada", value: 23.08 },
    { label: "Kashmiri", value: 3.56 },
    { label: "Konkani", value: 22.30 },
    { label: "Maithili", value: 26.78 },
    { label: "Malayalam", value: 14.17 },
    { label: "Manipuri", value: 7.42 },
    { label: "Marathi", value: 29.13 },
    { label: "Nepali", value: 21.52 },
    { label: "Odia", value: 23.71 },
    { label: "Punjabi", value: 19.79 },
    { label: "Sanskrit", value: 25.56 },
    { label: "Santali", value: 12.82 },
    { label: "Sindhi", value: 7.04 },
    { label: "Tamil", value: 8.03 },
    { label: "Telugu", value: 29.25 },
    { label: "Urdu", value: 40.65 },
  ]}
  theme="auto"
/>

## Key Capabilities

<Tabs>
  <Tab title="Basic Usage">
    <div>
      Simple translation between any of the 22 supported Indian languages and English.
    </div>

    <Tabs>
      <Tab title="Python">
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(api_subscription_key="YOUR_SARVAM_API_KEY")

        response = client.text.translate(
            input="भारत एक महान देश है। इसकी संस्कृति बहुत पुरानी और समृद्ध है।",
            source_language_code="hi-IN",
            target_language_code="gu-IN",
            model="sarvam-translate:v1"
        )

        print(response)
        ```
      </Tab>

      <Tab title="JavaScript">
        ```javascript
        import { SarvamAIClient } from "sarvamai";

        const client = new SarvamAIClient({
          apiSubscriptionKey: "YOUR_SARVAM_API_KEY"
        });

        async function main() {
          const response = await client.text.translate({
            input: "भारत एक महान देश है। इसकी संस्कृति बहुत पुरानी और समृद्ध है।",
            source_language_code: "hi-IN",
            target_language_code: "gu-IN",
            model: "sarvam-translate:v1"
          });

          console.log(response);
        }

        main();
        ```
      </Tab>

      <Tab title="cURL">
        ```bash
        curl -X POST https://api.sarvam.ai/translate \
          -H "Content-Type: application/json" \
          -H "api-subscription-key: YOUR_SARVAM_API_KEY" \
          -d '{
            "input": "भारत एक महान देश है। इसकी संस्कृति बहुत पुरानी और समृद्ध है।",
            "source_language_code": "hi-IN",
            "target_language_code": "gu-IN",
            "model": "sarvam-translate:v1"
          }'
        ```
      </Tab>
    </Tabs>
  </Tab>

  <Tab title="Advanced Options">
    <div>
      Customize numeral formats for enhanced translation quality and cultural appropriateness.
    </div>

    <Tabs>
      <Tab title="Python">
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(api_subscription_key="YOUR_SARVAM_API_KEY")

        # With advanced options
        response = client.text.translate(
            input="The meeting is scheduled for 15th March, 2024 at 10:30 AM",
            source_language_code="en-IN",
            target_language_code="hi-IN",
            model="sarvam-translate:v1",
            numerals_format="native"  # Options: international, native
        )

        print(response)
        ```
      </Tab>

      <Tab title="JavaScript">
        ```javascript
        import { SarvamAIClient } from "sarvamai";

        const client = new SarvamAIClient({
          apiSubscriptionKey: "YOUR_SARVAM_API_KEY"
        });

        async function main() {
          // With advanced options
          const response = await client.text.translate({
            input: "The meeting is scheduled for 15th March, 2024 at 10:30 AM",
            source_language_code: "en-IN",
            target_language_code: "hi-IN",
            model: "sarvam-translate:v1",
            numerals_format: "native"  // Options: international, native
          });

          console.log(response);
        }

        main();
        ```
      </Tab>

      <Tab title="cURL">
        ```bash
        curl -X POST https://api.sarvam.ai/translate \
          -H "Content-Type: application/json" \
          -H "api-subscription-key: YOUR_SARVAM_API_KEY" \
          -d '{
            "input": "The meeting is scheduled for 15th March, 2024 at 10:30 AM",
            "source_language_code": "en-IN",
            "target_language_code": "hi-IN",
            "model": "sarvam-translate:v1",
            "numerals_format": "native"
          }'
        ```
      </Tab>
    </Tabs>
  </Tab>
</Tabs>

<Note>
  The `output_script` option is not supported in Sarvam Translate. For script control, use the [Mayura](/api-reference-docs/getting-started/models/mayura) model.
</Note>

## Next Steps

<CardGroup cols={3}>
  <Card title="Developer quickstart" icon="sparkles" href="/api-reference-docs/api-guides-tutorials/text-processing">
    Learn how to integrate translation into your application.
  </Card>

  <Card title="API Reference" icon="terminal" href="/api-reference-docs/text/translate-text">
    Complete API documentation for translation endpoints.
  </Card>

  <Card title="Cookbook" icon="book" href="/api-reference-docs/cookbook/starter-notebooks/translate-api-tutorial">
    Step-by-step tutorial for translation implementation.
  </Card>
</CardGroup>