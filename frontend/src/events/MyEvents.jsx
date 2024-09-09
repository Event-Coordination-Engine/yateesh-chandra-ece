import React, { useState, useEffect } from "react";
import eventService from "../services/eventService";
import EventCard from "../events/MyEventCard";

const MyEvents = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const id = localStorage.getItem("id");

  // Function to fetch events
  const fetchEvents = async () => {
    setLoading(true);
    try {
      setTimeout(async () => {
        const response = await eventService.getEventByUserId(id);
        setEvents(response?.data?.body || []);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.log(error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [id]);

  return (
    <div>
      <h1 className="events-heading">My Events..!</h1>
      <div className="events-container">
      {loading ? (
          <p className="loading-text"><i class="fa fa-refresh fa-spin fa-1x fa-fw"></i>
           Loading</p> 
        ) : events.length === 0 ? (
          <p className="no-items-text"><i class="fas fa-atom"></i> No Events</p> 
        ) : (
        events.map((event, index) => (
          <EventCard key={index} event={event} refreshEvents={fetchEvents} sourcePage="my-events"/>
        ))
      )}
      </div>
    </div>
  );
};

export default MyEvents;
