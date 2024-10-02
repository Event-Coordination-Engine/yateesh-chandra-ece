import React from "react";
import { Link, useLocation } from "react-router-dom";
import { FaPowerOff } from "react-icons/fa";

const SideNavBar = ({ isNavOpen, handleSignout, closeNav }) => {
    const location = useLocation();
    const fromPage = location.state?.from;
    const userRole = localStorage.getItem("role");

    const handleLinkClick = () => {
        closeNav();
    };

    return (
        <div className={`side-nav ${isNavOpen ? "open" : ""}`}>
            <ul>
                <Link to="/dashboard" onClick={handleLinkClick}>
                    <li className={location.pathname === "/dashboard" ? "active" : ""}>
                        <span>Home</span>
                    </li>
                </Link>
                <Link to="/dashboard/my-events" onClick={handleLinkClick}>
                    <li className={(location.pathname === "/dashboard/my-events" || fromPage === "my-events") ? "active" : ""}>
                        <span>My Events</span>
                    </li>
                </Link>
                <Link to="/dashboard/pending-requests" onClick={handleLinkClick}>
                    <li className={(location.pathname === "/dashboard/pending-requests" || fromPage === "pending-requests") ? "active" : ""}>
                        <span>Pending Requests</span>
                    </li>
                </Link>
                <Link to="/dashboard/available-events" onClick={handleLinkClick}>
                    <li className={(location.pathname === "/dashboard/available-events" || fromPage === "available-events") ? "active" : ""}>
                        <span>Available Events</span>
                    </li>
                </Link>
                <Link to="/dashboard/registered-events" onClick={handleLinkClick}>
                    <li className={location.pathname === "/dashboard/registered-events" ? "active" : ""}>
                        <span>Registered Events</span>
                    </li>
                </Link>

                {userRole === "ADMIN" && (
                <Link to="/dashboard/all-attendees" onClick={handleLinkClick}>
                    <li className={location.pathname === "/dashboard/all-attendees" ? "active" : ""}>
                        <span>Old Registrations</span>
                    </li>
                </Link>
                )}
            </ul>
            <div className="sign-out">
                <button onClick={handleSignout}><FaPowerOff /> Sign Out</button>
            </div>
        </div>
    );
};

export default SideNavBar;
