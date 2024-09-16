import React, { useState } from "react";
import "./RequestEventPage.css";
import Swal from "sweetalert2";
import registrationService from "../services/registrationService";
import { useNavigate, useParams } from "react-router-dom";

const UserRegistration = () => {
    const { eventId } = useParams();
    const id = localStorage.getItem("id");
    const navigate = useNavigate()
    const [formData, setFormData] = useState({
        attendee_name: "",
        email : "",
        user_id : id,
        phone : "",
        event_id : eventId
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const navigateBack = () =>{
        navigate("/dashboard/available-events");
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            await registrationService.registerEvent(formData);
            console.log("Registered for the event");
            
            Swal.fire({
                title: "Registered for the event",
                icon: "success",
                timer: 1500,
                showConfirmButton: false,
            }).then(navigateBack);
        } catch (err) {
            if (err.response.data.detail == "Cannot register since max Capacity reached"){
                Swal.fire({
                    title: "Maximum registrations Reached",
                    text: "But We are working on the routes to get you into our event",
                    icon: "warning",
                });
            }
            else{
            Swal.fire({
                title: "Unable to register for event",
                text: err.response.data.detail,
                icon: "error",
            });
            console.log(err);}
        }
        
        console.log("Registration Form submitted:", formData);
    };
    
    return (
        <div className="request-event-page">
        <h1 className="page-heading">Register for event</h1>
        <form className="request-form" onSubmit={handleSubmit}>
            <div className="form-group">
            <label htmlFor="attendee_name">Attendee Name *</label>
            <input
                type="text"
                id="attendee_name"
                name="attendee_name"
                value={formData.attendee_name}
                onChange={handleChange}
                required
            />
            </div>
            <div className="form-group">
            <label htmlFor="email">Email Address *</label>
            <input
                type="text"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
            />
            </div>
            <div className="form-group">
            <label htmlFor="phone">Mobile Number</label>
            <input
                type="number"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
            />
            </div>
            <div className="event-actions">
                <button type="submit" className="edit-btn">Enroll</button>
                <button className="delete-btn" onClick={navigateBack}>Cancel</button>
            </div>
        </form>
        </div>
    );
};

export default UserRegistration;