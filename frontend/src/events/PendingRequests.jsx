import React, { useState, useEffect } from "react";
import eventService from "../services/eventService";
import MyEventCard from "../events/MyEventCard";

const PendingRequests = () => {
  const [events, setEvents] = useState([]);
  const id = localStorage.getItem("id");

  useEffect(() => {
    const fetchPendingEvents = async () => {
      try {
        const response = await eventService.getPendingEventsByUserId(id);
        console.log(response);
        setEvents(response?.data?.body);
      } catch (error) {
        console.log(error);
      }
    };
    fetchPendingEvents();
  }, [id]);

  return (
    <div>
      <h1 className="events-heading">Pending Requests</h1>
      <div className="events-container">
        {events.map((event, index) => (
          <MyEventCard key={index} event={event} sourcePage="pending-requests"/>
        ))}
      </div>
    </div>
  );
};

export default PendingRequests;
