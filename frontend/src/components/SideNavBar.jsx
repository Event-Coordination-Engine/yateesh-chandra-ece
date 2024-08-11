import React from "react";
import { Link, useLocation } from "react-router-dom";
import { FaPowerOff } from "react-icons/fa";

const SideNavBar = ({ isNavOpen, handleSignout }) => {
  const location = useLocation();
  const fromPage = location.state?.from;

  return (
    <div className={`side-nav ${isNavOpen ? "open" : ""}`}>
      <ul>
        <li className={location.pathname === "/dashboard" ? "active" : ""}>
          <Link to="/dashboard">Home</Link>
        </li>
        <li className={(location.pathname === "/dashboard/my-events" || fromPage === "my-events") ? "active" : ""}>
          <Link to="/dashboard/my-events">My Events</Link>
        </li>
        <li className={(location.pathname === "/dashboard/pending-requests" || fromPage === "pending-requests") ? "active" : ""}>
          <Link to="/dashboard/pending-requests">Pending Requests</Link>
        </li>
        <li className={location.pathname === "/dashboard/available-events" ? "active" : ""}>
          <Link to="/dashboard/available-events">Available Events</Link>
        </li>
        <li className={location.pathname === "/dashboard/registered-events" ? "active" : ""}>
          <Link to="/dashboard/registered-events">Registered Events</Link>
        </li>
      </ul>
      <div className="sign-out">
        <button onClick={handleSignout}><FaPowerOff /> Sign Out</button>
      </div>
    </div>
  );
};

export default SideNavBar;
