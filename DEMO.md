# SentinelSight Demo Script

**Time**: 3-5 Minutes
**Goal**: Demonstrate End-to-End ingestion to alert workflow.

## 1. Setup (Pre-Demo) (1 min)
- Ensure `docker-compose up` is running.
- Open `http://localhost:5173`.
- Have a valid RTSP URL ready (or a webcam stream exposed via RTSP).

## 2. Walkthrough (3 min)

### Dashboard Overview
- **Action**: Show the empty dashboard.
- **Script**: "This is the SentinelSight Dashboard. It provides a unified view of all camera feeds and real-time alerts. The design follows a 'dark mode' premium aesthetic to reduce eye strain for operators."

### Adding a Camera
- **Action**: Click "+ Add Stream". Enter Name "Main Gate" and RTSP URL.
- **Script**: "I'm adding a new camera stream. The system immediately attempts to connect and spins up an isolated inference process."
- **Visual**: Show the Camera Card appearing and the video feed loading with bounding boxes.

### Live Analytics
- **Action**: Point to the bounding box on a person.
- **Script**: "Here you see live inference using YOLOv8 running at the edge. It's detecting 'person' objects in real-time."

### Event Generation
- **Action**: Wait for an event to appear in the sidebar (or refresh if needed).
- **Script**: "When a rule is breached (like a person detected), an Event is generated. It captures a snapshot and metadata."
- **Visual**: Scroll through the Event Feed on the left.
- **Action**: Click the Snapshot (if implemented to expand) or just point out the details (Timestamp, Confidence).

### API & Architecture (Optional)
- **Action**: Briefly switch to `http://localhost:8000/docs`.
- **Script**: "Under the hood, everything is exposed via a REST API, allowing integration with 3rd party systems."

### Zone Configuration (New Feature)
- **Action**: Hover over the camera card and click the blue "Edit Zones" button.
- **Script**: "We've added a visual zone editor. Instead of messing with JSON configs, operators can simply draw the restricted area on the screen."
- **Action**: Click to draw a triangle or square around an area. Click 'Add Zone' then 'Save'.
- **Visual**: Show the zone being saved and explain how this immediately updates the inference engine's rules.

## 3. Wrap Up
- "This MVP demonstrates the core loop: Ingest -> Detect -> Alert -> Visualize. It's built to be modular and scalable."
