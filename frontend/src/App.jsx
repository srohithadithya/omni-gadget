import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import DiagnosePage from './pages/DiagnosePage';
import RecommendPage from './pages/RecommendPage';
import EMIAuditPage from './pages/EMIAuditPage';
import ChipflationPage from './pages/ChipflationPage';
import FullDecisionPage from './pages/FullDecisionPage';
import DashboardPage from './pages/DashboardPage';
import TrendsPage from './pages/TrendsPage';
import './index.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/diagnose" element={<DiagnosePage />} />
          <Route path="/recommend" element={<RecommendPage />} />
          <Route path="/emi-audit" element={<EMIAuditPage />} />
          <Route path="/chipflation" element={<ChipflationPage />} />
          <Route path="/full-decision" element={<FullDecisionPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/trends" element={<TrendsPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;