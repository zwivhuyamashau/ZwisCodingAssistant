from bedrock_client import bedrock
import json
import re
import os
from file_operations import RepoFileManager, FileOperationError

# needs improvement
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
        file_path = match.group(1)
        content = match.group(2).strip()
        updates.append((file_path, content))

    return updates

def ask_llm(context, prompt, repo_path, model="llama"):
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
        # Add Claude logic here
        response_text = "Claude is not yet implemented."

    elif model == "openai":
        # Add OpenAI logic here
        response_text = "OpenAI is not yet implemented."

    else:
        return f"Unknown model: {model}"

    # Handle file updates # needs improvement
    for file_path, content in extract_file_updates(response_text):
        try:
            file_manager.safe_write_to_file(file_path, content)
        except FileOperationError as e:
            print(f" Failed to update file: {file_path}")
            response_text += f"\n\nError updating {file_path}: {str(e)}"

    return response_text
