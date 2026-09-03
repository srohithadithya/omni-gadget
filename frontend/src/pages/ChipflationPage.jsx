import React, { useState } from 'react';
import apiClient from '../api/client';

function fmt(n) {
  return '₹' + Number(n).toLocaleString('en-IN');
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

function riskColor(risk) {
  if (risk === 'CRITICAL') return '#c084fc';
  if (risk === 'HIGH')     return '#ef4444';
  if (risk === 'MEDIUM')   return '#eab308';
  if (risk === 'LOW')      return '#22c55e';
  return '#22c55e';
}

function diColor(di) {
  if (di > 1.25) return '#ef4444';
  if (di < 0.95) return '#22c55e';
  return '#eab308';
}

function diLabel(decision) {
  const map = {
    OVERPRICED_HIGH_INFLATION: { cls: 'badge-red',    icon: '🔴', label: 'Overpriced — Hold' },
    STABLE_MODERATE_PRICING:   { cls: 'badge-yellow', icon: '⚠️', label: 'Moderate — Buy with Offers' },
    OPTIMAL_BUY_WINDOW:        { cls: 'badge-green',  icon: '✅', label: 'Optimal Buy Window' },
  };
  return map[decision] || { cls: 'badge-blue', icon: 'ℹ️', label: decision };
}

export default function ChipflationPage() {
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
  const [error, setError] = useState(null);

  function setField(k, v) { setForm(f => ({ ...f, [k]: v })); }

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

  async function run() {
    setLoading(true); setError(null);
    try {
      const { data } = await apiClient.chipflationIndex(form);
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }

  const verdict = result ? diLabel(result.decision) : null;

  return (
    <div>
      <div className="page-header">
        <h1>📈 Chipflation Index</h1>
        <p>Module 2 — Dynamic Buy-vs-Hold Decision Index (DI)</p>
      </div>

      <div className="card-grid">
        {/* Input */}
        <div>
          <div className="card">
            <div className="card-title">Market Inputs</div>

            <div className="field">
              <label>Device Category</label>
              <select value={form.category} onChange={e => onCatChange(e.target.value)}>
                {CATEGORIES.map(c => (
                  <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
                ))}
              </select>
              <span style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                {CATEGORY_PROFILES[form.category]?.driver}
              </span>
            </div>

            <div className="card-grid">
              <div className="field">
                <label>Current Market Price (₹)</label>
                <input type="number" min={0} value={form.current_price}
                  onChange={e => setField('current_price', +e.target.value)} />
              </div>
              <div className="field">
                <label>Historical Baseline (₹)</label>
                <input type="number" min={1} value={form.historical_baseline}
                  onChange={e => setField('historical_baseline', +e.target.value)} />
              </div>
            </div>

            <div className="field">
              <label>
                Chipflation Index — <span style={{ color: 'var(--primary-light)' }}>{form.chipflation_index.toFixed(2)}×</span>
              </label>
              <div className="slider-wrap">
                <input type="range" min={80} max={200} step={1}
                  value={Math.round(form.chipflation_index * 100)}
                  onChange={e => setField('chipflation_index', e.target.value / 100)} />
                <span className="slider-val">{form.chipflation_index.toFixed(2)}×</span>
              </div>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                1.00 = no inflation, 1.20 = 20% component cost increase
              </span>
            </div>

            <div className="field">
              <label>
                Your Current Device URL Score — <span style={{ color: 'var(--primary-light)' }}>{form.url_score}%</span>
              </label>
              <div className="slider-wrap">
                <input type="range" min={0} max={100} value={form.url_score}
                  onChange={e => setField('url_score', +e.target.value)} />
                <span className="slider-val">{form.url_score}%</span>
              </div>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Use Device Diagnosis page to calculate your actual score
              </span>
            </div>

            <div className="field">
              <label>
                Urgency Factor — <span style={{ color: 'var(--primary-light)' }}>{form.urgency_factor.toFixed(1)}</span>
              </label>
              <div className="slider-wrap">
                <input type="range" min={0.5} max={2.0} step={0.1}
                  value={form.urgency_factor}
                  onChange={e => setField('urgency_factor', +e.target.value)} />
                <span className="slider-val">{form.urgency_factor.toFixed(1)}×</span>
              </div>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                1.0 = flexible, 2.0 = urgent need
              </span>
            </div>

            {error && <div className="alert alert-red"><span className="alert-icon">⚠️</span>{error}</div>}

            <button className="btn btn-primary" onClick={run} disabled={loading}
              style={{ width: '100%', justifyContent: 'center', marginTop: 4 }}>
              {loading ? <><span className="btn-spinner" />Computing…</> : '📊 Compute Decision Index'}
            </button>
          </div>

          {/* DI formula reference */}
          <div className="card">
            <div className="card-title">DI Formula</div>
            <div style={{ fontFamily: 'monospace', fontSize: 12, color: 'var(--text-muted)', lineHeight: 2 }}>
              DI = (CI × CurrentPrice / Baseline) − (1 − URL/100) × Urgency<br /><br />
              DI &gt; 1.25 → OVERPRICED / HOLD<br />
              0.95 ≤ DI ≤ 1.25 → MODERATE<br />
              DI &lt; 0.95 → OPTIMAL BUY WINDOW
            </div>
          </div>
        </div>

        {/* Results */}
        <div>
          {result ? (
            <>
              {/* DI Gauge */}
              <div className="card" style={{ textAlign: 'center', padding: '28px 24px' }}>
                <div style={{
                  width: 140, height: 140, borderRadius: '50%', margin: '0 auto 16px',
                  border: `8px solid ${diColor(result.decision_index)}`,
                  display: 'flex', flexDirection: 'column',
                  alignItems: 'center', justifyContent: 'center',
                  background: `rgba(${result.decision_index > 1.25 ? '239,68,68' : result.decision_index < 0.95 ? '34,197,94' : '234,179,8'}, 0.05)`,
                }}>
                  <div style={{ fontSize: 38, fontWeight: 800, color: diColor(result.decision_index) }}>
                    {result.decision_index}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '.04em' }}>
                    Decision Index
                  </div>
                </div>
                <span className={`badge ${verdict.cls}`} style={{ fontSize: 13 }}>
                  {verdict.icon} {verdict.label}
                </span>
              </div>

              {/* Stats row */}
              <div className="card-grid" style={{ marginBottom: 0 }}>
                <div className="stat-box">
                  <div className="stat-label">Price vs Baseline</div>
                  <div className="stat-value" style={{
                    color: result.price_vs_baseline_pct > 0 ? 'var(--danger)' : 'var(--success)',
                    fontSize: 22,
                  }}>
                    {result.price_vs_baseline_pct > 0 ? '+' : ''}{result.price_vs_baseline_pct}%
                  </div>
                  <div className="stat-sub">vs historical avg</div>
                </div>
                <div className="stat-box">
                  <div className="stat-label">Chipflation Index</div>
                  <div className="stat-value" style={{ fontSize: 22, color: 'var(--primary-light)' }}>
                    {result.chipflation_index}×
                  </div>
                  <div className="stat-sub" style={{
                    color: result.market_status === 'INFLATED' ? 'var(--danger)' : 'var(--success)',
                    fontWeight: 600,
                  }}>
                    {result.market_status}
                  </div>
                </div>
              </div>

              {/* Component driver */}
              <div className="alert alert-blue" style={{ marginTop: 12 }}>
                <span className="alert-icon">🔬</span>
                <div>
                  <strong>Inflation Driver</strong><br />
                  {result.driver}
                </div>
              </div>

              {/* Advice */}
              <div className={`alert ${result.decision === 'OPTIMAL_BUY_WINDOW' ? 'alert-green' : result.decision === 'STABLE_MODERATE_PRICING' ? 'alert-yellow' : 'alert-red'}`}>
                <span className="alert-icon">{verdict.icon}</span>
                <div>
                  <strong>Recommendation</strong><br />
                  {result.advice}
                </div>
              </div>

              {/* Seasonal hint */}
              <div className="card">
                <div className="card-title">🗓 Optimal Purchase Window</div>
                <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.7 }}>
                  {result.seasonal_hint}
                </div>
                <div style={{ marginTop: 12 }}>
                  <span className="badge badge-purple" style={{ fontSize: 11 }}>
                    Buy Window: {result.buy_window.replace(/_/g, ' ')}
                  </span>
                </div>
              </div>
            </>
          ) : (
            <div className="card" style={{ minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 12, color: 'var(--text-muted)' }}>
              <div style={{ fontSize: 48 }}>📈</div>
              <div style={{ fontWeight: 600 }}>Set category and prices to compute DI</div>
              <div style={{ fontSize: 12 }}>Results will appear here</div>
            </div>
          )}
        </div>
      </div>

      {/* Live component table always visible */}
      <div className="section-divider" style={{ marginTop: 28 }}>Semiconductor Spot Market — Sep 2026</div>
      <div className="card">
        <div className="card-title">Component Inflation Tracker (Source: TrendForce / DRAMeXchange)</div>
        <table className="table">
          <thead>
            <tr>
              <th>Component</th>
              <th>Spot Price ($/GB)</th>
              <th>MoM</th>
              <th>YoY</th>
              <th>Risk</th>
              <th>Affects</th>
            </tr>
          </thead>
          <tbody>
            {COMPONENT_DATA.map(row => (
              <tr key={row.name}>
                <td style={{ fontWeight: 600 }}>{row.name}</td>
                <td style={{ fontFamily: 'monospace' }}>${row.price}</td>
                <td style={{ color: 'var(--danger)', fontWeight: 600 }}>+{row.mom}%</td>
                <td style={{ color: 'var(--danger)', fontWeight: 600 }}>+{row.yoy}%</td>
                <td>
                  <span className="badge" style={{
                    fontSize: 10,
                    background: `${riskColor(row.risk)}18`,
                    color: riskColor(row.risk),
                  }}>
                    {row.risk}
                  </span>
                </td>
                <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{row.affects}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="alert alert-red" style={{ marginTop: 16 }}>
          <span className="alert-icon">🏭</span>
          <div>
            <strong>Root Cause — AI Infrastructure Cycle</strong><br />
            TSMC, SK Hynix, and Micron are prioritising HBM3E and enterprise AI chip production over
            consumer-grade DRAM and NAND flash. New fab capacity takes 2–3 years to come online,
            leaving short-term supply structurally inelastic. Consumer electronics price inflation
            is expected to persist through Q1 2027.
          </div>
        </div>
      </div>
    </div>
  );
}
