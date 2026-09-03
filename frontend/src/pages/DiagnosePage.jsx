import React, { useState } from 'react';
import apiClient from '../api/client';

const CATEGORIES = ['mobile', 'laptop', 'audio', 'video', 'memory', 'wearable'];

const CATEGORY_DEFAULTS = {
  mobile:   { battery: 72, storage: 85, physical: 0.85, age: 42, eol: 60, lifespan: 5 },
  laptop:   { battery: 55, storage: 70, physical: 0.70, age: 60, eol: 72, lifespan: 6 },
  audio:    { battery: 80, storage: 95, physical: 0.90, age: 24, eol: 60, lifespan: 5 },
  video:    { battery: 99, storage: 99, physical: 0.80, age: 72, eol: 96, lifespan: 8 },
  memory:   { battery: 99, storage: 82, physical: 0.95, age: 36, eol: 84, lifespan: 7 },
  wearable: { battery: 65, storage: 90, physical: 0.75, age: 36, eol: 48, lifespan: 4 },
};

function barColor(pct) {
  if (pct >= 70) return '#22c55e';
  if (pct >= 40) return '#eab308';
  return '#ef4444';
}

function verdictBadge(decision) {
  if (decision === 'HOLD_CURRENT_DEVICE')    return { cls: 'badge-green',  icon: '✅', label: 'Hold Current Device' };
  if (decision === 'CONSIDER_REPLACEMENT')   return { cls: 'badge-yellow', icon: '⚠️', label: 'Consider Replacement' };
  return                                            { cls: 'badge-red',    icon: '🔴', label: 'Replace Immediately' };
}

