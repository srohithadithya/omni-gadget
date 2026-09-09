import React, { useState, useCallback, useEffect } from 'react';
import { useI18n } from '../i18n';
import apiClient from '../api/client';
import {
  Cpu, Scan, Settings, Battery, HardDrive, Smartphone, AlertTriangle, CheckCircle,
  Activity, Target, CreditCard, TrendingUp, Zap, LayoutDashboard, BarChart3, Monitor, MousePointer, Scroll,
  Zap as ZapIcon, TrendingUp as TrendingUpIcon
} from 'lucide-react';
import Button from '../components/Button';
import Card from '../components/Card';
import ProgressCircle from '../components/ProgressCircle';

const USAGES = ['gaming', 'daily_tasks', 'multitasking', 'photography', 'coding', 'data_science', 'video_editing', 'productivity', 'music', 'remote_work'];

// Auto-detect device from browser navigator
function autoDetectDevice() {
  const ua = navigator.userAgent || '';
  const platform = navigator.platform || '';

  let brand = 'Unknown', model = 'Unknown', category = 'mobile';
  let os = 'Unknown', osVersion = '', screenSize = '';

  // Detect OS
  if (/Windows/i.test(ua)) { os = 'Windows'; osVersion = ua.match(/Windows NT (\d+\.\d+)/)?.[1] || ''; }
  else if (/Mac/i.test(ua)) { os = 'macOS'; category = 'laptop'; }
  else if (/Linux/i.test(ua)) { os = 'Linux'; category = 'laptop'; }
  else if (/Android/i.test(ua)) {
    os = 'Android';
    osVersion = ua.match(/Android (\d+[\.\d]*)/)?.[1] || '';
    const m = ua.match(/;\s*([^;)]+)\s*Build/);
    brand = m?.[1]?.trim() || 'Android Device';
  }
  else if (/iPhone|iPad/i.test(ua)) {
    os = 'iOS';
    if (/iPad/i.test(ua)) { category = 'tablet'; brand = 'Apple'; model = 'iPad'; }
    else { brand = 'Apple'; model = 'iPhone'; }
    osVersion = ua.match(/OS (\d+_\d+)/)?.[1]?.replace('_', '.') || '';
  }

  // Detect brand from UA
  if (/Samsung/i.test(ua)) brand = 'Samsung';
  else if (/Pixel/i.test(ua)) { brand = 'Google'; model = 'Pixel'; }
  else if (/OnePlus/i.test(ua)) brand = 'OnePlus';
  else if (/Xiaomi|Redmi|POCO/i.test(ua)) { brand = 'Xiaomi'; model = ua.match(/(Xiaomi|Redmi|POCO)\s*\w*/)?.[0] || 'Xiaomi'; }
  else if (/Realme/i.test(ua)) brand = 'Realme';
  else if (/Vivo/i.test(ua)) brand = 'Vivo';
  else if (/Oppo/i.test(ua)) brand = 'Oppo';
  else if (/Motorola|Moto/i.test(ua)) brand = 'Motorola';
  else if (/MacBook/i.test(ua)) { brand = 'Apple'; model = 'MacBook'; category = 'laptop'; }
  else if (/Dell/i.test(ua)) { brand = 'Dell'; category = 'laptop'; }
  else if (/HP|Hewlett/i.test(ua)) { brand = 'HP'; category = 'laptop'; }
  else if (/Lenovo/i.test(ua)) { brand = 'Lenovo'; category = 'laptop'; }
  else if (/ASUS|Asus/i.test(ua)) { brand = 'ASUS'; category = 'laptop'; }
  else if (/Acer/i.test(ua)) { brand = 'Acer'; category = 'laptop'; }

  // Screen info
  screenSize = `${screen.width}x${screen.height}`;

  // Connection info
  const connection = navigator.connection;
  const networkType = connection?.effectiveType || 'unknown';

  return {
    brand,
    model,
    category,
    os,
    osVersion,
    screenSize,
    networkType,
    touchSupport: 'ontouchstart' in window,
    deviceMemory: navigator.deviceMemory || null,
    hardwareConcurrency: navigator.hardwareConcurrency || null,
    userAgent: ua,
  };
}

