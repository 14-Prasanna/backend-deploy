import React, { useState, useEffect } from 'react';

const CameraCard = ({ camera, onDelete }) => {
  const [imgSrc, setImgSrc] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    // Reset error when camera changes
    setError(false);
    setImgSrc(`https://backend-deploy-1-ww52.onrender.com/api/streams/${camera.id}`);
  }, [camera.id]);

  const handleError = () => {
    setError(true);
  };

  return (
    <div className="card flex flex-col gap-2 relative group">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="font-bold">{camera.name}</h3>
          <div className="text-xs text-text-secondary">{camera.site ? `${camera.site} • ` : ''}{camera.location}</div>
        </div>
        <span className={`px-2 py-0.5 rounded text-xs font-medium ${camera.status === 'online' ? 'bg-green-900 text-green-300 border border-green-700' : 'bg-red-900 text-red-300 border border-red-700'}`}>
          {camera.status ? camera.status.toUpperCase() : 'UNKNOWN'}
        </span>
      </div>

      <div className="relativerounded-lg overflow-hidden bg-black aspect-video flex items-center justify-center">
        {!error ? (
          <img
            src={imgSrc}
            alt={camera.name}
            className="w-full h-full object-cover"
            onError={handleError}
          />
        ) : (
          <div className="text-text-secondary flex flex-col items-center">
            <span className="text-2xl">⚠️</span>
            <span>Signal Lost</span>
          </div>
        )}

        {/* Overlay Zone Info or Status */}
        <div className="absolute top-2 left-2 bg-black/50 px-2 py-1 rounded text-xs backdrop-blur-sm">
          FPS: --
        </div>
      </div>

      <div className="flex justify-between text-sm text-text-secondary">
        <span></span>
        <button className="text-danger hover:text-white" onClick={() => onDelete(camera.id)}>Delete</button>
      </div>
    </div>
  );
};

export default CameraCard;
