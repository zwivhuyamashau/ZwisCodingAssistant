from bedrock_client import bedrock
import json
import re
import os
from file_operations import RepoFileManager, FileOperationError


def extract_file_updates(response: str) -> list:
    """
    Extract file updates from the LLM response.
    Expected format:
    <file_update path="/absolute/path/to/file">
    content
    </file_update>

    Returns:
        list of tuples (file_path, content)
    """
    updates = []
    pattern = r'<file_update path="([^"]+)">(.*?)</file_update>'
    matches = re.finditer(pattern, response, re.DOTALL)

    for match in matches:
        file_path = match.group(1).strip()
        content = match.group(2).strip()

        # Skip empty paths or content
        if not file_path or not content:
            continue

        # Handle Windows path backslashes that might be escaped
        file_path = file_path.replace('\\\\', '\\')

        updates.append((file_path, content))

    # Log the number of file updates found
    if updates:
        print(f"Found {len(updates)} file updates in LLM response")
    else:
        print("No file updates found in LLM response")

    return updates

def ask_llm(context, prompt, repo_path):

    model = os.getenv("LLM_MODEL", "llama")

    """
    Sends a prompt to the chosen LLM and applies file updates.

    Args:
        context: Code context to send to the LLM
        prompt: User question
        repo_path: Root path of the code repo
        model: Choose between "llama", "claude", "openai" (default: llama)

    Returns:
        str: LLM's raw response + any error messages
    """
    file_manager = RepoFileManager(repo_path)

    system_prompt = f"""You are a coding agent that reads and modifies code.
    When editing files, respond using this format:

    <file_update path="/path/to/file">
    updated content here
    </file_update>

    Use absolute or repo-relative paths.
    Repository path: {repo_path}

    Code snippets:
    {context}

    User request: {prompt}
    """

    if model == "llama":
        body = {
            "prompt": f"Human: {system_prompt}\nAssistant:",
            "temperature": 0.5
        }

        response = bedrock.invoke_model(
            modelId="meta.llama3-70b-instruct-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )

        result = json.loads(response["body"].read())
        response_text = result.get("generation", "No output received.")

    elif model == "claude":
        model_inference_Id = os.getenv('MODEL_INFERENCE_ID')
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 8000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": system_prompt
                        }
                    ]
                }
            ]
        })
        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Make the API call to Bedrock
            response = bedrock.invoke_model(
                body=body,
                modelId=model_inference_Id,
                accept=accept,
                contentType=contentType
            )

            # Read the response and extract the answer
            response_body = json.loads(response['body'].read())
            answer = response_body['content'][0]['text']  # Adjust based on actual response structure

            return answer

        except Exception as e:
            print(f"Error getting Bedrock response: {str(e)}")
            return "Error occurred while getting response."

    elif model == "openai":
        # Add OpenAI logic here
        response_text = "OpenAI is not yet implemented."

    else:
        return f"Unknown model: {model}"

    file_updates = extract_file_updates(response_text)
    if file_updates:
        response_text += "\n\n## File Updates Summary"

    for file_path, content in file_updates:
        try:
            file_manager.safe_write_to_file(file_path, content)
            response_text += f"\n Successfully updated: {file_path}"
        except FileOperationError as e:
            print(f" Failed to update file: {file_path}")
            response_text += f"\n Error updating {file_path}: {str(e)}"

    return response_text
