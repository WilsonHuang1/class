import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import AdoptForm from '../components/AdoptForm';
import MeetForm from '../components/MeetForm';

export default function PetDetail() {
  const { id } = useParams();
  const [pet, setPet] = useState(null);

  useEffect(() => {
    axios.get(`http://localhost:5000/api/pet/${id}`)
      .then(res => setPet(res.data))
      .catch(err => console.error('Error fetching pet details:', err));
  }, [id]);

  if (!pet) return <p>Loading...</p>;

  return (
    <div style={styles.container}>
      <h2>{pet.name}</h2>
      <p><strong>Species:</strong> {pet.species}</p>
      <p><strong>Breed:</strong> {pet.breed}</p>
      <p><strong>Age:</strong> {pet.age}</p>
      <p><strong>Description:</strong> {pet.description}</p>

      {pet.images && pet.images.length > 0 ? (
        pet.images.map((img, i) => (
          <img key={i} src={`http://localhost:5000/uploads/${img}`} alt={pet.name} style={styles.image} />
        ))
      ) : (
        <div style={{ ...styles.image, backgroundColor: '#eee' }}>No Image Available</div>
      )}

      <AdoptForm petName={pet.name} />
      <MeetForm petId={pet.id} />
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '800px',
    margin: '2rem auto',
    background: 'white',
    padding: '2rem',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
  },
  image: {
    width: '100%',
    maxHeight: '400px',
    objectFit: 'cover',
    marginBottom: '1rem',
    borderRadius: '6px',
  },
};
