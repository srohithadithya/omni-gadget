import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Apply saved theme on startup
const applyTheme = () => {
  const saved = localStorage.getItem('aide-theme');
  if (saved === 'light') {
    document.documentElement.classList.add('light');
  } else {
    document.documentElement.classList.remove('light');
  }
};

// Optional: expose a toggle function globally (e.g., via a context or a button)
window.toggleAideTheme = () => {
  const isLight = document.documentElement.classList.toggle('light');
  localStorage.setItem('aide-theme', isLight ? 'light' : 'dark');
};

applyTheme();

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);