import React, { useState, useEffect } from "react";
import registrationService from "../services/registrationService";
import RegCard from "./RegCard";

const RegisteredEvents = () => {
  const [events, setEvents] = useState([]);
  const id = localStorage.getItem("id");

  const fetchRegisteredEvents = async () => {
    try {
      const response = await registrationService.getRegisteredEventsByUser(id);
      console.log(response)
      setEvents(response?.data?.body || []);
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    fetchRegisteredEvents();
  }, [id]);

  return (
    <div>
      <h1 className="events-heading">My Events..!</h1>
      <div className="events-container">
        {events.map((event, index) => (
          <RegCard key={index} event={event} />
        ))}
      </div>
    </div>
  );
};

export default RegisteredEvents;
