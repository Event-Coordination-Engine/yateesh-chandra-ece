import React, { useState, useEffect } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom"; // Import hooks
import eventService from "../services/eventService";
import Swal from "sweetalert2";

const EditEventPage = () => {
    const { eventId } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const organizerId = localStorage.getItem("id");
    
    // Retrieve the source page from location state
    const { state } = location;
    console.log(state)
    const sourcePage = state?.from || "/"; // Default to "/" if no sourcePage is provided
    console.log(sourcePage)

    const [formData, setFormData] = useState({
        event_title: "",
        date_of_event: "",
        time_of_event: "",
        location: "",
        event_description: "",
        capacity: "",
        organizer_id: organizerId,
    });

    useEffect(() => {
        const fetchEvent = async () => {
            try {
                const response = await eventService.getEventById(eventId);
                const event = response.data.body;
                setFormData({
                    event_title: event.event_title,
                    date_of_event: convertDateFormat(event.date_of_event),
                    time_of_event: event.time_of_event,
                    location: event.location,
                    event_description: event.event_description,
                    capacity: event.capacity,
                    organizer_id: organizerId,
                });
            } catch (err) {
                console.log(err);
            }
        };
        fetchEvent();
    }, [eventId]);

    function convertDateFormat(dateStr) {
        const [year, month, day] = dateStr.split('-');
        return `${day}-${month}-${year}`;
    }

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const redirect = () => {
        navigate(`/dashboard/${sourcePage}`);
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            formData.date_of_event = convertDateFormat(formData.date_of_event);
            await eventService.updateEvent(eventId, formData);
            Swal.fire({
                title: "Event Updated",
                timer: 1400,
                showConfirmButton: false,
                icon: "success"
            }).then(() => {
                // Redirect back to the source page
                navigate(`/dashboard/${sourcePage}`);
            });
        } catch (err) {
            console.log(err);
            Swal.fire({
                title: err.response.data.body,
                timer: 1500,
                showConfirmButton: false,
                icon: "error"
            })
        }
        console.log("Form submitted:", formData);
    };

    return (
        <div className="request-event-page">
            <h1 className="page-heading">Edit Event</h1>
            <form className="request-form" onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="event_title">Event Name</label>
                    <input
                        type="text"
                        id="event_title"
                        name="event_title"
                        value={formData.event_title}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="date_of_event">Event Date</label>
                    <input
                        type="date"
                        id="date_of_event"
                        name="date_of_event"
                        value={formData.date_of_event}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="time_of_event">Event Time</label>
                    <input
                        type="time"
                        id="time_of_event"
                        name="time_of_event"
                        value={formData.time_of_event}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="location">Location</label>
                    <input
                        type="text"
                        id="location"
                        name="location"
                        value={formData.location}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="capacity">Capacity</label>
                    <input
                        type="text"
                        id="capacity"
                        name="capacity"
                        value={formData.capacity}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="event_description">Event Description</label>
                    <textarea
                        id="event_description"
                        name="event_description"
                        value={formData.event_description}
                        onChange={handleChange}
                        rows="4"
                        required
                    ></textarea>
                </div>
                <div className="button-group">
                    <button type="submit" className="login-submit-button">Update</button>
                    <button type="button" className="home-button" onClick={redirect}>Cancel</button>
                </div>
                
            </form>
        </div>
    );
};

export default EditEventPage;
