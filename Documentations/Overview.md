# Text Processing Overview

> Complete overview of Sarvam AI Text Processing APIs including translation, transliteration, and language identification for 22+ Indian languages using Mayura and Sarvam-Translate models.

<p>
  Sarvam AI offers two powerful text processing models:
</p>

<div>
  <div>
    <Card title="Sarvam-Translate" icon="language" href="/api-reference-docs/getting-started/models/sarvam-translate">
      Translation model that supports all 22 official Indian languages and
      is optimized for structured, long-form text.
    </Card>
  </div>

  <div>
    <Card title="Mayura" icon="language" href="/api-reference-docs/getting-started/models/mayura">
      Advanced text processing model with translation, transliteration, and
      script conversion capabilities for Indian languages.
    </Card>
  </div>
</div>

## Sarvam-Translate

Sarvam Translate enables high-quality translation between English and
22 scheduled Indian languages and is optimized for structured, long-form text.

## Text Processing Features

<Tabs>
  <Tab title="Basic Translation">
    <div>
      <h3>
        Basic Text Translation
      </h3>

      <p>
        Translate structured, long-form text between Indian languages. Features include:
      </p>

      <ul>
        <li>
          Support for all 22 scheduled Indian languages
        </li>

        <li>
          Formal Style Translation
        </li>

        <li>
          Numeral Format Control between international and native numeral systems
        </li>
      </ul>
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

        const response = await client.text.translate({
        input: "भारत एक महान देश है। इसकी संस्कृति बहुत पुरानी और समृद्ध है।",
        source_language_code: "hi-IN",
        target_language_code: "gu-IN",
        model: "sarvam-translate:v1"
        });

        console.log(response);
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
      <h3>
        Advanced Text Processing
      </h3>

      <p>
        Fine-tune text processing with various parameters:
      </p>

      <ul>
        <li>
          Formal Style Translation
        </li>

        <li>
          Choose between Male and Female voice characteristics for gender-specific translations
        </li>

        <li>
          Option to choose between international and native numeral systems
        </li>
      </ul>
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
            model="sarvam-translate:v1",
            speaker_gender="Male",
            mode="formal"
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
        input: "भारत एक महान देश है। इसकी संस्कृति बहुत पुरानी और समृद्ध है।",
        source_language_code: "hi-IN",
        target_language_code: "gu-IN",
        model: "sarvam-translate:v1",
        speaker_gender: "Male",
        mode: "formal"
        });

        console.log(response);
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
            "model": "sarvam-translate:v1",
            "speaker_gender": "Male",
            "mode": "formal"
          }'        
        ```
      </Tab>
    </Tabs>
  </Tab>
</Tabs>

<Note>
  Check out our detailed [API Reference](/api-reference-docs/text/translate-text)
  to explore Translation and all available options.
</Note>

## Mayura: Our Text Processing Model

Mayura is our state-of-the-art text processing model that excels in handling Indian languages with features like translation, transliteration, and script conversion.

## Text Processing Features

<Tabs>
  <Tab title="Basic Translation">
    <div>
      <h3>
        Basic Text Translation
      </h3>

      <p>
        Translate text between Indian languages with high accuracy. Features include:
      </p>

      <ul>
        <li>
          Support for multiple Indian languages
        </li>

        <li>
          Automatic language detection
        </li>

        <li>
          Natural and fluent translations
        </li>

        <li>
          Context-aware processing
        </li>
      </ul>
    </div>

    <Tabs>
      <Tab title="Python">
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(
          api_subscription_key="YOUR_SARVAM_API_KEY",
        )

        response = client.text.translate(
          input="Hello, how are you?",
          source_language_code="auto",
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
          source_language_code: "auto",
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
        "source_language_code": "auto",
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
        Advanced Text Processing
      </h3>

      <p>
        Fine-tune text processing with various parameters:
      </p>

      <ul>
        <li>
          Translation modes (formal, modern-colloquial, classic-colloquial, code-mixed)
        </li>

        <li>
          Mixed language handling
        </li>
      </ul>
    </div>

    <Tabs>
      <Tab title="Python">
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(
            api_subscription_key="YOUR_SARVAM_API_KEY"
        )

        response = client.text.translate(
            input="Welcome to Sarvam AI!",
            source_language_code="en-IN",
            target_language_code="hi-IN",
            model="mayura:v1",
            mode="modern-colloquial"
        )

        print(response.translated_text)
        ```
      </Tab>

      <Tab title="JavaScript">
        ```javascript
        import { SarvamAIClient } from "sarvamai";

        const client = new SarvamAIClient({
          apiSubscriptionKey: "YOUR_SARVAM_API_KEY"
        });

        const response = await client.text.translate({
          input: "Welcome to Sarvam AI!",
          source_language_code: "en-IN",
          target_language_code: "hi-IN",
          model: "mayura:v1",
          mode: "modern-colloquial"
        });

        console.log(response.translatedText);
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
        "mode": "modern-colloquial"
        }'
        ```
      </Tab>
    </Tabs>
  </Tab>
</Tabs>

<Card title="Key Considerations">
  * Maximum text length: 1000 characters per request
  * Supports 10 Indic Languages and English
  * Automatic language detection available
  * Translation modes: formal (default), modern-colloquial, classic-colloquial, code-mixed
</Card>

<Note>
  Check out our detailed [API Reference](/api-reference-docs/text/translate-text)
  to explore Translation and all available options.
</Note>