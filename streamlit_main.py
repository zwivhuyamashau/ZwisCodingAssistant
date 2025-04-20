import os
import streamlit as st
from github_fetcher import clone_repo
from code_processor import get_code_chunks
from embeddings import TitanEmbeddings
from langchain.vectorstores import FAISS
from llm_clients import ask_llm
from memory import ConversationMemory
from file_operations import RepoFileManager

# --- Check AWS Credentials ---
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

if not aws_access_key_id or not aws_secret_access_key:
    st.error("❌ AWS credentials not found. Please set environment variables:")
    st.markdown("""
    Configure these environment variables before running the app:
    - `AWS_ACCESS_KEY_ID`
    - `AWS_SECRET_ACCESS_KEY`
    """)
    st.stop()

# --- Page Configuration ---
st.set_page_config(
    page_title="Zwis Coding Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Initialization ---
if 'conversation_memory' not in st.session_state:
    st.session_state.conversation_memory = ConversationMemory()
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'embedding_model' not in st.session_state:
    st.session_state.embedding_model = TitanEmbeddings()
if 'repo_cloned' not in st.session_state:
    st.session_state.repo_cloned = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- UI Components ---
def show_sidebar():
    with st.sidebar:
        st.header("Zwi's coding Agent 🛠️")
        
        if st.session_state.get('repo_cloned'):
            st.markdown("---")
            st.subheader("Repository Info 🗂️")
            st.caption(f"Location: {st.session_state.get('repo_path', '')}")
            
            if st.button("Clear Session 🔄"):
                st.session_state.clear()
                st.rerun()
        
        st.markdown("---")
        with st.expander("Usage Guide 📖", expanded=True):
            st.markdown("""
            **How to use:**
            1. Enter GitHub repo URL below
            2. Clone repository
            3. Chat with the AI about the codebase

            **Features:**
            - Code analysis
            - File modifications
            - Context-aware conversations
            - Automatic code indexing

            **Requirements:**
            - AWS credentials set via environment variables
            - GitHub repository access
            """)

# --- Main Interface ---
def main():
    st.title("🤖 Zwi's coding Agent")
    st.markdown("*Your intelligent partner for codebase analysis and modification*")
    
    # --- Repository Setup Card ---
    with st.container(border=True):
        st.subheader("Repository Setup 🛠️")
        col1, col2 = st.columns([3, 2])
        with col1:
            repo_url = st.text_input(
                "GitHub URL",
                placeholder="https://github.com/user/repo.git",
                help="SSH or HTTPS URL of the repository"
            )
        with col2:
            repo_name = st.text_input(
                "Local Directory Name",
                placeholder="my-repo",
                help="Name for local copy of the repository"
            )
        
        if st.button("Clone Repository 🌐", type="primary"):
            if repo_url and repo_name:
                try:
                    with st.status("Cloning repository...", expanded=True) as status:
                        st.write("🔗 Connecting to GitHub...")
                        clone_repo(repo_url, repo_name)
                        st.session_state.repo_path = os.path.abspath(repo_name)
                        st.session_state.file_manager = RepoFileManager(st.session_state.repo_path)
                        
                        st.write("🔍 Analyzing code structure...")
                        chunks = get_code_chunks(repo_name)
                        
                        st.write("🧠 Indexing codebase...")
                        texts = [chunk[1] for chunk in chunks]
                        metadatas = [{"path": chunk[0]} for chunk in chunks]
                        
                        st.session_state.vector_store = FAISS.from_texts(
                            texts=texts,
                            metadatas=metadatas,
                            embedding=st.session_state.embedding_model
                        )
                        
                        status.update(label="Repository ready!", state="complete")
                        st.session_state.repo_cloned = True
                        st.toast("Repository cloned successfully!", icon="🎉")
                except Exception as e:
                    st.error(f"🚨 Cloning failed: {str(e)}")
            else:
                st.warning("Please provide both repository URL and directory name")

    # --- Chat Interface ---
    if st.session_state.get('repo_cloned'):
        st.divider()
        st.subheader("Code Chat 💬")
        
        # Chat History
        chat_container = st.container(height=500)
        with chat_container:
            for msg in st.session_state.chat_history:
                avatar = "👤" if msg["role"] == "user" else "🤖"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.markdown(msg["content"])
        
        # Input Area
        if prompt := st.chat_input("Ask about the codebase or request changes..."):
            # Handle exit command
            if prompt.lower() in ["exit", "quit"]:
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.session_state.chat_history.append({"role": "assistant", "content": "👋 Goodbye! Session ended."})
                st.rerun()
            
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.status("Processing...", state="running") as status:
                try:
                    # Context retrieval
                    st.write("🔎 Searching code context...")
                    query_embedding = st.session_state.embedding_model.embed_query(prompt)
                    relevant_docs = st.session_state.vector_store.similarity_search_by_vector(
                        query_embedding, 
                        k=20
                    )
                    relevant_chunks = [(doc.metadata['path'], doc.page_content) for doc in relevant_docs]
                    context = "\n\n".join([f"**{path}**:\n```{code}```" for path, code in relevant_chunks])
                    
                    # Generate response
                    st.write("💡 Generating response...")
                    recent_history = st.session_state.conversation_memory.get_recent_history()
                    history_text = "\n".join(
                        [f"User: {ih['user_input']}\nAssistant: {ih['assistant_response']}" 
                         for ih in recent_history]
                    )
                    full_prompt = f"{history_text}\nUser: {prompt}\nContext:\n{context}\nAssistant:"
                    response = ask_llm(context, full_prompt, st.session_state.repo_path)
                    
                    # Update conversation
                    st.session_state.conversation_memory.add_interaction(prompt, context, response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                    # Refresh index
                    st.write("🔄 Updating code index...")
                    chunks = get_code_chunks(st.session_state.repo_path)
                    texts = [chunk[1] for chunk in chunks]
                    metadatas = [{"path": chunk[0]} for chunk in chunks]
                    st.session_state.vector_store = FAISS.from_texts(
                        texts=texts,
                        metadatas=metadatas,
                        embedding=st.session_state.embedding_model
                    )
                    
                    status.update(label="Response ready!", state="complete")
                except Exception as e:
                    st.error(f"🚨 Processing error: {str(e)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": f"Error: {str(e)}"})
            
            st.rerun()

# --- Run Application ---
show_sidebar()
main()