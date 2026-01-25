# Transliteration API

> Complete overview of Sarvam AI Transliteration API for script conversion between Indian languages. Convert between Roman, Devanagari, and other scripts with high accuracy.

## Transliteration Types

<CardGroup cols={3}>
  <Card title="Romanization" icon="font" color="#00aa55">
    Convert Indic scripts to Roman script (English alphabet). Example: मैं ऑफिस
    → main office
  </Card>

  {" "}

  <Card title="Indic Script Conversion" icon="language" color="#0062ff">
    Convert code-mixed, romanized, or English text to Indic scripts. Example: main
    office → मैं ऑफिस
  </Card>

  <Card title="Spoken Form" icon="comment-dots" color="#da62c4">
    Convert written text to natural spoken form. Example: 9:30am → सुबह साढ़े नौ
    बजे
  </Card>
</CardGroup>

## Code Examples

<Tabs>
  <Tab title="Basic Usage">
    <Tabs>
      <Tab title="Python">
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(
            api_subscription_key="YOUR_SARVAM_API_KEY"
        )

        response = client.text.transliterate(
            input="मैं ऑफिस जा रहा हूँ",
            source_language_code="hi-IN",
            target_language_code="en-IN",
            spoken_form=True
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

        const response = await client.text.transliterate({
            input: "मैं ऑफिस जा रहा हूँ",
            source_language_code: "hi-IN",
            target_language_code: "en-IN",
            spoken_form: true
        });

        console.log(response);
        ```
      </Tab>

      <Tab title="cURL">
        ```bash
        curl -X POST https://api.sarvam.ai/transliterate \
        -H "api-subscription-key: <YOUR_SARVAM_API_KEY>" \
        -H "Content-Type: application/json" \
        -d '{
        "input": "मैं ऑफिस जा रहा हूँ",
        "source_language_code": "hi-IN",
        "target_language_code": "en-IN",
        "spoken_form": true
        }'
        ```
      </Tab>
    </Tabs>
  </Tab>

  <Tab title="Advanced Options">
    <div>
      <h3>
        Advanced Transliteration Features
      </h3>

      <p>
        Explore different parameters to customize your transliteration output:
      </p>
    </div>

    <Tabs>
      <Tab title="Numerals Format">
        <p>
          Choose between international (0-9) or native numerals (e.g., ०-९) for number representation in the output text.
        </p>

        <Tabs>
          <Tab title="Python">
            ```python
            from sarvamai import SarvamAI

            client = SarvamAI(
                api_subscription_key="YOUR_SARVAM_API_KEY"
            )

            response = client.text.transliterate(
                input="मेरा phone number है 9840950950",
                source_language_code="hi-IN",
                target_language_code="hi-IN",
                numerals_format="native"
            )

            print(response.transliterated_text)
            ```
          </Tab>

          <Tab title="JavaScript">
            ```javascript
            import { SarvamAIClient } from "sarvamai";

            const client = new SarvamAIClient({
                apiSubscriptionKey: "YOUR_SARVAM_API_KEY"
            });

            const response = await client.text.transliterate({
                input: "मेरा phone number है 9840950950",
                source_language_code: "hi-IN",
                target_language_code: "hi-IN",
                numerals_format: "native"
            });

            console.log(response.transliterated_text);
            ```
          </Tab>

          <Tab title="cURL">
            ```bash
              curl -X POST https://api.sarvam.ai/transliterate \
            -H "api-subscription-key: <YOUR_SARVAM_API_KEY>"  \
            -H "Content-Type: application/json" \
            -d '{
            "input": "मैं ऑफिस जा रहा हूँ",
            "source_language_code": "hi-IN",
            "target_language_code": "en-IN",
            "numerals_format": "native"
            }'
            ```
          </Tab>
        </Tabs>
      </Tab>

      <Tab title="Spoken Form">
        <p>
          Convert text into natural spoken form. Note: This has no effect if output language is en-IN.
        </p>

        <Tabs>
          <Tab title="Python">
            ```python
            from sarvamai import SarvamAI

            client = SarvamAI(
                api_subscription_key="YOUR_SARVAM_API_KEY"
            )

            response = client.text.transliterate(
                input="मेरे पास ₹200 है",
                source_language_code="hi-IN",
                target_language_code="hi-IN",
                spoken_form=True
            )

            print(response.transliterated_text)
            ```
          </Tab>

          <Tab title="JavaScript">
            ```javascript
            import { SarvamAIClient } from "sarvamai";

            const client = new SarvamAIClient({
                apiSubscriptionKey: "YOUR_SARVAM_API_KEY"
            });

            const response = await client.text.transliterate({
                input: "मेरे पास ₹200 है",
                source_language_code: "hi-IN",
                target_language_code: "hi-IN",
                spoken_form: true
            });

            console.log(response.transliterated_text);
            ```
          </Tab>

          <Tab title="cURL">
            ```bash
            curl -X POST https://api.sarvam.ai/transliterate \
            -H "api-subscription-key: <YOUR_SARVAM_API_KEY>" \
            -H "Content-Type: application/json" \
            -d '{
            "input": "input",
            "source_language_code": "auto",
            "target_language_code": "en-IN",
            "spoken_form": true
            }'
            ```
          </Tab>
        </Tabs>
      </Tab>

      <Tab title="Spoken Form Numerals">
        <p>
          Choose between English or native language for number pronunciation when spoken_form is enabled.
        </p>

        <Tabs>
          <Tab title="Python">
            ```python
            from sarvamai import SarvamAI

            client = SarvamAI(
                api_subscription_key="YOUR_SARVAM_API_KEY"
            )

            response = client.text.transliterate(
                input="मेरे पास ₹200 है",
                source_language_code="hi-IN",
                target_language_code="hi-IN",
                spoken_form=True
            )

            print(response.transliterated_text)
            ```
          </Tab>

          <Tab title="JavaScript">
            ```javascript
            import { SarvamAIClient } from "sarvamai";

            const client = new SarvamAIClient({
                apiSubscriptionKey: "YOUR_SARVAM_API_KEY"
            });

            const response = await client.text.transliterate({
                input: "मेरे पास ₹200 है",
                source_language_code: "hi-IN",
                target_language_code: "hi-IN",
                spoken_form: true,
                spoken_form_numerals_language: "english"
            });

            console.log(response.transliterated_text);
            ```
          </Tab>

          <Tab title="cURL">
            ```bash
            curl -X POST https://api.sarvam.ai/transliterate \
              -H "api-subscription-key: <YOUR_SARVAM_API_KEY>"  \
              -H "Content-Type: application/json" \
              -d '{
                 "input": "मेरे पास ₹200 है",
                "source_language_code": "hi-IN",
                "target_language_code": "hi-IN",
                "spoken_form": true

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
            from sarvamai import SarvamAI

            client = SarvamAI(
                api_subscription_key="YOUR_SARVAM_API_KEY"
            )

            response = client.text.transliterate(
                input="मेरे पास ₹200 है और time है 9:30am",
                source_language_code="hi-IN",
                target_language_code="hi-IN",
                spoken_form=True,
                numerals_format="native",
                spoken_form_numerals_language="native"
            )

            print(response.transliterated_text)
            ```
          </Tab>

          <Tab title="JavaScript">
            ```javascript
            import { SarvamAIClient } from "sarvamai";

            const client = new SarvamAIClient({
                apiSubscriptionKey: "YOUR_SARVAM_API_KEY"
            });

            const response = await client.text.transliterate({
                input: "मेरे पास ₹200 है और time है 9:30am",
                source_language_code: "hi-IN",
                target_language_code: "hi-IN",
                spoken_form: true,
                numerals_format: "native",
                spoken_form_numerals_language: "native"
            });

            console.log(response.transliterated_text);
            ```
          </Tab>

          <Tab title="cURL">
            ```bash
            curl -X POST https://api.sarvam.ai/transliterate \
            -H "api-subscription-key: <YOUR_SARVAM_API_KEY>" \
            -H "Content-Type: application/json" \
            -d '{
            "input": "मेरे पास ₹200 है और time है 9:30am",
            "source_language_code": "hi-IN",
            "target_language_code": "hi-IN",
            "spoken_form": true,
            "numerals_format": "native",
            "spoken_form_numerals_language": "native"
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
  <Card title="Input Options" icon="keyboard">
    * Multiple Indic languages
    * Code-mixed text support
    * Romanized text input
    * English text input
  </Card>

  {" "}

  <Card title="Output Formats" icon="text-size">
    * Roman script (English)
    * Native script conversion
    * Spoken form output
    * Natural number formats
  </Card>

  {" "}

  <Card title="Number Handling" icon="calculator">
    * International numerals (0-9)
    * Native numerals (१-९)
    * English number words
    * Native number words
  </Card>
