from ultralytics import YOLO
import cv2
import numpy as np
from datetime import datetime
import json

class CentroidTracker:
    def __init__(self, max_disappeared=5):
        self.next_object_id = 0
        self.objects = {} # ID -> point
        self.disappeared = {} # ID -> count
        self.object_timers = {} # ID -> {zone_name: entry_time}
        self.max_disappeared = max_disappeared

    def update(self, rects):
        if len(rects) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        input_centroids = np.zeros((len(rects), 2), dtype="int")
        for (i, (startX, startY, endX, endY)) in enumerate(rects):
            cX = int((startX + endX) / 2.0)
            cY = int(endY) # Foot point
            input_centroids[i] = (cX, cY)

        if len(self.objects) == 0:
            for i in range(0, len(input_centroids)):
                self.register(input_centroids[i])
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())
            
            # Distance calc
            D = np.linalg.norm(np.array(object_centroids) - input_centroids[:, np.newaxis], axis=2)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols: continue
                
                # Check distance threshold (e.g. tracking jump)
                if D[row, col] > 100: continue 

                object_id = object_ids[col]
                self.objects[object_id] = input_centroids[row]
                self.disappeared[object_id] = 0
                used_rows.add(row)
                used_cols.add(col)

            for col in range(len(object_ids)):
                 if col not in used_cols:
                     object_id = object_ids[col]
                     self.disappeared[object_id] += 1
                     if self.disappeared[object_id] > self.max_disappeared:
                         self.deregister(object_id)

            for row in range(len(input_centroids)):
                if row not in used_rows:
                    self.register(input_centroids[row])

        return self.objects

    def register(self, centroid):
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.object_timers[self.next_object_id] = {}
        self.next_object_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]
        del self.object_timers[object_id]

class InferenceEngine:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)
        self.classes = self.model.names
        self.tracker = CentroidTracker()
        self.last_alerts = {} # Simple dedup: {rule_zone_id: timestamp}

    def detect(self, frame):
        results = self.model(frame, verbose=False)
        return results[0]

    def check_rules(self, frame, detections, zone_config, camera_id):
        alerts = []
        if not zone_config: return alerts
        try: zones = json.loads(zone_config)
        except: return alerts

        boxes = detections.boxes.xyxy.cpu().numpy()
        clss = detections.boxes.cls.cpu().numpy()
        
        # Filter for people
        person_boxes = []
        for box, cls in zip(boxes, clss):
            if self.classes[int(cls)] == 'person':
                person_boxes.append(box)
        
        # Update tracker
        objects = self.tracker.update(person_boxes)
        
        current_time = datetime.now()
        
        for object_id, centroid in objects.items():
            point = (centroid[0], centroid[1])
            
            for zone in zones:
                poly_points = np.array(zone['points'], np.int32)
                is_inside = cv2.pointPolygonTest(poly_points, point, False) >= 0
                zone_name = zone.get('name', 'Zone')
                
                # Update Timer
                if is_inside:
                    if zone_name not in self.tracker.object_timers[object_id]:
                        self.tracker.object_timers[object_id][zone_name] = current_time
                else:
                    if zone_name in self.tracker.object_timers[object_id]:
                        del self.tracker.object_timers[object_id][zone_name]
                        
                # Check Rules
                if is_inside:
                    # Invoking rule logic
                    start_time = self.tracker.object_timers[object_id].get(zone_name)
                    if start_time:
                         duration = (current_time - start_time).total_seconds()
                         zone_triggers = zone.get('triggers', ['intrusion']) # Default to intrusion for backward compat

                         event_type = None
                         
                         # Intrusion: Immediate (or short debounce)
                         if 'intrusion' in zone_triggers and duration < 2: 
                             event_type = "Intrusion"
                         
                         # Loitering: > 5 seconds
                         elif 'loitering' in zone_triggers and duration > 5:
                             event_type = "Loitering"
                             
                         if event_type:
                             # Simple dedup mechanism (throttle alerts per obj/zone)
                             dedup_key = f"{camera_id}_{object_id}_{zone_name}_{event_type}"
                             last = self.last_alerts.get(dedup_key)
                             
                             if not last or (current_time - last).total_seconds() > 10:
                                 alerts.append({
                                     "camera_id": camera_id,
                                     "rule_name": f"{event_type}: {zone_name}",
                                     "object_type": "person",
                                     "confidence": 0.9, # Tracker confidence?
                                     "timestamp": current_time,
                                     "box": [0,0,0,0] # Centroids don't track full box in this simple ver
                                 })
                                 self.last_alerts[dedup_key] = current_time
                                 
        return alerts
