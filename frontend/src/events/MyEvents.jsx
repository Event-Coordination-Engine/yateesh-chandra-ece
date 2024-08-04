import React, { useState, useEffect } from "react";
import eventService from "../services/eventService";
import EventCard from "../events/MyEventCard";

const MyEvents = () => {
  const [events, setEvents] = useState([]);
  const id = localStorage.getItem("id");

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await eventService.getEventByUserId(id);
        console.log(response);
        setEvents(response?.data?.body);
      } catch (error) {
        console.log(error);
      }
    };
    fetchEvents();
  }, [id]);

  return (
    <div>
      <h1 className="events-heading">My Events..!</h1>
      <div className="events-container">
        {events.map((event, index) => (
          <EventCard key={index} event={event} />
        ))}
      </div>
    </div>
  );
};

export default MyEvents;
