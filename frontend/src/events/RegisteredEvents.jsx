import React, { useState, useEffect } from "react";
import registrationService from "../services/registrationService";
import RegCard from "./RegCard";

const RegisteredEvents = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const id = localStorage.getItem("id");

    const fetchRegisteredEvents = async () => {
        setLoading(true);
        try {
            setTimeout(async () => {
                const response = await registrationService.getRegisteredEventsByUser(id);
                setEvents(response?.data?.body || []);
                setLoading(false);
            }, 1000);
        } catch (error) {
            console.error(error);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRegisteredEvents();
    }, [id]);

    return (
        <div>
            <h1 className="events-heading">My Registered Events..!</h1>
            <div className="events-container">
            {loading ? (
                    <p className="loading-text"><i class="fa fa-refresh fa-spin fa-1x fa-fw"></i>
                     Loading</p> 
                ) : events.length === 0 ? (
                    <p className="no-items-text"><i class="fas fa-frown"></i> No Active Events</p> 
                ) : (
                events.map((event, index) => (
                    <RegCard key={index} event={event} />
                )))}
            </div>
        </div>
    );
};

export default RegisteredEvents;
