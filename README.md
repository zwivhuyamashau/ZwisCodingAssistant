# Python-based AI Assistant for Code Repository Interaction

This project is a Python-based AI assistant designed to help users understand and interact with code repositories. It leverages various modules for cloning repositories, processing code, embedding vectors, searching for relevant code, and interacting with large language models (LLMs) to provide contextually relevant answers.

## Usage
1. Clone the repository.
2. Install the required dependencies.
3. Add the AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY and AWS_DEFAULT_REGION to your environment path.
4. Run the main.py file.

## How It Works

### 1. **Repository Cloning**
The user starts by providing a GitHub repository URL along with a folder name where the repository will be cloned. The `clone_repo` function from the `github_fetcher.py` module is used to clone the repository to the specified folder.

### 2. **Code Chunking**
Once the repository is cloned, the assistant processes the code to extract manageable chunks of code (default size is 500 characters). This is done using the `get_code_chunks` function from `code_processor.py`, which returns a list of tuples, where each tuple contains the file path and its corresponding code chunk.

### 3. **Embedding and Storage**
The extracted code chunks are then embedded into vectors using the `get_titan_embedding` function from `embeddings.py`. This function utilizes the Amazon Titan embedding model. The resulting embedded vectors are stored in a FAISS (Facebook AI Similarity Search) vector store, which is managed by the `vector_store.py` module.

### 4. **User Input and Search**
The user is prompted to enter a query, which is then embedded into a vector using the same `get_titan_embedding` function. The FAISS vector store is queried for the top-k most similar code chunks to the user's query vector. This search process is handled by the `search` function in `vector_store.py`.

### 5. **Context Construction and LLM Interaction**
The relevant code chunks returned from the search are used to build a context string. This string, along with the user's query and recent conversation history, forms a prompt that is sent to a Large Language Model (LLM) client, implemented in `llm_clients.py`. The LLM generates a response based on this context.

### 6. **Conversation Memory**
The conversation history is tracked using a `ConversationMemory` object, implemented in `memory.py`. This object stores recent interactions, ensuring that the assistant has a sense of context in subsequent interactions.

### 7. **Looping**
The user can continue interacting with the assistant by entering additional queries. The assistant repeats the process from step 4, using the latest conversation history and code chunks to provide relevant answers.

## Modules

- **`github_fetcher.py`**: Clones the specified GitHub repository.
- **`code_processor.py`**: Extracts code chunks from the repository.
- **`embeddings.py`**: Embeds code chunks using the Amazon Titan embedding model.
- **`vector_store.py`**: Stores and searches code chunks using FAISS.
- **`llm_clients.py`**: Interacts with a Large Language Model (LLM) for response generation.
- **`memory.py`**: Manages conversation history.

## Requirements
- Python 3.x
- Necessary Python libraries (e.g., `faiss`, `requests`, `openai`)



