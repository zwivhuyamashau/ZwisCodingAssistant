# Zwi Coding Assistant – Python-based AI Assistant for Code Repository Interaction

Zwi Coding Assistant is a Python-based AI assistant designed to help users understand and interact with code repositories. It leverages modules for cloning repositories, processing code, generating vector embeddings, searching relevant code snippets, and interacting with large language models (LLMs) to provide intelligent, context-aware support.

---

## 🚀 Features

- Clone and analyze any GitHub repository
- Extract and embed code using Amazon Titan embeddings
- Search for relevant code using FAISS
- Interact with LLMs for insightful code explanations or modifications
- Choose between a **CLI** or **Streamlit-based Chat Interface**

---

## 🧑‍💻 Usage

### CLI Interface

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/zwi-coding-assistant.git
   cd zwi-coding-assistant
   ```

2. Set the environment variables: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
3. Run the CLI:
   ```bash
   python cli_main.py
   ```

---

### Streamlit Interface

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/zwi-coding-assistant.git
   cd zwi-coding-assistant
   ```

2. Set the environment variables: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
3. Launch the Streamlit app:
   ```bash
   streamlit run streamlit_main.py
   ```

---

## 🔐 Setting Environment Variables

To authenticate with AWS, you must set the following environment variables:

### Windows Command Prompt

```cmd
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key
```

### Windows PowerShell

```powershell
$env:AWS_ACCESS_KEY_ID="your_access_key"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key"
```

### macOS/Linux (Bash or Zsh)

```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
```

---

## 💡 How It Works

### CLI Workflow

1. Enter a GitHub repository URL and a folder name for cloning.
2. The assistant clones the repository and processes the codebase.
3. It then generates code embeddings using Amazon Titan.
4. You can ask questions or request code modifications directly from the terminal.
5. The assistant returns contextually relevant answers or edits to the codebase.

### Streamlit Workflow

1. Enter a GitHub repository URL and folder name via the UI.
2. The assistant clones and processes the repository in the background.
3. Use the Streamlit chat interface to ask questions or request changes.
4. The assistant responds interactively in real-time.

---

## 📦 Modules Overview

- **`github_fetcher.py`** – Clones a GitHub repository.
- **`code_processor.py`** – Extracts and segments code into manageable chunks.
- **`embeddings.py`** – Generates embeddings using Amazon Titan.
- **`vector_store.py`** – Stores and retrieves vectors using FAISS.
- **`llm_clients.py`** – Interfaces with a Large Language Model for generating responses.
- **`memory.py`** – Maintains session history to improve conversational context.
- **`file_operations.py`** – Modifies files based on user instructions.

---

## 📈 Next Milestones

The project is under active development. Planned features include:

- ✅ Enhanced **Streamlit UI** with better usability and responsiveness
- 🔄 Support for **multiple LLMs** (e.g., OpenAI, Anthropic, Mistral, etc.)
- ✍️ Advanced **file writing and review** capabilities
- 📄 Integration of **PDF and web scraping** for richer context

---
