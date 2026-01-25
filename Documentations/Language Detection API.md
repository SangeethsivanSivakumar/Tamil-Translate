# Language Detection

POST https://api.sarvam.ai/text-lid
Content-Type: application/json

Identifies the language (e.g., en-IN, hi-IN) and script (e.g., Latin, Devanagari) of the input text, supporting multiple languages.

Reference: https://docs.sarvam.ai/api-reference-docs/text/identify-language

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Language Identification
  version: endpoint_text.identifyLanguage
paths:
  /text-lid:
    post:
      operationId: identify-language
      summary: Language Identification
      description: >-
        Identifies the language (e.g., en-IN, hi-IN) and script (e.g., Latin,
        Devanagari) of the input text, supporting multiple languages.
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
                $ref: >-
                  #/components/schemas/Sarvam_Model_API_LanguageIdentificationResponse
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
              $ref: >-
                #/components/schemas/Sarvam_Model_API_LanguageIdentificationRequest
components:
  schemas:
    Sarvam_Model_API_LanguageIdentificationRequest:
      type: object
      properties:
        input:
          type: string
          description: >-
            The text input for language and script identification. Max Input
            Limit is 1000 characters
      required:
        - input
    Sarvam_Model_API_LanguageIdentificationResponse:
      type: object
      properties:
        request_id:
          type:
            - string
            - 'null'
        language_code:
          type:
            - string
            - 'null'
          description: |-
            The detected language code of the input text.

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
        script_code:
          type:
            - string
            - 'null'
          description: |-
            The detected script code of the input text.

            Available scripts:
            - **`Latn`**: Latin (Romanized script)
            - **`Deva`**: Devanagari (Hindi, Marathi)
            - **`Beng`**: Bengali
            - **`Gujr`**: Gujarati
            - **`Knda`**: Kannada
            - **`Mlym`**: Malayalam
            - **`Orya`**: Odia
            - **`Guru`**: Gurmukhi
            - **`Taml`**: Tamil
            - **`Telu`**: Telugu
      required:
        - request_id

```

## SDK Code Examples

```python
from sarvamai import SarvamAI

client = SarvamAI(
    api_subscription_key="YOUR_API_SUBSCRIPTION_KEY",
)
client.text.identify_language(
    input="input",
)

```

```typescript
import { SarvamClient } from "sarvamai";

const client = new SarvamClient({ apiSubscriptionKey: "YOUR_API_SUBSCRIPTION_KEY" });
await client.text.identifyLanguage({
    input: "input"
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

	url := "https://api.sarvam.ai/text-lid"

	payload := strings.NewReader("{\n  \"input\": \"string\"\n}")

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

url = URI("https://api.sarvam.ai/text-lid")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Post.new(url)
request["api-subscription-key"] = '<apiKey>'
request["Content-Type"] = 'application/json'
request.body = "{\n  \"input\": \"string\"\n}"

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.post("https://api.sarvam.ai/text-lid")
  .header("api-subscription-key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"input\": \"string\"\n}")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('POST', 'https://api.sarvam.ai/text-lid', [
  'body' => '{
  "input": "string"
}',
  'headers' => [
    'Content-Type' => 'application/json',
    'api-subscription-key' => '<apiKey>',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.sarvam.ai/text-lid");
var request = new RestRequest(Method.POST);
request.AddHeader("api-subscription-key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"input\": \"string\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = [
  "api-subscription-key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = ["input": "string"] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.sarvam.ai/text-lid")! as URL,
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