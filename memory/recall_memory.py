import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np

MEMORY_PATH = Path("memory/solved_memory.jsonl")
MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def recall_similar(problem_text: str, top_k: int = 1):
    if not MEMORY_PATH.exists():
        return []

    with open(MEMORY_PATH, "r") as f:
        records = [json.loads(line) for line in f]

    if not records:
        return []

    query_emb = MODEL.encode(problem_text)
    past_texts = [r["original_input"] for r in records]
    past_embs = MODEL.encode(past_texts)

    sims = np.dot(past_embs, query_emb) / (
        np.linalg.norm(past_embs, axis=1) * np.linalg.norm(query_emb)
    )

    ranked = sorted(
        zip(records, sims),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        {
            "similarity": round(score, 3),
            "final_answer": rec["final_answer"],
            "parsed_problem": rec["parsed_problem"]
        }
        for rec, score in ranked[:top_k]
        if score > 0.75
    ]
