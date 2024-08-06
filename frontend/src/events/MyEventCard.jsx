import React, { useState } from "react";
import "./EventCard.css";

const MyEventCard = ({ event }) => {
  const [expanded, setExpanded] = useState(false);

  const toggleExpanded = () => {
    setExpanded(!expanded);
  };

  return (
    <div
      className={`event-card ${expanded ? "expanded" : ""}`}
      onClick={toggleExpanded}
    >
      <h3 className="event-title">{event.event_title}</h3>
      <div
        className="event-status"
        style={{
          color: event.status === "approved" ? "green" : "red",
        }}
      >
        Status: {event.status}
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
              <strong>Capacity:</strong> {event.capacity}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyEventCard;
