from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.sse import event_generator

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
async def stream_events(request: Request):
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
