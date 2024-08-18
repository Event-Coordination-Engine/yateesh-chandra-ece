import React, { useState } from "react";
import "./EventCard.css";
import eventService from "../services/eventService";
import { useNavigate } from "react-router-dom";
import Swal from "sweetalert2";

const MyEventCard = ({ event, refreshEvents, sourcePage }) => {
    const [expanded, setExpanded] = useState(false);
    const navigate = useNavigate(); 

    const toggleExpanded = () => {
        setExpanded(!expanded);
    };

    const deleteMethod = async (id) => {
        try {
            await eventService.deleteEvent(id);
            Swal.fire({
                title: 'Deleted!',
                text: 'Your event has been deleted.',
                icon: 'success',
                timer: 2000,
                showConfirmButton: false
            });
            // Call the refresh function to update the list of events
            refreshEvents();
        } catch (err) {
            console.error(err);
            Swal.fire('Error!', 'There was an error deleting the event.', 'error');
        }
    };

    const handleDelete = (id) => {
        Swal.fire({
            title: "Delete Event?",
            text: "Once deleted, it is gone for good!",
            icon: 'warning',
            confirmButtonText: "Delete",
            showCancelButton: true,
            cancelButtonText: "Go Back"
        }).then((result) => {
            if (result.isConfirmed) {
                deleteMethod(id);
            }
        });
    };

    const handleEdit = () => {
        navigate(`/dashboard/edit-event/${event.event_id}`, { state: { from: sourcePage } }); // Navigate to the EditEventPage with the event ID
    };

    return (
        <div
            className={`event-card ${expanded ? "expanded" : ""}`}
            onClick={toggleExpanded}
        >
            <h3 className="event-title">{event.event_title}</h3>
            <div
                className="event-status"
                style={{
                    color: event.status === "approved" ? "green" : "red",
                }}
            >
                Status: {event.status}
            </div>
            {expanded && (
                <div className="expanded-content">
                    <p className="event-description">{event.event_description}</p>
                    <div className="event-details">
                        <div className="event-detail">
                            <strong>Date:</strong> {event.date_of_event}
                        </div>
                        <div className="event-detail">
                            <strong>Time:</strong> {event.time_of_event}
                        </div>
                        <div className="event-detail">
                            <strong>Location:</strong> {event.location}
                        </div>
                        <div className="event-detail">
                            <strong>Capacity:</strong> {event.capacity}
                        </div>
                    </div>
                </div>
            )}
            <div className="event-actions">
                <button className="edit-btn" onClick={handleEdit}>Edit</button>
                <button className="delete-btn" onClick={() => handleDelete(event.event_id)}>Delete</button>
            </div>
        </div>
    );
};

export default MyEventCard;
