import React, { useState } from "react";
import { Route, Routes } from "react-router-dom";
import TopBar from "./TopBar";
import SideNavBar from "../components/SideNavBar";
import SweetAlert from "../sweetalerts/SweetAlert";
import MyEvents from "../events/MyEvents";
import PendingRequests from "../events/PendingRequests";
import RequestEventPage from "../events/RequestEventPage";
import EditEventPage from "../events/EditEventPage";
import Unauthorized from "./Unauthorized";

function Index() {
  const [isNavOpen, setIsNavOpen] = useState(false);
  const userRole = localStorage.getItem("role");

  const toggleNav = () => {
    setIsNavOpen(!isNavOpen);
  };

  const handleSignout = () => {
    SweetAlert.signOutAlert(
      () => {
        localStorage.clear();
        setTimeout(() => {
          window.location.href = "/"; // Redirect to home after sign out
        }, 1500);
      },
      "Signing out"
    );
  };

  return (
    <div className="app">
      {userRole === "ADMIN" || userRole === "USER" ? (
        <>
        <SideNavBar
        isNavOpen={isNavOpen}
        handleSignout={handleSignout}
      />
      <div className="main-content">
        <header className="app-header">
          <TopBar fun={toggleNav} />
        </header>
        <div className="content">
          <Routes>
            <Route path="/" element={<RequestEventPage />} />
            <Route path="my-events" element={<MyEvents />} />
            <Route path="pending-requests" element={<PendingRequests />} />
            <Route path="edit-event/:eventId" element={<EditEventPage />} />
            {/* Add other routes here */}
          </Routes>
        </div>
      </div>
      </>):
      (<div><Unauthorized/></div>)}
    </div>
  );
}

export default Index;
