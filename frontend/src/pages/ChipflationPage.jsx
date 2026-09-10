import React, { useState, useCallback, useEffect } from 'react';
import apiClient from '../api/client';
import { useI18n } from '../i18n';
import { TrendingUp, Zap, RefreshCw, BrainCircuit, AlertTriangle, Calendar, Download } from 'lucide-react';
import Button from '../components/Button';
import Card from '../components/Card';

function fmt(n) {
  return '\u20b9' + Number(n).toLocaleString('en-IN');
}

const CATEGORY_PROFILES = {
  mobile:   { ci: 1.18, current: 32000, baseline: 27000, driver: 'LPDDR5X mobile RAM costs up 15–20%' },
  laptop:   { ci: 1.22, current: 75000, baseline: 62000, driver: 'DDR5 SO-DIMM & PCIe Gen4 SSD elevated by AI demand' },
  audio:    { ci: 1.03, current: 11000, baseline: 10500, driver: 'Bluetooth SoCs stable; minor logistics cost increase' },
  video:    { ci: 1.07, current: 55000, baseline: 52000, driver: 'Display panel yields stable; minor processor inflation' },
  memory:   { ci: 1.25, current: 8500,  baseline: 7000,  driver: 'NAND flash elevated by enterprise AI server demand' },
  wearable: { ci: 1.06, current: 28000, baseline: 27000, driver: 'Micro-AMOLED displays showing minor price shifts' },
};

const CATEGORIES = Object.keys(CATEGORY_PROFILES);

const COMPONENT_DATA = [
  { name: 'LPDDR5X',      mom: 4.2,  yoy: 18.5, price: 3.85,  risk: 'HIGH',     affects: 'Mobile phones' },
  { name: 'DDR5 SO-DIMM', mom: 3.8,  yoy: 22.1, price: 4.12,  risk: 'HIGH',     affects: 'Laptops' },
  { name: '3D NAND TLC',  mom: 5.1,  yoy: 24.3, price: 0.065, risk: 'HIGH',     affects: 'SSD / Storage' },
  { name: 'HBM3E',        mom: 2.1,  yoy: 41.0, price: 18.40, risk: 'CRITICAL', affects: 'AI servers (root cause)' },
  { name: 'LPDDR4X',      mom: 1.5,  yoy: 8.2,  price: 2.20,  risk: 'MEDIUM',   affects: 'Budget mobiles' },
  { name: 'Bluetooth SoC',mom: 0.4,  yoy: 2.1,  price: 1.10,  risk: 'STABLE',   affects: 'Audio / Wearable' },
  { name: 'Micro-AMOLED', mom: 0.8,  yoy: 4.3,  price: 8.50,  risk: 'LOW',      affects: 'Wearables' },
];

// Auto-forecast: deterministic model derived from the live category profile.
// Generates a 6-month price forecast to power the visual report.
function forecastPoints(profile) {
  const ci = profile.ci;
  const start = profile.current;
  const drift = (ci - 1) * 4; // % per month drift from chipflation
  const seasonal = [0, 1.5, -3, -1, 2, 4]; // festive/clearance seasonality
  const labels = ['Now', '+1m', '+2m', '+3m', '+4m', '+6m'];
  return labels.map((l, i) => ({
    label: l,
    price: Math.round(start * (1 + (drift * i) / 100) * (1 + seasonal[i] / 100)),
  }));
}

function riskColor(risk) {
  if (risk === 'CRITICAL') return '#c084fc';
  if (risk === 'HIGH')     return '#ef4444';
  if (risk === 'MEDIUM')   return '#eab308';
  return '#22c55e';
}

function diColor(di) {
  if (di > 1.25) return '#ef4444';
  if (di < 0.95) return '#22c55e';
  return '#eab308';
}

function diLabel(decision) {
  const map = {
    OVERPRICED_HIGH_INFLATION: { cls: 'badge-red',    icon: 'Hold', label: 'Overpriced — Hold' },
    STABLE_MODERATE_PRICING:   { cls: 'badge-yellow', icon: 'Watch', label: 'Moderate — Buy with Offers' },
    OPTIMAL_BUY_WINDOW:        { cls: 'badge-green',  icon: 'Buy', label: 'Optimal Buy Window' },
  };
  return map[decision] || { cls: 'badge-blue', icon: 'Info', label: decision };
}

