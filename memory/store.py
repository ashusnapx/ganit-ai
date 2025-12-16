import json
from datetime import datetime
from pathlib import Path

MEMORY_PATH = Path("memory/solved_memory.jsonl")
MEMORY_PATH.parent.mkdir(exist_ok=True)


def store_solved_example(payload: dict):
    payload["timestamp"] = datetime.utcnow().isoformat()

    with open(MEMORY_PATH, "a") as f:
        f.write(json.dumps(payload) + "\n")
