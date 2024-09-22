import React, { useState, useEffect } from "react";
import eventService from "../services/eventService";
import EventCard from "../events/MyEventCard";
import { useNavigate } from "react-router-dom";

const MyEvents = () => {
  const [events, setEvents] = useState([]);
  const nav = useNavigate()
  const [loading, setLoading] = useState(true);
  const id = localStorage.getItem("id");
  const [searchTerm, setSearchTerm] = useState(""); // Add state for search term

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

  const filteredEvents = events.filter((event) =>
    event.event_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    event.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

    const navtoadd = () => {
      nav(`/dashboard/add-event`, { state: { from: "my-events" } }); // Navigate with state
  };


  return (
    <div>
      <h1 className="events-heading">My Events..!</h1>
      <div className="admin-header">
        <button className="approve-all-btn" onClick={navtoadd}>Add Event</button>
        <input
          className="search-input"
          type="text"
          placeholder="Search events..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)} // Update search term on input change
        />
      </div>
      <div className="events-container">
      {loading ? (
          <p className="loading-text"><i class="fa fa-refresh fa-spin fa-1x fa-fw"></i>
           Loading</p> 
        ) : filteredEvents.length === 0 ? (
          <p className="no-items-text"><i class="fas fa-atom"></i> No Events</p> 
        ) : (
        filteredEvents.map((event, index) => (
          <EventCard key={index} event={event} refreshEvents={fetchEvents} sourcePage="my-events"/>
        ))
      )}
      </div>
    </div>
  );
};

export default MyEvents;
