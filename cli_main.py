from github_fetcher import clone_repo
from code_processor import get_code_chunks
from langchain.vectorstores import FAISS
from embeddings import TitanEmbeddings
from llm_clients import ask_llm
from memory import ConversationMemory
from file_operations import RepoFileManager
import os

conversation_memory = ConversationMemory()

# Step 1: Get Repo URL and Repo Name from the User
repo_url = input("Enter the GitHub repository URL: ")
repo_name = input("Enter the repository name (folder name where the repo will be cloned): ")

# Step 2: Clone Repo
clone_repo(repo_url, repo_name)

# Initialize file manager with absolute path
repo_path = os.path.abspath(repo_name)
file_manager = RepoFileManager(repo_path)

# Step 3: Chunk Code
chunks = get_code_chunks(repo_name)

# Step 4: Create vector store with LangChain
embedding_model = TitanEmbeddings()
texts = [chunk[1] for chunk in chunks]
metadatas = [{"path": chunk[0]} for chunk in chunks]
vectorstore = FAISS.from_texts(texts=texts, metadatas=metadatas, embedding=embedding_model)

print("\nInstructions:")
print("- Type 'exit' or 'quit' to end the session")
print("- The AI can modify files within the repository")
print(f"- Repository base path: {repo_path}")

while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    # Retrieve relevant code snippets based on user input
    query_embedding = embedding_model.embed_query(user_input)
    relevant_docs = vectorstore.similarity_search_by_vector(query_embedding, k=20)
    context = [(doc.metadata['path'], doc.page_content) for doc in relevant_docs]

    # Combine recent history for context
    recent_history = conversation_memory.get_recent_history()
    history_text = ""
    for interaction in recent_history:
        history_text += f"User: {interaction['user_input']}\n"
        history_text += f"Assistant: {interaction['assistant_response']}\n"

    # Construct the prompt with history and current context
    prompt = f"{history_text}\nUser: {user_input}\nContext:\n{context}\nAssistant:"

    # Get response from LLM with repository path for file operations
    assistant_response = ask_llm(context, prompt, repo_path)

    # Display and store the interaction
    print(f"Assistant: {assistant_response}")
    conversation_memory.add_interaction(user_input, context, assistant_response)

    # Refresh code chunks after potential modifications
    chunks = get_code_chunks(repo_name)
    texts = [chunk[1] for chunk in chunks]
    metadatas = [{"path": chunk[0]} for chunk in chunks]
    vectorstore = FAISS.from_texts(texts=texts, metadatas=metadatas, embedding=embedding_model)
