import React, { useState, useEffect } from "react";
import eventService from "../services/eventService";
import MyEventCard from "../events/MyEventCard";

const PendingRequests = () => {
  const [events, setEvents] = useState([]);
  const id = localStorage.getItem("id");

  const fetchPendingEvents = async () => {
    try {
      const response = await eventService.getPendingEventsByUserId(id);
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
      <h1 className="events-heading">Pending Requests</h1>
      <div className="events-container">
        {events.map((event, index) => (
          <MyEventCard key={index} event={event} refreshEvents={fetchPendingEvents} sourcePage="pending-requests"/>
        ))}
      </div>
    </div>
  );
};

export default PendingRequests;