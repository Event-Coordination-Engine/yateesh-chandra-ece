import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "./TopBar";
import SideNavBar from "../components/SideNavBar";
import SweetAlert from "../sweetalerts/SweetAlert";
import MyEvents from "../events/MyEvents";
import PendingRequests from "../events/PendingRequests";
import RequestEventPage from "../events/RequestEventPage";

function Index() {
  const [isNavOpen, setIsNavOpen] = useState(false);
  const [activeLink, setActiveLink] = useState("home");

  const navigate = useNavigate();

  const toggleNav = () => {
    setIsNavOpen(!isNavOpen);
  };

  const handleSignout = () => {
    SweetAlert.signOutAlert(
      () => {
        localStorage.clear();
        setTimeout(() => {
          navigate("/");
        }, 1500);
      },
      "Signing out"
    );
  };

  const renderContent = () => {
    switch (activeLink) {
      case "my-events":
        return <MyEvents />;
      case "pending-requests":
        return <PendingRequests />;
      case "home":
          return <RequestEventPage />;
      default:
        return <h1>Welcome to the Event Management System!</h1>;
    }
  };

  return (
    <div className="app">
      <SideNavBar
        isNavOpen={isNavOpen}
        activeLink={activeLink}
        setActiveLink={setActiveLink}
        handleSignout={handleSignout}
      />
      <div className="main-content">
        <header className="app-header">
          <TopBar fun={toggleNav} />
        </header>
        <div className="content">{renderContent()}</div>
      </div>
    </div>
  );
}

export default Index;
