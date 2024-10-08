import React, { useState, useEffect } from "react";
import AdminRegistrationCard from "./AdminRegistrationCard";
import registrationService from "../services/registrationService";

const AdminOldRegistrations = () => {
    const [data, setData] = useState([]);
    
    const fetchEvents = async () => {
        try {
            const response = await registrationService.getInactiveEvents();
            setData(response?.data?.body || []);
        } catch (error) {
            console.error(error);
        }
    };
    
    useEffect(() => {
        fetchEvents();
    }, []);
    
    return (
        <div>
            <h1 className="events-heading">Registrations</h1>
            <div>
                <AdminRegistrationCard events={data} />
            </div>
        </div>
    );
};

export default AdminOldRegistrations;