# SentinelSight - AI Video Analytics Platform

SentinelSight is a modern, modular Video Analysis platform designed to ingest RTSP streams, perform real-time object detection (using YOLOv8), and generate actionable alerts for security operations.

## Features
- **Multi-Camera Ingestion**: Robust RTSP handling with auto-reconnection.
- **AI Analytics**: Real-time people detection using YOLOv8.
- **Zone Monitoring**: Define (JSON) zones to trigger "Intrusion" or "Loitering" alerts.
- **Event Dashboard**: Premium dark-mode UI to view live feeds and historical alerts.
- **Event Persistence**: SQLite database for portability and ease of setup.

## Architecture
- **Backend**: FastAPI, OpenCV, Ultralytics YOLO, SQLAlchemy.
- **Frontend**: React, Vite, Vanilla CSS.
- **Deployment**: Docker Compose.

## Prerequisites
- Docker & Docker Compose
- Or: Python 3.9+ and Node.js 18+

## How to Run (Docker)
1. **Clone/ Navigate** to the repository root.
2. **Run**:
   ```bash
   docker-compose up --build
   ```
3. **Access**:
   - Dashboard: `http://localhost:5173`
   - API Docs: `http://localhost:8000/docs`

## How to Run (Local Dev)
### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```
### Frontend
```bash
cd frontend
npm install
npm run dev
```

## How to Test
1. Open the Dashboard (`http://localhost:5173`).
2. Click **"+ Add Stream"**.
3. Enter an RTSP URL. 
   - *Public Test Stream*: `rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov` (Note: This might not have people, prefer a camera or local file stream).
   - *Local File*: You can modify the backend code to accept file paths for testing if needed.
4. View the **Live Feed**. Bounding boxes will appear around detected people.
5. Watch the **Sidebar** for new events.

## Known Limitations
- **Object Tracking**: Currently, every frame detection is independent. No ID tracking across frames.
- **Zone Editor**: Visual editor implemented. Click "Edit Zones" on any camera card to draw polygons.
- **Authentication**: No login required for MVP.

## Next Steps
- Implement Zone Drawing UI.
- Add Object Tracking (DeepSORT).
- Add MQTT output.
