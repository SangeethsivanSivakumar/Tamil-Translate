# Developer Quickstart

> Learn how to make your first API request with Sarvam AI in under 5 minutes. Complete guide with code examples for chat completion, speech-to-text, and translation APIs.

{/* <div
  style={{
    background:
      "linear-gradient(135deg, rgba(0, 98, 255, 0.03) 0%, rgba(218, 98, 196, 0.03) 100%)",
    padding: "3rem",
    borderRadius: "16px",
    marginBottom: "3rem",
    border: "1px solid rgba(0, 98, 255, 0.08)",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
  }}
>
  <h1
    style={{
      fontSize: "2.75rem",
      marginBottom: "0rem",
      display: "flex",
      alignItems: "center",
      gap: "1.75rem",
      fontWeight: "500",
      lineHeight: "1",
      letterSpacing: "-0.02em",
    }}
  > */}

Get started with Sarvam APIs in under a minute using just a few lines of code  {/* </h1>
</div> */}

<Steps>
  <Step title="Create an API Key" icon="key">
    Visit the [Sarvam AI dashboard](https://dashboard.sarvam.ai) and create a new API key. Keep this key secure - you'll need it to authenticate your requests.
  </Step>

  <Step title="Set Up Your Environment" icon="gear">
    Export your API key as an environment variable:

    <CodeGroup>
      <CodeBlock title="macOS / Linux" active>
        ```bash
        export SARVAM_API_KEY="your_api_key_here"
        ```
      </CodeBlock>

      <CodeBlock title="Windows">
        ```powershell
        $env:SARVAM_API_KEY="your_api_key_here"
        ```
      </CodeBlock>
    </CodeGroup>
  </Step>

  <Step title="Install the SDK" icon="download">
    Choose your preferred language and install our SDK:

    <CodeGroup>
      <CodeBlock title="Python" active>
        ```bash
        pip install -U sarvamai
        ```
      </CodeBlock>

      <CodeBlock title="JavaScript">
        ```bash
        npm install sarvamai@latest
        ```
      </CodeBlock>
    </CodeGroup>
  </Step>

  <Step title="Make Your First API Call" icon="rocket">
    <CodeGroup>
      <CodeBlock title="Python" active>
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(
            api_subscription_key="YOUR_API_KEY",
        )

        response = client.text.translate(
            input="Hi, My Name is Vinayak.",
            source_language_code="auto",
            target_language_code="gu-IN",
            speaker_gender="Male"
        )

        print(response)
        ```
      </CodeBlock>

      <CodeBlock title="JavaScript">
        ```javascript
        import { SarvamAIClient } from "sarvamai";

        const client = new SarvamAIClient({
            apiSubscriptionKey: "YOUR_API_KEY"
        });

        const response = await client.text.translate({
            input: "Hi, My Name is Vinayak.",
            source_language_code: "auto",
            target_language_code: "gu-IN",
            speaker_gender: "Male"
        });

        console.log(response);
        ```
      </CodeBlock>

      <CodeBlock title="curl">
        ```bash
        curl -X POST https://api.sarvam.ai/translate \
        -H "api-subscription-key: <YOUR_SARVAM_API_KEY>" \
        -H "Content-Type: application/json" \
        -d '{
        "input": "input",
        "source_language_code": "auto",
        "target_language_code": "gu-IN"
        }'
        ```
      </CodeBlock>
    </CodeGroup>
  </Step>
</Steps>

<Note>
  **Quick Tips:** - Store your API key securely and never commit it to version
  control - Use environment variables or a secure configuration manager
</Note>

## Sarvam AI APIs

<Tabs>
  <Tab title="Speech to Text">
    <Tabs>
      <Tab title="Python">
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(
            api_subscription_key="YOUR_SARVAM_API_KEY",
        )

        response = client.speech_to_text.transcribe(
            file=open("audio.wav", "rb"),
            model="saarika:v2.5",
            language_code="gu-IN"
        )

        print(response)
        ```
      </Tab>

      <Tab title="JavaScript">
        ```javascript
        import {SarvamAIClient} from "sarvamai";
        import fs from 'fs';

        const client = new SarvamAIClient({
            apiSubscriptionKey: process.env.SARVAM_API_KEY
        });

        // Read your audio file
        const audioFile = fs.createReadStream("recording.wav");

        const response = await client.speechToText.transcribe({
            file: audioFile,
            language_code: "en-IN",
            model: "saarika:v2.5"
        });

        console.log(response);
        ```
      </Tab>

      <Tab title="curl">
        ```bash
        curl -X POST https://api.sarvam.ai/speech-to-text \
        -H "api-subscription-key: <YOUR_SARVAM_API_KEY>" \
        -H "Content-Type: multipart/form-data" \
        -F model="saarika:v2.5" \
        -F language_code="en-IN" \
        -F file=@"file.wav;type=audio/wav"
        ```
      </Tab>
    </Tabs>
  </Tab>

  <Tab title="Speech To Text Translate">
    <Tabs>
      <Tab title="Python">
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(
            api_subscription_key="YOUR_SARVAM_API_KEY",
        )

        response = client.speech_to_text.translate(
            file=open("audio.wav", "rb"),
            model="saaras:v2.5"
        )

        print(response)
        ```
      </Tab>

      <Tab title="JavaScript">
        ```javascript
        import {SarvamAIClient} from "sarvamai";
        import fs from 'fs';

        const client = new SarvamAIClient({
            apiSubscriptionKey: process.env.SARVAM_API_KEY
        });

        // Read your audio file
        const audioFile = fs.createReadStream("recording.wav");

        const response = await client.speechToText.translate({
            file: audioFile,
            model: "saaras:v2.5"
        });

        console.log(response);
        ```
      </Tab>

      <Tab title="curl">
        ```bash
        curl -X POST https://api.sarvam.ai/speech-to-text-translate \
        -H "api-subscription-key: <YOUR_SARVAM_API_KEY>" \
        -H "Content-Type: multipart/form-data" \
        -F file=@<file1>
        ```
      </Tab>
    </Tabs>
  </Tab>

  <Tab title="Text to Speech">
    <Tabs>
      <Tab title="Python">
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(
            api_subscription_key="YOUR_SARVAM_API_KEY",
        )

        response = client.text_to_speech.convert(
            text="Hello, how are you?",
            target_language_code="hi-IN",
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

        const response = await client.textToSpeech.convert({
            text: "Hello, how are you?",
            target_language_code: "hi-IN",
        });

        console.log(response);
        ```
      </Tab>

      <Tab title="curl">
        ```bash
        curl -X POST https://api.sarvam.ai/text-to-speech \
        -H "api-subscription-key: <YOUR_SARVAM_API_KEY>" \
        -H "Content-Type: application/json" \
        -d '{
        "text":"Welcome to Sarvam AI!",
        "target_language_code": "bn-IN",
        "speaker": "anushka"
        }'
        ```
      </Tab>
    </Tabs>
  </Tab>

  <Tab title="Text Translation">
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

      <Tab title="curl">
        ```bash
        curl -X POST https://api.sarvam.ai/translate \
        -H "api-subscription-key: <YOUR_SARVAM_API_KEY>" \
        -H "Content-Type: application/json" \
        -d '{
        "input": "input",
        "source_language_code": "auto",
        "target_language_code": "en-IN"
        }'
        ```
      </Tab>
    </Tabs>
  </Tab>

  <Tab title="Chat Completion">
    <Tabs>
      <Tab title="Python">
        ```python
        from sarvamai import SarvamAI

        client = SarvamAI(
            api_subscription_key="YOUR_SARVAM_API_KEY"
        )

        response = client.chat.completions(
            messages=[
                {"role": "user", "content": "Hey, what is the capital of India?"}
            ]
        )

        print(response)
        ```
      </Tab>

      <Tab title="JavaScript">
        ```javascript
        import { SarvamAIClient } from "sarvamai";

        // Initialize the SarvamAI client with your API key
        const client = new SarvamAIClient({
            apiSubscriptionKey: "YOUR_SARVAM_API_KEY"
        });

        async function main() {
            const response = await client.chat.completions({
                messages: [
                    {
                        role: "user",
                        content: "What is the capital of India?"
                    }
                ]
            });
            // Log the assistant's reply
            console.log(response.choices[0].message.content);
        }

        main();
        ```
      </Tab>

      <Tab title="curl">
        ```bash
        curl -X POST https://api.sarvam.ai/v1/chat/completions \
        -H "Authorization: Bearer $SARVAM_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
        "model": "sarvam-m",
        "messages": [
        {
        "role": "user",
        "content": "What is the capital of India?"
        }
        ]
        }'
        ```
      </Tab>
    </Tabs>
  </Tab>
</Tabs>

## Next Steps

<Steps>
  <Step title="Learn More about our Models" icon="brain">
    Explore Sarvam AI's specialized [Models](/api-reference-docs/getting-started/models) for Indian languages - from speech processing to text generation and translation.
  </Step>

  <Step title="Explore API Capabilities" icon="sparkles">
    Discover our comprehensive [API Capabilities](/api-reference-docs/introduction) for speech technologies, text processing, and analytics.
  </Step>

  <Step title="View Examples" icon="code">
    Browse our [Cookbook](/api-reference-docs/cookbook/starter-notebooks/) for some inspiration and step-by-step tutorials.
  </Step>

  <Step title="Discord" icon="fa-brands fa-discord">
    Join our [Discord community](https://discord.com/invite/5rAsykttcs) for support, discussions, and updates.
  </Step>
</Steps>