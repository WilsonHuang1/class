import React, { useEffect, useState } from 'react';
import axios from 'axios';
import EditPetModal from '../components/EditPetModal';
import MeetModal from '../components/MeetModal';

export default function AdminDashboard() {
  const [pets, setPets] = useState([]);
  const [adoptions, setAdoptions] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [selectedPet, setSelectedPet] = useState(null);
  const [showEdit, setShowEdit] = useState(false);

  const fetchAll = () => {
    axios.get('http://localhost:5000/api/pets').then(res => setPets(res.data));
    axios.get('http://localhost:5000/api/adoptions').then(res => setAdoptions(res.data));
    axios.get('http://localhost:5000/api/appointments').then(res => setAppointments(res.data));
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const deletePet = (id) => {
    if (window.confirm("Delete this pet?")) {
      axios.delete(`http://localhost:5000/api/pet/${id}`).then(fetchAll);
    }
  };

  const handleEdit = (pet) => {
    setSelectedPet(pet);
    setShowEdit(true);
  };

  return (
    <div style={styles.page}>
      <h2 style={styles.header}>Admin Dashboard</h2>

      <div style={styles.section}>
        <h3>🐾 All Pets</h3>
        <table style={styles.table}>
          <thead>
            <tr>
              <th>Name</th><th>Species</th><th>Breed</th><th>Age</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {pets.map(pet => (
              <tr key={pet.id}>
                <td>{pet.name}</td>
                <td>{pet.species}</td>
                <td>{pet.breed}</td>
                <td>{pet.age}</td>
                <td>
                  <button onClick={() => handleEdit(pet)} style={styles.editBtn}>Edit</button>
                  <button onClick={() => deletePet(pet.id)} style={styles.deleteBtn}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={styles.section}>
        <h3>📩 Adoption Requests</h3>
        <table style={styles.table}>
          <thead>
            <tr><th>Name</th><th>Email</th><th>Pet</th><th>Message</th><th>Time</th></tr>
          </thead>
          <tbody>
            {adoptions.map((a, i) => (
              <tr key={i}>
                <td>{a.name}</td>
                <td>{a.email}</td>
                <td>{a.pet_name}</td>
                <td>{a.message}</td>
                <td>{a.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={styles.section}>
        <h3>📅 Meet & Greet Appointments</h3>
        <table style={styles.table}>
          <thead>
            <tr><th>Name</th><th>Email</th><th>Pet</th><th>Date/Time</th></tr>
          </thead>
          <tbody>
            {appointments.map((m, i) => (
              <tr key={i}>
                <td>{m.name}</td>
                <td>{m.email}</td>
                <td>{m.pet_name}</td>
                <td>{m.datetime}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showEdit && <EditPetModal pet={selectedPet} onClose={() => {
        setShowEdit(false);
        fetchAll();
      }} />}
    </div>
  );
}

const styles = {
  page: {
    padding: '2rem',
    fontFamily: 'Segoe UI, sans-serif',
    backgroundColor: '#f8f9fa',
    minHeight: '100vh',
  },
  header: {
    fontSize: '2rem',
    marginBottom: '1rem',
  },
  section: {
    marginBottom: '2rem',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    backgroundColor: '#fff',
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
  },
  editBtn: {
    marginRight: '0.5rem',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    padding: '5px 10px',
    cursor: 'pointer',
  },
  deleteBtn: {
    backgroundColor: '#dc3545',
    color: '#fff',
    border: 'none',
    padding: '5px 10px',
    cursor: 'pointer',
  }
};
