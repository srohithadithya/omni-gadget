import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Home,
  Activity,
  Target,
  CreditCard,
  TrendingUp,
  Zap,
  BarChart3,
  LayoutDashboard,
  Moon,
  Sun,
} from 'lucide-react';

const NAV = [
  { path: '/', icon: Home, label: 'Home' },
  { path: '/diagnose', icon: Activity, label: 'Device Diagnosis' },
  { path: '/recommend', icon: Target, label: 'Find Gadgets' },
  { path: '/emi-audit', icon: CreditCard, label: 'EMI Audit' },
  { path: '/chipflation', icon: TrendingUp, label: 'Chipflation Index' },
  { path: '/full-decision', icon: Zap, label: 'Full Decision' },
  { path: '/dashboard', icon: LayoutDashboard, label: 'My Dashboard' },
  { path: '/trends', icon: BarChart3, label: 'Market Trends' },
];

export default function Layout({ children }) {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('aide-theme');
    return saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  });

  // Handle theme changes
  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('aide-theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  return (
    <div className="app-layout">
      {/* Skip to content link */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* Mobile hamburger */}
      <button
        className="mobile-hamburger"
        aria-label="Open menu"
        onClick={() => setIsMobileMenuOpen(true)}
      >
        <span className="hamburger-line" />
        <span className="hamburger-line" />
        <span className="hamburger-line" />
      </button>

      {/* Sidebar */}
      <aside
        className={`${isSidebarOpen ? 'sidebar sidebar-open' : 'sidebar'} `
        + (theme === 'dark' ? 'sidebar-dark' : '')}
      >
        <div className="sidebar-logo">
          <h2>⚡ AIDE-OS</h2>
          <span>v4.0.0-PROD</span>
        </div>
        <nav className="sidebar-nav">
          {NAV.map((nav) => (
            <button
              key={nav.path}
              className={`nav-item ${
                pathname === nav.path ? 'nav-item-active' : ''
              }`}
              onClick={() => {
                navigate(nav.path);
                setIsSidebarOpen(false);
                setIsMobileMenuOpen(false);
              }}
            >
              <span className="nav-icon">
                <nav.icon className="h-4 w-4" />
              </span>
              {nav.label}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="status-dot">
            <span className="dot" />
            <span>Engine online</span>
          </div>
          <div className="sidebar-footer-text">
            Built for smart buyers
          </div>
        </div>
      </aside>

      {/* Sidebar backdrop for mobile */}
      {isMobileMenuOpen && (
        <div className="sidebar-backdrop" onClick={() => setIsMobileMenuOpen(false)} />
      )}

      <main className="main-content" id="main-content">
        {children}
      </main>

      {/* Mobile bottom tab bar */}
      <nav className="mobile-tab-bar">
        {NAV.slice(0, 5).map((nav) => (
          <a
            key={nav.path}
            href={nav.path}
            className={`mobile-tab-item ${
              pathname === nav.path ? 'mobile-tab-item-active' : ''
            }`}
            onClick={(e) => {
              e.preventDefault();
              navigate(nav.path);
              setIsMobileMenuOpen(false);
            }}
          >
            <span className="icon">
              <nav.icon className="h-5 w-5" />
            </span>
            <span className="label">{nav.label}</span>
          </a>
        ))}
      </nav>
    </div>
  );
}