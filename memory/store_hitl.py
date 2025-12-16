import json
from datetime import datetime
from pathlib import Path

MEMORY_PATH = Path("memory/hitl_corrections.jsonl")
MEMORY_PATH.parent.mkdir(exist_ok=True)


def store_hitl_signal(payload: dict):
    payload["timestamp"] = datetime.utcnow().isoformat()

    with open(MEMORY_PATH, "a") as f:
        f.write(json.dumps(payload) + "\n")
