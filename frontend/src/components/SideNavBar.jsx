import React from "react";
import { Link, useLocation } from "react-router-dom";
import { FaPowerOff } from "react-icons/fa";

const SideNavBar = ({ isNavOpen, handleSignout }) => {
  const location = useLocation();
  const fromPage = location.state?.from;

  return (
    <div className={`side-nav ${isNavOpen ? "open" : ""}`}>
      <ul>
        <Link to="/dashboard">
          <li className={location.pathname === "/dashboard" ? "active" : ""}>
            <span>Home</span>
          </li>
        </Link>
        <Link to="/dashboard/my-events">
          <li className={(location.pathname === "/dashboard/my-events" || fromPage === "my-events") ? "active" : ""}>
            <span>My Events</span>
          </li>
        </Link>
        <Link to="/dashboard/pending-requests">
          <li className={(location.pathname === "/dashboard/pending-requests" || fromPage === "pending-requests") ? "active" : ""}>
            <span>Pending Requests</span>
          </li>
        </Link>
        <Link to="/dashboard/available-events">
          <li className={(location.pathname === "/dashboard/available-events" || fromPage === "available-events") ? "active" : ""}>
            <span>Available Events</span>
          </li>
        </Link>
        <Link to="/dashboard/registered-events">
          <li className={location.pathname === "/dashboard/registered-events" ? "active" : ""}>
            <span>Registered Events</span>
          </li>
        </Link>
      </ul>
      <div className="sign-out">
        <button onClick={handleSignout}><FaPowerOff /> Sign Out</button>
      </div>
    </div>
  );
};

export default SideNavBar;
