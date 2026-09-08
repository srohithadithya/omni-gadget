import React, { useState, useEffect, useCallback } from 'react';
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
  Menu,
  X,
  Globe,
} from 'lucide-react';
import { useI18n } from '../i18n';

const NAV_ITEMS = [
  { path: '/', icon: Home, labelKey: 'NAV.nav_home' },
  { path: '/diagnose', icon: Activity, labelKey: 'NAV.nav_diagnose' },
  { path: '/recommend', icon: Target, labelKey: 'NAV.nav_recommend' },
  { path: '/emi-audit', icon: CreditCard, labelKey: 'NAV.nav_emi' },
  { path: '/chipflation', icon: TrendingUp, labelKey: 'NAV.nav_chipflation' },
  { path: '/full-decision', icon: Zap, labelKey: 'NAV.nav_decision' },
  { path: '/dashboard', icon: LayoutDashboard, labelKey: 'NAV.nav_dashboard' },
  { path: '/trends', icon: BarChart3, labelKey: 'NAV.nav_trends' },
];

const LANGUAGES = [
  { code: 'en', label: 'EN' },
  { code: 'te', label: 'తె' },
  { code: 'hi', label: 'हि' },
  { code: 'ta', label: 'த' },
  { code: 'ka', label: 'ಕ' },
];

export default function Layout({ children }) {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const { t, language, setLanguage } = useI18n();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('aide-theme') || 'dark';
  });

  // Apply theme class to <html> on mount and when theme changes
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(theme);
    localStorage.setItem('aide-theme', theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  }, []);

  const handleNav = useCallback((path) => {
    navigate(path);
    setMobileMenuOpen(false);
    setSidebarOpen(false);
  }, [navigate]);

  return (
    <div className="app-layout">
      {/* Skip to content */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* Mobile hamburger */}
      <button
        className="mobile-hamburger"
        aria-label="Open menu"
        onClick={() => setMobileMenuOpen(true)}
        style={{ display: 'none', position: 'fixed', top: 12, left: 12, zIndex: 60, background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', padding: '8px', cursor: 'pointer' }}
      >
        <Menu size={20} color="var(--text)" />
      </button>

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-logo" style={{ padding: 'var(--spacing-6) var(--spacing-4)', borderBottom: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Zap size={22} color="var(--primary)" />
            <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>AIDE-OS</h2>
          </div>
          <span style={{ fontSize: '0.65rem', color: 'var(--text-dim)', marginTop: 2 }}>v4.0.0-PROD</span>
        </div>

        <nav className="sidebar-nav" style={{ padding: 'var(--spacing-3) var(--spacing-2)', flex: 1, overflowY: 'auto' }}>
          {NAV_ITEMS.map((item) => (
            <button
              key={item.path}
              className={`nav-item ${pathname === item.path ? 'nav-item-active' : ''}`}
              onClick={() => handleNav(item.path)}
              style={{
                display: 'flex', alignItems: 'center', gap: 10, width: '100%',
                padding: '10px 12px', borderRadius: 'var(--radius-md)', border: 'none',
                background: pathname === item.path ? 'rgba(217,119,6,0.1)' : 'transparent',
                color: pathname === item.path ? 'var(--text)' : 'var(--text-muted)',
                cursor: 'pointer', fontSize: '0.82rem', fontWeight: 500,
                transition: 'all 0.15s ease', fontFamily: 'inherit',
              }}
            >
              <item.icon size={16} />
              {t(item.labelKey)}
            </button>
          ))}
        </nav>

        {/* Theme toggle + Language selector in sidebar footer */}
        <div style={{ padding: 'var(--spacing-4)', borderTop: '1px solid var(--border)' }}>
          {/* Language pills */}
          <div className="lang-selector" style={{ marginBottom: 10, justifyContent: 'center' }}>
            {LANGUAGES.map(lang => (
              <button
                key={lang.code}
                className={language === lang.code ? 'active' : ''}
                onClick={() => setLanguage(lang.code)}
                title={lang.code}
              >
                {lang.label}
              </button>
            ))}
          </div>

          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              width: '100%', padding: '10px', borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border)', background: 'var(--bg-elevated)',
              color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.82rem',
              fontWeight: 500, transition: 'all 0.15s ease', fontFamily: 'inherit',
            }}
          >
            {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
          </button>

          <div className="status-dot" style={{ marginTop: 10 }}>
            <span className="dot" />
            <span>{t('COMMON.status_active')}</span>
          </div>
        </div>
      </aside>

      {/* Mobile backdrop */}
      {mobileMenuOpen && (
        <div
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 40 }}
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Mobile slide-out menu */}
      {mobileMenuOpen && (
        <div style={{
          position: 'fixed', top: 0, left: 0, bottom: 0, width: 260,
          background: 'var(--bg-card)', borderRight: '1px solid var(--border)',
          zIndex: 50, padding: 'var(--spacing-4)', animation: 'fadeInLeft 0.2s ease-out',
          overflowY: 'auto',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-4)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Zap size={20} color="var(--primary)" />
              <span style={{ fontWeight: 700 }}>AIDE-OS</span>
            </div>
            <button onClick={() => setMobileMenuOpen(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
              <X size={20} />
            </button>
          </div>
          {NAV_ITEMS.map(item => (
            <button
              key={item.path}
              onClick={() => handleNav(item.path)}
              style={{
                display: 'flex', alignItems: 'center', gap: 10, width: '100%',
                padding: '10px 12px', borderRadius: 'var(--radius-md)', border: 'none',
                background: pathname === item.path ? 'rgba(217,119,6,0.1)' : 'transparent',
                color: pathname === item.path ? 'var(--text)' : 'var(--text-muted)',
                cursor: 'pointer', fontSize: '0.82rem', fontWeight: 500,
                marginBottom: 2, fontFamily: 'inherit',
              }}
            >
              <item.icon size={16} />
              {t(item.labelKey)}
            </button>
          ))}
          <div style={{ marginTop: 'var(--spacing-4)', borderTop: '1px solid var(--border)', paddingTop: 'var(--spacing-4)' }}>
            <div className="lang-selector" style={{ marginBottom: 10, justifyContent: 'center' }}>
              {LANGUAGES.map(lang => (
                <button key={lang.code} className={language === lang.code ? 'active' : ''} onClick={() => setLanguage(lang.code)}>
                  {lang.label}
                </button>
              ))}
            </div>
            <button onClick={toggleTheme} style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              width: '100%', padding: '10px', borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border)', background: 'var(--bg-elevated)',
              color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.82rem', fontFamily: 'inherit',
            }}>
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
              {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
            </button>
          </div>
        </div>
      )}

      {/* Main content */}
      <main className="main-content" id="main-content" style={{ padding: 'var(--spacing-8)', paddingBottom: 'var(--spacing-16)' }}>
        <div className="page-enter">
          {children}
        </div>
      </main>
    </div>
  );
}
