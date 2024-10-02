import React, { useState, useEffect } from "react";
import eventService from "../services/eventService";
import EventCard from "../events/MyEventCard";
import { useNavigate } from "react-router-dom";
import { FaInfoCircle } from "react-icons/fa";

const MyEvents = () => {
    const [events, setEvents] = useState([]);
    const nav = useNavigate();
    const [loading, setLoading] = useState(true);
    const id = localStorage.getItem("id");
    const [searchTerm, setSearchTerm] = useState("");
    const [showTooltip, setShowTooltip] = useState(false);

    const fetchEvents = async () => {
        setLoading(true);
        try {
            setTimeout(async () => {
                const response = await eventService.getEventByUserId(id);
                setEvents(response?.data?.body || []);
                setLoading(false);
            }, 1000);
        } catch (error) {
            console.error(error);
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
        nav(`/dashboard/add-event`, { state: { from: "my-events" } });
    };

    return (
        <div>
            <h1 className="events-heading">My Events..!</h1>
            <div className="admin-header">
                <button className="approve-all-btn" onClick={navtoadd}>
                    Add Event <span
                    className="info-icon"
                    onMouseEnter={() => setShowTooltip(true)}
                    onMouseLeave={() => setShowTooltip(false)}
                >
                    <FaInfoCircle />
                    {showTooltip && (
                        <div className="tooltip">Once Event is created, it needs admin approval</div>
                    )}
                </span>
                </button>
                <input
                    className="search-input"
                    type="text"
                    placeholder="Search events..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </div>
            <div className="events-container">
                {loading ? (
                    <p className="loading-text">
                        <i className="fa fa-refresh fa-spin fa-1x fa-fw"></i> Loading
                    </p>
                ) : filteredEvents.length === 0 ? (
                    <p className="no-items-text">
                        <i className="fas fa-atom"></i> No Events
                    </p>
                ) : (
                    filteredEvents.map((event, index) => (
                        <EventCard key={index} event={event} refreshEvents={fetchEvents} sourcePage="my-events" />
                    ))
                )}
            </div>
        </div>
    );
};

export default MyEvents;
