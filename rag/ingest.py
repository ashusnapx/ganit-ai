import os
import json
from sentence_transformers import SentenceTransformer
import faiss

KB_DIR = "rag/kb_docs"
INDEX_PATH = "rag/faiss.index"
META_PATH = "rag/metadata.json"

CHUNK_SIZE = 300  # characters
MODEL_NAME = "all-MiniLM-L6-v2"


def infer_topic_from_filename(filename: str) -> str:
    if "algebra" in filename:
        return "algebra"
    if "calculus" in filename:
        return "calculus"
    if "probability" in filename:
        return "probability"
    if "linear" in filename:
        return "linear_algebra"
    return "general"


def infer_difficulty(text: str) -> str:
    if "determinant" in text or "conditional" in text:
        return "medium"
    return "easy"


def chunk_text(text: str):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE
    return chunks


def ingest():
    model = SentenceTransformer(MODEL_NAME)

    embeddings = []
    metadata = []

    for filename in os.listdir(KB_DIR):
        if not filename.endswith(".md"):
            continue

        path = os.path.join(KB_DIR, filename)
        with open(path, "r") as f:
            content = f.read()

        topic = infer_topic_from_filename(filename)
        chunks = chunk_text(content)

        for chunk in chunks:
            emb = model.encode(chunk)
            embeddings.append(emb)

            metadata.append({
                "text": chunk,
                "source": filename,
                "topic": topic,
                "difficulty": infer_difficulty(chunk)
            })

    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))

    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Ingested {len(metadata)} chunks into FAISS")


if __name__ == "__main__":
    import numpy as np
    ingest()
