# Mayura

> Mayura - Advanced multilingual translation model for Indian languages with customizable translation styles, script control, and intelligent code-mixed content handling.

Mayura is our powerful translation model designed to convert text between English and Indian languages while preserving meaning and context.
It supports advanced features such as:

* **Customizable translation styles**
* **Script control**
* **Intelligent handling of code-mixed content**

For example:\
`"मैं ऑफिस जा रहा हूँ"` → `"I am going to the office"`\
This preserves the original meaning across different scripts and languages.

## Key Features

<CardGroup cols={2}>
  <Card title="Language Support" icon="language">
    Support for 11 languages including English and major Indian languages. Automatic language detection available by setting source\_language\_code to "auto".
  </Card>

  <Card title="Translation Modes" icon="wand-magic-sparkles">
    Multiple translation styles: formal, modern-colloquial, classic-colloquial, and code-mixed for different contexts.
  </Card>

  <Card title="Script Control" icon="pen-nib">
    Flexible output script options: Roman, native, and spoken forms for customized text representation.
  </Card>

  <Card title="Smart Processing" icon="gears">
    Numeral format control for improved translation accuracy.
  </Card>

  <Card title="Context Preservation" icon="shield">
    Maintains meaning and context across languages while handling cultural nuances appropriately.
  </Card>

  <Card title="Code-Mixed Support" icon="code">
    Intelligent handling of mixed-language content common in Indian conversations.
  </Card>
</CardGroup>

## Language Support

Mayura supports bidirectional translation between the following languages:

Languages (Code):

Hindi (`hi-IN`), Bengali (`bn-IN`), Tamil (`ta-IN`), Telugu (`te-IN`), Gujarati (`gu-IN`), Kannada (`kn-IN`), Malayalam (`ml-IN`), Marathi (`mr-IN`), Punjabi (`pa-IN`), Odia (`od-IN`), English (`en-IN`)

All of the above supports both English ↔ Indian language translations.

<Note>
  All Indian languages support bidirectional translation with English. To enable automatic language detection, set source\_language\_code to "auto" in your API request.
</Note>

<Note>
  Use the [Sarvam-Translate](/api-reference-docs/getting-started/models/sarvam-translate) model to support all 22 official Indian languages.
</Note>

## Corpus BLEU (Bilingual Evaluation Understudy) Benchmark

Corpus BLEU score is a metric that evaluates the overall quality of machine translation by comparing it to reference translations across an entire dataset.
Higher scores (closer to 100) indicate better performance.

<ColumnChartMayura
  data={[
    { label: "Bengali", value: 18.14 },
    { label: "Gujarati", value: 27.32 },
    { label: "Hindi", value: 24.86 },
    { label: "Kannada", value: 23.86 },
    { label: "Malayalam", value: 14.64 },
    { label: "Marathi", value: 32.56 },
    { label: "Odia", value: 27.57 },
    { label: "Punjabi", value: 9.19 },
    { label: "Tamil", value: 6.78 },
    { label: "Telugu", value: 37.57 },
  ]}
  theme="auto"
/>

## Key Capabilities

