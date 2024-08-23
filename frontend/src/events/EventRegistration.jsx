import React, { useState, useEffect } from "react";
import eventService from "../services/eventService";
import EventRegCard from "./EventRegCard";
import registrationService from "../services/registrationService";

const EventRegistration = () => {
  const [events, setEvents] = useState([]);
  const id = localStorage.getItem("id");

  const fetchPendingEvents = async () => {
    try {
      const response = await registrationService.availableEvents(id);
      setEvents(response?.data?.body || []);
    } catch (error) {
      console.log(error);
    }
  };

  // Use effect to fetch events on component mount and id change
  useEffect(() => {
    fetchPendingEvents();
  }, [id]);

  return (
    <div>
      <h1 className="events-heading">Available Events</h1>
      <div className="events-container">
        {events.map((event, index) => (
          <EventRegCard key={index} event={event} refreshEvents={fetchPendingEvents} sourcePage="available-events"/>
        ))}
      </div>
    </div>
  );
};

export default EventRegistration;