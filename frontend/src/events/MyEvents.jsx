import React, { useState, useEffect } from "react";
import eventService from "../services/eventService";
import EventCard from "../events/MyEventCard";

const MyEvents = () => {
  const [events, setEvents] = useState([]);
  const id = localStorage.getItem("id");

  // Function to fetch events
  const fetchEvents = async () => {
    try {
      const response = await eventService.getEventByUserId(id);
      setEvents(response?.data?.body || []);
    } catch (error) {
      console.log(error);
    }
  };

  // Use effect to fetch events on component mount and id change
  useEffect(() => {
    fetchEvents();
  }, [id]);

  return (
    <div>
      <h1 className="events-heading">My Events..!</h1>
      <div className="events-container">
        {events.map((event, index) => (
          <EventCard key={index} event={event} refreshEvents={fetchEvents} sourcePage="my-events"/>
        ))}
      </div>
    </div>
  );
};

export default MyEvents;
