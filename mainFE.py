import streamlit as st
from github_fetcher import clone_repo
from code_processor import get_code_chunks
from embeddings import get_titan_embedding
from vector_store import FAISSVectorStore
from llm_clients import ask_llama
from memory import ConversationMemory
from file_operations import RepoFileManager
import os

# Initialize session state variables
if 'conversation_memory' not in st.session_state:
    st.session_state.conversation_memory = ConversationMemory()
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'repo_cloned' not in st.session_state:
    st.session_state.repo_cloned = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# App title and description
st.title("GitHub Repository AI Assistant")
st.markdown("""
This assistant lets you chat about a GitHub repository's codebase.
It can analyze code and modify files when instructed.
""")

# Repository setup form
with st.form("repo_setup"):
    repo_url = st.text_input("GitHub Repository URL")
    repo_name = st.text_input("Repository name (for local folder)")
    clone_btn = st.form_submit_button("Clone Repository")

    if clone_btn and repo_url and repo_name:
        try:
            with st.spinner("Cloning repository..."):
                clone_repo(repo_url, repo_name)
                st.session_state.repo_path = os.path.abspath(repo_name)
                st.session_state.file_manager = RepoFileManager(st.session_state.repo_path)
                
                # Process code chunks
                with st.spinner("Processing code..."):
                    chunks = get_code_chunks(repo_name)
                    dim = 1024
                    embeddings = [get_titan_embedding(chunk[1]) for chunk in chunks]
                    st.session_state.vector_store = FAISSVectorStore(dim)
                    st.session_state.vector_store.add(embeddings, chunks)
                
                st.session_state.repo_cloned = True
                st.success("Repository cloned and processed successfully!")
        except Exception as e:
            st.error(f"Error cloning repository: {str(e)}")

# Display instructions if repo is cloned
if st.session_state.get('repo_cloned', False):
    with st.expander("Instructions", expanded=True):
        st.markdown("""
        - Type 'exit' or 'quit' to end the session
        - The AI can modify files within the repository
        - File modifications will be shown in the response
        - Repository base path: {}
        - Use either absolute paths or paths relative to the repository root
        """.format(st.session_state.repo_path))
        st.code(f"Example absolute path: {os.path.join(st.session_state.repo_path, 'README.md')}")
        st.code("Example relative path: README.md")

# Chat interface
if st.session_state.get('repo_cloned', False):
    st.subheader("Chat with Repository")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input form
    with st.form("chat_form"):
        user_input = st.text_area("Your message:", key="input", height=100)
        submit_btn = st.form_submit_button("Send")
        
        if submit_btn and user_input:
            if user_input.lower() in ["exit", "quit"]:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": "Goodbye!"})
                st.rerun()
            
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            with st.spinner("Analyzing..."):
                try:
                    # Retrieve relevant code snippets
                    query_embedding = get_titan_embedding(user_input)
                    relevant_chunks = st.session_state.vector_store.search(query_embedding, top_k=20)
                    context = "\n\n".join([f"{path}:\n{code}" for path, code in relevant_chunks])
                    
                    # Get conversation history
                    recent_history = st.session_state.conversation_memory.get_recent_history()
                    history_text = "\n".join(
                        [f"User: {ih['user_input']}\nAssistant: {ih['assistant_response']}" 
                         for ih in recent_history]
                    )
                    
                    # Construct prompt
                    prompt = f"{history_text}\nUser: {user_input}\nContext:\n{context}\nAssistant:"
                    
                    # Get LLM response
                    assistant_response = ask_llama(context, prompt, st.session_state.repo_path)
                    
                    # Add to conversation memory
                    st.session_state.conversation_memory.add_interaction(user_input, context, assistant_response)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
                    
                    # Refresh code chunks after modifications
                    with st.spinner("Updating code index..."):
                        chunks = get_code_chunks(st.session_state.repo_path)
                        embeddings = [get_titan_embedding(chunk[1]) for chunk in chunks]
                        st.session_state.vector_store = FAISSVectorStore(1024)
                        st.session_state.vector_store.add(embeddings, chunks)
                    
                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            
            st.rerun()