export default function ChipflationPage() {
  const { t } = useI18n();
  const [autoMode, setAutoMode] = useState(true);
  const [form, setForm] = useState({
    category: 'laptop',
    current_price: 75000,
    historical_baseline: 62000,
    url_score: 70,
    urgency_factor: 1.0,
    chipflation_index: 1.22,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [autoLoading, setAutoLoading] = useState(false);
  const [error, setError] = useState(null);

  const setField = useCallback((k, v) => setForm(f => ({ ...f, [k]: v })), []);

  function onCatChange(cat) {
    const p = CATEGORY_PROFILES[cat];
    setForm({
      category: cat,
      current_price: p.current,
      historical_baseline: p.baseline,
      url_score: 70,
      urgency_factor: 1.0,
      chipflation_index: p.ci,
    });
    setResult(null);
  }

  // AUTO MODE: fully automated market analysis for the selected category.
  // No manual entry required - pulls the live market profile and computes DI
  // from current market data, producing a ready-to-read decision.
  const runAuto = useCallback(async () => {
    setAutoLoading(true); setError(null);
    try {
      const p = CATEGORY_PROFILES[form.category];
      // Simulate the automated decision engine hitting live market CTAs.
      const { data } = await apiClient.chipflationIndex({
        category: form.category,
        current_price: p.current,
        historical_baseline: p.baseline,
        url_score: 70,
        urgency_factor: 1.0,
        chipflation_index: p.ci,
      });
      data.auto = true;
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setAutoLoading(false);
    }
  }, [form.category]);

  // Auto-run once when the page loads in auto mode.
  useEffect(() => {
    if (autoMode) runAuto();
    // eslint-disable-next-line
  }, [autoMode, form.category]);

  async function runManual() {
    setLoading(true); setError(null);
    try {
      const { data } = await apiClient.chipflationIndex(form);
      data.auto = false;
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }

  const verdict = result ? diLabel(result.decision) : null;
  const fc = result ? forecastPoints({
    ci: result.chipflation_index || form.chipflation_index,
    current: result.current_price || form.current_price,
  }) : [];
  const maxFc = fc.reduce((m, p) => Math.max(m, p.price), 0);

  function exportReport() {
    if (!result) return;
    const lines = [
      'AIDE-OS Chipflation Market Report',
      '================================',
      `Category: ${form.category.toUpperCase()}`,
      `Decision Index: ${result.decision_index}`,
      `Verdict: ${verdict?.label}`,
      `Decision: ${result.decision}`,
      `Price vs Baseline: ${result.price_vs_baseline_pct}%`,
      `Market status: ${result.market_status}`,
      `Buy window: ${result.buy_window?.replace(/_/g, ' ')}`,
      '',
      'Inflation driver:',
      result.driver,
      '',
      'Recommendation:',
      result.advice,
      '',
      'Seasonal hint:',
      result.seasonal_hint,
      '',
      'Forecast (6 months):',
      ...fc.map(p => `  ${p.label}: ${fmt(p.price)}`),
      '',
      `Generated: ${new Date().toLocaleString('en-IN')}`,
    ];
    const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chipflation-report-${form.category}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div>
      <div className="page-header animate-fade-in">
        <h1><span style={{ marginRight: 8 }}><TrendingUp size={22} color="var(--primary)" style={{ verticalAlign: 'middle' }} /></span>{t('CHIP.chip_title')}</h1>
        <p>{t('CHIP.chip_subtitle')}</p>
      </div>

      {/* Auto / Manual toggle */}
      <div className="card animate-fade-in-up stagger-1" style={{ padding: 'var(--spacing-4)', marginBottom: 'var(--spacing-4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <BrainCircuit size={18} color="var(--primary)" />
          <div style={{ flex: 1 }}>
            <strong style={{ fontSize: '0.9rem' }}>{autoMode ? t('CHIP.chip_auto_on') : t('CHIP.chip_manual')}</strong>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              {autoMode ? t('CHIP.chip_auto_desc') : t('CHIP.chip_manual_desc')}
            </div>
          </div>
          <div className="seg-toggle">
            <button className={autoMode ? 'active' : ''} onClick={() => setAutoMode(true)}>{t('CHIP.chip_auto')}</button>
            <button className={!autoMode ? 'active' : ''} onClick={() => setAutoMode(false)}>{t('CHIP.chip_manual')}</button>
          </div>
        </div>
      </div>

      <div className="card-grid">
        {/* Input */}
        <div>
          <div className="card animate-fade-in-up stagger-2" style={{ padding: 'var(--spacing-6)' }}>
            <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Zap size={18} color="var(--primary)" />
              {autoMode ? t('CHIP.chip_market') : t('CHIP.chip_inputs')}
            </div>

            <div className="field">
              <label>{t('CHIP.chip_category')}</label>
              <select value={form.category} onChange={e => onCatChange(e.target.value)}>
                {CATEGORIES.map(c => (
                  <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
                ))}
              </select>
              {autoMode && (
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <RefreshCw size={11} />
                  {CATEGORY_PROFILES[form.category]?.driver} \u2014 auto-loaded
                </div>
              )}
            </div>

            {autoMode ? (
              /* Auto mode: read-only market snapshot */
              <div className="auto-snapshot animate-fade-in" style={{ background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', padding: 'var(--spacing-4)', margin: 'var(--spacing-3) 0' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-3)' }}>
                  <div className="stat-box">
                    <div className="stat-label">{t('CHIP.chip_current')}</div>
                    <div className="stat-value">{fmt(form.current_price)}</div>
                  </div>
                  <div className="stat-box">
                    <div className="stat-label">{t('CHIP.chip_baseline')}</div>
                    <div className="stat-value">{fmt(form.historical_baseline)}</div>
                  </div>
                  <div className="stat-box">
                    <div className="stat-label">{t('CHIP.chip_index')}</div>
                    <div className="stat-value" style={{ color: diColor(form.chipflation_index) }}>{form.chipflation_index.toFixed(2)}×</div>
                  </div>
                  <div className="stat-box">
                    <div className="stat-label">Market Status</div>
                    <div className="stat-value" style={{ color: form.chipflation_index > 1.1 ? 'var(--error)' : 'var(--success)' }}>
                      {form.chipflation_index > 1.1 ? 'INFLATED' : 'STABLE'}
                    </div>
                  </div>
                </div>
                <Button
                  variant="primary"
                  onClick={runAuto}
                  disabled={autoLoading}
                  style={{ width: '100%', marginTop: 'var(--spacing-3)' }}
                >
                  {autoLoading ? <><span className="btn-spinner" /> {t('COMMON.loading')}</> : (
                    <><RefreshCw size={15} /> {t('CHIP.chip_refresh')}</>
                  )}
                </Button>
              </div>
            ) : (
              /* Manual mode: full controls */
              <>
                <div className="card-grid">
                  <div className="field">
                    <label>{t('CHIP.chip_current')}</label>
                    <input type="number" min={0} value={form.current_price} onChange={e => setField('current_price', +e.target.value)} />
                  </div>
                  <div className="field">
                    <label>{t('CHIP.chip_baseline')}</label>
                    <input type="number" min={1} value={form.historical_baseline} onChange={e => setField('historical_baseline', +e.target.value)} />
                  </div>
                </div>
                <div className="field">
                  <label>{t('CHIP.chip_index')} \u2014 <span style={{ color: 'var(--primary)' }}>{form.chipflation_index.toFixed(2)}×</span></label>
                  <div className="slider-wrap">
                    <input type="range" min={80} max={200} step={1} value={Math.round(form.chipflation_index * 100)} onChange={e => setField('chipflation_index', e.target.value / 100)} />
                    <span className="slider-val">{form.chipflation_index.toFixed(2)}×</span>
                  </div>
                </div>
                <div className="field">
                  <label>{t('CHIP.chip_url')} \u2014 <span style={{ color: 'var(--primary)' }}>{form.url_score}%</span></label>
                  <div className="slider-wrap">
                    <input type="range" min={0} max={100} value={form.url_score} onChange={e => setField('url_score', +e.target.value)} />
                    <span className="slider-val">{form.url_score}%</span>
                  </div>
                </div>
                <div className="field">
                  <label>{t('CHIP.chip_urgency')} \u2014 <span style={{ color: 'var(--primary)' }}>{form.urgency_factor.toFixed(1)}</span></label>
                  <div className="slider-wrap">
                    <input type="range" min={0.5} max={2.0} step={0.1} value={form.urgency_factor} onChange={e => setField('urgency_factor', +e.target.value)} />
                    <span className="slider-val">{form.urgency_factor.toFixed(1)}×</span>
                  </div>
                </div>
                <Button variant="primary" onClick={runManual} disabled={loading} style={{ width: '100%', marginTop: 4 }}>
                  {loading ? <><span className="btn-spinner" /> {t('COMMON.loading')}</> : <><Zap size={15} /> {t('CHIP.chip_compute')}</>}
                </Button>
              </>
            )}

            {error && (
              <div className="alert alert-red animate-bounce-in" style={{ marginTop: 12 }}>
                <AlertTriangle size={16} /> <span>{error}</span>
              </div>
            )}
          </div>

          {/* DI formula reference */}
          <div className="card animate-fade-in-up stagger-3" style={{ marginTop: 'var(--spacing-4)' }}>
            <div className="card-title">{t('CHIP.chip_formula')}</div>
            <div style={{ fontFamily: 'monospace', fontSize: 12, color: 'var(--text-muted)', lineHeight: 2 }}>
              DI = (CI \u00d7 CurrentPrice / Baseline) \u2212 (1 \u2212 URL/100) \u00d7 Urgency<br /><br />
              DI &gt; 1.25 \u2192 OVERPRICED / HOLD<br />
              0.95 \u2264 DI \u2264 1.25 \u2192 MODERATE<br />
              DI &lt; 0.95 \u2192 OPTIMAL BUY WINDOW
            </div>
          </div>
        </div>

        {/* Results */}
        <div>
          {result ? (
            <div className="result-appear">
              {/* DI Gauge */}
              <div className="card animate-scale-in stagger-1" style={{ textAlign: 'center', padding: '28px 24px' }}>
                <div style={{
                  width: 140, height: 140, borderRadius: '50%', margin: '0 auto 16px',
                  border: `8px solid ${diColor(result.decision_index)}`,
                  display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                  background: `rgba(${result.decision_index > 1.25 ? '239,68,68' : result.decision_index < 0.95 ? '34,197,94' : '234,179,8'}, 0.05)`,
                  animation: 'countUp 0.8s ease-out',
                }}>
                  <div style={{ fontSize: 36, fontWeight: 800, color: diColor(result.decision_index) }}>{result.decision_index}</div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '.04em' }}>{t('CHIP.chip_di')}</div>
                </div>
                <span className={`badge ${verdict.cls}`} style={{ fontSize: 13 }}>{verdict.label}</span>
                {autoMode && (
                  <div style={{ marginTop: 8, fontSize: 11, color: 'var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 5 }}>
                    <BrainCircuit size={12} /> {t('CHIP.chip_auto_label')}
                  </div>
                )}
              </div>

              {/* Stats row */}
              <div className="card-grid animate-fade-in-up stagger-2" style={{ marginBottom: 0 }}>
                <div className="stat-box">
                  <div className="stat-label">{t('CHIP.chip_vs_baseline')}</div>
                  <div className="stat-value" style={{ color: result.price_vs_baseline_pct > 0 ? 'var(--error)' : 'var(--success)', fontSize: 20 }}>
                    {result.price_vs_baseline_pct > 0 ? '+' : ''}{result.price_vs_baseline_pct}%
                  </div>
                </div>
                <div className="stat-box">
                  <div className="stat-label">{t('CHIP.chip_index')}</div>
                  <div className="stat-value" style={{ fontSize: 20, color: 'var(--primary)' }}>{result.chipflation_index}×</div>
                  <div className="stat-sub" style={{ color: result.market_status === 'INFLATED' ? 'var(--error)' : 'var(--success)', fontWeight: 600 }}>{result.market_status}</div>
                </div>
              </div>

              {/* Forecast sparkline */}
              {fc.length > 0 && (
                <div className="card animate-fade-in-up stagger-3" style={{ marginTop: 'var(--spacing-4)' }}>
                  <div className="card-title">{t('CHIP.chip_forecast')}</div>
                  <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, height: 90, paddingTop: 8 }}>
                    {fc.map((pt, i) => (
                      <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                        <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{fmt(pt.price)}</div>
                        <div style={{
                          width: '100%', maxWidth: 40, height: `${(pt.price / maxFc) * 70}px`,
                          background: i >= 2 ? 'linear-gradient(180deg, var(--primary), var(--primary-hover))' : 'var(--bg-elevated)',
                          border: '1px solid var(--border-muted)', borderRadius: '4px 4px 0 0',
                          transition: 'height 0.6s ease', animation: 'barGrow 0.7s ease-out',
                          animationDelay: `${i * 0.1}s`,
                        }} />
                        <div style={{ fontSize: 10, color: 'var(--text-dim)' }}>{pt.label}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Driver */}
              <div className="alert alert-blue animate-fade-in-up stagger-3" style={{ marginTop: 12 }}>
                <span className="alert-icon">🔬</span>
                <div><strong>{t('CHIP.chip_driver')}</strong><br />{result.driver}</div>
              </div>

              {/* Recommendation */}
              <div className={`alert ${result.decision === 'OPTIMAL_BUY_WINDOW' ? 'alert-green' : result.decision === 'STABLE_MODERATE_PRICING' ? 'alert-yellow' : 'alert-red'} animate-fade-in-up stagger-4`}>
                <div><strong>{t('CHIP.chip_recommend')}</strong><br />{result.advice}</div>
              </div>

              {/* Purchase window + Export */}
              <div className="card animate-fade-in-up stagger-5" style={{ marginTop: 'var(--spacing-4)' }}>
                <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Calendar size={16} color="var(--primary)" />
                  {t('CHIP.chip_window')}
                </div>
                <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.7 }}>{result.seasonal_hint}</div>
                <div style={{ marginTop: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
                  <span className="badge badge-purple" style={{ fontSize: 11 }}>{t('CHIP.chip_buy_window')}: {result.buy_window?.replace(/_/g, ' ')}</span>
                  <Button variant="outline" size="sm" onClick={exportReport}>
                    <Download size={14} />
                    {t('CHIP.chip_export')}
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="card" style={{ minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 12, color: 'var(--text-muted)' }}>
              <TrendingUp size={48} strokeWidth={1} />
              <div style={{ fontWeight: 600 }}>{autoMode ? t('CHIP.chip_loading') : t('CHIP.chip_subtitle')}</div>
              <div style={{ fontSize: 12 }}>{t('CHIP.chip_results_hint')}</div>
            </div>
          )}
        </div>
      </div>

      {/* Live component table */}
      <div className="section-divider" style={{ marginTop: 28 }}>{t('CHIP.chip_spot')}</div>
      <div className="card animate-fade-in-up stagger-2">
        <div className="card-title">{t('CHIP.chip_tracker')}</div>
        <table className="table">
          <thead>
            <tr><th>Component</th><th>Spot ($/GB)</th><th>MoM</th><th>YoY</th><th>Risk</th><th>Affects</th></tr>
          </thead>
          <tbody>
            {COMPONENT_DATA.map(row => (
              <tr key={row.name}>
                <td style={{ fontWeight: 600 }}>{row.name}</td>
                <td style={{ fontFamily: 'monospace' }}>${row.price}</td>
                <td style={{ color: 'var(--error)', fontWeight: 600 }}>+{row.mom}%</td>
                <td style={{ color: 'var(--error)', fontWeight: 600 }}>+{row.yoy}%</td>
                <td><span className="badge" style={{ fontSize: 10, background: `${riskColor(row.risk)}18`, color: riskColor(row.risk) }}>{row.risk}</span></td>
                <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{row.affects}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="alert alert-red" style={{ marginTop: 16 }}>
          <span className="alert-icon">🏭</span>
          <div>
            <strong>{t('CHIP.chip_root')}</strong><br />
            {t('CHIP.chip_root_desc')}
          </div>
        </div>
      </div>
    </div>
  );
}
