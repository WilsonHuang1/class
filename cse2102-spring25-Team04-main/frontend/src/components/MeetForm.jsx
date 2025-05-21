import React, { useState } from 'react';
import axios from 'axios';

export default function MeetForm({ petId }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [datetime, setDatetime] = useState('');
  const [status, setStatus] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // First fetch pet name from backend
      const res = await axios.get(`http://localhost:5000/api/pet/${petId}`);
      const pet_name = res.data.name;

      await axios.post('http://localhost:5000/api/appointments', {
        name,
        email,
        time: datetime,
        pet_name
      });

      setStatus('Booking successful!');
      setName('');
      setEmail('');
      setDatetime('');
    } catch (error) {
      console.error('Booking failed:', error);
      setStatus('Booking failed.');
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginTop: '2rem' }}>
      <h3>Schedule a Meet & Greet</h3>
      <input
        type="text"
        placeholder="Your Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />
      <input
        type="email"
        placeholder="Your Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="datetime-local"
        value={datetime}
        onChange={(e) => setDatetime(e.target.value)}
        required
      />
      <button type="submit">Book Appointment</button>
      {status && <p>{status}</p>}
    </form>
  );
}
