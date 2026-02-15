import json
from pathlib import Path
from domain.models import EventResult, LockerEvent
from domain.repositories import EventStore

class FileEventStore(EventStore):
    def __init__(self, file_path: str = "events.jsonl"):
        self.file_path = Path(file_path)
        self.file_path.touch(exist_ok=True)

    def load_all(self) -> list[LockerEvent]:
        events = self._load_event()
        return events
    
    def load_by_locker(self, locker_id: str) -> list[LockerEvent]:
        events = self._load_event(locker_id)
        return events
    
    def append(self, event: LockerEvent) -> int:
        for load_event in self.load_all():
            # event_id already exists
            if event.event_id == load_event.event_id:
                return EventResult.DUPLICATE
        self._append_event(event)
        return EventResult.SUCCESS

    def _load_event(self, locker_id: str | None = None) -> list[LockerEvent]:
        events = []
        with self.file_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    event = LockerEvent(
                            data["event_id"],
                            data["occurred_at"], 
                            data["locker_id"], 
                            data["type"],
                            data["payload"]
                        )
                    if not locker_id or (locker_id and locker_id == data["locker_id"]):
                        events.append(event)
        return events 

    def _append_event(self, event: LockerEvent) -> None:
        with self.file_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                    "event_id": str(event.event_id),
                    "occurred_at": str(event.occurred_at),
                    "locker_id": event.locker_id,
                    "type": event.type,
                    "payload": event.payload
                }) + "\n")
