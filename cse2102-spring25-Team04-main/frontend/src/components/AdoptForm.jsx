import React from 'react';

export default function AdoptForm({ petName }) {
  return (
    <form
      action="https://formsubmit.co/vincentkariuki963@gmail.com"
      method="POST"
      style={styles.form}
    >
      <h3>Interested in adopting {petName}?</h3>

      <input
        type="text"
        name="name"
        placeholder="Your Name"
        required
        style={styles.input}
      />

      <input
        type="email"
        name="email"
        placeholder="Your Email"
        required
        style={styles.input}
      />

      <textarea
        name="message"
        placeholder="Why do you want to adopt?"
        required
        style={styles.textarea}
      />

      {/* Hidden Inputs for Settings */}
      <input type="hidden" name="_subject" value={`Adoption Request for ${petName}`} />
      <input type="hidden" name="_captcha" value="false" />
      <input type="hidden" name="_template" value="box" />
      <input type="hidden" name="_next" value="http://localhost:5173/pets" />

      <button type="submit" style={styles.button}>Submit Request</button>
    </form>
  );
}

const styles = {
  form: {
    display: 'flex',
    flexDirection: 'column',
    maxWidth: '500px',
    marginTop: '1.5rem',
    background: '#fff',
    padding: '1.5rem',
    borderRadius: '8px',
    boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
  },
  input: {
    padding: '0.75rem',
    marginBottom: '1rem',
    fontSize: '1rem',
    border: '1px solid #ccc',
    borderRadius: '4px'
  },
  textarea: {
    padding: '0.75rem',
    marginBottom: '1rem',
    fontSize: '1rem',
    minHeight: '100px',
    border: '1px solid #ccc',
    borderRadius: '4px'
  },
  button: {
    backgroundColor: '#2c3e50',
    color: 'white',
    padding: '0.75rem',
    fontSize: '1rem',
    cursor: 'pointer',
    border: 'none',
    borderRadius: '4px'
  }
};
