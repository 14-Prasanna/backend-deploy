import React, { useState, useEffect, useRef } from 'react';

const ZoneEditor = ({ camera, onSave, onCancel }) => {
    const [points, setPoints] = useState([]);
    const [zones, setZones] = useState([]);
    const canvasRef = useRef(null);
    const [image, setImage] = useState(null);

    useEffect(() => {
        // Load current zones
        try {
            if (camera.zone_config) {
                setZones(JSON.parse(camera.zone_config));
            }
        } catch (e) { }

        // Grab a snapshot for background
        const img = new Image();
        img.src = `https://backend-deploy-1-ww52.onrender.com/api/streams/${camera.id}`; // Use live frame as snapshot
        img.crossOrigin = "Anonymous";
        img.onload = () => setImage(img);
    }, [camera]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas || !image) return;

        const ctx = canvas.getContext('2d');
        canvas.width = 640; // Fixed width for consistency
        canvas.height = 480;

        // Draw background
        ctx.drawImage(image, 0, 0, canvas.width, canvas.height);

        // Draw existing zones
        zones.forEach((zone, idx) => {
            drawPolygon(ctx, zone.points, 'rgba(0, 255, 0, 0.3)', 'rgba(0, 255, 0, 0.8)');
            // Label
            if (zone.points.length > 0) {
                ctx.fillStyle = 'white';
                ctx.font = "16px Arial";
                ctx.fillText(zone.name || `Zone ${idx + 1}`, zone.points[0][0], zone.points[0][1]);
            }
        });

        // Draw current drawing
        if (points.length > 0) {
            drawPolygon(ctx, points, 'rgba(37, 99, 235, 0.3)', '#2563eb');
        }
    }, [image, points, zones]);

    const drawPolygon = (ctx, pts, fillColor, strokeColor) => {
        if (pts.length < 2) return;
        ctx.beginPath();
        ctx.moveTo(pts[0][0], pts[0][1]);
        for (let i = 1; i < pts.length; i++) {
            ctx.lineTo(pts[i][0], pts[i][1]);
        }
        ctx.closePath();
        ctx.fillStyle = fillColor;
        ctx.fill();
        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = 2;
        ctx.stroke();

        // Draw vertices
        try {
            pts.forEach(p => {
                ctx.beginPath();
                ctx.arc(p[0], p[1], 4, 0, Math.PI * 2);
                ctx.fillStyle = 'white';
                ctx.fill();
            });
        } catch (e) { }
    };

    const handleClick = (e) => {
        const rect = canvasRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Scale coordinates to canvas resolution (640x480)
        const scaleX = 640 / rect.width;
        const scaleY = 480 / rect.height;

        setPoints([...points, [x * scaleX, y * scaleY]]);
    };

    const [triggers, setTriggers] = useState({ intrusion: true, loitering: false });

    // ... existing canvas setup ...

    const handleSaveZone = () => {
        if (points.length < 3) return alert("Need at least 3 points");
        const name = prompt("Enter Zone Name (e.g., 'Restricted Area')", "Zone " + (zones.length + 1));
        if (!name) return;

        const activeTriggers = [];
        if (triggers.intrusion) activeTriggers.push('intrusion');
        if (triggers.loitering) activeTriggers.push('loitering');

        if (activeTriggers.length === 0) return alert("Select at least one rule (Intrusion or Loitering)");

        const newZone = {
            name: name,
            points: points,
            triggers: activeTriggers
        };

        const updatedZones = [...zones, newZone];
        setZones(updatedZones);
        setPoints([]);
    };

    const handleClear = () => {
        setPoints([]);
        setZones([]);
    };

    const handleFinish = () => {
        if (confirm("Save these zones?")) {
            onSave(JSON.stringify(zones));
        }
    };

    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
            <div className="bg-white p-4 rounded-lg flex flex-col gap-4 max-w-4xl w-full">
                <h2 className="text-xl font-bold text-gray-800">Edit Zones: {camera.name}</h2>
                <div className="relative bg-black aspect-[4/3] rounded overflow-hidden cursor-crosshair">
                    {!image && <div className="absolute inset-0 flex items-center justify-center text-white">Loading snapshot...</div>}
                    <canvas
                        ref={canvasRef}
                        className="w-full h-full object-contain"
                        onClick={handleClick}
                    />
                </div>
                <div className="flex justify-between items-center text-gray-800">
                    <div className="text-sm">
                        Click to add points. <br />
                        Points: {points.length}
                    </div>
                    <div className="flex gap-4 items-center">
                        <label className="flex items-center gap-1">
                            <input type="checkbox" checked={triggers.intrusion} onChange={e => setTriggers({ ...triggers, intrusion: e.target.checked })} />
                            Intrusion
                        </label>
                        <label className="flex items-center gap-1">
                            <input type="checkbox" checked={triggers.loitering} onChange={e => setTriggers({ ...triggers, loitering: e.target.checked })} />
                            Loitering
                        </label>
                    </div>
                    <div className="flex gap-2">
                        <button className="btn-primary bg-gray-500" onClick={onCancel}>Cancel</button>
                        <button className="btn-primary bg-red-500" onClick={handleClear}>Clear All</button>
                        <button className="btn-primary" onClick={handleSaveZone}>Add Zone</button>
                        <button className="btn-primary bg-green-600" onClick={handleFinish}>Save & Exit</button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ZoneEditor;
