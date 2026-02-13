import json
from pathlib import Path
from typing import Dict, Any
from domain.repositories import EventStore

class InMemoryEventStore(EventStore):
    def __init__(self, file_path: str = "events.jsonl"):
        self.file_path = Path(file_path)
        self.file_path.touch(exist_ok=True)

    def append_event(self, event: Dict[str, Any]) -> None:
        with self.file_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def read_events(self):
        with self.file_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)
