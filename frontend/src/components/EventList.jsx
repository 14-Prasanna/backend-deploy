import React from 'react';

const EventList = ({ events }) => {
    return (
        <div className="flex flex-col gap-2 h-full overflow-y-auto">
            {events.length === 0 ? (
                <div className="text-center text-text-secondary p-4">No events detected</div>
            ) : (
                events.map((event) => (
                    <div key={event.id} className="card flex gap-4 hover:bg-bg-tertiary transition-colors cursor-pointer">
                        <div className="w-24 h-16 bg-black rounded overflow-hidden flex-shrink-0">
                            <img
                                src={`https://backend-deploy-1-ww52.onrender.com/${event.snapshot_path}`}
                                alt="Event Snapshot"
                                className="w-full h-full object-cover"
                            />
                        </div>
                        <div className="flex flex-col justify-center flex-grow">
                            <div className="flex justify-between items-center">
                                <span className="font-bold text-danger">{event.rule_name}</span>
                                <span className="text-xs text-text-secondary">
                                    {new Date(event.timestamp).toLocaleTimeString()}
                                </span>
                            </div>
                            <span className="text-sm text-text-secondary">
                                {event.object_type} detected ({(event.confidence * 100).toFixed(0)}%)
                            </span>
                            <span className="text-xs text-accent">Cam #{event.camera_id}</span>
                        </div>
                    </div>
                ))
            )}
        </div>
    );
};

export default EventList;
