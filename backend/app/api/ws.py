"""WebSocket endpoint for real-time Agent step streaming."""
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Connection pool: {session_id: set([websocket, ...])}
_connections: dict[str, set[WebSocket]] = {}


@router.websocket("/ws/{session_id}")
async def agent_stream(ws: WebSocket, session_id: str):
    await ws.accept()
    if session_id not in _connections:
        _connections[session_id] = set()
    _connections[session_id].add(ws)

    try:
        # Listen for Redis pub/sub messages (if Redis available)
        try:
            import redis
            r = redis.Redis.from_url("redis://localhost:6379", decode_responses=True)
            pubsub = r.pubsub()
            pubsub.subscribe(f"agent_stream:{session_id}")
            while True:
                msg = pubsub.get_message(timeout=1.0)
                if msg and msg["type"] == "message":
                    await ws.send_text(msg["data"])
                await asyncio.sleep(0.1)
        except Exception:
            # Redis not available — keep connection alive
            while True:
                try:
                    await ws.receive_text()
                except WebSocketDisconnect:
                    break
    except WebSocketDisconnect:
        pass
    finally:
        _connections[session_id].discard(ws)
        if not _connections[session_id]:
            del _connections[session_id]


def push_event(session_id: str, event: dict):
    """Send an event to all WebSocket clients in a session."""
    msg = json.dumps(event, ensure_ascii=False)
    for ws in _connections.get(session_id, set()):
        try:
            asyncio.create_task(ws.send_text(msg))
        except Exception:
            pass
