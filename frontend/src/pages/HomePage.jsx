import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useI18n } from '../i18n';
import { Activity, Target, CreditCard, TrendingUp, Zap, LayoutDashboard, BarChart3, Monitor, MousePointer, Scroll, Zap as ZapIcon, TrendingUp as TrendingUpIcon } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Button from '../components/Button';
import Card from '../components/Card';

export default function HomePage() {
  const navigate = useNavigate();
  const { t } = useI18n();
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    // Mock data for chipflation trend over last 6 months
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    setChartData(
      months.map((month, index) => ({
        month,
        value: 0.8 + Math.random() * 0.4, // between 0.8 and 1.2
      }))
    );
  }, []);

  const FEATURES = [
    { icon: Activity, path: '/diagnose', key: 'NAV.nav_diagnose', desc: 'Check your device health and get a longevity score' },
    { icon: Target, path: '/recommend', key: 'NAV.nav_recommend', desc: 'Find the best gadgets for your budget and needs' },
    { icon: CreditCard, path: '/emi-audit', key: 'NAV.nav_emi', desc: 'Uncover hidden EMI charges and true cost with GST' },
    { icon: TrendingUp, path: '/chipflation', key: 'NAV.nav_chipflation', desc: 'Track market pricing pressure and chip shortage impact' },
    { icon: Zap, path: '/full-decision', key: 'NAV.nav_decision', desc: 'Run all engines at once for a complete recommendation' },
    { icon: LayoutDashboard, path: '/dashboard', key: 'NAV.nav_dashboard', desc: 'Track all your decisions and scores in one place' },
    { icon: BarChart3, path: '/trends', key: 'NAV.nav_trends', desc: 'See popular products and market trends by region' },
  ];

  return (
    <div>
      {/* Hero Banner */}
      <div className="gradient-banner" style={{ marginBottom: 'var(--spacing-8)', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
        <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)', marginBottom: 8, letterSpacing: '-0.02em', position: 'relative', zIndex: 2 }}>
          {t('HOME.home_title')}
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: 600, margin: '0 auto var(--spacing-6)', lineHeight: 1.7, whiteSpace: 'pre-line', position: 'relative', zIndex: 2 }}>
          {t('HOME.home_subtitle')}
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--spacing-4)', flexWrap: 'wrap', position: 'relative', zIndex: 2 }}>
          <Button
            variant="primary"
            size="lg"
            onClick={() => navigate('/diagnose')}
          >
            {t('HOME.home_cta_diagnose')}
          </Button>
          <Button
            variant="outline"
            size="lg"
            onClick={() => navigate('/recommend')}
          >
            {t('HOME.home_cta_find')}
          </Button>
        </div>
        {/* Animated decorative element */}
        <div style={{ position: 'absolute', top: -20, right: -20, width: 120, height: 120, background: 'rgba(217,119,6,0.03)', borderRadius: '50%', animation: 'float 6s ease-in-out infinite' }}></div>
      </div>

      {/* Statistics Cards */}
      <div style={{ marginBottom: 'var(--spacing-8)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 'var(--spacing-4)' }}>
          <Card interactive onClick={() => navigate('/diagnose')}>
            <div style={{ textAlign: 'center' }}>
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
          </Card>
          <Card interactive onClick={() => navigate('/trends')}>
            <div style={{ textAlign: 'center' }}>
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
          </Card>
          <Card interactive onClick={() => navigate('/emi-audit')}>
            <div style={{ textAlign: 'center' }}>
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
          </Card>
          <Card interactive onClick={() => navigate('/chipflation')}>
            <div style={{ textAlign: 'center' }}>
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
          </Card>
        </div>
      </div>

      {/* Chipflation Trend Chart */}
      <div className="card" style={{ marginBottom: 'var(--spacing-8)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-4)' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)', margin: 0 }}>
            {t('HOME.home_chipflation_trend')}
          </h3>
          <Button variant="outline" size="sm" onClick={() => navigate('/chipflation')}>
            {t('HOME.home_view_all')}
            <TrendingUpIcon size={16} style={{ marginLeft: 4 }} />
          </Button>
        </div>
        <div style={{ height: 200 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" tick={false} />
              <YAxis tick={false} />
              <Tooltip formatter={(value) => `${value.toFixed(2)}`} />
              <Legend verticalAlign="top" height={36} />
              <Line type="monotone" dataKey="value" stroke="var(--primary)" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Core Engines */}
      <div>
        <div className="section-divider" style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', textAlign: 'center', marginBottom: 'var(--spacing-6)' }}>
          {t('HOME.home_core_title')}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--spacing-6)' }}>
          {/* Device Diagnosis Card */}
          <Card interactive onClick={() => navigate('/diagnose')}>
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '200px' }}>
              <div>
                <div style={{ width: 56, height: 56, borderRadius: 'var(--radius-lg)', background: 'rgba(217,119,6,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--spacing-3)' }}>
                  <Activity size={28} color="var(--primary)" />
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)', marginBottom: 'var(--spacing-2)' }}>
                  {t('HOME.home_device_diagnosis_title')}
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6, flexGrow: 1 }}>
                  {t('HOME.home_device_diagnosis_desc')}
                </p>
              </div>
              <a href="/diagnose" onClick={(e) => { e.preventDefault(); navigate('/diagnose'); }} style={{ alignSelf: 'flex-end', color: 'var(--primary)', fontWeight: 600, textDecoration: 'none', fontSize: '0.875rem' }}>
                {t('HOME.home_learn_more')}
                <ZapIcon size={16} style={{ marginLeft: 4 }} />
              </a>
            </div>
          </Card>
          {/* Smart Recommendations Card */}
          <Card interactive onClick={() => navigate('/recommend')}>
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '200px' }}>
              <div>
                <div style={{ width: 56, height: 56, borderRadius: 'var(--radius-lg)', background: 'rgba(217,119,6,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--spacing-3)' }}>
                  <Target size={28} color="var(--primary)" />
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)', marginBottom: 'var(--spacing-2)' }}>
                  {t('HOME.home_smart_recommendations_title')}
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6, flexGrow: 1 }}>
                  {t('HOME.home_smart_recommendations_desc')}
                </p>
              </div>
              <a href="/recommend" onClick={(e) => { e.preventDefault(); navigate('/recommend'); }} style={{ alignSelf: 'flex-end', color: 'var(--primary)', fontWeight: 600, textDecoration: 'none', fontSize: '0.875rem' }}>
                {t('HOME.home_learn_more')}
                <TrendingUpIcon size={16} style={{ marginLeft: 4 }} />
              </a>
            </div>
          </Card>
          {/* EMI Audit Card */}
          <Card interactive onClick={() => navigate('/emi-audit')}>
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '200px' }}>
              <div>
                <div style={{ width: 56, height: 56, borderRadius: 'var(--radius-lg)', background: 'rgba(217,119,6,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--spacing-3)' }}>
                  <CreditCard size={28} color="var(--primary)" />
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)', marginBottom: 'var(--spacing-2)' }}>
                  {t('HOME.home_emi_audit_title')}
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6, flexGrow: 1 }}>
                  {t('HOME.home_emi_audit_desc')}
                </p>
              </div>
              <a href="/emi-audit" onClick={(e) => { e.preventDefault(); navigate('/emi-audit'); }} style={{ alignSelf: 'flex-end', color: 'var(--primary)', fontWeight: 600, textDecoration: 'none', fontSize: '0.875rem' }}>
                {t('HOME.home_learn_more')}
                <ZapIcon size={16} style={{ marginLeft: 4 }} />
              </a>
            </div>
          </Card>
          {/* Full Decision Card */}
          <Card interactive onClick={() => navigate('/full-decision')}>
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '200px' }}>
              <div>
                <div style={{ width: 56, height: 56, borderRadius: 'var(--radius-lg)', background: 'rgba(217,119,6,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--spacing-3)' }}>
                  <Zap size={28} color="var(--primary)" />
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)', marginBottom: 'var(--spacing-2)' }}>
                  {t('HOME.home_full_decision_title')}
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6, flexGrow: 1 }}>
                  {t('HOME.home_full_decision_desc')}
                </p>
              </div>
              <a href="/full-decision" onClick={(e) => { e.preventDefault(); navigate('/full-decision'); }} style={{ alignSelf: 'flex-end', color: 'var(--primary)', fontWeight: 600, textDecoration: 'none', fontSize: '0.875rem' }}>
                {t('HOME.home_learn_more')}
                <LayoutDashboard size={16} style={{ marginLeft: 4 }} />
              </a>
            </div>
          </Card>
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