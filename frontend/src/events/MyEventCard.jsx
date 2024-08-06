// MyEventCard.jsx
import React, { useState } from "react";
import "./EventCard.css";

const EventCard = ({ event }) => {

  
  return (

    <div className="event-card">
      <h3 className="event-title">{event.event_title}</h3>
      <p className="event-description">{event.event_description}</p>
      <div className="event-details">
        <span className="event-date">{event.date_of_event}</span>
        <span className="event-time">{event.time_of_event}</span>
      </div>
      <div className="event-location">Location: {event.location}</div>
      <div className="event-capacity">Capacity: {event.capacity}</div>
    </div>
  );
};

export default EventCard;