<Tabs>
  <Tab title="Basic Usage">
    <div>
      Simple translation between languages with default settings. Perfect for getting started with the Mayura API.
    </div>

    <Tabs>
      <Tab title="Python">
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(
            api_subscription_key="YOUR_SARVAM_API_KEY"
        )

        response = client.text.translate(
            input="मैं ऑफिस जा रहा हूँ",
            source_language_code="hi-IN",
            target_language_code="en-IN"
        )

        print(response)
        ```
      </Tab>

      <Tab title="JavaScript">
        ```javascript
        import { SarvamAIClient } from "sarvamai";

        const client = new SarvamAIClient({
          apiSubscriptionKey: 'YOUR_SARVAM_API_KEY'
        });

        async function main() {
          const response = await client.text.translate({
            input: 'मैं ऑफिस जा रहा हूँ',
            source_language_code: 'hi-IN',
            target_language_code: 'en-IN'
          });

          console.log(response);
        }

        main();
        ```
      </Tab>

      <Tab title="cURL">
        ```bash
        curl -X POST https://api.sarvam.ai/translate \
          -H "api-subscription-key: YOUR_SARVAM_API_KEY" \
          -H "Content-Type: application/json" \
          -d '{
            "input": "मैं ऑफिस जा रहा हूँ",
            "source_language_code": "hi-IN",
            "target_language_code": "en-IN"
          }'
        ```
      </Tab>
    </Tabs>
  </Tab>

  <Tab title="Translation Modes">
    <div>
      Customize the translation style with different modes to match your needs - formal, colloquial, or code-mixed.
    </div>

    <Tabs>
      <Tab title="Python">
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(
            api_subscription_key="YOUR_SARVAM_API_KEY"
        )

        # Translation with style control
        response = client.text.translate(
            input="Your EMI of Rs. 3000 is pending",
            source_language_code="en-IN",
            target_language_code="hi-IN",
            mode="modern-colloquial",     # Options: formal, modern-colloquial, classic-colloquial, code-mixed
            speaker_gender="Female"       # For code-mixed translations
        )

        print(response)
        ```
      </Tab>

      <Tab title="JavaScript">
        ```javascript
        import { SarvamAIClient } from "sarvamai";

        const client = new SarvamAIClient({
          apiSubscriptionKey: 'YOUR_SARVAM_API_KEY'
        });

        async function main() {
          // Translation with style control
          const response = await client.text.translate({
            input: 'Your EMI of Rs. 3000 is pending',
            source_language_code: 'en-IN',
            target_language_code: 'hi-IN',
            mode: 'modern-colloquial',     // Options: formal, modern-colloquial, classic-colloquial, code-mixed
            speakerGender: 'Female'        // For code-mixed translations
          });

          console.log(response);
        }

        main();
        ```
      </Tab>

      <Tab title="cURL">
        ```bash
        curl -X POST https://api.sarvam.ai/translate \
          -H "api-subscription-key: YOUR_SARVAM_API_KEY" \
          -H "Content-Type: application/json" \
          -d '{
            "input": "Your EMI of Rs. 3000 is pending",
            "source_language_code": "en-IN",
            "target_language_code": "hi-IN",
            "mode": "modern-colloquial",
            "speaker_gender": "Female"
          }'
        ```
      </Tab>
    </Tabs>
  </Tab>

  <Tab title="Script Control">
    <div>
      Control the output script format with options for Roman, native, and spoken forms.
    </div>

    <Tabs>
      <Tab title="Python">
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(
            api_subscription_key="YOUR_SARVAM_API_KEY"
        )

        # With script and numeral control
        response = client.text.translate(
            input="Your EMI of Rs. 3000 is pending",
            source_language_code="en-IN",
            target_language_code="hi-IN",
            output_script="fully-native",    # Options: roman, fully-native, spoken-form-in-native
            numerals_format="native"         # Options: international, native
        )

        print(response)
        ```
      </Tab>

      <Tab title="JavaScript">
        ```javascript
        import { SarvamAIClient } from "sarvamai";

        const client = new SarvamAIClient({
          apiSubscriptionKey: 'YOUR_SARVAM_API_KEY'
        });

        async function main() {
          // With script and numeral control
          const response = await client.text.translate({
            input: 'Your EMI of Rs. 3000 is pending',
            source_language_code: 'en-IN',
            target_language_code: 'hi-IN',
            outputScript: 'fully-native',    // Options: roman, fully-native, spoken-form-in-native
            numeralsFormat: 'native'         // Options: international, native
          });

          console.log(response);
        }

        main();
        ```
      </Tab>

      <Tab title="cURL">
        ```bash
        curl -X POST https://api.sarvam.ai/translate \
          -H "api-subscription-key: YOUR_SARVAM_API_KEY" \
          -H "Content-Type: application/json" \
          -d '{
            "input": "Your EMI of Rs. 3000 is pending",
            "source_language_code": "en-IN",
            "target_language_code": "hi-IN",
            "output_script": "fully-native",
            "numerals_format": "native"
          }'
        ```
      </Tab>
    </Tabs>

    <Note>
      Output script options provide different text representations:

      * roman: "aapka Rs. 3000 ka EMI pending hai"
      * fully-native: "आपका रु. 3000 का ई.एम.ऐ. पेंडिंग है।"
      * spoken-form-in-native: "आपका थ्री थाउजेंड रूपीस का ईएमअइ पेंडिंग है।"
    </Note>
  </Tab>

  <Tab title="Advanced Options">
    <div>
      Customize language detection for better translation quality.
    </div>

    <Tabs>
      <Tab title="Python">
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(
            api_subscription_key="YOUR_SARVAM_API_KEY"
        )

        # With advanced options
        response = client.text.translate(
            input="Your text here",
            source_language_code="auto",    # Set to "auto" to enable automatic language detection
            target_language_code="hi-IN"
        )

        print(response)
        ```
      </Tab>

      <Tab title="JavaScript">
        ```javascript
        import { SarvamAIClient } from "sarvamai";

        const client = new SarvamAIClient({
          apiSubscriptionKey: 'YOUR_SARVAM_API_KEY'
        });

        async function main() {
          // With advanced options
          const response = await client.text.translate({
            input: 'Your text here',
            source_language_code: 'auto',     // Set to "auto" to enable automatic language detection
            target_language_code: 'hi-IN'
          });

          console.log(response);
        }

        main();
        ```
      </Tab>

      <Tab title="cURL">
        ```bash
        curl -X POST https://api.sarvam.ai/translate \
          -H "api-subscription-key: YOUR_SARVAM_API_KEY" \
          -H "Content-Type: application/json" \
          -d '{
            "input": "Your text here",
            "source_language_code": "auto",
            "target_language_code": "hi-IN"
          }'
        ```
      </Tab>
    </Tabs>

    <Note>
      To use automatic language detection, you must explicitly set source\_language\_code to "auto" in your request. The model will then automatically detect the input language.
    </Note>
  </Tab>
</Tabs>

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