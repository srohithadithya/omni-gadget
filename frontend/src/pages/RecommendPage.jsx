import React, { useState } from 'react';
import apiClient from '../api/client';

const CATEGORIES = ['mobile', 'laptop', 'audio', 'video', 'memory', 'wearable'];

const USE_CASES = {
  mobile:   ['gaming', 'daily_tasks', 'multitasking', 'photography'],
  laptop:   ['coding', 'data_science', 'video_editing', 'productivity'],
  audio:    ['anc', 'music', 'remote_work', 'travel'],
  video:    ['gaming', 'streaming', 'home_theater'],
  memory:   ['fast_storage', 'video_editing', 'gaming'],
  wearable: ['fitness', 'health_tracking', 'daily_use'],
};

const BUDGET_PRESETS = {
  mobile:   [15000, 25000, 40000, 70000],
  laptop:   [35000, 55000, 75000, 110000],
  audio:    [3000, 7000, 15000, 28000],
  video:    [30000, 55000, 85000, 130000],
  memory:   [3000, 6000, 9000, 15000],
  wearable: [5000, 12000, 20000, 30000],
};

function fmt(n) {
  return '₹' + Number(n).toLocaleString('en-IN');
}

function riskBadge(risk) {
  const map = {
    very_low: { cls: 'badge-green',  label: 'Very Low Risk' },
    low:      { cls: 'badge-green',  label: 'Low Risk' },
    medium:   { cls: 'badge-yellow', label: 'Medium Risk' },
    high:     { cls: 'badge-red',    label: 'High Inflation' },
  };
  return map[risk] || { cls: 'badge-blue', label: risk };
}

function valueBadge(vv) {
  const map = {
    GREAT_VALUE: { cls: 'badge-green',  label: '🏷 Great Value' },
    FAIR:        { cls: 'badge-blue',   label: '✔ Fair Price' },
    OVERPRICED:  { cls: 'badge-red',    label: '⚠ Overpriced' },
  };
  return map[vv] || { cls: 'badge-blue', label: vv };
}

function Stars({ n }) {
  const full = Math.floor(n);
  return (
    <span className="stars">
      {'★'.repeat(full)}{'☆'.repeat(5 - full)} {n}
    </span>
  );
}

function ProductCard({ match, label }) {
  const p = match.product;
  const vb = valueBadge(match.value_verdict);
  const rb = riskBadge(p.chipflation_risk);
  const isRefurb = label === 'refurbished';

  return (
    <div className="product-card">
      <div className="product-header">
        <div>
          <div className="product-name">{p.brand} {p.model_name}</div>
          <div className="product-brand">{p.tier?.replace(/-/g, ' ').toUpperCase()}</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="product-price">
            {fmt(isRefurb && p.refurb_price_inr ? p.refurb_price_inr : (p.display_price || p.price_inr))}
          </div>
          <div className="product-baseline">{fmt(p.baseline_inr)}</div>
        </div>
      </div>

      <div className="product-tags">
        <span className={`badge ${vb.cls}`} style={{ fontSize: 11 }}>{vb.label}</span>
        <span className={`badge ${rb.cls}`} style={{ fontSize: 11 }}>{rb.label}</span>
        {isRefurb && (
          <span className="badge badge-purple" style={{ fontSize: 11 }}>♻ Refurbished</span>
        )}
        {p.rating && <Stars n={p.rating} />}
        {p.review_count && (
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            {Number(p.review_count).toLocaleString()} reviews
          </span>
        )}
      </div>

      {p.display_spec && (
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>
          📐 {p.display_spec}
          {p.ram_gb ? `  •  💾 ${p.ram_gb}GB RAM` : ''}
          {p.storage_gb ? `  •  💿 ${p.storage_gb}GB Storage` : ''}
        </div>
      )}

      {(p.pros?.length > 0 || p.cons?.length > 0) && (
        <div className="pros-cons">
          <ul>
            {(p.pros || []).slice(0, 3).map(pr => <li key={pr}>{pr}</li>)}
          </ul>
          <ul>
            {(p.cons || []).slice(0, 2).map(c => <li key={c} className="con">{c}</li>)}
          </ul>
        </div>
      )}

      {isRefurb && p.refurb_source && (
        <div style={{ marginTop: 10, fontSize: 12, color: 'var(--text-muted)' }}>
          🛒 Available at: <strong style={{ color: 'var(--primary-light)' }}>{p.refurb_source || p.source}</strong>
        </div>
      )}
    </div>
  );
}

