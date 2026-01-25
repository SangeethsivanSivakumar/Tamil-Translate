# Transliteration

POST https://api.sarvam.ai/transliterate
Content-Type: application/json

**Transliteration** converts text from one script to another while preserving the original pronunciation. For example, **'नमस्ते'** becomes **'namaste'** in English, and **'how are you'** can be written as **'हाउ आर यू'** in Devanagari. This process ensures that the sound of the original text remains intact, even when written in a different script.

Transliteration is useful when you want to represent words phonetically across different writing systems, such as converting **'मैं ऑफिस जा रहा हूँ'** to **'main office ja raha hun'** in English letters.

**Translation**, on the other hand, converts text from one language to another while preserving the meaning rather than pronunciation. For example, **'मैं ऑफिस जा रहा हूँ'** translates to **'I am going to the office'** in English, changing both the script and the language while conveying the intended message.
### Examples of **Transliteration**:
- **'Good morning'** becomes **'गुड मॉर्निंग'** in Hindi, where the pronunciation is preserved but the meaning is not translated.
- **'सुप्रभात'** becomes **'suprabhat'** in English.

Available languages:
- **`en-IN`**: English
- **`hi-IN`**: Hindi
- **`bn-IN`**: Bengali
- **`gu-IN`**: Gujarati
- **`kn-IN`**: Kannada
- **`ml-IN`**: Malayalam
- **`mr-IN`**: Marathi
- **`od-IN`**: Odia
- **`pa-IN`**: Punjabi
- **`ta-IN`**: Tamil
- **`te-IN`**: Telugu

