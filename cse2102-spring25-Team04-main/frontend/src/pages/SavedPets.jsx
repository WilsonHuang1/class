import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function SavedPets() {
  const [pets, setPets] = useState([]);
  const user = JSON.parse(localStorage.getItem('user'));

  useEffect(() => {
    if (!user) return;
    axios.get(`http://localhost:5000/api/user/${user.id}/saved`)
      .then(res => setPets(res.data))
      .catch(() => alert('Failed to load saved pets.'));
  }, [user]);

  if (!user) return <p>Please log in to view saved pets.</p>;

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Saved Pets</h2>
      {pets.length === 0 ? <p>No saved pets yet.</p> : (
        <ul>
          {pets.map(pet => <li key={pet.id}>{pet.name} ({pet.species})</li>)}
        </ul>
      )}
    </div>
  );
}