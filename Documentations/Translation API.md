# Translation

POST https://api.sarvam.ai/translate
Content-Type: application/json

**Translation** converts text from one language to another while preserving its meaning.
For Example: **'मैं ऑफिस जा रहा हूँ'** translates to **'I am going to the office'** in English, where the script and language change, but the original meaning remains the same.

Available languages:
- **`bn-IN`**: Bengali
- **`en-IN`**: English
- **`gu-IN`**: Gujarati
- **`hi-IN`**: Hindi
- **`kn-IN`**: Kannada
- **`ml-IN`**: Malayalam
- **`mr-IN`**: Marathi
- **`od-IN`**: Odia
- **`pa-IN`**: Punjabi
- **`ta-IN`**: Tamil
- **`te-IN`**: Telugu

### Newly added languages:
- **`as-IN`**: Assamese
- **`brx-IN`**: Bodo
- **`doi-IN`**: Dogri
- **`kok-IN`**: Konkani
- **`ks-IN`**: Kashmiri
- **`mai-IN`**: Maithili
- **`mni-IN`**: Manipuri (Meiteilon)
- **`ne-IN`**: Nepali
- **`sa-IN`**: Sanskrit
- **`sat-IN`**: Santali
- **`sd-IN`**: Sindhi
- **`ur-IN`**: Urdu

