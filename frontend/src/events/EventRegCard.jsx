import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const EventRegCard = ({ event, sourcePage }) => {
    const [expanded, setExpanded] = useState(false);
    const navigate = useNavigate(); 

    const toggleExpanded = () => {
        setExpanded(!expanded);
    };

    const handlePost = () => {
        navigate(`/dashboard/register-event/${event.event_id}`, { state: { from: sourcePage } });
    };

    return (
        <div
            className={`event-card ${expanded ? "expanded" : ""}`}
            onClick={toggleExpanded}
        >
            <h3 style={{
                    color: "green"
                }} className="event-title">{event.event_title}</h3>
            <div className="event-details">
                <div className="event-detail">
                    <strong>Date:</strong> {event.date_of_event}
                </div>
                <div className="event-detail">
                    <strong>Time:</strong> {event.time_of_event}
                </div>
            </div>
            {expanded && (
                <div className="expanded-content">
                    <div className="event-details">
                        <div className="event-detail">
                            <strong>Location:</strong> {event.location}
                        </div>
                        <div className="event-detail">
                            <strong>Capacity:</strong> {event.capacity}
                        </div>
                    </div>
                    <p className="event-description"><b>Description :</b> {event.event_description}</p>
                </div>
            )}
            <div className="button-action">
                <button className="edit-btn" onClick={handlePost}>Register</button>
            </div>
        </div>
    );
};

export default EventRegCard;
