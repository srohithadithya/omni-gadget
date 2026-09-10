import React, { useState } from 'react';
import apiClient from '../api/client';
import { useI18n } from '../i18n';
import {
  Zap, CheckCircle, AlertTriangle, XCircle,
  Gauge, TrendingUp, CreditCard, Target,
  Battery, HardDrive, Smartphone, Monitor,
  Headphones, Film, MemoryStick, Watch,
  ArrowRight, ChevronRight, Loader2,
} from 'lucide-react';
import Button from '../components/Button';
import Card from '../components/Card';

const CATEGORIES = ['mobile', 'laptop', 'audio', 'video', 'memory', 'wearable'];

const CATEGORY_ICONS = {
  mobile: Smartphone,
  laptop: Monitor,
  audio: Headphones,
  video: Film,
  memory: MemoryStick,
  wearable: Watch,
};

const DEFAULTS = {
  mobile:   { age: 42, battery: 72, storage: 85, physical: 0.85, use: 'gaming', budget: 35000, price: 32000, baseline: 27000, tenure: 6, pfee: 299, forgone: 1500, discount: 2000 },
  laptop:   { age: 60, battery: 55, storage: 70, physical: 0.70, use: 'coding', budget: 75000, price: 68000, baseline: 60000, tenure: 12, pfee: 299, forgone: 2000, discount: 4500 },
  audio:    { age: 24, battery: 80, storage: 95, physical: 0.90, use: 'anc', budget: 15000, price: 11000, baseline: 10500, tenure: 6, pfee: 199, forgone: 500, discount: 800 },
  video:    { age: 72, battery: 99, storage: 99, physical: 0.80, use: 'streaming', budget: 85000, price: 55000, baseline: 52000, tenure: 12, pfee: 299, forgone: 1500, discount: 3500 },
  memory:   { age: 36, battery: 99, storage: 82, physical: 0.95, use: 'gaming', budget: 9000, price: 8500, baseline: 7000, tenure: 6, pfee: 199, forgone: 300, discount: 500 },
  wearable: { age: 36, battery: 65, storage: 90, physical: 0.75, use: 'fitness', budget: 20000, price: 14000, baseline: 13000, tenure: 6, pfee: 199, forgone: 500, discount: 800 },
};

