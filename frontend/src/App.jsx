import React, { useState, useEffect } from 'react';
import CameraCard from './components/CameraCard';
import EventList from './components/EventList';
import ZoneEditor from './components/ZoneEditor';

function App() {
  const [cameras, setCameras] = useState([]);
  const [events, setEvents] = useState([]);
  const [activeTab, setActiveTab] = useState('Overview');
  const [editingCamera, setEditingCamera] = useState(null);

  const API_BASE = 'http://localhost:8000/api';

  const fetchCameras = async () => {
    try {
      const res = await fetch(`${API_BASE}/cameras/`);
      const data = await res.json();
      setCameras(data);
    } catch (err) { console.error(err); }
  };

  const fetchEvents = async () => {
    try {
      const res = await fetch(`${API_BASE}/events/?limit=20`);
      const data = await res.json();
      setEvents(data);
    } catch (err) { console.error(err); }
  };

  useEffect(() => {
    fetchCameras();
    const interval = setInterval(fetchEvents, 2000); // Poll events
    return () => clearInterval(interval);
  }, []);

  const [showAddModal, setShowAddModal] = useState(false);
  const [newCam, setNewCam] = useState({ url: '', name: '', site: '', location: '' });

  const submitAddCamera = async () => {
    if (!newCam.url) return alert("RTSP URL is required");

    try {
      await fetch(`${API_BASE}/cameras/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newCam.name || "Camera " + (cameras.length + 1),
          rtsp_url: newCam.url,
          site: newCam.site || "Default Site",
          location: newCam.location || "Default Location",
          zone_config: '[]'
        })
      });
      setShowAddModal(false);
      setNewCam({ url: '', name: '', site: '', location: '' });
      fetchCameras();
    } catch (e) {
      alert("Failed to add camera");
    }
  };

  // Deprecated prompt-based handler
  const handleAddCamera = async () => {
    setShowAddModal(true);
  };

  const handleSaveZones = async (zoneConfig) => {
    if (!editingCamera) return;
    try {
      await fetch(`${API_BASE}/cameras/${editingCamera.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ zone_config: zoneConfig })
      });
      setEditingCamera(null);
      // Refresh cameras to update local state if needed (though zone_config is mostly used backend)
      fetchCameras();
      alert("Zones saved successfully!");
    } catch (e) {
      alert("Failed to save zones");
    }
  };

  return (
    <div className="flex h-screen w-full bg-[#f3f4f6]">
      {/* Zone Editor Modal */}
      {editingCamera && (
        <ZoneEditor
          camera={editingCamera}
          onSave={handleSaveZones}
          onCancel={() => setEditingCamera(null)}
        />
      )}

      {/* Add Camera Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-96 flex flex-col gap-4">
            <h2 className="text-lg font-bold">Add New Stream</h2>
            <input className="border p-2 rounded" placeholder="RTSP URL (e.g. rtsp://...)" value={newCam.url} onChange={e => setNewCam({ ...newCam, url: e.target.value })} />
            <input className="border p-2 rounded" placeholder="Camera Name" value={newCam.name} onChange={e => setNewCam({ ...newCam, name: e.target.value })} />
            <input className="border p-2 rounded" placeholder="Site (e.g. HQ)" value={newCam.site} onChange={e => setNewCam({ ...newCam, site: e.target.value })} />
            <input className="border p-2 rounded" placeholder="Location (e.g. Lobby)" value={newCam.location} onChange={e => setNewCam({ ...newCam, location: e.target.value })} />
            <div className="flex justify-end gap-2">
              <button className="text-gray-500 px-4 py-2" onClick={() => setShowAddModal(false)}>Cancel</button>
              <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700" onClick={submitAddCamera}>Add Camera</button>
            </div>
          </div>
        </div>
      )}

      {/* Sidebar */}
      <div className="sidebar">
        <h2 className="text-xl font-bold mb-8 px-2">Sentinel<span className="text-blue-600">Sight</span></h2>

        <div className={`nav-item ${activeTab === 'Overview' ? 'active' : ''}`} onClick={() => setActiveTab('Overview')}>
          Overview
        </div>
        <div className={`nav-item ${activeTab === 'Events' ? 'active' : ''}`} onClick={() => setActiveTab('Events')}>
          Realtime Alerts
        </div>
        <div className="nav-item">
          Settings
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-grow flex flex-col h-full overflow-hidden">
        {/* Top Header */}
        <div className="top-bar">
          <input type="text" className="search-bar" placeholder="Search insights..." />
          <button className="btn-primary" onClick={() => setShowAddModal(true)}>+ Add Stream</button>
        </div>

        <div className="p-8 overflow-y-auto flex-grow">
          {activeTab === 'Overview' ? (
            <>
              <h1 className="text-2xl font-bold mb-6">Security Overview</h1>

              {/* Metrics Cards */}
              <div className="metrics-grid">
                <div className="metric-card blue">
                  <div className="card-label">Total Cameras</div>
                  <div className="card-value">{cameras.length}</div>
                </div>
                <div className="metric-card red">
                  <div className="card-label">Total Alerts</div>
                  <div className="card-value">{events.length}</div>
                </div>
                <div className="metric-card green">
                  <div className="card-label">System Status</div>
                  <div className="card-value">Online</div>
                </div>
              </div>

              {/* Live Feeds Section */}
              <h2 className="text-lg font-bold mb-4">Live Camera Feeds</h2>
              <div className="camera-grid">
                {cameras.map(cam => (
                  <div key={cam.id} className="relative group">
                    <CameraCard camera={cam} onDelete={() => { }} />
                    {/* Edit Zones Button overlay */}
                    <button
                      className="absolute top-2 right-2 bg-blue-600 text-white text-xs px-3 py-1 rounded shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={() => setEditingCamera(cam)}
                    >
                      Edit Zones
                    </button>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <>
              <h1 className="text-2xl font-bold mb-6">Realtime Alerts</h1>
              <EventList events={events} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
