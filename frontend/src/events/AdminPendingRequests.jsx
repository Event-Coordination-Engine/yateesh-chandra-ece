import React, { useState, useEffect } from "react";
import eventService from "../services/eventService";
import AdminEventCard from "./AdminEventCard";

const AdminPendingRequests = () => {
  const [events, setEvents] = useState([]);
  // const id = localStorage.getItem("id");

    const fetchPendingEvents = async () => {
      try {
          const response = await eventService.getPendingEvents();
          setEvents(response?.data?.body || []);
      } catch (error) {
        console.log(error);
      }
    };

    useEffect(() => {
      fetchPendingEvents();
    }, []);

  return (
    <div>
      <h1 className="events-heading">Pending Requests</h1>
      <div className="events-container">
        {events.map((event, index) => (
          <AdminEventCard key={index} event={event} refreshEvents={fetchPendingEvents}/>
        ))}
      </div>
    </div>
  );
};

export default AdminPendingRequests;
