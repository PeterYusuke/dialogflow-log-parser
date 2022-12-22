# dialogflow-log-parser
[![Coverage Status](https://coveralls.io/repos/github/PeterYusuke/dialogflow-log-parser/badge.svg?branch=main)](https://coveralls.io/github/PeterYusuke/dialogflow-log-parser?branch=main)

A module for dialogflow log parser

Only response textPaylod from dialogflow ES log file can be parsed into dict object. 

# Usage 

This module parses dialogflow logs into python dictionary type.

## Example usage
pip
```
pip install dialogflow-log-parser
```

python
```python
from dialogflow_log_parser.es import response_to_dict

# store log string
textPayload = '[text from dialogflow ES textPayload]'

# parse string to dictionary object
response_dict = response_to_dict(textPayload)

```

## Example of file and parsed object(json)
Please check test/es/data folder, so that you can know what kind of dictionary you get.  
Also use swagger.yml file in  [swagger editor](https://editor.swagger.io/) to see the entire response json data.

Log file
```conf
Dialogflow Response : 
    id: "response_id"
    lang: "ja"
    session_id: "dfMessenger-session-id"
    timestamp: "2000-01-01T01:00:21.720007Z"
    result {
      source: "agent"
      resolved_query: "WELCOME"
      action: "input.welcome"
      score: 1.0
        parameters {
        }
        metadata {
          intent_id: "intent_id"
          intent_name: "Default Welcome Intent"
          webhook_used: "false"
          webhook_for_slot_filling_used: "false"
          is_fallback_intent: "false"
        }
        fulfillment {
          speech: "hello"
          messages {
            lang: "ja"
            type {
              number_value: 0.0
            }
            speech {
              string_value: "hello"
            }
          }
        }
    }
    status {
      code: 200
      error_type: "success"
    }

```

Parsed json
```json
{
  "id": "response_id",
  "lang": "ja",
  "session_id": "dfMessenger-session-id",
  "timestamp": "2000-01-01T01:00:21.720007Z",
  "result": {
    "source": "agent",
    "resolved_query": "WELCOME",
    "action": "input.welcome",
    "score": 1.0,
    "parameters": [],
    "metadata": {
      "intent_id": "intent_id",
      "intent_name": "Default Welcome Intent",
      "webhook_used": "false",
      "webhook_for_slot_filling_used": "false",
      "is_fallback_intent": "false"
    },
    "fulfillment": {
      "speech": "hello",
      "messages": [
        {
          "lang": "ja",
          "type": 0.0,
          "speech": "hello"
        }
      ]
    }
  },
  "status": {
    "code": 200,
    "error_type": "success"
  }
}
```

# Issues
Feel free to post issues for adding some function. (i.e. request textPayload or CX edition.)
