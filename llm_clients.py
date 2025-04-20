from embeddings import bedrock
import json

def ask_llama(context, prompt):
    full_prompt = f"""Human: The following are code snippets from a project:
    {context}

    User question: {prompt}

    Assistant:"""

    body = {
        "prompt": full_prompt,
        "temperature": 0.5
    }

    response = bedrock.invoke_model(
        modelId="meta.llama3-70b-instruct-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )

    result = json.loads(response["body"].read())
    return result.get("generation", "No output received.")