For hands-on practice, you can explore the notebook tutorial on [Translate API Tutorial](https://github.com/sarvamai/sarvam-ai-cookbook/blob/main/notebooks/translate/Translate_API_Tutorial.ipynb).

Reference: https://docs.sarvam.ai/api-reference-docs/text/translate-text

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Translate Text
  version: endpoint_text.translate
paths:
  /translate:
    post:
      operationId: translate
      summary: Translate Text
      description: >-
        **Translation** converts text from one language to another while
        preserving its meaning.

        For Example: **'मैं ऑफिस जा रहा हूँ'** translates to **'I am going to
        the office'** in English, where the script and language change, but the
        original meaning remains the same.


        Available languages:

        - **`bn-IN`**: Bengali

        - **`en-IN`**: English

        - **`gu-IN`**: Gujarati

        - **`hi-IN`**: Hindi

        - **`kn-IN`**: Kannada

        - **`ml-IN`**: Malayalam

        - **`mr-IN`**: Marathi

        - **`od-IN`**: Odia

        - **`pa-IN`**: Punjabi

        - **`ta-IN`**: Tamil

        - **`te-IN`**: Telugu


        ### Newly added languages:

        - **`as-IN`**: Assamese

        - **`brx-IN`**: Bodo

        - **`doi-IN`**: Dogri

        - **`kok-IN`**: Konkani

        - **`ks-IN`**: Kashmiri

        - **`mai-IN`**: Maithili

        - **`mni-IN`**: Manipuri (Meiteilon)

        - **`ne-IN`**: Nepali

        - **`sa-IN`**: Sanskrit

        - **`sat-IN`**: Santali

        - **`sd-IN`**: Sindhi

        - **`ur-IN`**: Urdu


        For hands-on practice, you can explore the notebook tutorial on
        [Translate API
        Tutorial](https://github.com/sarvamai/sarvam-ai-cookbook/blob/main/notebooks/translate/Translate_API_Tutorial.ipynb).
      tags:
        - - subpackage_text
      parameters:
        - name: api-subscription-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Sarvam_Model_API_TranslationResponse'
        '400':
          description: Bad Request
          content: {}
        '403':
          description: Forbidden
          content: {}
        '422':
          description: Unprocessable Entity
          content: {}
        '429':
          description: Quota Exceeded
          content: {}
        '500':
          description: Internal Server Error
          content: {}
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Sarvam_Model_API_TranslationRequest'
components:
  schemas:
    Sarvam_Model_API_TranslateSourceLanguage:
      type: string
      enum:
        - value: auto
        - value: bn-IN
        - value: en-IN
        - value: gu-IN
        - value: hi-IN
        - value: kn-IN
        - value: ml-IN
        - value: mr-IN
        - value: od-IN
        - value: pa-IN
        - value: ta-IN
        - value: te-IN
        - value: as-IN
        - value: brx-IN
        - value: doi-IN
        - value: kok-IN
        - value: ks-IN
        - value: mai-IN
        - value: mni-IN
        - value: ne-IN
        - value: sa-IN
        - value: sat-IN
        - value: sd-IN
        - value: ur-IN
    Sarvam_Model_API_TranslateTargetLanguage:
      type: string
      enum:
        - value: bn-IN
        - value: en-IN
        - value: gu-IN
        - value: hi-IN
        - value: kn-IN
        - value: ml-IN
        - value: mr-IN
        - value: od-IN
        - value: pa-IN
        - value: ta-IN
        - value: te-IN
        - value: as-IN
        - value: brx-IN
        - value: doi-IN
        - value: kok-IN
        - value: ks-IN
        - value: mai-IN
        - value: mni-IN
        - value: ne-IN
        - value: sa-IN
        - value: sat-IN
        - value: sd-IN
        - value: ur-IN
    Sarvam_Model_API_TranslateSpeakerGender:
      type: string
      enum:
        - value: Male
        - value: Female
    Sarvam_Model_API_TranslateMode:
      type: string
      enum:
        - value: formal
        - value: modern-colloquial
        - value: classic-colloquial
        - value: code-mixed
    Sarvam_Model_API_TranslateModel:
      type: string
      enum:
        - value: mayura:v1
        - value: sarvam-translate:v1
    Sarvam_Model_API_TransliterateMode:
      type: string
      enum:
        - value: roman
        - value: fully-native
        - value: spoken-form-in-native
    Sarvam_Model_API_NumeralsFormat:
      type: string
      enum:
        - value: international
        - value: native
    Sarvam_Model_API_TranslationRequest:
      type: object
      properties:
        input:
          type: string
          description: >-
            The text you want to translate is the input text that will be
            processed by the translation model. The maximum is 1000 characters
            for Mayura:v1 and 2000 characters for Sarvam-Translate:v1.
        source_language_code:
          $ref: '#/components/schemas/Sarvam_Model_API_TranslateSourceLanguage'
          description: >+
            Source language code for translation input.


            **mayura:v1 Languages:** Bengali, English, Gujarati, Hindi, Kannada,
            Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu


            **sarvam-translate:v1 Languages:** All mayura:v1 languages and
            Assamese, Bodo, Dogri, Konkani, Kashmiri, Maithili, Manipuri,
            Nepali, Sanskrit, Santali, Sindhi, Urdu


            **Note:** mayura:v1 supports automatic language detection using
            'auto' as the source language code.

        target_language_code:
          $ref: '#/components/schemas/Sarvam_Model_API_TranslateTargetLanguage'
          description: >+
            The language code of the translated text. This specifies the target
            language for translation.


            **mayura:v1 Languages:** Bengali, English, Gujarati, Hindi, Kannada,
            Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu


            **sarvam-translate:v1 Languages:** All mayura:v1 and Assamese, Bodo,
            Dogri, Konkani, Kashmiri, Maithili, Manipuri, Nepali, Sanskrit,
            Santali, Sindhi, Urdu

        speaker_gender:
          $ref: '#/components/schemas/Sarvam_Model_API_TranslateSpeakerGender'
          description: Please specify the gender of the speaker for better translations.
        mode:
          $ref: '#/components/schemas/Sarvam_Model_API_TranslateMode'
          description: >-
            Specifies the tone or style of the translation.


            **Model Support:**

            - **mayura:v1**: Supports formal, classic-colloquial, and
            modern-colloquial modes

            - **sarvam-translate:v1**: Only formal mode is supported


            **Default:** formal
        model:
          $ref: '#/components/schemas/Sarvam_Model_API_TranslateModel'
          description: >-
            Specifies the translation model to use.

            - mayura:v1: Supports 12 languages with all modes, output scripts,
            and automatic language detection.

            - sarvam-translate:v1: Supports all 22 scheduled languages of India,
            formal mode only.
        output_script:
          oneOf:
            - $ref: '#/components/schemas/Sarvam_Model_API_TransliterateMode'
            - type: 'null'
          description: >-
            **output_script**: This is an optional parameter which controls the
            transliteration style applied to the output text.


            **Transliteration**: Converting text from one script to another
            while preserving pronunciation.


            For mayura:v1 - We support transliteration with four options:

            - **`null`**(default): No transliteration applied.

            - **`roman`**: Transliteration in Romanized script.

            - **`fully-native`**: Transliteration in the native script with
            formal style.

            - **`spoken-form-in-native`**: Transliteration in the native script
            with spoken style.


            For sarvam-translate:v1 - Transliteration is not supported.

            ### Example:

            English: Your EMI of Rs. 3000 is pending.

            Default modern translation: आपका Rs. 3000 का EMI pending है (when
            `null` is passed).


            With postprocessing enabled:

            - **roman output**: aapka Rs. 3000 ka EMI pending hai.
        numerals_format:
          $ref: '#/components/schemas/Sarvam_Model_API_NumeralsFormat'
          description: >-
            `numerals_format` is an optional parameter with two options
            (supported for both mayura:v1 and sarvam-translate:v1):


            - **`international`** (default): Uses regular numerals (0-9).

            - **`native`**: Uses language-specific native numerals.


            ### Example:

            - If `international` format is selected, we use regular numerals
            (0-9). For example: `मेरा phone number है: 9840950950`.

            - If `native` format is selected, we use language-specific native
            numerals, like: `मेरा phone number है: ९८४०९५०९५०`.
      required:
        - input
        - source_language_code
        - target_language_code
    Sarvam_Model_API_TranslationResponse:
      type: object
      properties:
        request_id:
          type:
            - string
            - 'null'
        translated_text:
          type: string
          description: Translated text result in the requested target language.
        source_language_code:
          type: string
          description: Detected or provided source language of the input text.
      required:
        - request_id
        - translated_text
        - source_language_code

```

## SDK Code Examples

```python
from sarvamai import SarvamAI

client = SarvamAI(
    api_subscription_key="YOUR_API_SUBSCRIPTION_KEY",
)
client.text.translate(
    input="input",
    source_language_code="auto",
    target_language_code="bn-IN",
)

```

```typescript
import { SarvamClient } from "sarvamai";

const client = new SarvamClient({ apiSubscriptionKey: "YOUR_API_SUBSCRIPTION_KEY" });
await client.text.translate({
    input: "input",
    sourceLanguageCode: "auto",
    targetLanguageCode: "en-IN"
});

```

```go
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.sarvam.ai/translate"

	payload := strings.NewReader("{\n  \"input\": \"string\",\n  \"source_language_code\": \"auto\",\n  \"target_language_code\": \"bn-IN\"\n}")

	req, _ := http.NewRequest("POST", url, payload)

	req.Header.Add("api-subscription-key", "<apiKey>")
	req.Header.Add("Content-Type", "application/json")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.sarvam.ai/translate")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Post.new(url)
request["api-subscription-key"] = '<apiKey>'
request["Content-Type"] = 'application/json'
request.body = "{\n  \"input\": \"string\",\n  \"source_language_code\": \"auto\",\n  \"target_language_code\": \"bn-IN\"\n}"

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.post("https://api.sarvam.ai/translate")
  .header("api-subscription-key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"input\": \"string\",\n  \"source_language_code\": \"auto\",\n  \"target_language_code\": \"bn-IN\"\n}")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('POST', 'https://api.sarvam.ai/translate', [
  'body' => '{
  "input": "string",
  "source_language_code": "auto",
  "target_language_code": "bn-IN"
}',
  'headers' => [
    'Content-Type' => 'application/json',
    'api-subscription-key' => '<apiKey>',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.sarvam.ai/translate");
var request = new RestRequest(Method.POST);
request.AddHeader("api-subscription-key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"input\": \"string\",\n  \"source_language_code\": \"auto\",\n  \"target_language_code\": \"bn-IN\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = [
  "api-subscription-key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "input": "string",
  "source_language_code": "auto",
  "target_language_code": "bn-IN"
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.sarvam.ai/translate")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "POST"
request.allHTTPHeaderFields = headers
request.httpBody = postData as Data

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```