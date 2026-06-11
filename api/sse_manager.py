"""SSE (Server-Sent Events) Manager for real-time Agent state streaming."""
import asyncio
import json
from typing import Dict, Any


class SSEManager:
    """Manages per-session event queues for SSE streaming."""

    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}

    def create_session(self, session_id: str) -> None:
        """Create an event queue for a new session."""
        if session_id not in self._queues:
            self._queues[session_id] = asyncio.Queue()

    def disconnect(self, session_id: str) -> None:
        """Remove a session's event queue."""
        self._queues.pop(session_id, None)

    async def emit(self, session_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """Push an SSE event to the session's queue.

        Args:
            session_id: Target session.
            event_type: One of step_start, step_update, step_complete,
                        approval_required, step_error, execution_complete.
            data: Event payload dict.
        """
        if session_id not in self._queues:
            self.create_session(session_id)

        await self._queues[session_id].put({
            "event": event_type,
            "data": data,
        })

    async def stream(self, session_id: str):
        """Async generator yielding SSE-formatted strings.

        Args:
            session_id: Session to stream events for.

        Yields:
            SSE-formatted strings: 'event: {type}\\ndata: {json}\\n\\n'
        """
        if session_id not in self._queues:
            self.create_session(session_id)

        queue = self._queues[session_id]

        try:
            while True:
                event = await queue.get()
                yield f"event: {event['event']}\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            self.disconnect(session_id)

    def emit_sync(self, session_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """Synchronous wrapper for emit — schedules coroutine on running loop.

        Use this from sync contexts (e.g., LangGraph nodes called via ThreadPoolExecutor).
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return  # No event loop running (e.g., in tests without async)

        if session_id not in self._queues:
            self.create_session(session_id)

        loop.call_soon_threadsafe(
            lambda: asyncio.create_task(self.emit(session_id, event_type, data))
        )
