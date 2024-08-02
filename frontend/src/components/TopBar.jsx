import React from "react";
import { FaBars, FaUserCircle } from "react-icons/fa";

const TopBar = ({ fun }) => {
  return (
    <div className="top-bar">
      <button className="nav-toggle-btn" onClick={fun}>
        <FaBars />
      </button>
      <button className="nav-toggle-btn" onClick={fun}>
        <FaUserCircle />
      </button>
    </div>
  );
};

export default TopBar;
