import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useI18n } from '../i18n';
import { Activity, Target, CreditCard, TrendingUp, Zap, LayoutDashboard, BarChart3 } from 'lucide-react';

const FEATURES = [
  { icon: Activity, path: '/diagnose', key: 'NAV.nav_diagnose', desc: 'Check your device health and get a longevity score' },
  { icon: Target, path: '/recommend', key: 'NAV.nav_recommend', desc: 'Find the best gadgets for your budget and needs' },
  { icon: CreditCard, path: '/emi-audit', key: 'NAV.nav_emi', desc: 'Uncover hidden EMI charges and true cost with GST' },
  { icon: TrendingUp, path: '/chipflation', key: 'NAV.nav_chipflation', desc: 'Track market pricing pressure and chip shortage impact' },
  { icon: Zap, path: '/full-decision', key: 'NAV.nav_decision', desc: 'Run all engines at once for a complete recommendation' },
  { icon: LayoutDashboard, path: '/dashboard', key: 'NAV.nav_dashboard', desc: 'Track all your decisions and scores in one place' },
  { icon: BarChart3, path: '/trends', key: 'NAV.nav_trends', desc: 'See popular products and market trends by region' },
];

export default function HomePage() {
  const navigate = useNavigate();
  const { t } = useI18n();

  return (
    <div>
      {/* Hero Banner */}
      <div className="gradient-banner" style={{ marginBottom: 'var(--spacing-8)', textAlign: 'center' }}>
        <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)', marginBottom: 8, letterSpacing: '-0.02em' }}>
          {t('HOME.home_title')}
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: 600, margin: '0 auto var(--spacing-6)', lineHeight: 1.7 }}>
          {t('HOME.home_subtitle')}
        </p>
        <button
          className="btn btn-primary"
          onClick={() => navigate('/full-decision')}
          style={{ fontSize: '0.95rem', padding: '12px 28px', borderRadius: 'var(--radius-full)' }}
        >
          <Zap size={18} style={{ marginRight: 6 }} />
          {t('HOME.home_run_full')}
        </button>
      </div>

      {/* Feature Grid */}
      <div style={{ marginBottom: 'var(--spacing-6)' }}>
        <div className="section-divider" style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>
          {t('HOME.home_quick_start')}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 'var(--spacing-4)' }}>
        {FEATURES.map((feat, i) => (
          <div
            key={feat.path}
            className={`card animate-fade-in-up stagger-${i + 1}`}
            onClick={() => navigate(feat.path)}
            style={{
              cursor: 'pointer',
              padding: 'var(--spacing-5)',
              display: 'flex',
              alignItems: 'flex-start',
              gap: 'var(--spacing-3)',
            }}
          >
            <div style={{
              width: 40, height: 40, borderRadius: 'var(--radius-md)',
              background: 'rgba(217,119,6,0.1)', display: 'flex', alignItems: 'center',
              justifyContent: 'center', flexShrink: 0,
            }}>
              <feat.icon size={20} color="var(--primary)" />
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.92rem', marginBottom: 4 }}>
                {t(feat.key)}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                {feat.desc}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Status bar */}
      <div className="card animate-fade-in" style={{ marginTop: 'var(--spacing-8)', padding: 'var(--spacing-4)', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
        <div className="status-dot" style={{ justifyContent: 'center', marginBottom: 8 }}>
          <span className="dot" />
          <span>{t('COMMON.status_active')}</span>
        </div>
        {t('APP.tagline')}
      </div>
    </div>
  );
}
