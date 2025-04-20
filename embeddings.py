import json
import os
from bedrock_client import bedrock

def get_titan_embedding(text):
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({
            "inputText": text,
            "dimensions": 1024,  
            "normalize": True
        })
    )
    result = json.loads(response['body'].read())
    return result['embedding']