export default function DiagnosePage() {
  const { t } = useI18n();
  const [form, setForm] = useState({
    battery: 75, storage: 80, physical: 0.85, age: 36, usage: 'daily_tasks',
    brand: '', model: '', category: 'mobile',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoDetected, setAutoDetected] = useState(null);
  const [isAutoMode, setIsAutoMode] = useState(false);

  // Run auto-detect on mount
  useEffect(() => {
    const detected = autoDetectDevice();
    setAutoDetected(detected);
  }, []);

  const useAutoDetect = useCallback(() => {
    if (!autoDetected) return;
    setIsAutoMode(true);
    setForm(f => ({
      ...f,
      brand: autoDetected.brand,
      model: autoDetected.model,
      category: autoDetected.category,
    }));
  }, [autoDetected]);

  const setField = useCallback((k, v) => setForm(f => ({ ...f, [k]: v })), []);

  const runDiagnosis = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await apiClient.diagnose({
        category: form.category,
        age_months: form.age,
        battery_health_pct: form.battery,
        storage_health_pct: form.storage,
        physical_condition: form.physical,
        usage_type: form.usage,
      });
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }, [form]);

  const healthColor = (score) => {
    if (score >= 80) return 'var(--success)';
    if (score >= 50) return 'var(--warning)';
    return 'var(--error)';
  };

  return (
    <div>
      <div className="page-header animate-fade-in">
        <h1>{t('DIAGNOSE.diag_title')}</h1>
        <p>{t('DIAGNOSE.diag_subtitle')}</p>
      </div>

      {/* Auto-detect banner */}
      {autoDetected && !isAutoMode && (
        <div className="auto-detect-banner animate-fade-in">
          <div className="detect-icon"><Scan size={18} /></div>
          <div className="detect-text" style={{ flex: 1 }}>
            <strong>{t('COMMON.auto_detected')}:</strong> {autoDetected.brand} {autoDetected.model} ({autoDetected.os} {autoDetected.osVersion})
            {autoDetected.screenSize && <span style={{ marginLeft: 8, opacity: 0.6 }}>{autoDetected.screenSize}</span>}
            {autoDetected.hardwareConcurrency && <span style={{ marginLeft: 8, opacity: 0.6 }}>{autoDetected.hardwareConcurrency} cores</span>}
          </div>
          <Button variant="primary" size="sm" onClick={useAutoDetect}>
            {t('DIAGNOSE.diag_auto')}
          </Button>
        </div>
      )}

      {/* Auto-detected info */}
      {isAutoMode && autoDetected && (
        <Card className="animate-scale-in" style={{ marginBottom: 'var(--spacing-4)', padding: 'var(--spacing-4)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <CheckCircle size={16} color="var(--success)" />
            <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{t('COMMON.auto_detected')}</span>
            <button
              onClick={() => setIsAutoMode(false)}
              style={{ marginLeft: 'auto', background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontSize: '0.78rem', fontFamily: 'inherit' }}
            >
              {t('COMMON.switch_to_manual')}
            </button>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: 8 }}>
            <div><span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>{t('DIAGNOSE.diag_brand')}</span><br/><strong>{autoDetected.brand}</strong></div>
            <div><span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>{t('DIAGNOSE.diag_model')}</span><br/><strong>{autoDetected.model || 'N/A'}</strong></div>
            <div><span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>OS</span><br/><strong>{autoDetected.os} {autoDetected.osVersion}</strong></div>
            {autoDetected.deviceMemory && <div><span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>RAM</span><br/><strong>{autoDetected.deviceMemory} GB</strong></div>}
          </div>
        </Card>
      )}

      <div className="card-grid">
        {/* Input Form */}
        <Card className="animate-fade-in-up stagger-1" style={{ padding: 'var(--spacing-6)' }}>
          <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Settings size={18} color="var(--primary)" />
            {t('DIAGNOSE.diag_manual')}
          </div>

          <div className="card-grid" style={{ marginBottom: 0 }}>
            <div className="field">
              <label>{t('DIAGNOSE.diag_brand')}</label>
              <input type="text" value={form.brand} onChange={e => setField('brand', e.target.value)} placeholder="e.g. Samsung, Apple" />
            </div>
            <div className="field">
              <label>{t('DIAGNOSE.diag_model')}</label>
              <input type="text" value={form.model} onChange={e => setField('model', e.target.value)} placeholder="e.g. Galaxy S24" />
            </div>
          </div>

          <div className="field">
            <label>{t('DIAGNOSE.diag_usage')}</label>
            <select value={form.usage} onChange={e => setField('usage', e.target.value)}>
              {USAGES.map(u => <option key={u} value={u}>{u.replace(/_/g, ' ')}</option>)}
            </select>
          </div>

          <div className="field">
            <label className="tooltip-wrap">
              {t('DIAGNOSE.diag_age')}
              <span className="tooltip-text">How many months you've owned this device</span>
            </label>
            <input type="number" min={0} max={240} value={form.age} onChange={e => setField('age', +e.target.value)} />
          </div>

          <div className="field">
            <label className="tooltip-wrap">
              {t('DIAGNOSE.diag_battery')}
              <span className="tooltip-text">Check in Settings > Battery or use a battery health app</span>
            </label>
            <div className="slider-wrap">
              <input type="range" min={0} max={100} value={form.battery} onChange={e => setField('battery', +e.target.value)} />
              <span className="slider-val" style={{ color: healthColor(form.battery) }}>{form.battery}%</span>
            </div>
          </div>

          <div className="field">
            <label className="tooltip-wrap">
              {t('DIAGNOSE.diag_storage')}
              <span className="tooltip-text">Available storage as percentage of total</span>
            </label>
            <div className="slider-wrap">
              <input type="range" min={0} max={100} value={form.storage} onChange={e => setField('storage', +e.target.value)} />
              <span className="slider-val" style={{ color: healthColor(form.storage) }}>{form.storage}%</span>
            </div>
          </div>

          <div className="field">
            <label className="tooltip-wrap">
              {t('DIAGNOSE.diag_physical')}
              <span className="tooltip-text">1.0 = brand new, 0.0 = heavily damaged. 0.85 = minor scratches</span>
            </label>
            <div className="slider-wrap">
              <input type="range" min={0} max={1} step={0.05} value={form.physical} onChange={e => setField('physical', +e.target.value)} />
              <span className="slider-val">{form.physical}</span>
            </div>
          </div>

          {error && (
            <div className="alert alert-red animate-bounce-in">
              <AlertTriangle size={16} />
              <span>{error}</span>
            </div>
          )}

          <Button
            variant="primary"
            onClick={runDiagnosis}
            disabled={loading}
            style={{ width: '100%' }}
          >
            {loading ? <><span className="btn-spinner" /> {t('COMMON.loading')}</> : (
              <><Cpu size={16} /> {t('DIAGNOSE.diag_run')}</>
            )}
          </Button>
        </Card>

        {/* Results */}
        <Card>
          {result ? (
            <>
              {/* Health Score Big Number */}
              <div className="card" style={{ textAlign: 'center', padding: 'var(--spacing-8)', marginBottom: 'var(--spacing-4)' }}>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>
                  {t('DIAGNOSE.diag_score')}
                </div>
                <ProgressCircle
                  value={result.url_score_pct}
                  size={120}
                  strokeWidth={12}
                  label={`${result.url_score_pct}%`}
                />
                <div style={{ marginTop: 12 }}>
                  <span className={`badge ${result.url_score_pct >= 70 ? 'badge-success' : result.url_score_pct >= 40 ? 'badge-warning' : 'badge-error'}`}>
                    {t(`DIAGNOSE.diag_${result.url_score_pct >= 70 ? 'excellent' : result.url_score_pct >= 50 ? 'good' : result.url_score_pct >= 30 ? 'fair' : 'poor'}`)}
                  </span>
                </div>
              </div>

              {/* Years left + advice */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-4)', marginBottom: 'var(--spacing-4)' }}>
                <Card className="stat-box">
                  <div className="stat-label">{t('DIAGNOSE.diag_years_left')}</div>
                  <div className="stat-value" style={{ color: 'var(--primary)' }}>{result.estimated_years_left} yr</div>
                </Card>
                <Card className="stat-box">
                  <div className="stat-label">{t('DIAGNOSE.diag_status')}</div>
                  <div className="stat-value" style={{
                    fontSize: 16,
                    color: result.url_score_pct >= 70 ? 'var(--success)' : result.url_score_pct >= 40 ? 'var(--warning)' : 'var(--error)',
                  }}>
                    {result.url_score_pct >= 70 ? t('DIAGNOSE.diag_excellent') : result.url_score_pct >= 50 ? t('DIAGNOSE.diag_good') : t('DIAGNOSE.diag_fair')}
                  </div>
                </Card>
              </div>

              {/* Advice */}
              {result.maintenance_advice && (
                <Card className="animate-fade-in-up stagger-2" style={{ marginTop: 'var(--spacing-4)' }}>
                  <div className="card-title">{t('DIAGNOSE.diag_advice')}</div>
                  <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.7 }}>
                    {result.maintenance_advice}
                  </div>
                </Card>
              )}
            </>
          ) : (
            <div className="card" style={{
              minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexDirection: 'column', gap: 12, color: 'var(--text-muted)',
            }}>
              <Smartphone size={48} strokeWidth={1} />
              <div style={{ fontWeight: 600 }}>{t('DIAGNOSE.diag_subtitle')}</div>
              <div style={{ fontSize: '0.82rem' }}>{t('DIAGNOSE.diag_auto')}</div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}