import React, { useState } from "react";
import "./RequestEventPage.css";
import eventService from "../services/eventService";
import Swal from "sweetalert2";

const RequestEventPage = () => {
    const id = localStorage.getItem("id");
    const [formData, setFormData] = useState({
        event_title: "",
        date_of_event: "",
        time_of_event: "",
        location: "",
        event_description: "",
        capacity : "",
        organizer_id : id,
    });

    function convertDateFormat(dateStr) {
        const [year, month, day] = dateStr.split('-');
        return `${day}-${month}-${year}`;
    }

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            // Create a new object with the updated date format
            const updatedFormData = {
                ...formData,
                date_of_event: convertDateFormat(formData.date_of_event),
            };
    
            // Call the API with the updated form data
            await eventService.createEvent(updatedFormData);
            
            console.log("Event Added");
            
            Swal.fire({
                title: "Event Added",
                icon: "success",
                timer: 1500,
                showConfirmButton: false,
            });
        } catch (err) {
            Swal.fire({
                title: "Unable to add event",
                text: err.response.data.detail,
                icon: "error",
            });
            console.log(err);
        }
        
        console.log("Form submitted:", formData);
    };
    
    return (
        <div className="request-event-page">
        <h1 className="page-heading">Event Form</h1>
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
                type="number"
                id="capacity"
                name="capacity"
                value={formData.capacity}
                onChange={handleChange}
                required
            />
            </div>
            <div className="form-group">
            <label htmlFor="event_description">Event description</label>
            <textarea
                id="event_description"
                name="event_description"
                value={formData.event_description}
                onChange={handleChange}
                rows="4"
                required
            ></textarea>
            </div>
            <button type="submit" className="submit-btn">Submit Request</button>
        </form>
        </div>
    );
};

export default RequestEventPage;