export default function RecommendPage() {
  const [form, setForm] = useState({
    category: 'mobile',
    use_case: 'gaming',
    max_budget_inr: 35000,
    min_ram_gb: '',
    min_storage_gb: '',
    prefer_refurbished: false,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function setField(k, v) { setForm(f => ({ ...f, [k]: v })); }

  function onCategoryChange(cat) {
    setForm(f => ({
      ...f, category: cat,
      use_case: USE_CASES[cat][0],
      max_budget_inr: BUDGET_PRESETS[cat][1],
    }));
    setResult(null);
  }

  async function run() {
    setLoading(true); setError(null);
    try {
      const payload = {
        ...form,
        min_ram_gb: form.min_ram_gb ? +form.min_ram_gb : null,
        min_storage_gb: form.min_storage_gb ? +form.min_storage_gb : null,
      };
      const { data } = await apiClient.recommend(payload);
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }

  const totalResults = result
    ? (result.primary?.length || 0) + (result.alternatives?.length || 0) + (result.refurbished?.length || 0)
    : 0;

  return (
    <div>
      <div className="page-header">
        <h1>🎯 Find Best Gadget</h1>
        <p>Modules 3 & 4 — Requirement-Based Recommender & Alternative Matcher</p>
      </div>

      <div className="card-grid">
        {/* Input */}
        <div>
          <div className="card">
            <div className="card-title">Your Requirements</div>

            <div className="field">
              <label>Device Category</label>
              <select value={form.category} onChange={e => onCategoryChange(e.target.value)}>
                {CATEGORIES.map(c => (
                  <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
                ))}
              </select>
            </div>

            <div className="field">
              <label>Primary Use Case</label>
              <select value={form.use_case} onChange={e => setField('use_case', e.target.value)}>
                {(USE_CASES[form.category] || []).map(u => (
                  <option key={u} value={u}>{u.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</option>
                ))}
              </select>
            </div>

            <div className="field">
              <label>Max Budget</label>
              <div className="slider-wrap">
                <input
                  type="range"
                  min={BUDGET_PRESETS[form.category][0]}
                  max={BUDGET_PRESETS[form.category][3]}
                  step={1000}
                  value={form.max_budget_inr}
                  onChange={e => setField('max_budget_inr', +e.target.value)}
                />
                <span className="slider-val">{fmt(form.max_budget_inr)}</span>
              </div>
              <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                {BUDGET_PRESETS[form.category].map(b => (
                  <button key={b}
                    className={`btn btn-outline`}
                    style={{
                      padding: '4px 10px', fontSize: 11,
                      background: form.max_budget_inr === b ? 'rgba(99,102,241,.15)' : '',
                      borderColor: form.max_budget_inr === b ? 'var(--primary)' : '',
                      color: form.max_budget_inr === b ? 'var(--primary-light)' : '',
                    }}
                    onClick={() => setField('max_budget_inr', b)}
                  >
                    {fmt(b)}
                  </button>
                ))}
              </div>
            </div>

            {['mobile', 'laptop'].includes(form.category) && (
              <div className="card-grid">
                <div className="field">
                  <label>Min RAM (GB) — optional</label>
                  <input type="number" min={2} max={64} placeholder="e.g. 8"
                    value={form.min_ram_gb}
                    onChange={e => setField('min_ram_gb', e.target.value)} />
                </div>
                <div className="field">
                  <label>Min Storage (GB) — optional</label>
                  <input type="number" min={32} max={2048} placeholder="e.g. 256"
                    value={form.min_storage_gb}
                    onChange={e => setField('min_storage_gb', e.target.value)} />
                </div>
              </div>
            )}

            <div className="field">
              <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={form.prefer_refurbished}
                  onChange={e => setField('prefer_refurbished', e.target.checked)}
                  style={{ width: 16, height: 16, accentColor: 'var(--primary)' }}
                />
                Prefer certified refurbished (lower cost)
              </label>
            </div>

            {error && <div className="alert alert-red"><span className="alert-icon">⚠️</span>{error}</div>}

            <button className="btn btn-primary" onClick={run} disabled={loading}
              style={{ width: '100%', justifyContent: 'center', marginTop: 4 }}>
              {loading ? <><span className="btn-spinner" /> Finding matches…</> : '🎯 Find Best Matches'}
            </button>
          </div>

          {/* Chipflation context for category */}
          <div className="card">
            <div className="card-title">Category Chipflation Risk</div>
            {(() => {
              const riskMap = {
                mobile:   { risk: 'HIGH', note: 'LPDDR5X mobile RAM costs up 15–20%' },
                laptop:   { risk: 'HIGH', note: 'DDR5 SO-DIMM & PCIe Gen4 SSD elevated by AI demand' },
                audio:    { risk: 'LOW',  note: 'Bluetooth SoCs stable; minor logistics cost increase' },
                video:    { risk: 'LOW',  note: 'Display panel yields stable; minor processor inflation' },
                memory:   { risk: 'HIGH', note: 'NAND flash elevated by enterprise AI server demand' },
                wearable: { risk: 'LOW',  note: 'Micro-AMOLED displays showing minor price shifts' },
              };
              const r = riskMap[form.category];
              return (
                <div className={`alert ${r.risk === 'HIGH' ? 'alert-red' : 'alert-green'}`}>
                  <span className="alert-icon">{r.risk === 'HIGH' ? '⚠️' : '✅'}</span>
                  <div>
                    <strong>{form.category.toUpperCase()} — {r.risk} CHIPFLATION RISK</strong><br />
                    {r.note}
                  </div>
                </div>
              );
            })()}
          </div>
        </div>

        {/* Results */}
        <div>
          {result ? (
            <>
              <div style={{ marginBottom: 12, color: 'var(--text-muted)', fontSize: 13 }}>
                Found <strong style={{ color: 'var(--text)' }}>{totalResults} matches</strong> for{' '}
                <strong style={{ color: 'var(--primary-light)' }}>
                  {form.use_case.replace(/_/g,' ')} under {fmt(form.max_budget_inr)}
                </strong>
              </div>

              {result.primary?.length > 0 && (
                <>
                  <div className="section-divider">🏆 Primary Recommendations</div>
                  {result.primary.map((m, i) => (
                    <ProductCard key={i} match={m} label="primary" />
                  ))}
                </>
              )}

              {result.alternatives?.length > 0 && (
                <>
                  <div className="section-divider">🔄 Alternatives</div>
                  {result.alternatives.map((m, i) => (
                    <ProductCard key={i} match={m} label="alternative" />
                  ))}
                </>
              )}

              {result.refurbished?.length > 0 && (
                <>
                  <div className="section-divider">♻️ Certified Refurbished / Open-Box</div>
                  {result.refurbished.map((m, i) => (
                    <ProductCard key={i} match={m} label="refurbished" />
                  ))}
                </>
              )}

              {totalResults === 0 && (
                <div className="alert alert-yellow">
                  <span className="alert-icon">⚠️</span>
                  <div>No matches found within your budget for this use case. Try increasing your budget or enabling refurbished options.</div>
                </div>
              )}
            </>
          ) : (
            <div className="card" style={{ minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 12, color: 'var(--text-muted)' }}>
              <div style={{ fontSize: 48 }}>🎯</div>
              <div style={{ fontWeight: 600 }}>Set your requirements and find matches</div>
              <div style={{ fontSize: 12 }}>Primary, alternative, and refurbished options will appear here</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
