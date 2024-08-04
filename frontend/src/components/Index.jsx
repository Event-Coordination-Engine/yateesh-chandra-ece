import React, { useState, useEffect } from "react";
import { FaPowerOff } from "react-icons/fa";
import TopBar from "./TopBar";
import { useNavigate } from "react-router-dom";
import eventService from "../services/eventService";
import EventCard from "../events/EventCard";
import SweetAlert from "../sweetalerts/SweetAlert";


function Index() {
  const [isNavOpen, setIsNavOpen] = useState(false);
  const id = localStorage.getItem("id");
  const role = localStorage.getItem("role");
  const phone = localStorage.getItem("phone");
  const email = localStorage.getItem("email");
  
  const [events, setEvents] = useState([]);
  const navigate = useNavigate();

  const toggleNav = () => {
    setIsNavOpen(!isNavOpen);
  };

  const handleSignout = () => {
    SweetAlert.signOutAlert(
        () => {localStorage.clear();
            setTimeout(() => {
                navigate("/");
            }, 1500);
        }
    , "Signing out");
    };

  useEffect(() => {
    getEventByUser();
  }, []);

  const getEventByUser = async () => {
    try {
      await eventService.getEventByUserId(id).then((response) => {
        console.log(response);
        setEvents(response?.data?.body);
      });
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="app">
      <div className={`side-nav ${isNavOpen ? "open" : ""}`}>
        <ul>
          <li><a href="#home">Home</a></li>
          <li><a href="#my-requests">My Events</a></li>
          <li><a href="#pending-requests">Pending Requests</a></li>
          <li><a href="#available-events">Available Events</a></li>
          <li><a href="#registered-events">Registered Events</a></li>
        </ul>
        <div className="sign-out">
          <button onClick={handleSignout}><FaPowerOff /> Sign Out</button>
        </div>
      </div>
      <div className="main-content">
        <header className="app-header">
          <TopBar fun={toggleNav} />
        </header>
        <div className="content">
          <div className="events-container">
            {events.map((event, index) => (
              <EventCard key={index} event={event} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Index;
