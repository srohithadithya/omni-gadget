import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const NAV = [
  { path: '/',            icon: '🏠', label: 'Home' },
  { path: '/diagnose',    icon: '🔋', label: 'Device Diagnosis' },
  { path: '/recommend',   icon: '🎯', label: 'Find Gadgets' },
  { path: '/emi-audit',   icon: '💳', label: 'EMI Audit' },
  { path: '/chipflation', icon: '📈', label: 'Chipflation Index' },
  { path: '/full-decision', icon: '⚡', label: 'Full Decision' },
  { path: '/dashboard',    icon: '📋', label: 'My Dashboard' },
  { path: '/trends',       icon: '📊', label: 'Market Trends' },
];

export default function Layout({ children }) {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="app-layout">
      {/* Mobile Hamburger */}
      <div className="mobile-hamburger">
        <button
          className="hamburger-btn"
          aria-label="Open menu"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        >
          <span className="hamburger-line" />
          <span className="hamburger-line" />
          <span className="hamburger-line" />
        </button>
      </div>

      {/* Sidebar - hidden on mobile when menu closed */}
      <aside className={`${isMobileMenuOpen ? 'sidebar sidebar-open' : 'sidebar'}`}>
        <div className="sidebar-logo">
          <h2>⚡ AIDE-OS</h2>
          <span>v4.0.0-PROD</span>
        </div>
        <nav className="sidebar-nav">
          {NAV.map(n => (
            <button
              key={n.path}
              className={`nav-item ${pathname === n.path ? 'active' : ''}`}
              onClick={() => {
                navigate(n.path);
                setIsMobileMenuOpen(false); // close menu on nav click
              }}
            >
              <span className="nav-icon">{n.icon}</span>
              {n.label}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer" style={{ background: 'rgba(0,0,0,0.15)', borderRadius: '0 0 0 16px' }}>
          <div className="status-dot">
            <span className="dot" />
            Engine online
          </div>
          <div style={{ marginTop: 8, fontSize: 10, color: 'var(--text-muted)', lineHeight: 1.4 }}>
            AI-Driven Electronic<br />Device Ecosystem
          </div>
        </div>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}
