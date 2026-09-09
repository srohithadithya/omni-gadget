import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useI18n } from '../i18n';
import { Activity, Target, CreditCard, TrendingUp, Zap, LayoutDashboard, BarChart3, Monitor, MousePointer, Scroll, Zap as ZapIcon, TrendingUp as TrendingUpIcon } from 'lucide-react';

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
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: 600, margin: '0 auto var(--spacing-6)', lineHeight: 1.7, whiteSpace: 'pre-line' }}>
          {t('HOME.home_subtitle')}
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--spacing-4)', flexWrap: 'wrap' }}>
          <button
            className="btn btn-primary"
            onClick={() => navigate('/diagnose')}
            style={{ fontSize: '0.95rem', padding: '12px 28px', borderRadius: 'var(--radius-full)' }}
          >
            {t('HOME.home_cta_diagnose')}
          </button>
          <button
            className="btn btn-outline"
            onClick={() => navigate('/recommend')}
            style={{ fontSize: '0.95rem', padding: '12px 28px', borderRadius: 'var(--radius-full)', border: '1px solid var(--border)', background: 'transparent', color: 'var(--text)' }}
          >
            {t('HOME.home_cta_find')}
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div style={{ marginBottom: 'var(--spacing-8)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 'var(--spacing-4)' }}>
          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: 4 }}>
              <Activity size={24} color="var(--primary)" />
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)', marginBottom: 4 }}>
              {t('HOME.home_stat_categories')}
            </div>
            <div style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
              {t('HOME.home_stat_categories')}
            </div>
          </div>
          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: 4 }}>
              <Monitor size={24} color="var(--primary)" />
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)', marginBottom: 4 }}>
              {t('HOME.home_stat_products')}
            </div>
            <div style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
              {t('HOME.home_stat_products')}
            </div>
          </div>
          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: 4 }}>
              <MousePointer size={24} color="var(--primary)" />
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)', marginBottom: 4 }}>
              {t('HOME.home_stat_hidden_fees')}
            </div>
            <div style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
              {t('HOME.home_stat_hidden_fees')}
            </div>
          </div>
          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: 4 }}>
              <Scroll size={24} color="var(--primary)" />
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)', marginBottom: 4 }}>
              {t('HOME.home_stat_sale_events')}
            </div>
            <div style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
              {t('HOME.home_stat_sale_events')}
            </div>
          </div>
        </div>
      </div>

      {/* Core Engines */}
      <div>
        <div className="section-divider" style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', textAlign: 'center', marginBottom: 'var(--spacing-6)' }}>
          {t('HOME.home_core_title')}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--spacing-6)' }}>
          {/* Device Diagnosis Card */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '180px' }}>
            <div>
              <div style={{ width: 48, height: 48, borderRadius: 'var(--radius-lg)', background: 'rgba(217,119,6,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--spacing-3)' }}>
                <Activity size={24} color="var(--primary)" />
              </div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)', marginBottom: 'var(--spacing-2)' }}>
                {t('HOME.home_device_diagnosis_title')}
              </h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6, flexGrow: 1 }}>
                {t('HOME.home_device_diagnosis_desc')}
              </p>
            </div>
            <a href="/diagnose" style={{ alignSelf: 'flex-end', color: 'var(--primary)', fontWeight: 600, textDecoration: 'none', fontSize: '0.875rem' }}>
              {t('HOME.home_learn_more')}
              <ZapIcon size={16} style={{ marginLeft: 4 }} />
            </a>
          </div>
          {/* Smart Recommendations Card */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '180px' }}>
            <div>
              <div style={{ width: 48, height: 48, borderRadius: 'var(--radius-lg)', background: 'rgba(217,119,6,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--spacing-3)' }}>
                <Target size={24} color="var(--primary)" />
              </div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)', marginBottom: 'var(--spacing-2)' }}>
                {t('HOME.home_smart_recommendations_title')}
              </h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6, flexGrow: 1 }}>
                {t('HOME.home_smart_recommendations_desc')}
              </p>
            </div>
            <a href="/recommend" style={{ alignSelf: 'flex-end', color: 'var(--primary)', fontWeight: 600, textDecoration: 'none', fontSize: '0.875rem' }}>
              {t('HOME.home_learn_more')}
              <TrendingUpIcon size={16} style={{ marginLeft: 4 }} />
            </a>
          </div>
        </div>
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