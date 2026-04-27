import asyncio
from collections import defaultdict
from typing import Callable, Any

class EventBus:
    def __init__(self):
        self._listeners = defaultdict(list)

    def on(self, event_type: str, callback: Callable[[dict], Any]):
        self._listeners[event_type].append(callback)

    async def emit(self, event_type: str, data: dict):
        if event_type not in self._listeners:
            return

        for callback in self._listeners[event_type]:
            result = callback(data)
            if asyncio.iscoroutine(result):
                await result