import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_PATH = "rag/faiss.index"
META_PATH = "rag/metadata.json"
MODEL_NAME = "all-MiniLM-L6-v2"


class Retriever:
    def __init__(self, top_k: int = 4):
        self.top_k = top_k
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = faiss.read_index(INDEX_PATH)

        with open(META_PATH, "r") as f:
            self.metadata = json.load(f)

    def retrieve(self, query: str):
        query_emb = self.model.encode(query)
        query_emb = np.array([query_emb]).astype("float32")

        distances, indices = self.index.search(query_emb, self.top_k)

        results = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])

        return results
