from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
from ..stream_manager import stream_manager
import time

router = APIRouter()

def gen_frames(camera_id):
    while True:
        frame = stream_manager.get_stream_frame(camera_id)
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.1) # Wait if no frame available

@router.get("/{camera_id}")
def video_feed(camera_id: int):
    return StreamingResponse(
        gen_frames(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
