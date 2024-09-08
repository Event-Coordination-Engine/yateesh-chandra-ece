import React, { useState, useEffect } from "react";
import EventRegCard from "./EventRegCard";
import registrationService from "../services/registrationService";

const EventRegistration = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const id = localStorage.getItem("id");
  const role = localStorage.getItem("role");

  const availableEvents = async () => {
    setLoading(true);
    try {
        setTimeout(async () => {
          const response = await registrationService.availableEvents(id);
          setEvents(response?.data?.body || []);
          setLoading(false);
        },1000);
    } catch (error) {
      console.log(error);
      setLoading(false);
    }
  };

  const approvedEvents = async () => {
    setLoading(true);
    try {
      setTimeout(async () => {
        const response = await registrationService.approvedEvents();
        setEvents(response?.data?.body || []);
        setLoading(false);
    }, 1000)
    } catch (error) {
      console.log(error);
      setLoading(false);
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
        {loading ? (
          <p className="loading-text"><i class="fa fa-refresh fa-spin fa-1x fa-fw"></i>
           Loading</p> 
        ) : events.length === 0 ? (
          <p className="no-items-text"><i class="fas fa-frown"></i>  No Active Events</p> 
        ) : (
        events.map((event, index) => (
          <EventRegCard key={index} event={event} refreshEvents={availableEvents} sourcePage="available-events"/>
        )))}
      </div>
      )}
      
      {role == "ADMIN" &&(
      <div className="events-container">
        {loading ? (
          <p className="loading-text"><i class="fa fa-refresh fa-spin fa-1x fa-fw"></i>
           Loading</p> 
        ) : events.length === 0 ? (
          <p className="no-items-text"><i class="fas fa-frown"></i>  No Active Events</p> 
        ) : (
        events.map((event, index) => (
          <EventRegCard key={index} event={event} refreshEvents={approvedEvents} sourcePage="available-events"/>
        )))}
      </div>
      )}
    </div>
  );
};

export default EventRegistration;