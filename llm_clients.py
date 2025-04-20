from embeddings import bedrock
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
        file_path = match.group(1)
        content = match.group(2).strip()
        updates.append((file_path, content))

    return updates

def ask_llama(context, prompt, repo_path):
    """
    Send a prompt to the LLM and process any file updates.

    Args:
        context: The code context to provide to the LLM
        prompt: The user's prompt/question
        repo_path: Path to the git repository for file operations

    Returns:
        str: The LLM's response
    """
    # Initialize file manager with repository path
    file_manager = RepoFileManager(repo_path)

    full_prompt = f"""Human: You are a coding assistant that can read and modify code. When you need to update a file, wrap the content in XML tags:
    <file_update path="/path/to/file">
    Updated content here
    </file_update>

    IMPORTANT: You can use either absolute paths or paths relative to the repository root.
    Current repository path: {repo_path}

    The following are code snippets from a project:
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
    response_text = result.get("generation", "No output received.")

    # Process any file updates
    updates = extract_file_updates(response_text)

    for file_path, content in updates:
        try:
            file_manager.safe_write_to_file(file_path, content)
        except FileOperationError as e:
            print(f"✗ Failed to update file: {file_path}")
            print(f"  Error: {str(e)}")
            # Add error information to the response
            response_text += f"\n\nError updating {file_path}: {str(e)}"

    return response_text
