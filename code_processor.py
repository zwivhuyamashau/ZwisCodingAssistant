# code_processor.py
from pathlib import Path

def get_code_chunks(repo_path, extensions=(".py", ".js", ".ts",".md"), chunk_size=500):
    chunks = []
    for file_path in Path(repo_path).rglob("*"):
        if file_path.suffix in extensions:
            text = file_path.read_text(errors="ignore")
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                chunks.append((str(file_path), chunk))
    return chunks
