import cv2
import threading
import time
import queue
from .inference import InferenceEngine
from .database import SessionLocal
from .models import Event
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CameraStream:
    def __init__(self, camera_id, rtsp_url, zone_config):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.zone_config = zone_config
        self.cap = None
        self.running = False
        self.thread = None
        self.latest_frame = None
        self.lock = threading.Lock()
        self.inference_engine = InferenceEngine() # Each stream gets own engine or shared? Shared is better for memory but need thread safety. 
        # For simplicity, instantiating new one or we can pass a shared one. Let's start with new one to avoid GIL issues effectively? No, model should be shared.
        # Actually YOLO is thread safe usually if called correctly. Let's use a shared one in manager.
        
    def update_status(self, status):
        try:
            db = SessionLocal()
            from .models import Camera # Deferred import to avoid circular dep
            # Or use sql update query directly for speed
            db.query(Camera).filter(Camera.id == self.camera_id).update({"status": status})
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to update status for {self.camera_id}: {e}")

    def start(self, shared_inference_engine):
        self.running = True
        self.thread = threading.Thread(target=self.update, args=(shared_inference_engine,))
        self.thread.daemon = True
        self.thread.start()

    def update(self, inference_engine):
        logger.info(f"Connecting to {self.rtsp_url}...")
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if self.cap.isOpened():
             self.update_status("online")
        
        while self.running:
            if not self.cap.isOpened():
                self.update_status("offline")
                logger.warning(f"Camera {self.camera_id} disconnected. Reconnecting in 5s...")
                time.sleep(5)
                self.cap = cv2.VideoCapture(self.rtsp_url)
                if self.cap.isOpened(): self.update_status("online")
                continue
                
            ret, frame = self.cap.read()
            if not ret:
                self.update_status("offline")
                logger.warning(f"Failed to read frame from {self.camera_id}. Reconnecting...")
                self.cap.release()
                continue
            
            # Resize for performance if needed
            frame = cv2.resize(frame, (640, 480))
            
            # Inference
            results = inference_engine.detect(frame)
            
            # Check rules
            alerts = inference_engine.check_rules(frame, results, self.zone_config, self.camera_id)
            
            if alerts:
                self.save_events(alerts, frame)
            
            # Annotate frame
            annotated_frame = results.plot()
            
            with self.lock:
                self.latest_frame = annotated_frame
            
            # Limit FPS to save CPU
            # time.sleep(0.01) 

    def save_events(self, alerts, frame):
        db = SessionLocal()
        for alert in alerts:
            # Basic throttling: Don't save if similar event in last X seconds? 
            # For MVP, just save everything or maybe 1 per second per rule.
            # Skipping throttling for now for simplicity, rely on frontend or rule engine to not spam.
            
            # Save snapshot
            timestamp = int(time.time() * 1000)
            snapshot_filename = f"event_{self.camera_id}_{timestamp}.jpg"
            snapshot_path = f"backend/data/{snapshot_filename}" # Path relative to root? Or absolute? 
            # We are running from root.
            cv2.imwrite(snapshot_path, frame)
            
            event = Event(
                camera_id=self.camera_id,
                rule_name=alert['rule_name'],
                object_type=alert['object_type'],
                confidence=alert['confidence'],
                snapshot_path=snapshot_path
            )
            db.add(event)
        db.commit()
        db.close()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        self.update_status("offline")

    def get_frame(self):
        with self.lock:
            if self.latest_frame is not None:
                ret, jpeg = cv2.imencode('.jpg', self.latest_frame)
                return jpeg.tobytes()
            return None

class StreamManager:
    def __init__(self):
        self.streams = {}
        self.inference_engine = InferenceEngine()

    def add_stream(self, camera_id, rtsp_url, zone_config):
        if camera_id in self.streams:
            self.stop_stream(camera_id)
            
        stream = CameraStream(camera_id, rtsp_url, zone_config)
        stream.start(self.inference_engine)
        self.streams[camera_id] = stream

    def stop_stream(self, camera_id):
        if camera_id in self.streams:
            self.streams[camera_id].stop()
            del self.streams[camera_id]

    def get_stream_frame(self, camera_id):
        if camera_id in self.streams:
            return self.streams[camera_id].get_frame()
        return None
        
# Global instance
stream_manager = StreamManager()
