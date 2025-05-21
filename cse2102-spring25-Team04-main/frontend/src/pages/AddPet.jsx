import React, { useState } from 'react';
import axios from 'axios';

export default function AddPet() {
  const [form, setForm] = useState({
    name: '',
    species: '',
    breed: '',
    age: '',
    description: ''
  });
  const [images, setImages] = useState([]);
  const [status, setStatus] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    setImages([...e.target.files]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = new FormData();

    Object.entries(form).forEach(([key, value]) => {
      data.append(key, value);
    });

    images.forEach(file => data.append('images', file));

    axios.post('http://localhost:5000/api/pet', data)
      .then(() => {
        setStatus('Pet added successfully!');
        setForm({ name: '', species: '', breed: '', age: '', description: '' });
        setImages([]);
      })
      .catch(() => setStatus('Failed to add pet.'));
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <h2>Add a New Pet</h2>
      <input name="name" value={form.name} onChange={handleChange} placeholder="Name" required style={styles.input} />
      <input name="species" value={form.species} onChange={handleChange} placeholder="Species" required style={styles.input} />
      <input name="breed" value={form.breed} onChange={handleChange} placeholder="Breed" required style={styles.input} />
      <input name="age" type="number" value={form.age} onChange={handleChange} placeholder="Age" required style={styles.input} />
      <textarea name="description" value={form.description} onChange={handleChange} placeholder="Description" required style={styles.textarea} />
      <input type="file" multiple onChange={handleFileChange} style={styles.input} />
      <button type="submit" style={styles.button}>Add Pet</button>
      {status && <p>{status}</p>}
    </form>
  );
}

const styles = {
  form: {
    display: 'flex',
    flexDirection: 'column',
    maxWidth: '500px',
    margin: '2rem auto',
    gap: '1rem'
  },
  input: {
    padding: '0.75rem',
    fontSize: '1rem'
  },
  textarea: {
    padding: '0.75rem',
    fontSize: '1rem',
    minHeight: '100px'
  },
  button: {
    backgroundColor: '#27ae60',
    color: 'white',
    padding: '0.75rem',
    fontSize: '1rem',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  }
};
