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
      <td data-label="Attendee Name">{event.attendee_name}</td>
      <td data-label="Email">{event.email}</td>
      <td data-label="Phone">{event.phone}</td>
      <td data-label="Registered By">{event.registered_by}</td>
      <td data-label="Registration Date">{event.registration_date}</td>
      <td data-label="Event Name">{event.event_name}</td>
    </tr>
  ))}
</tbody>

      </table>
    </div>
  );
};

export default AdminRegistrationCard;
