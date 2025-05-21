
import React, { useState } from 'react';
import axios from 'axios';

export default function EditPetModal({ pet, onClose }) {
  const [form, setForm] = useState(pet);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.put(`http://localhost:5000/api/pet/${pet.id}`, form)
      .then(() => onClose())
      .catch(() => alert("Failed to update pet"));
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <h3>Edit Pet Info</h3>
        <form onSubmit={handleSubmit}>
          <input name="name" value={form.name} onChange={handleChange} placeholder="Name" required style={styles.input} />
          <input name="species" value={form.species} onChange={handleChange} placeholder="Species" required style={styles.input} />
          <input name="breed" value={form.breed} onChange={handleChange} placeholder="Breed" style={styles.input} />
          <input name="age" value={form.age} onChange={handleChange} placeholder="Age" type="number" style={styles.input} />
          <textarea name="description" value={form.description} onChange={handleChange} placeholder="Description" style={styles.input} />
          <div style={styles.actions}>
            <button type="submit" style={styles.save}>Save</button>
            <button type="button" onClick={onClose} style={styles.cancel}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.4)', display: 'flex', justifyContent: 'center', alignItems: 'center'
  },
  modal: {
    background: 'white', padding: '2rem', borderRadius: '8px', width: '400px',
  },
  input: {
    width: '100%', marginBottom: '1rem', padding: '0.75rem', fontSize: '1rem'
  },
  actions: {
    display: 'flex', justifyContent: 'space-between'
  },
  save: {
    backgroundColor: '#27ae60', color: 'white', padding: '0.5rem 1rem', border: 'none', borderRadius: '4px'
  },
  cancel: {
    backgroundColor: '#bdc3c7', padding: '0.5rem 1rem', border: 'none', borderRadius: '4px'
  }
};
