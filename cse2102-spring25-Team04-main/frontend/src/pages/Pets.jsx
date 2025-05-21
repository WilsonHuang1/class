import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function Pets() {
  const [pets, setPets] = useState([]);
  const [species, setSpecies] = useState([]);
  const [selectedSpecies, setSelectedSpecies] = useState('All');
  const isAdmin = localStorage.getItem('isAdmin') === 'true';
  const navigate = useNavigate();

  const fetchPets = () => {
    axios.get('http://localhost:5000/api/pets')
      .then(res => {
        setPets(res.data);
        const uniqueSpecies = [...new Set(res.data.map(p => p.species))];
        setSpecies(uniqueSpecies);
      })
      .catch(err => console.error('Error fetching pets:', err));
  };

  useEffect(() => {
    fetchPets();
  }, []);

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this pet?')) {
      axios.delete(`http://localhost:5000/api/pet/${id}`)
        .then(() => fetchPets())
        .catch(() => alert('Failed to delete'));
    }
  };

  const filteredPets = selectedSpecies === 'All' ? pets : pets.filter(p => p.species === selectedSpecies);

  return (
    <div style={styles.container}>
      <h2>Available Pets</h2>

      <div style={styles.filter}>
        <label style={{ marginRight: '0.5rem' }}>Filter by Species:</label>
        <select value={selectedSpecies} onChange={(e) => setSelectedSpecies(e.target.value)}>
          <option value="All">All</option>
          {species.map((s, i) => (
            <option key={i} value={s}>{s}</option>
          ))}
        </select>
      </div>

      <div style={styles.grid}>
        {filteredPets.map(pet => (
          <div key={pet.id} style={styles.card}>
            {pet.images && pet.images.length > 0 ? (
              <img
                src={`http://localhost:5000/uploads/${pet.images[0]}`}
                alt={pet.name}
                style={styles.image}
              />
            ) : (
              <div style={{ ...styles.image, backgroundColor: '#eee', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                No Image
              </div>
            )}
            <h3 style={{ color: '#2980b9' }}>{pet.name}</h3>
            <p><strong>Species:</strong> {pet.species}</p>
            <p><strong>Breed:</strong> {pet.breed}</p>
            <p><strong>Age:</strong> {pet.age}</p>
            <p>{pet.description}</p>

            {isAdmin && (
              <button onClick={() => handleDelete(pet.id)} style={styles.delete}>Delete</button>
            )}
            <button onClick={() => navigate(`/pet/${pet.id}`)} style={styles.view}>View Details</button>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  container: {
    width: '100%',
    padding: '1rem 0',
  },
  filter: {
    marginBottom: '1rem',
    textAlign: 'left',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '1.5rem',
  },
  card: {
    border: '1px solid #ddd',
    borderRadius: '8px',
    padding: '1rem',
    backgroundColor: '#fff',
    textAlign: 'center',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
  },
  image: {
    width: '100%',
    height: '200px',
    objectFit: 'cover',
    borderRadius: '6px',
    marginBottom: '1rem',
  },
  delete: {
    marginTop: '0.5rem',
    background: '#e74c3c',
    color: 'white',
    border: 'none',
    padding: '0.5rem 1rem',
    borderRadius: '4px',
    cursor: 'pointer',
    marginRight: '0.5rem',
  },
  view: {
    background: '#3498db',
    color: 'white',
    border: 'none',
    padding: '0.5rem 1rem',
    borderRadius: '4px',
    cursor: 'pointer',
  },
};