For hands-on practice, you can explore the notebook tutorial on [Transliterate API Tutorial](https://github.com/sarvamai/sarvam-ai-cookbook/blob/main/notebooks/transliterate/Transliterate_API_Tutorial.ipynb).

Reference: https://docs.sarvam.ai/api-reference-docs/text/transliterate-text

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Transliterate Text
  version: endpoint_text.transliterate
paths:
  /transliterate:
    post:
      operationId: transliterate
      summary: Transliterate Text
      description: >-
        **Transliteration** converts text from one script to another while
        preserving the original pronunciation. For example, **'नमस्ते'** becomes
        **'namaste'** in English, and **'how are you'** can be written as **'हाउ
        आर यू'** in Devanagari. This process ensures that the sound of the
        original text remains intact, even when written in a different script.


        Transliteration is useful when you want to represent words phonetically
        across different writing systems, such as converting **'मैं ऑफिस जा रहा
        हूँ'** to **'main office ja raha hun'** in English letters.


        **Translation**, on the other hand, converts text from one language to
        another while preserving the meaning rather than pronunciation. For
        example, **'मैं ऑफिस जा रहा हूँ'** translates to **'I am going to the
        office'** in English, changing both the script and the language while
        conveying the intended message.

        ### Examples of **Transliteration**:

        - **'Good morning'** becomes **'गुड मॉर्निंग'** in Hindi, where the
        pronunciation is preserved but the meaning is not translated.

        - **'सुप्रभात'** becomes **'suprabhat'** in English.


        Available languages:

        - **`en-IN`**: English

        - **`hi-IN`**: Hindi

        - **`bn-IN`**: Bengali

        - **`gu-IN`**: Gujarati

        - **`kn-IN`**: Kannada

        - **`ml-IN`**: Malayalam

        - **`mr-IN`**: Marathi

        - **`od-IN`**: Odia

        - **`pa-IN`**: Punjabi

        - **`ta-IN`**: Tamil

        - **`te-IN`**: Telugu


        For hands-on practice, you can explore the notebook tutorial on
        [Transliterate API
        Tutorial](https://github.com/sarvamai/sarvam-ai-cookbook/blob/main/notebooks/transliterate/Transliterate_API_Tutorial.ipynb).
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
                $ref: '#/components/schemas/Sarvam_Model_API_TransliterationResponse'
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
              $ref: '#/components/schemas/Sarvam_Model_API_TransliterationRequest'
components:
  schemas:
    Sarvam_Model_API_TransliterateSourceLanguage:
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
    Sarvam_Model_API_TranslatiterateTargetLanguage:
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
    Sarvam_Model_API_NumeralsFormat:
      type: string
      enum:
        - value: international
        - value: native
    Sarvam_Model_API_SpokenFormNumeralsFormat:
      type: string
      enum:
        - value: english
        - value: native
    Sarvam_Model_API_TransliterationRequest:
      type: object
      properties:
        input:
          type: string
          description: The text you want to transliterate.
        source_language_code:
          $ref: '#/components/schemas/Sarvam_Model_API_TransliterateSourceLanguage'
          description: >+
            The language code of the input text. This specifies the source
            language for transliteration.



             Note:  The source language should either be an Indic language or English. As we supports both Indic-to-English and English-to-Indic transliteration.

        target_language_code:
          $ref: '#/components/schemas/Sarvam_Model_API_TranslatiterateTargetLanguage'
          description: >+
            The language code of the transliteration text. This specifies the
            target language for transliteration.



             Note:The target language should either be an Indic language or English. As we supports both Indic-to-English and English-to-Indic transliteration.

        numerals_format:
          $ref: '#/components/schemas/Sarvam_Model_API_NumeralsFormat'
          description: >-
            `numerals_format` is an optional parameter with two options:


            - **`international`** (default): Uses regular numerals (0-9).

            - **`native`**: Uses language-specific native numerals.


            ### Example:

            - If `international` format is selected, we use regular numerals
            (0-9). For example: `मेरा phone number है: 9840950950`.

            - If `native` format is selected, we use language-specific native
            numerals, like: `मेरा phone number है: ९८४०९५०९५०`.
        spoken_form_numerals_language:
          $ref: '#/components/schemas/Sarvam_Model_API_SpokenFormNumeralsFormat'
          description: >+
            `spoken_form_numerals_language` is an optional parameter with two
            options and only works when spoken_form is true:


            - **`english`** : Numbers in the text will be spoken in English.

            - **`native(default)`**: Numbers in the text will be spoken in the
            native language.


            ### Examples:

            - **Input:** "मेरे पास ₹200 है"
              - If `english` format is selected: "मेरे पास टू हन्डर्ड रूपीस है"
              - If `native` format is selected: "मेरे पास दो सौ रुपये है"

        spoken_form:
          type: boolean
          default: false
          description: |2
              - Default: `False`
              - Converts text into a natural spoken form when `True`.
              - **Note:** No effect if output language is `en-IN`.

            ### Example:
            - **Input:** `मुझे कल 9:30am को appointment है`
              - **Output:** `मुझे कल सुबह साढ़े नौ बजे को अपॉइंटमेंट है`
      required:
        - input
        - source_language_code
        - target_language_code
    Sarvam_Model_API_TransliterationResponse:
      type: object
      properties:
        request_id:
          type:
            - string
            - 'null'
        transliterated_text:
          type: string
          description: Transliterated text result in the requested target language.
        source_language_code:
          type: string
          description: Detected or provided source language of the input text.
      required:
        - request_id
        - transliterated_text
        - source_language_code

```

## SDK Code Examples

```python
from sarvamai import SarvamAI

client = SarvamAI(
    api_subscription_key="YOUR_API_SUBSCRIPTION_KEY",
)
client.text.transliterate(
    input="input",
    source_language_code="auto",
    target_language_code="bn-IN",
)

```

```typescript
import { SarvamClient } from "sarvamai";

const client = new SarvamClient({ apiSubscriptionKey: "YOUR_API_SUBSCRIPTION_KEY" });
await client.text.transliterate({
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

	url := "https://api.sarvam.ai/transliterate"

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

url = URI("https://api.sarvam.ai/transliterate")

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
HttpResponse<String> response = Unirest.post("https://api.sarvam.ai/transliterate")
  .header("api-subscription-key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"input\": \"string\",\n  \"source_language_code\": \"auto\",\n  \"target_language_code\": \"bn-IN\"\n}")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('POST', 'https://api.sarvam.ai/transliterate', [
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
var client = new RestClient("https://api.sarvam.ai/transliterate");
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

let request = NSMutableURLRequest(url: NSURL(string: "https://api.sarvam.ai/transliterate")! as URL,
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