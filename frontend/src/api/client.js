// Centralised API client
// Production: points at the Render backend (VITE_API_URL).
// Dev: empty baseURL falls through to the Vite proxy (/api -> localhost:8000).
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || '';

const API = axios.create({
  baseURL: API_BASE,
  timeout: 20000,
  headers: { 'Content-Type': 'application/json' },
});

const apiClient = {
  health: () => API.get('/api/v1/health'),
  categories: () => API.get('/api/v1/categories'),

  deviceLongevity: (data) => API.post('/api/v1/device-longevity', data),
  chipflationIndex: (data) => API.post('/api/v1/chipflation-index', data),
  emiAudit: (data) => API.post('/api/v1/emi-audit', data),
  emiSchedule: (data) => API.post('/api/v1/emi-schedule', data),
  recommend: (data) => API.post('/api/v1/recommend', data),
  fullDecision: (data) => API.post('/api/v1/full-decision', data),

  // History & trends (GET)
  history: () => API.get('/api/v1/history'),
  popular: () => API.get('/api/v1/popular'),
  trends: () => API.get('/api/v1/trends'),
};

export default apiClient;
