# Research & Best Practices Notes

## 1. Global Products Studied
I analyzed three leading Video Management Systems (VMS) and AI analytics platforms to inform the architecture of SentinelSight:

### A. Milestone XProtect (VMS)
- **Key Concept**: Centralized Management & Open Platform.
- **Pattern Adopted**: The concept of treating cameras as first-class entities with metadata (location, status) and a centralized management API.
- **Why**: Essential for scaling beyond a single site.

### B. BriefCam (Video Analytics)
- **Key Concept**: "Review, Respond, Research".
- **Pattern Adopted**: The "Respond" (Real-time alerts) module was the primary focus for this MVP.
- **Why**: Real-time actionable intelligence is the highest value proposition for security operators.

### C. Frigate (Local NVR)
- **Key Concept**: Local-first processing with privacy in mind.
- **Pattern Adopted**:
    - **Zones**: Using defined polygons to reduce false positives.
    - **Local Inference**: Running object detection locally without sending video validity.
    - **Snapshots**: Storing event snapshots rather than full 24/7 high-res recording for storage efficiency.

## 2. Features Adopted & Architecture Decisions
- **Modular Microservices**: Separated Ingestion (Stream Manager), Inference, and API/UI. This mimics scalable cloud-native architectures.
- **Resilient Ingestion**: Auto-reconnection logic for RTSP streams is critical for real-world reliability, a lesson from dealing with flaky IP cameras.
- **Event-Driven**: The system generates discrete "Events" (alerts) rather than just a continuous stream of data.

## 3. Future Roadmap (Next Steps)
If given 2 more weeks, I would add:
1.  **MQTT Integration**: Publish events to a broker (e.g., Mosquitto) for integration with Home Assistant or other IoT systems (Frigate style).
2.  **Object Tracking**: Implement DeepSORT or ByteTrack to track unique IDs across frames and reduce duplicate event counting.
3.  **Video Clip Storage**: Save 10-second clips around the event (pre/post buffer) instead of just snapshots.
4.  **Role-Based Access Control (RBAC)**: secure the API and Dashboard.
