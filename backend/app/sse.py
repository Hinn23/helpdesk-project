import asyncio
import json
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


class EventManager:
    def __init__(self):
        self._subscribers = []
        self._lock = asyncio.Lock()
        self._loop = None

    def set_loop(self, loop):
        self._loop = loop

    async def subscribe(self):
        queue = asyncio.Queue()
        async with self._lock:
            self._subscribers.append(queue)
        return queue

    async def unsubscribe(self, queue):
        async with self._lock:
            if queue in self._subscribers:
                self._subscribers.remove(queue)

    def broadcast_sync(self, event: str, data: dict):
        if not self._loop or not self._loop.is_running():
            return
        asyncio.run_coroutine_threadsafe(self._broadcast(event, data), self._loop)

    async def _broadcast(self, event: str, data: dict):
        payload = f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"
        async with self._lock:
            for q in self._subscribers[:]:
                try:
                    await q.put(payload)
                except Exception:
                    self._subscribers.remove(q)


events = EventManager()


async def event_generator() -> AsyncGenerator[str, None]:
    queue = await events.subscribe()
    try:
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=30)
                yield msg
            except asyncio.TimeoutError:
                yield ":\n\n"
    finally:
        await events.unsubscribe(queue)
