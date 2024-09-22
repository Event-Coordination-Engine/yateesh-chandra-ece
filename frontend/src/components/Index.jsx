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
import AdminPendingRequests from "../events/AdminPendingRequests";
import RegisteredEvents from "../events/RegisteredEvents";
import EventRegistration from "../events/EventRegistration";
import UserRegistration from "../events/UserRegistration";
import AdminRegistrations from "../events/AdminRegistrations";
import userService from "../services/userService";
import AdminOldRegistrations from "../events/AdminOldRegistrations";
import Dashboard from "../pages/Dashboard";

function Index() {
    const [isNavOpen, setIsNavOpen] = useState(false);
    const userRole = localStorage.getItem("role");
    const logId = localStorage.getItem("log_id");

    const toggleNav = () => {
        setIsNavOpen(!isNavOpen);
    };

    const closeNav = () => {
        setIsNavOpen(false);
    };

    const logout = async () => {
        try {
            const res = await userService.logoutUser(logId);
            console.log(res);
        } catch (err) {
            console.log(err);
        }
    };

    const handleSignout = () => {
        SweetAlert.signOutAlert(
            () => {
                localStorage.clear();
                logout();
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
                        toggleNav={toggleNav}
                        closeNav={closeNav}  // Pass closeNav function
                    />
                    <div className="main-content">
                        <header className="app-header">
                            <TopBar fun={toggleNav} />
                        </header>
                        <div className="content">
                            <Routes>
                                <Route path="/" element={<Dashboard />} />
                                <Route path="my-events" element={<MyEvents />} />
                                {userRole === "USER" && (<Route path="pending-requests" element={<PendingRequests />} />)}
                                {userRole === "ADMIN" && (<Route path="pending-requests" element={<AdminPendingRequests />} />)}
                                {userRole === "USER" && (<Route path="registered-events" element={<RegisteredEvents />} />)}
                                {userRole === "ADMIN" && (<Route path="registered-events" element={<AdminRegistrations />} />)}
                                {userRole === "ADMIN" && (<Route path="all-attendees" element={<AdminOldRegistrations />} />)}
                                <Route path="available-events" element={<EventRegistration/>}/>
                                <Route path="register-event/:eventId" element={<UserRegistration />} />
                                <Route path="add-event" element={<RequestEventPage />} />
                                <Route path="edit-event/:eventId" element={<EditEventPage />} />
                            </Routes>
                        </div>
                    </div>
                </>
            ) : (
                <div><Unauthorized /></div>
            )}
        </div>
    );
}

export default Index;
