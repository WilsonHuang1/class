
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

export default function Navbar() {
  const isAdmin = localStorage.getItem('isAdmin') === 'true';
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem('isAdmin');
    navigate('/');
  };

  return (
    <nav style={styles.nav}>
      <h1 style={styles.logo}>🐾 PetAdopt</h1>
      <div style={styles.links}>
        <Link to="/" style={styles.link}>Home</Link>
        <Link to="/pets" style={styles.link}>Pets</Link>
        {isAdmin && <Link to="/add" style={styles.link}>Add Pet</Link>}
        {isAdmin && <Link to="/admin" style={styles.link}>Dashboard</Link>}
        {!isAdmin ? (
          <Link to="/login" style={styles.link}>Login</Link>
        ) : (
          <button onClick={logout} style={styles.button}>Logout</button>
        )}
      </div>
    </nav>
  );
}

const styles = {
  nav: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '1rem 2rem',
    background: '#2c3e50',
    color: 'white',
    alignItems: 'center',
  },
  logo: {
    fontSize: '1.5rem',
  },
  links: {
    display: 'flex',
    gap: '1rem',
  },
  link: {
    color: 'white',
    textDecoration: 'none',
    fontWeight: '500',
  },
  button: {
    background: 'transparent',
    border: '1px solid white',
    color: 'white',
    padding: '0.4rem 0.75rem',
    borderRadius: '4px',
    cursor: 'pointer',
  }
};
