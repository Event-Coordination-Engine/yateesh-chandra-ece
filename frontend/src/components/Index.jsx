import React, { useState } from "react";
import { FaPowerOff } from "react-icons/fa";
import TopBar from "./TopBar";

function Index() {
  const [isNavOpen, setIsNavOpen] = useState(false);

  const toggleNav = () => {
    setIsNavOpen(!isNavOpen);
  };

  return (
    <div className="app">
      <div className={`side-nav ${isNavOpen ? "open" : ""}`}>
        <ul>
          <li><a href="#home">Home</a></li>
          <li><a href="#my-requests">My Requests</a></li>
          <li><a href="#pending-requests">Pending Requests</a></li>
          <li><a href="#available-events">Available Events</a></li>
          <li><a href="#registered-events">Registered Events</a></li>
        </ul>
        <div className="sign-out">
          <button><FaPowerOff/> Sign Out</button>
        </div>
      </div>
      <div className="main-content">
        <header className="app-header">
          <TopBar fun={toggleNav} />
        </header>
        <div className="content"></div>
      </div>
    </div>
  );
}

export default Index;
