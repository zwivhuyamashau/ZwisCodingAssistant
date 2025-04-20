import json
from langchain.embeddings.base import Embeddings
from bedrock_client import bedrock

class TitanEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [self._get_titan_embedding(text) for text in texts]

    def embed_query(self, text):
        return self._get_titan_embedding(text)

    def _get_titan_embedding(self, text):
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