import boto3
import json
import os

# Fetch AWS credentials from environment variables when using bedrock
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_DEFAULT_REGION', 'us-east-1') 

bedrock = boto3.client(
        "bedrock-runtime",
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

def get_titan_embedding(text):
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({
            "inputText": text,
            "dimensions": 1024,  # Specify the desired dimension
            "normalize": True
        })
    )
    result = json.loads(response['body'].read())
    return result['embedding']
