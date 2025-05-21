
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Pets from './pages/Pets';
import AddPet from './pages/AddPet';
import Login from './pages/Login';
import PetDetail from './pages/PetDetail';
import AdminDashboard from './pages/AdminDashboard';
import Navbar from './components/Navbar';

export default function App() {
  const isAdmin = localStorage.getItem('isAdmin') === 'true';

  return (
    <div style={styles.page}>
      <Navbar />
      <main style={styles.main}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/pets" element={<Pets />} />
          <Route path="/pet/:id" element={<PetDetail />} />
          {isAdmin && <Route path="/add" element={<AddPet />} />}
          {isAdmin && <Route path="/admin" element={<AdminDashboard />} />}
          <Route path="/login" element={<Login />} />
        </Routes>
      </main>
    </div>
  );
}

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#f9f9f9',
    fontFamily: 'Segoe UI, sans-serif',
  },
  main: {
    flex: 1,
    padding: '2rem 4vw',
    width: '100%',
  },
};