export default function DiagnosePage() {
  const [form, setForm] = useState({
    category: 'mobile',
    age_months: 42,
    battery_health_pct: 72,
    storage_health_pct: 85,
    physical_condition: 0.85,
    eol_months: 60,
    max_lifespan_years: 5,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function setField(key, val) {
    setForm(f => ({ ...f, [key]: val }));
  }

  function onCategoryChange(cat) {
    const d = CATEGORY_DEFAULTS[cat];
    setForm({
      category: cat,
      age_months: d.age,
      battery_health_pct: d.battery,
      storage_health_pct: d.storage,
      physical_condition: d.physical,
      eol_months: d.eol,
      max_lifespan_years: d.lifespan,
    });
    setResult(null);
  }

  async function run() {
    setLoading(true); setError(null);
    try {
      const { data } = await apiClient.deviceLongevity(form);
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }

  const vb = result ? verdictBadge(result.decision) : null;

  return (
    <div>
      <div className="page-header">
        <h1>🔋 Device Diagnosis</h1>
        <p>Module 6 — Useful Remaining Life (URL) Calculator</p>
      </div>

      <div className="card-grid">
        {/* Left: Input form */}
        <div>
          <div className="card">
            <div className="card-title">Device Telemetry Input</div>

            {/* Category selector */}
            <div className="field">
              <label>Device Category</label>
              <select value={form.category} onChange={e => onCategoryChange(e.target.value)}>
                {CATEGORIES.map(c => (
                  <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
                ))}
              </select>
            </div>

            <div className="card-grid">
              <div className="field">
                <label>Device Age (months)</label>
                <input type="number" min={0} max={240}
                  value={form.age_months}
                  onChange={e => setField('age_months', +e.target.value)} />
              </div>
              <div className="field">
                <label>OS/EOL Limit (months)</label>
                <input type="number" min={12} max={120}
                  value={form.eol_months}
                  onChange={e => setField('eol_months', +e.target.value)} />
              </div>
              <div className="field">
                <label>Max Lifespan (years)</label>
                <input type="number" min={1} max={15} step={0.5}
                  value={form.max_lifespan_years}
                  onChange={e => setField('max_lifespan_years', +e.target.value)} />
              </div>
            </div>

            {/* Sliders */}
            {[
              { key: 'battery_health_pct',  label: 'Battery Health',        max: 100, unit: '%',   display: v => `${v}%` },
              { key: 'storage_health_pct',  label: 'Storage Health (TBW)',   max: 100, unit: '%',   display: v => `${v}%` },
              { key: 'physical_condition',  label: 'Physical Condition',     max: 1,   unit: '',    display: v => `${(v * 100).toFixed(0)}%`, step: 0.01 },
            ].map(s => (
              <div className="field" key={s.key}>
                <label>{s.label}</label>
                <div className="slider-wrap">
                  <input
                    type="range" min={0} max={s.max} step={s.step || 1}
                    value={form[s.key]}
                    onChange={e => setField(s.key, +e.target.value)}
                  />
                  <span className="slider-val">{s.display(form[s.key])}</span>
                </div>
              </div>
            ))}

            {error && <div className="alert alert-red"><span className="alert-icon">⚠️</span>{error}</div>}

            <button className="btn btn-primary" onClick={run} disabled={loading} style={{ width: '100%', justifyContent: 'center', marginTop: 4 }}>
              {loading ? <><span className="btn-spinner" /> Calculating…</> : '⚡ Calculate URL Score'}
            </button>
          </div>

          {/* Formula reference */}
          <div className="card">
            <div className="card-title">URL Score Formula</div>
            <div style={{ fontFamily: 'monospace', fontSize: 12, color: 'var(--text-muted)', lineHeight: 2 }}>
              URL = (0.35 × BH + 0.25 × SH + 0.25 × AgeFactor + 0.15 × Phys) × 100<br />
              <br />
              BH = Battery Health / 100<br />
              SH = Storage Health / 100<br />
              AgeFactor = 1 − (Age / EOL)<br />
              Phys = Physical Condition (0–1)
            </div>
            <div className="alert alert-blue" style={{ marginTop: 12 }}>
              <span className="alert-icon">ℹ️</span>
              <div>Score ≥ 60% → <strong>Hold device</strong>. Score &lt; 60% → plan replacement.</div>
            </div>
          </div>
        </div>

        {/* Right: Results */}
        <div>
          {result ? (
            <>
              <div className="card">
                <div className="card-title">Diagnosis Result</div>
                <div style={{ display: 'flex', gap: 16, marginBottom: 16, flexWrap: 'wrap' }}>
                  <div className="stat-box" style={{ flex: 1, minWidth: 120 }}>
                    <div className="stat-label">URL Score</div>
                    <div className="stat-value" style={{ color: barColor(result.url_score_pct) }}>
                      {result.url_score_pct}%
                    </div>
                    <div className="stat-sub">threshold: 60%</div>
                  </div>
                  <div className="stat-box" style={{ flex: 1, minWidth: 120 }}>
                    <div className="stat-label">Years Remaining</div>
                    <div className="stat-value">{result.estimated_years_left}</div>
                    <div className="stat-sub">est. useful life</div>
                  </div>
                </div>

                <span className={`badge ${vb.cls}`} style={{ marginBottom: 16, display: 'inline-flex' }}>
                  {vb.icon} {vb.label}
                </span>

                {/* Component breakdown */}
                <div style={{ marginTop: 8 }}>
                  {[
                    ['Battery Health (w=0.35)',      result.component_scores.battery_pct],
                    ['Storage Health (w=0.25)',       result.component_scores.storage_pct],
                    ['Age Factor (w=0.25)',           result.component_scores.age_factor_pct],
                    ['Physical Condition (w=0.15)',   result.component_scores.physical_pct],
                  ].map(([label, val]) => (
                    <div className="progress-row" key={label}>
                      <span className="progress-label">{label}</span>
                      <div className="progress-track">
                        <div className="progress-fill"
                          style={{ width: `${val}%`, background: barColor(val) }} />
                      </div>
                      <span className="progress-pct" style={{ color: barColor(val) }}>{val}%</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className={`alert ${result.decision === 'HOLD_CURRENT_DEVICE' ? 'alert-green' : result.decision === 'CONSIDER_REPLACEMENT' ? 'alert-yellow' : 'alert-red'}`}>
                <span className="alert-icon">{vb.icon}</span>
                <div>
                  <strong>Maintenance Recommendation</strong><br />
                  {result.maintenance_advice}
                </div>
              </div>

              {/* Next step prompt */}
              <div className="card" style={{ marginTop: 4 }}>
                <div className="card-title">What Next?</div>
                {result.decision !== 'HOLD_CURRENT_DEVICE' ? (
                  <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.7 }}>
                    Your device needs replacement. Head to{' '}
                    <a href="/recommend">Find Gadgets</a> to get matched recommendations,
                    then check <a href="/emi-audit">EMI Audit</a> before financing.
                  </div>
                ) : (
                  <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.7 }}>
                    Your device is still viable. Check the{' '}
                    <a href="/chipflation">Chipflation Index</a> to see if current
                    market conditions are worth upgrading anyway.
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="card" style={{ minHeight: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 12, color: 'var(--text-muted)' }}>
              <div style={{ fontSize: 48 }}>🔋</div>
              <div style={{ fontWeight: 600 }}>Enter device telemetry and run the diagnosis</div>
              <div style={{ fontSize: 12 }}>Results will appear here</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
