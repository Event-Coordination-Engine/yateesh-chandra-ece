import React from "react";
import { Link } from "react-router-dom";
import "./Dashboard.css"; // Ensure you create this CSS file for styles

const Dashboard = () => {
    const userRole = localStorage.getItem("role");

    return (
        <div className="home-page">
            <header className="home-header">
                <h1>Welcome to the Event Management System</h1>
                <p>Your platform for managing events efficiently.</p>
            </header>

            <div className="home-content">
                <section className="quick-actions">
                    <div className="action-buttons">
                        <Link to="/dashboard/my-events" className="action-button">
                            My Events
                        </Link>
                        {userRole === "ADMIN" && (
                            <Link to="/dashboard/pending-requests" className="action-button">
                                Pending Requests
                            </Link>
                        )}
                    </div>
                </section>

                <section className="upcoming-events">
                    <Link to="/dashboard/available-events">
                        <h2>Upcoming Events</h2>
                    </Link>
                </section>
            </div>
        </div>
    );
};

export default Dashboard;
