import React, { useState, useEffect } from "react";
import EventRegCard from "./EventRegCard";
import registrationService from "../services/registrationService";

const EventRegistration = () => {
  const [events, setEvents] = useState([]);
  const id = localStorage.getItem("id");
  const role = localStorage.getItem("role");

  const availableEvents = async () => {
    try {
      const response = await registrationService.availableEvents(id);
      setEvents(response?.data?.body || []);
    } catch (error) {
      console.log(error);
    }
  };

  const approvedEvents = async () => {
    try {
      const response = await registrationService.approvedEvents();
      setEvents(response?.data?.body || []);
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    if(role === "ADMIN") {
      approvedEvents();
    } else if(role === "USER") {
      availableEvents();
    }
  }, [id]);

  return (
    <div>
      <h1 className="events-heading">Available Events</h1>
      {role == "USER" &&(
      <div className="events-container">
        {events.map((event, index) => (
          <EventRegCard key={index} event={event} refreshEvents={availableEvents} sourcePage="available-events"/>
        ))}
      </div>
      )}
      
      {role == "ADMIN" &&(
      <div className="events-container">
        {events.map((event, index) => (
          <EventRegCard key={index} event={event} refreshEvents={approvedEvents} sourcePage="available-events"/>
        ))}
      </div>
      )}
    </div>
  );
};

export default EventRegistration;