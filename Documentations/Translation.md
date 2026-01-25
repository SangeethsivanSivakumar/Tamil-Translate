# Text Translation API

> Complete overview of Sarvam AI Text Translation API supporting English to Indian languages and vice versa with multiple translation modes and high accuracy.

## Translation Types

<CardGroup cols={3}>
  <Card title="English to Indic" icon="language" color="#00aa55">
    Translate from English to various Indian languages with support for
    different translation modes.
  </Card>

  {" "}

  <Card title="Indic to English" icon="arrow-right-arrow-left" color="#0062ff">
    Convert Indian languages to English with high accuracy and natural output.
  </Card>

  <Card title="Indic to Indic" icon="arrows-rotate" color="#da62c4">
    Translate between different Indian languages while preserving context and
    meaning.
  </Card>
</CardGroup>

## Translation Modes

<CardGroup cols={3}>
  <Card title="Formal" icon="building">
    Highly professional, uses pure language forms. Ideal for official documents
    and legal papers.
  </Card>

  {" "}

  <Card title="Classic-Colloquial" icon="book">
    Balanced mix of languages, slightly informal. Perfect for business emails and
    general communication.
  </Card>

  <Card title="Modern-Colloquial" icon="comments">
    Casual and direct style with mixed language. Best for chatbots and social
    media content.
  </Card>
</CardGroup>

## Code Examples

