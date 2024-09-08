import React, { useState, useEffect } from "react";
import eventService from "../services/eventService";
import AdminEventCard from "./AdminEventCard";

const AdminPendingRequests = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

    const fetchPendingEvents = async () => {
      setLoading(true);
      try {
        setTimeout(async () => {
          const response = await eventService.getPendingEvents();
          setEvents(response?.data?.body || []);
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.log(error);
        setLoading(false);
      }
    };

    useEffect(() => {
      fetchPendingEvents();
    }, []);

  return (
    <div>
      <h1 className="events-heading">Pending Requests</h1>
      <div className="events-container">
        {loading ? (
          <p className="loading-text"><i class="fa fa-refresh fa-spin fa-1x fa-fw"></i>
           Loading</p> 
        ) : events.length === 0 ? (
          <p className="no-items-text"><i class="fas fa-smile-beam"> </i>    Nothing to Approve</p> 
        ) : (
        events.map((event, index) => (
          <AdminEventCard key={index} event={event} refreshEvents={fetchPendingEvents}/>
        )))}
      </div>
    </div>
  );
};

export default AdminPendingRequests;
