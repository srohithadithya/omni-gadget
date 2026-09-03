// Centralised API client — all calls go through Vite proxy
import axios from 'axios';

const API = axios.create({
  baseURL: '',  // Uses Vite proxy to /api
  timeout: 15000,
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
