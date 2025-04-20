# Python-based AI Assistant(Zwi Coding assistent) for Code Repository Interaction

This project is a Python-based AI assistant designed to help users understand and interact with code repositories. It leverages various modules for cloning repositories, processing code, embedding vectors, searching for relevant code, and interacting with large language models (LLMs) to provide contextually relevant answers.

## Usage

### CLI Interface

1. Clone the repository.
2. Install the required dependencies.
3. Set the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
4. Run the `cli_main.py` file.

### Streamlit Interface

1. Clone the repository.
2. Install the required dependencies.
3. Set the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
4. Run the `streamlit_main.py` file.

### Environment Variables

* `AWS_ACCESS_KEY_ID`: Your AWS access key ID.
* `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key.

### How to Use

**CLI Interface**

1. Enter the GitHub repository URL and repository name (folder name where the repo will be cloned).
2. The AI will clone the repository, process the code, and generate embeddings.
3. You can then interact with the AI by entering queries or requesting changes to the codebase.
4. The AI will respond with relevant answers or modifications to the codebase.

**Streamlit Interface**

1. Enter the GitHub repository URL and repository name (folder name where the repo will be cloned).
2. The AI will clone the repository, process the code, and generate embeddings.
3. You can then interact with the AI by entering queries or requesting changes to the codebase in the chat interface.
4. The AI will respond with relevant answers or modifications to the codebase.

### Modules

* **`github_fetcher.py`**: Clones the specified GitHub repository.
* **`code_processor.py`**: Extracts code chunks from the repository.
* **`embeddings.py`**: Embeds code chunks using the Amazon Titan embedding model.
* **`vector_store.py`**: Stores and searches code chunks using FAISS.
* **`llm_clients.py`**: Interacts with a Large Language Model (LLM) for response generation.
* **`memory.py`**: Manages conversation history.
* **`file_operations.py`**: Handles file modifications within the repository.

###