function fmt(n) {
  return '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

function verdictStyle(v) {
  if (v === 'HOLD_CURRENT_DEVICE') return { cls: 'badge-green', Icon: CheckCircle, label: 'Hold Current Device' };
  if (v === 'BUY_NOW') return { cls: 'badge-green', Icon: CheckCircle, label: 'Buy Now' };
  if (v === 'BUY_WITH_BEST_OFFER') return { cls: 'badge-yellow', Icon: AlertTriangle, label: 'Buy With Best Offer' };
  return { cls: 'badge-red', Icon: XCircle, label: v?.replace(/_/g, ' ') || v };
}

export default function FullDecisionPage() {
  const { t } = useI18n();
  const [form, setForm] = useState({ ...DEFAULTS.mobile, category: 'mobile' });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function setField(k, v) { setForm(f => ({ ...f, [k]: v })); }

  function onCategoryChange(cat) {
    setForm({ ...DEFAULTS[cat], category: cat });
    setResult(null);
  }

  async function run() {
    setLoading(true); setError(null);
    try {
      const payload = {
        current_category: form.category,
        current_age_months: form.age,
        current_battery_health_pct: form.battery,
        current_storage_health_pct: form.storage,
        current_physical_condition: form.physical,
        target_use_case: form.use,
        max_budget_inr: form.budget,
        target_current_price: form.price,
        target_historical_baseline: form.baseline,
        emi_tenure_months: form.tenure,
        bank_processing_fee: form.pfee,
        forgone_cash_discount: form.forgone,
        no_cost_discount: form.discount,
      };
      const { data } = await apiClient.fullDecision(payload);
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }

  const vd = result ? verdictStyle(result.master_verdict) : null;
  const dl = result?.device_longevity;
  const ma = result?.market_analysis;
  const emi = result?.emi_audit;

  return (
    <div>
      <div className="page-header">
        <h1><Zap size={22} style={{ marginRight: 6, verticalAlign: 'middle' }} /> {t('DECISION.dec_title')}</h1>
        <p>{t('DECISION.dec_subtitle')}</p>
      </div>

      <div className="card-grid">
        {/* Input */}
        <div>
          <div className="card">
            <div className="card-title"><Gauge size={16} style={{ marginRight: 6, verticalAlign: 'middle' }} />{t('DECISION.dec_your_situation')}</div>

            <div className="field">
              <label>{t('DECISION.dec_current_device')}</label>
              <select value={form.category} onChange={e => onCategoryChange(e.target.value)}>
                {CATEGORIES.map(c => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
              </select>
            </div>

            <div className="section-divider"><HardDrive size={14} style={{ marginRight: 4, verticalAlign: 'middle' }} />{t('DECISION.dec_current_device')}</div>
            <div className="card-grid">
              <div className="field">
                <label>Age (months)</label>
                <input type="number" min={0} value={form.age} onChange={e => setField('age', +e.target.value)} />
              </div>
              <div className="field">
                <label><Battery size={13} style={{ marginRight: 3, verticalAlign: 'middle' }} />Battery Health %</label>
                <input type="number" min={0} max={100} value={form.battery} onChange={e => setField('battery', +e.target.value)} />
              </div>
              <div className="field">
                <label><HardDrive size={13} style={{ marginRight: 3, verticalAlign: 'middle' }} />Storage Health %</label>
                <input type="number" min={0} max={100} value={form.storage} onChange={e => setField('storage', +e.target.value)} />
              </div>
              <div className="field">
                <label>Physical (0-1)</label>
                <input type="number" min={0} max={1} step={0.05} value={form.physical} onChange={e => setField('physical', +e.target.value)} />
              </div>
            </div>

            <div className="section-divider"><Target size={14} style={{ marginRight: 4, verticalAlign: 'middle' }} />{t('DECISION.dec_target')}</div>
            <div className="card-grid">
              <div className="field">
                <label>Price (₹)</label>
                <input type="number" min={0} value={form.price} onChange={e => setField('price', +e.target.value)} />
              </div>
              <div className="field">
                <label>Historical Baseline (₹)</label>
                <input type="number" min={1} value={form.baseline} onChange={e => setField('baseline', +e.target.value)} />
              </div>
              <div className="field">
                <label>Budget (₹)</label>
                <input type="number" min={0} value={form.budget} onChange={e => setField('budget', +e.target.value)} />
              </div>
              <div className="field">
                <label>Use Case</label>
                <select value={form.use} onChange={e => setField('use', e.target.value)}>
                  {['gaming','daily_tasks','multitasking','photography','coding','data_science','video_editing','productivity','anc','music','remote_work','travel','streaming','home_theater','fitness','health_tracking','fast_storage'].map(u => (
                    <option key={u} value={u}>{u.replace(/_/g,' ')}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="section-divider"><CreditCard size={14} style={{ marginRight: 4, verticalAlign: 'middle' }} />{t('DECISION.dec_emi_details')}</div>
            <div className="card-grid">
              <div className="field">
                <label>Tenure (months)</label>
                <input type="number" min={1} max={60} value={form.tenure} onChange={e => setField('tenure', +e.target.value)} />
              </div>
              <div className="field">
                <label>Processing Fee (₹)</label>
                <input type="number" min={0} value={form.pfee} onChange={e => setField('pfee', +e.target.value)} />
              </div>
              <div className="field">
                <label>Forgone Discount (₹)</label>
                <input type="number" min={0} value={form.forgone} onChange={e => setField('forgone', +e.target.value)} />
              </div>
              <div className="field">
                <label>No-Cost Discount (₹)</label>
                <input type="number" min={0} value={form.discount} onChange={e => setField('discount', +e.target.value)} />
              </div>
            </div>

            {error && <div className="alert alert-red"><span className="alert-icon"><AlertTriangle size={16} /></span>{error}</div>}
            <Button variant="primary" onClick={run} disabled={loading}
              style={{ width: '100%', marginTop: 4 }}>
              {loading ? <><span className="btn-spinner" /> {t('DECISION.dec_running')}</> : <><Zap size={16} /> {t('DECISION.dec_run')}</>}
            </Button>
          </div>
        </div>

        {/* Results */}
        <div>
          {result ? (
            <>
              {/* Master Verdict */}
              <div className="card" style={{ textAlign: 'center', padding: '24px' }}>
                <div style={{ fontSize: 48, marginBottom: 8, display: 'flex', justifyContent: 'center' }}>
                  {vd && <vd.Icon size={48} color={vd.cls === 'badge-green' ? 'var(--success)' : vd.cls === 'badge-yellow' ? 'var(--warning)' : 'var(--danger)'} />}
                </div>
                <div style={{ fontSize: 22, fontWeight: 800, marginBottom: 8 }}>{result.master_verdict?.replace(/_/g, ' ')}</div>
                <span className={`badge ${vd.cls}`} style={{ fontSize: 13 }}>{vd.label}</span>
                <div style={{ marginTop: 12, fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.7, maxWidth: 400, margin: '12px auto 0' }}>
                  {result.master_advice}
                </div>
              </div>

              {/* Module Scores */}
              <div className="section-divider"><Gauge size={14} style={{ marginRight: 4, verticalAlign: 'middle' }} />{t('DECISION.dec_module')}</div>

              {/* URL */}
              {dl && (
                <div className="card">
                  <div className="card-title"><Battery size={16} style={{ marginRight: 6, verticalAlign: 'middle' }} />{t('DECISION.dec_score')} — URL</div>
                  <div className="card-grid">
                    <div className="stat-box">
                      <div className="stat-label">URL Score</div>
                      <div className="stat-value" style={{ color: dl.url_score_pct >= 60 ? 'var(--success)' : dl.url_score_pct >= 40 ? 'var(--warning)' : 'var(--danger)' }}>
                        {dl.url_score_pct}%
                      </div>
                    </div>
                    <div className="stat-box">
                      <div className="stat-label">Years Left</div>
                      <div className="stat-value">{dl.estimated_years_left} yr</div>
                    </div>
                  </div>
                  <div style={{ marginTop: 10, fontSize: 12, color: 'var(--text-muted)' }}>{dl.maintenance_advice}</div>
                </div>
              )}

              {/* DI */}
              {ma && (
                <div className="card">
                  <div className="card-title"><TrendingUp size={16} style={{ marginRight: 6, verticalAlign: 'middle' }} />Market Analysis (DI)</div>
                  <div className="card-grid">
                    <div className="stat-box">
                      <div className="stat-label">Decision Index</div>
                      <div className="stat-value" style={{ color: ma.decision_index > 1.25 ? 'var(--danger)' : ma.decision_index < 0.95 ? 'var(--success)' : 'var(--warning)' }}>
                        {ma.decision_index}
                      </div>
                    </div>
                    <div className="stat-box">
                      <div className="stat-label">Market Status</div>
                      <div className="stat-value" style={{ fontSize: 16, color: ma.market_status === 'INFLATED' ? 'var(--danger)' : 'var(--success)' }}>
                        {ma.market_status}
                      </div>
                    </div>
                  </div>
                  <div style={{ marginTop: 10, fontSize: 12, color: 'var(--text-muted)' }}>
                    Price vs baseline: <strong style={{ color: ma.price_vs_baseline_pct > 0 ? 'var(--danger)' : 'var(--success)' }}>
                      {ma.price_vs_baseline_pct > 0 ? '+' : ''}{ma.price_vs_baseline_pct}%
                    </strong> · CI: {ma.chipflation_index}×
                  </div>
                  <div style={{ marginTop: 6, fontSize: 11, color: 'var(--text-muted)' }}>{ma.seasonal_hint}</div>
                </div>
              )}

              {/* EMI */}
              {emi && (
                <div className="card">
                  <div className="card-title"><CreditCard size={16} style={{ marginRight: 6, verticalAlign: 'middle' }} />{t('DECISION.dec_emi_details')}</div>
                  <div className="card-grid">
                    <div className="stat-box">
                      <div className="stat-label">Hidden Charges</div>
                      <div className="stat-value" style={{ fontSize: 18, color: 'var(--danger)' }}>{fmt(emi.total_hidden_charges)}</div>
                    </div>
                    <div className="stat-box">
                      <div className="stat-label">True Outlay</div>
                      <div className="stat-value" style={{ fontSize: 18, color: 'var(--primary-light)' }}>{fmt(emi.true_effective_outlay)}</div>
                    </div>
                  </div>
                  <div style={{ marginTop: 10, fontSize: 12, color: 'var(--text-muted)' }}>{emi.advice}</div>
                </div>
              )}

              {/* Recommendations */}
              {result.recommendations && (
                <div className="card">
                  <div className="card-title"><Target size={16} style={{ marginRight: 6, verticalAlign: 'middle' }} />{t('DECISION.dec_verdict')}</div>
                  {result.recommendations.primary?.map((m, i) => (
                    <div key={i} className="product-card" style={{ marginBottom: 8 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <div>
                          <div style={{ fontWeight: 700 }}>{m.product.brand} {m.product.model_name || m.product.model}</div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{m.product.tier} · Match: {m.match_score}</div>
                        </div>
                        <div style={{ fontWeight: 800, color: 'var(--primary-light)' }}>{fmt(m.product.price_inr)}</div>
                      </div>
                    </div>
                  ))}
                  {result.recommendations.alternatives?.slice(0, 2).map((m, i) => (
                    <div key={i} className="product-card" style={{ marginBottom: 8 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <div>
                          <div style={{ fontWeight: 700 }}>{m.product.brand} {m.product.model_name || m.product.model}</div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{m.product.tier} · Match: {m.match_score}</div>
                        </div>
                        <div style={{ fontWeight: 800, color: 'var(--primary-light)' }}>{fmt(m.product.price_inr)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="card" style={{ minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 12, color: 'var(--text-muted)' }}>
              <div style={{ fontSize: 48 }}><Zap size={48} strokeWidth={1.5} /></div>
              <div style={{ fontWeight: 600 }}>Set your situation and run all 4 engines</div>
              <div style={{ fontSize: 12 }}>One click gives you the complete picture</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}