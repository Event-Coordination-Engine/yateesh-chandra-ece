import React, { useState, useEffect } from "react";
import AdminRegistrationCard from "./AdminRegistrationCard";
import registrationService from "../services/registrationService";

const AdminRegistrations = () => {
    const [data, setData] = useState([]);

    const fetchEvents = async () => {
        try {
            const response = await registrationService.getAllRegistrations();
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

export default AdminRegistrations;