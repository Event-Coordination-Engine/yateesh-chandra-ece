import React from 'react';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {

  const navigate = useNavigate()
  
  const handleButton = () => {
    navigate("/login");
  }

  return (
    <div className="home-page">
      <header className="hero-section">
        <div className="hero-content">
          <h1>Welcome to ECE</h1>
          <p>Your one-step solution for co-ordinating events effortlessly!</p>
          <button className="cta-button cursor-pointer" onClick={handleButton}>Dive In</button>
        </div>
      </header>
      
      <section id="features" className="features-section">
        <div className="feature">
          <h2>Easy Event Creation</h2>
          <p>Create and customize events with just a few clicks.</p>
        </div>
        <div className="feature">
          <h2>Real-Time Analytics</h2>
          <p>Track event performance and make data-driven decisions.</p>
        </div>
        <div className="feature">
          <h2>Seamless Performance</h2>
          <p>Register and attend the Events to explore the unknown.</p>
        </div>
      </section>

      <footer className="footer">
        <p>&copy; 2024 EventManager. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default HomePage;