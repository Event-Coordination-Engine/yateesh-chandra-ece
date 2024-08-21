import React, { useState } from "react";

const RegCard = ({ event }) => {
    const [expanded, setExpanded] = useState(false);

    const toggleExpanded = () => {
        setExpanded(!expanded);
    };

    return (
        <div
            className={`event-card ${expanded ? "expanded" : ""}`}
            onClick={toggleExpanded}
        >
            <h3 className="event-title" style={{
                    color: "Green",
                    fontWeight : "bold"
                }}>{event.event_name}</h3>
            <div
                className="event-status"
                style={{
                    color: "blue",
                    fontWeight : "bold"
                }}
            >
                Registered as : {event.attendee_name || 'Pending'} {/* Fallback if status is not provided */}
            </div>
            {expanded && (
                <div className="expanded-content">
                    <p className="event-description">{event.event_description}</p>
                    <div className="event-details">
                        <div className="event-detail">
                            <strong>Date:</strong> {event.date_of_event}
                        </div>
                        <div className="event-detail">
                            <strong>Time:</strong> {event.time_of_event}
                        </div>
                        <div className="event-detail">
                            <strong>Location:</strong> {event.location}
                        </div>
                        <div className="event-detail">
                            <strong>Email:</strong> {event.email}
                        </div>
                        <div className="event-detail">
                            <strong>Registered Date :</strong> {event.registration_date}
                        </div>
                        {event.phone && (
                            <div className="event-detail">
                                <strong>Phone:</strong> {event.phone}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default RegCard;
