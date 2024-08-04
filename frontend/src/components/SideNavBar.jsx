import React from "react";
import { FaPowerOff } from "react-icons/fa";

const SideNavBar = ({ isNavOpen, activeLink, setActiveLink, handleSignout }) => {
  return (
    <div className={`side-nav ${isNavOpen ? "open" : ""}`}>
      <ul>
        <li className={activeLink === "home" ? "active" : ""}>
          <a href="#home" onClick={() => setActiveLink("home")}>Home</a>
        </li>
        <li className={activeLink === "my-events" ? "active" : ""}>
          <a href="#my-requests" onClick={() => setActiveLink("my-events")}>My Events</a>
        </li>
        <li className={activeLink === "pending-requests" ? "active" : ""}>
          <a href="#pending-requests" onClick={() => setActiveLink("pending-requests")}>Pending Requests</a>
        </li>
        <li className={activeLink === "available-events" ? "active" : ""}>
          <a href="#available-events" onClick={() => setActiveLink("available-events")}>Available Events</a>
        </li>
        <li className={activeLink === "registered-events" ? "active" : ""}>
          <a href="#registered-events" onClick={() => setActiveLink("registered-events")}>Registered Events</a>
        </li>
      </ul>
      <div className="sign-out">
        <button onClick={handleSignout}><FaPowerOff /> Sign Out</button>
      </div>
    </div>
  );
};

export default SideNavBar;
