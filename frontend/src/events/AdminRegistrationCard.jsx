import React from "react";

const AdminRegistrationCard = ({ events }) => {
  return (
    <div className="table-container">
      <table className="styled-table">
        <thead>
          <tr>
            <th>Attendee Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Registered By</th>
            <th>Registration Date</th>
            <th>Event Name</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event, index) => (
            <tr key={index}>
              <td>{event.attendee_name}</td>
              <td>{event.email}</td>
              <td>{event.phone}</td>
              <td>{event.registered_by}</td>
              <td>{event.registration_date}</td>
              <td>{event.event_name}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminRegistrationCard;