</CardGroup>

## API Response Format

<Tabs>
  <Tab title="Response Schema">
    <ParamField body="request_id" type="string">
      Unique identifier for the request
    </ParamField>

    <ParamField body="transliterated_text" type="string" required>
      The transliterated text result in the requested target language script

      **Example:** `"main office ja raha hun"`
    </ParamField>

    <ParamField body="source_language_code" type="string" required>
      The detected or provided source language of the input text in BCP-47 format

      **Supported Languages:** bn-IN, en-IN, gu-IN, hi-IN, kn-IN, ml-IN, mr-IN, od-IN, pa-IN, ta-IN, te-IN

      **Example:** `"hi-IN"`
    </ParamField>
  </Tab>

  <Tab title="Example Response">
    **Romanization (Indic to English):**

    ```json
    {
      "request_id": "20241115_12345678-1234-5678-1234-567812345678",
      "transliterated_text": "main office ja raha hun",
      "source_language_code": "hi-IN"
    }
    ```

    **Indic Script Conversion (English to Indic):**

    ```json
    {
      "request_id": "20241115_12345678-1234-5678-1234-567812345678",
      "transliterated_text": "मैं ऑफिस जा रहा हूँ",
      "source_language_code": "en-IN"
    }
    ```

    **Spoken Form:**

    ```json
    {
      "request_id": "20241115_12345678-1234-5678-1234-567812345678",
      "transliterated_text": "मुझे कल सुबह साढ़े नौ बजे को अपॉइंटमेंट है",
      "source_language_code": "hi-IN"
    }
    ```

    **With Native Numerals:**

    ```json
    {
      "request_id": "20241115_12345678-1234-5678-1234-567812345678",
      "transliterated_text": "मेरा फोन नंबर है: ९८४०९५०९५०",
      "source_language_code": "hi-IN"
    }
    ```

    **Auto-Detected Source Language:**

    ```json
    {
      "request_id": "20241115_12345678-1234-5678-1234-567812345678",
      "transliterated_text": "namaste",
      "source_language_code": "hi-IN"
    }
    ```
  </Tab>
</Tabs>

<Note>
  Check out our detailed [API Reference](/api-reference-docs/text/transliterate-text)
  to explore Transliteration and all available options.
</Note>

<Note>
  Need help with transliteration? Contact us on
  [discord](https://discord.com/invite/5rAsykttcs) for guidance.
</Note>