<Tabs>
  <Tab title="Basic Translation">
    <Tabs>
      <Tab title="Python">
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(
            api_subscription_key="YOUR_SARVAM_API_KEY"
        )

        response = client.text.translate(
            input="Hello, how are you?",
            source_language_code="en-IN",
            target_language_code="hi-IN",
            speaker_gender="Male"
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

        const response = await client.text.translate({
            input: "Hello, how are you?",
            source_language_code: "en-IN",
            target_language_code: "hi-IN",
            speaker_gender: "Male"
        });

        console.log(response);
        ```
      </Tab>

      <Tab title="cURL">
        ```bash
        curl -X POST https://api.sarvam.ai/translate \
        -H "api-subscription-key: <YOUR_SARVAM_API_KEY>" \
        -H "Content-Type: application/json" \
        -d '{
        "input": "Hello, how are you?",
        "source_language_code": "en-IN",
        "target_language_code": "hi-IN",
        "speaker_gender": "Male"
        }'
        ```
      </Tab>
    </Tabs>
  </Tab>

  <Tab title="Advanced Options">
    <div>
      <h3>
        Advanced Translation Features
      </h3>

      <p>
        Explore different parameters to customize your translation output:
      </p>
    </div>

    <Tabs>
      <Tab title="Speaker Gender">
        <p>
          Choose between Male and Female voice characteristics for gender-specific translations.
        </p>

        <Tabs>
          <Tab title="Python">
            ```python
            response = client.text.translate(
                input="Welcome to our service!",
                source_language_code="en-IN",
                target_language_code="hi-IN",
                model="mayura:v1",
                speaker_gender="Female"
            )
            ```
          </Tab>

          <Tab title="JavaScript">
            ```javascript
            const response = await client.text.translate({
                input: "Welcome to our service!",
                source_language_code: "en-IN",
                target_language_code: "hi-IN",
                model: "mayura:v1",
                speaker_gender: "Female"
            });
            ```
          </Tab>

          <Tab title="cURL">
            ```bash
            curl -X POST https://api.sarvam.ai/translate \
            -H "api-subscription-key: <YOUR_SARVAM_API_KEY>" \
            -H "Content-Type: application/json" \
            -d '{
            "input": "Hello, how are you?",
            "source_language_code": "en-IN",
            "target_language_code": "hi-IN",
            "speaker_gender": "Female"
            }'
            ```
          </Tab>
        </Tabs>
      </Tab>

      <Tab title="Translation Mode">
        <p>
          Select the tone and style of translation - formal, modern-colloquial, or classic-colloquial for different use cases.
        </p>

        <Tabs>
          <Tab title="Python">
            ```python
            response = client.text.translate(
                input="Welcome to our service!",
                source_language_code="en-IN",
                target_language_code="hi-IN",
                model="mayura:v1",
                mode="modern-colloquial"
            )
            ```
          </Tab>

          <Tab title="JavaScript">
            ```javascript
            const response = await client.text.translate({
                input: "Welcome to our service!",
                source_language_code: "en-IN",
                target_language_code: "hi-IN",
                model: "mayura:v1",
                mode: "modern-colloquial"
            });
            ```
          </Tab>

          <Tab title="cURL">
            ```bash
            curl -X POST https://api.sarvam.ai/translate \
            -H "api-subscription-key: <YOUR_SARVAM_API_KEY>" \
            -H "Content-Type: application/json" \
            -d '{
            "input": "Welcome to our service!",
            "source_language_code": "en-IN",
            "target_language_code": "hi-IN",
            "model": "mayura:v1",
            "mode": "modern-colloquial"
            }'
            ```
          </Tab>
        </Tabs>
      </Tab>

      <Tab title="Output Script">
        <p>
          Choose between different script options (roman/fully-native/spoken-form-in-native) for the translated text output.
        </p>

        <Tabs>
          <Tab title="Python">
            ```python
            response = client.text.translate(
                input="Welcome to our service!",
                source_language_code="en-IN",
                target_language_code="hi-IN",
                model="mayura:v1",
                output_script="fully-native"
            )
            ```
          </Tab>

          <Tab title="JavaScript">
            ```javascript
            const response = await client.text.translate({
                input: "Welcome to our service!",
                source_language_code: "en-IN",
                target_language_code: "hi-IN",
                model: "mayura:v1",
                output_script: "fully-native"
            });
            ```
          </Tab>

          <Tab title="cURL">
            ```bash
            curl -X POST https://api.sarvam.ai/translate \
            -H "api-subscription-key: <YOUR_SARVAM_API_KEY>" \
            -H "Content-Type: application/json" \
            -d '{
            "input": "Welcome to our service!",
            "source_language_code": "en-IN",
            "target_language_code": "hi-IN",
            "model": "mayura:v1",
            "output_script": "fully-native"
            }'
            ```
          </Tab>
        </Tabs>
      </Tab>

      <Tab title="Numerals Format">
        <p>
          Specify the format for numbers in the output - choose between international (1,2,3) or native numerals (१,२,३).
        </p>

        <Tabs>
          <Tab title="Python">
            ```python
            response = client.text.translate(
                input="Welcome to our service!",
                source_language_code="en-IN",
                target_language_code="hi-IN",
                model="mayura:v1",
                numerals_format="native"
            )
            ```
          </Tab>

          <Tab title="JavaScript">
            ```javascript
            const response = await client.text.translate({
                input: "Welcome to our service!",
                source_language_code: "en-IN",
                target_language_code: "hi-IN",
                model: "mayura:v1",
                numerals_format: "native"
            });
            ```
          </Tab>

          <Tab title="cURL">
            ```bash
            curl -X POST https://api.sarvam.ai/translate \
            -H "api-subscription-key: <YOUR_SARVAM_API_KEY>" \
            -H "Content-Type: application/json" \
            -d '{
            "input": "Welcome to our service!",
            "source_language_code": "en-IN",
            "target_language_code": "hi-IN",
            "model": "mayura:v1",
            "numerals_format": "native"
            }'
            ```
          </Tab>
        </Tabs>
      </Tab>

      <Tab title="All Parameters">
        <p>
          Example using all available parameters together for maximum customization.
        </p>

        <Tabs>
          <Tab title="Python">
            ```python
            response = client.text.translate(
                input="Welcome to our service!",
                source_language_code="en-IN",
                target_language_code="hi-IN",
                model="mayura:v1",
                speaker_gender="Female",
                mode="modern-colloquial",
                output_script="fully-native",
                numerals_format="native"
            )
            ```
          </Tab>

          <Tab title="JavaScript">
            ```javascript
            const response = await client.text.translate({
                input: "Welcome to our service!",
                source_language_code: "en-IN",
                target_language_code: "hi-IN",
                model: "mayura:v1",
                speaker_gender: "Female",
                mode: "modern-colloquial",
                output_script: "fully-native",
                numerals_format: "native"
            });
            ```
          </Tab>

          <Tab title="cURL">
            ```bash
            curl -X POST https://api.sarvam.ai/translate \
            -H "api-subscription-key: <YOUR_SARVAM_API_KEY>" \
            -H "Content-Type: application/json" \
            -d '{
            "input": "Welcome to Sarvam AI!",
            "source_language_code": "en-IN",
            "target_language_code": "hi-IN",
            "model": "mayura:v1",
            "speaker_gender": "Female",
            "mode": "modern-colloquial",
            "output_script": "fully-native",
            "numerals_format": "native"
            }'
            ```
          </Tab>
        </Tabs>
      </Tab>
    </Tabs>
  </Tab>
</Tabs>

## API Features

<CardGroup cols={2}>
  <Card title="Translation Options" icon="language">
    * Multiple Indian languages support
    * Three translation modes
    * Gender-specific translations
    * Code-mixed text support
  </Card>

  {" "}

  <Card title="Output Formats" icon="text-size">
    * Multiple script options
    * Native/International numerals
    * Customizable formatting
    * Transliteration support
  </Card>

  {" "}

  <Card title="Advanced Features" icon="wand-magic-sparkles">
    * Automatic language detection
    * Context preservation
    * Entity handling
  </Card>
</CardGroup>

## API Response Format

<Tabs>
  <Tab title="Response Schema">
    <ParamField body="request_id" type="string">
      Unique identifier for the request
    </ParamField>

    <ParamField body="translated_text" type="string" required>
      The translated text result in the requested target language

      **Example:** `"नमस्ते, आप कैसे हैं?"`
    </ParamField>

    <ParamField body="source_language_code" type="string" required>
      The detected or provided source language of the input text in BCP-47 format

      **Supported Languages:**

      * **mayura:v1:** bn-IN, en-IN, gu-IN, hi-IN, kn-IN, ml-IN, mr-IN, od-IN, pa-IN, ta-IN, te-IN
      * **sarvam-translate:v1:** All mayura:v1 languages plus as-IN, brx-IN, doi-IN, kok-IN, ks-IN, mai-IN, mni-IN, ne-IN, sa-IN, sat-IN, sd-IN, ur-IN

      **Example:** `"en-IN"`
    </ParamField>
  </Tab>

  <Tab title="Example Response">
    **Basic Translation:**

    ```json
    {
      "request_id": "20241115_12345678-1234-5678-1234-567812345678",
      "translated_text": "नमस्ते, आप कैसे हैं?",
      "source_language_code": "en-IN"
    }
    ```

    **With Roman Script Output:**

    ```json
    {
      "request_id": "20241115_12345678-1234-5678-1234-567812345678",
      "translated_text": "namaste, aap kaise hain?",
      "source_language_code": "en-IN"
    }
    ```

    **With Native Numerals:**

    ```json
    {
      "request_id": "20241115_12345678-1234-5678-1234-567812345678",
      "translated_text": "मेरा फोन नंबर है ९८४०९५०९५०",
      "source_language_code": "en-IN"
    }
    ```

    **Auto-Detected Source Language:**

    ```json
    {
      "request_id": "20241115_12345678-1234-5678-1234-567812345678",
      "translated_text": "Hello, how are you?",
      "source_language_code": "hi-IN"
    }
    ```
  </Tab>
</Tabs>

<Note>
  Check out our detailed [API Reference](/api-reference-docs/text/translate-text)
  to explore Translation and all available options.
</Note>

<Note>
  Need help with translation? Contact us on
  [discord](https://discord.com/invite/5rAsykttcs) for guidance.
</Note>