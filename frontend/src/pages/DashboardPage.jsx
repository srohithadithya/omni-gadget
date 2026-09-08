import React, { useState, useEffect, useCallback } from 'react';
import {
  ClipboardList,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Activity,
  Zap,
  TrendingUp,
  RefreshCw,
  ArrowRight,
  BarChart3,
} from 'lucide-react';
import apiClient from '../api/client';
import { useI18n } from '../i18n';

const REFRESH_INTERVAL = 30000;

function verdictInfo(verdict, t) {
  if (verdict === 'HOLD_CURRENT_DEVICE')
    return { cls: 'badge-green', icon: <CheckCircle size={14} />, label: t('DASHBOARD.dash_hold') };
  if (verdict === 'CONSIDER_REPLACEMENT')
    return { cls: 'badge-yellow', icon: <AlertTriangle size={14} />, label: t('DASHBOARD.dash_consider') };
  if (verdict === 'BUY_NOW')
    return { cls: 'badge-red', icon: <XCircle size={14} />, label: t('DASHBOARD.dash_buy') };
  return { cls: 'badge-blue', icon: <ClipboardList size={14} />, label: verdict || 'N/A' };
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function barColor(pct) {
  if (pct >= 70) return '#22c55e';
  if (pct >= 40) return '#eab308';
  return '#ef4444';
}

export default function DashboardPage() {
  const { t } = useI18n();
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await apiClient.history();
      setHistory(res.data);
      setError(null);
      setLastRefresh(new Date());
    } catch (e) {
      // If the endpoint doesn't exist yet, show a graceful fallback
      if (e.response?.status === 404 || e.code === 'ERR_NETWORK') {
        setHistory({ decisions: [] });
      } else {
        setError(e.response?.data?.detail || e.message);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
    const id = setInterval(fetchHistory, REFRESH_INTERVAL);
    return () => clearInterval(id);
  }, [fetchHistory]);

  const decisions = history?.decisions || [];

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <ClipboardList size={24} />
              {t('DASHBOARD.dash_title')}
            </h1>
            <p>{t('DASHBOARD.dash_subtitle')}</p>
          </div>
          {lastRefresh && (
            <div style={{ fontSize: 11, color: 'var(--text-muted)', textAlign: 'right' }}>
              <div style={{ color: '#fbbf24', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}>
                <RefreshCw size={12} />
                {t('DASHBOARD.dash_auto_refresh')}
              </div>
              {t('DASHBOARD.dash_last_updated')}: {lastRefresh.toLocaleTimeString('en-IN')}
            </div>
          )}
        </div>
      </div>

      {loading ? (
        <div
          className="card"
          style={{
            minHeight: 200,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 12,
            color: 'var(--text-muted)',
          }}
        >
          <span
            className="btn-spinner"
            style={{ borderColor: 'rgba(251,191,36,.3)', borderTopColor: '#fbbf24' }}
          />
          {t('COMMON.loading')}
        </div>
      ) : error ? (
        <div className="alert alert-red">
          <span className="alert-icon">
            <AlertTriangle size={18} />
          </span>
          <div>
            <strong>{t('COMMON.error')}:</strong> {error}
          </div>
        </div>
      ) : decisions.length === 0 ? (
        <div
          className="card"
          style={{
            minHeight: 300,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            gap: 12,
            color: 'var(--text-muted)',
            background: 'linear-gradient(135deg, rgba(251,191,36,.06), rgba(217,119,6,.03))',
            border: '1px solid rgba(251,191,36,.15)',
          }}
        >
          <BarChart3 size={52} style={{ color: '#fbbf24' }} />
          <div style={{ fontWeight: 600, fontSize: 16 }}>{t('DASHBOARD.dash_no_history')}</div>
          <div style={{ fontSize: 13 }}>
            {t('DASHBOARD.dash_subtitle')}
          </div>
          <a
            href="/full-decision"
            className="btn btn-primary"
            style={{
              marginTop: 8,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: 'linear-gradient(135deg, #d97706, #b45309)',
            }}
          >
            <Zap size={16} />
            {t('DASHBOARD.dash_run_now')}
          </a>
        </div>
      ) : (
        <>
          {/* Summary stats */}
          <div className="card-grid four" style={{ marginBottom: 20 }}>
            <div className="stat-box" style={{ borderLeft: '3px solid #f59e0b' }}>
              <div className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <BarChart3 size={14} />
                {t('DASHBOARD.dash_total')}
              </div>
              <div className="stat-value" style={{ color: '#fbbf24', fontSize: 24 }}>
                {decisions.length}
              </div>
            </div>
            <div className="stat-box" style={{ borderLeft: '3px solid #22c55e' }}>
              <div className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <CheckCircle size={14} />
                {t('DASHBOARD.dash_hold')}
              </div>
              <div className="stat-value" style={{ color: '#22c55e', fontSize: 24 }}>
                {decisions.filter((d) => d.verdict === 'HOLD_CURRENT_DEVICE').length}
              </div>
            </div>
            <div className="stat-box" style={{ borderLeft: '3px solid #eab308' }}>
              <div className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <AlertTriangle size={14} />
                {t('DASHBOARD.dash_consider')}
              </div>
              <div className="stat-value" style={{ color: '#eab308', fontSize: 24 }}>
                {decisions.filter((d) => d.verdict === 'CONSIDER_REPLACEMENT').length}
              </div>
            </div>
            <div className="stat-box" style={{ borderLeft: '3px solid #ef4444' }}>
              <div className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <XCircle size={14} />
                {t('DASHBOARD.dash_buy')}
              </div>
              <div className="stat-value" style={{ color: '#ef4444', fontSize: 24 }}>
                {decisions.filter((d) => d.verdict === 'BUY_NOW').length}
              </div>
            </div>
          </div>

          {/* Decision cards */}
          <div className="section-divider" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Activity size={16} />
            {t('DASHBOARD.dash_history')}
          </div>
          {decisions.map((d, i) => {
            const vi = verdictInfo(d.verdict, t);
            return (
              <div
                key={d.id || i}
                className="card"
                style={{
                  borderLeft: '3px solid #d97706',
                  transition: 'border-color .15s',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#f59e0b')}
                onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border)')}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: 12,
                  }}
                >
                  <div>
                    <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 2 }}>
                      {formatDate(d.created_at || d.date)}
                    </div>
                    <div style={{ fontSize: 16, fontWeight: 700 }}>
                      {d.category
                        ? d.category.charAt(0).toUpperCase() + d.category.slice(1)
                        : 'Device'}{' '}
                      Decision
                    </div>
                  </div>
                  <span
                    className={`badge ${vi.cls}`}
                    style={{ fontSize: 11, display: 'flex', alignItems: 'center', gap: 4 }}
                  >
                    {vi.icon} {vi.label}
                  </span>
                </div>

                {/* Score grid */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                    gap: 12,
                    marginBottom: 12,
                  }}
                >
                  <div className="stat-box" style={{ padding: 10 }}>
                    <div className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <TrendingUp size={12} />
                      URL Score
                    </div>
                    <div className="stat-value" style={{ fontSize: 20, color: barColor(d.url_score || 0) }}>
                      {d.url_score != null ? `${d.url_score}%` : '—'}
                    </div>
                  </div>
                  <div className="stat-box" style={{ padding: 10 }}>
                    <div className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <Activity size={12} />
                      Decision Index
                    </div>
                    <div className="stat-value" style={{ fontSize: 20, color: '#fbbf24' }}>
                      {d.di_score != null ? d.di_score : '—'}
                    </div>
                  </div>
                  {d.total_emi_cost != null && (
                    <div className="stat-box" style={{ padding: 10 }}>
                      <div className="stat-label">EMI Total Cost</div>
                      <div className="stat-value" style={{ fontSize: 20, color: '#fca5a5' }}>
                        {t('COMMON.currency')}{Number(d.total_emi_cost).toLocaleString('en-IN')}
                      </div>
                    </div>
                  )}
                  {d.product_name && (
                    <div className="stat-box" style={{ padding: 10 }}>
                      <div className="stat-label">Product</div>
                      <div style={{ fontSize: 13, fontWeight: 600, marginTop: 4, color: 'var(--text)' }}>
                        {d.product_name}
                      </div>
                    </div>
                  )}
                </div>

                {/* Verdict detail */}
                {d.maintenance_advice && (
                  <div
                    style={{
                      fontSize: 12,
                      color: 'var(--text-muted)',
                      lineHeight: 1.6,
                      marginTop: 4,
                      paddingTop: 10,
                      borderTop: '1px solid var(--border)',
                    }}
                  >
                    {d.maintenance_advice}
                  </div>
                )}
              </div>
            );
          })}
        </>
      )}
    </div>
  );
}
