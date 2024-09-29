import React, { useState, useEffect } from "react";
import eventService from "../services/eventService";
import AdminEventCard from "./AdminEventCard";
import Swal from "sweetalert2";

const AdminPendingRequests = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");

    const fetchPendingEvents = async () => {
        setLoading(true);
        try {
            setTimeout(async () => {
                const response = await eventService.getPendingEvents();
                setEvents(response?.data?.body || []);
                setLoading(false);
            }, 1000);
        } catch (error) {
            console.error(error);
            setLoading(false);
        }
    };

    const approveAll = () => {
        Swal.fire({
            title: "Approve All Events?",
            text: "This will approve all pending events.",
            icon: "warning",
            confirmButtonText: "Approve All",
            showCancelButton: true,
            cancelButtonText: "Cancel",
        }).then(async (result) => {
            if (result.isConfirmed) {
                await eventService.approve_all();
                Swal.fire({
                    title: "Approved!",
                    text: "All events have been approved.",
                    icon: "success",
                    timer: 2000,
                    showConfirmButton: false,
                });
                fetchPendingEvents();
            }
        });
    };

    useEffect(() => {
        fetchPendingEvents();
    }, []);

    const filteredEvents = events.filter((event) =>
        event.event_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.location.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div>
            <h1 className="events-heading">Pending Requests</h1>
            <div className="admin-header">
                <button className="approve-all-btn" onClick={approveAll}>Approve All</button>
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
                        <i className="fas fa-smile-beam"></i> No Pending events
                    </p>
                ) : (
                    filteredEvents.map((event, index) => (
                        <AdminEventCard key={index} event={event} refreshEvents={fetchPendingEvents} />
                    ))
                )}
            </div>
        </div>
    );
};

export default AdminPendingRequests;
