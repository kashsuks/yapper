import queue
import threading
import time
from typing import Dict, Iterator, Optional


class LogEvent:
    def __init__(self, category: str, level: str, message: str, ts: Optional[float] = None):
        self.category = category
        self.level = level
        self.message = message
        self.ts = ts or time.time()

    def to_sse(self) -> str:
        payload = {
            "category": self.category,
            "level": self.level,
            "message": self.message,
            "ts": self.ts,
        }
        import json

        return f"data: {json.dumps(payload)}\n\n"


class CategoryState:
    def __init__(self):
        self.status: str = "idle"
        self.last_message: str = ""
        self.last_level: str = "info"
        self.last_ts: float = 0.0


class LogBroker:
    def __init__(self):
        self._listeners: Dict[int, queue.Queue[LogEvent]] = {}
        self._next_id: int = 1
        self._lock = threading.Lock()
        self.categories: Dict[str, CategoryState] = {}

    def publish(self, event: LogEvent):
        with self._lock:
            if event.category not in self.categories:
                self.categories[event.category] = CategoryState()
            cat = self.categories[event.category]
            cat.last_message = event.message
            cat.last_level = event.level
            cat.last_ts = event.ts

            cat.status = "error" if event.level.lower() == "error" else "ok"

            for q in list(self._listeners.values()):
                try:
                    q.put_nowait(event)
                except Exception:
                    pass

    def subscribe(self) -> Iterator[str]:
        with self._lock:
            listener_id = self._next_id
            self._next_id += 1
            q: queue.Queue[LogEvent] = queue.Queue(maxsize=1024)
            self._listeners[listener_id] = q

        try:
            snapshot = []
            with self._lock:
                for category, state in self.categories.items():
                    snapshot.append(LogEvent(category, state.last_level, state.last_message, state.last_ts))
            for evt in snapshot:
                yield evt.to_sse()

            while True:
                try:
                    evt = q.get(timeout=15)
                    yield evt.to_sse()
                except queue.Empty:
                    yield ": keep-alive\n\n"
        finally:
            with self._lock:
                self._listeners.pop(listener_id, None)


globalBroker = LogBroker()