import React, { useState } from 'react';
import axios from 'axios';

export default function MeetModal({ petName, onClose }) {
  const [form, setForm] = useState({
    name: '',
    email: '',
    datetime: '',
  });
  const [status, setStatus] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:5000/api/appointments', {
      ...form,
      pet_name: petName,
    })
    .then(() => {
      setStatus('Appointment scheduled!');
      setForm({ name: '', email: '', datetime: '' });
    })
    .catch(() => setStatus('Failed to schedule.'));
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <button onClick={onClose} style={styles.closeBtn}>X</button>
        <h3>Schedule Meet & Greet for {petName}</h3>
        <form onSubmit={handleSubmit}>
          <input name="name" placeholder="Your Name" value={form.name} onChange={handleChange} required style={styles.input} />
          <input name="email" placeholder="Your Email" value={form.email} onChange={handleChange} required type="email" style={styles.input} />
          <input name="datetime" type="datetime-local" value={form.datetime} onChange={handleChange} required style={styles.input} />
          <button type="submit" style={styles.submit}>Schedule</button>
        </form>
        {status && <p>{status}</p>}
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
    backgroundColor: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center'
  },
  modal: {
    backgroundColor: '#fff', padding: '2rem', borderRadius: '8px', width: '90%', maxWidth: '500px'
  },
  input: {
    width: '100%', marginBottom: '1rem', padding: '0.75rem', fontSize: '1rem'
  },
  submit: {
    backgroundColor: '#007bff', color: 'white', padding: '0.75rem 1.5rem', border: 'none', borderRadius: '4px'
  },
  closeBtn: {
    position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', fontSize: '1.25rem'
  }
};
