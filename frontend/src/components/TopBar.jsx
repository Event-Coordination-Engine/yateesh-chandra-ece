import React from "react";
import { FaBars, FaUserCircle } from "react-icons/fa";

const TopBar = ({ fun }) => {

    const name = localStorage.getItem("name")
    return (
        <div className="top-bar">
            <button className="nav-toggle-btn" onClick={fun}>
                <FaBars />
            </button>
            <div className="user-info">
                <span className="user-name">{name}</span>
                <FaUserCircle className="user-icon" />
            </div>
        </div>
    );
};

export default TopBar;
