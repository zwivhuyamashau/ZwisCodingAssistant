import faiss
import numpy as np

class FAISSVectorStore:
    def __init__(self, dim):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.text_chunks = []

    def add(self, embeddings, chunks):
        valid_embeddings = []
        valid_chunks = []

        for emb, chunk in zip(embeddings, chunks):
            if len(emb) == self.dim:
                valid_embeddings.append(emb)
                valid_chunks.append(chunk)
            else:
                print(f"Skipping invalid embedding of size {len(emb)}")

        if valid_embeddings:
            self.index.add(np.array(valid_embeddings).astype("float32"))
            self.text_chunks.extend(valid_chunks)
        else:
            print("No valid embeddings to add.")

    def search(self, query_embedding, top_k=5):
        if self.index.ntotal == 0:
            print("Index is empty. Cannot perform search.")
            return []

        D, I = self.index.search(np.array([query_embedding]).astype("float32"), top_k)
        return [self.text_chunks[i] for i in I[0] if i < len(self.text_chunks)]
