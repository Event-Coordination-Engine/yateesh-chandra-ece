import React, { useState, useEffect } from "react";
import eventService from "../services/eventService";
import MyEventCard from "../events/MyEventCard";
import 'font-awesome/css/font-awesome.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

const PendingRequests = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const id = localStorage.getItem("id");

    const fetchPendingEvents = async () => {
        setLoading(true);
        try {
            setTimeout(async () => {
                const response = await eventService.getPendingEventsByUserId(id);
                setEvents(response?.data?.body || []);
                setLoading(false);
            }, 1000);
        } catch (error) {
            console.error(error);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPendingEvents();
    }, [id]);

    return (
        <div>
            <h1 className="events-heading">Pending Requests</h1>
            <div className="events-container">
                 {loading ? (
                    <p className="loading-text"><i class="fa fa-refresh fa-spin fa-1x fa-fw"></i>
                     Loading</p> 
                ) : events.length === 0 ? (
                    <p className="no-items-text"><i class="fas fa-smile-beam"> </i> All Items Approved</p> 
                ) : (
                    events.map((event, index) => (
                        <MyEventCard
                            key={index}
                            event={event}
                            refreshEvents={fetchPendingEvents}
                            sourcePage="pending-requests"
                        />
                    ))
                )}
            </div>
        </div>
    );
};

export default PendingRequests;