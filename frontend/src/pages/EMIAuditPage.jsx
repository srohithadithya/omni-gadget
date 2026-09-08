import React, { useState, useCallback } from 'react';
import { useI18n } from '../i18n';
import apiClient from '../api/client';
import { CreditCard, AlertTriangle, CheckCircle, Receipt, Banknote, Shield, Info } from 'lucide-react';

function fmt(n) {
  return '\u20b9' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

export default function EMIAuditPage() {
  const { t } = useI18n();
  const [form, setForm] = useState({
    price: 29999, tenure: 12, rate: 12, pfee: 999, cashDiscount: 2000, noCostDiscount: 1500,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showGST, setShowGST] = useState(false);
  const [gstRate, setGstRate] = useState(18);
  const [isBusiness, setIsBusiness] = useState(false);

  const setField = useCallback((k, v) => setForm(f => ({ ...f, [k]: v })), []);

  const runAudit = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const { data } = await apiClient.emiAudit({
        product_price: form.price,
        tenure_months: form.tenure,
        annual_rate_pct: form.rate,
        processing_fee: form.pfee,
        forgone_cash_discount: form.cashDiscount,
        no_cost_emi_hidden_discount: form.noCostDiscount,
      });
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }, [form]);

  // GST calculations (client-side)
  const gstAmount = result ? (result.true_effective_outlay || form.price) * gstRate / (100 + gstRate) : 0;
  const gstReturn = isBusiness ? gstAmount : 0;
  const effectiveAfterGST = result ? (result.true_effective_outlay || 0) - gstReturn : 0;

  return (
    <div>
      <div className="page-header animate-fade-in">
        <h1>{t('EMI.emi_title')}</h1>
        <p>{t('EMI.emi_subtitle')}</p>
      </div>

      <div className="card-grid">
        {/* Input */}
        <div className="card animate-fade-in-up stagger-1" style={{ padding: 'var(--spacing-6)' }}>
          <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <CreditCard size={18} color="var(--primary)" />
            {t('EMI.emi_breakdown')}
          </div>

          <div className="card-grid" style={{ marginBottom: 0 }}>
            <div className="field">
              <label className="tooltip-wrap">
                {t('EMI.emi_price')}
                <span className="tooltip-text">The sticker price of the product</span>
              </label>
              <input type="number" min={0} value={form.price} onChange={e => setField('price', +e.target.value)} />
            </div>
            <div className="field">
              <label className="tooltip-wrap">
                {t('EMI.emi_tenure')}
                <span className="tooltip-text">Number of monthly installments</span>
              </label>
              <input type="number" min={1} max={60} value={form.tenure} onChange={e => setField('tenure', +e.target.value)} />
            </div>
          </div>

          <div className="card-grid" style={{ marginBottom: 0 }}>
            <div className="field">
              <label className="tooltip-wrap">
                {t('EMI.emi_rate')}
                <span className="tooltip-text">Annual interest rate charged by your bank</span>
              </label>
              <input type="number" min={0} max={36} step={0.5} value={form.rate} onChange={e => setField('rate', +e.target.value)} />
            </div>
            <div className="field">
              <label className="tooltip-wrap">
                {t('EMI.emi_processing_fee')}
                <span className="tooltip-text">One-time processing fee charged upfront</span>
              </label>
              <input type="number" min={0} value={form.pfee} onChange={e => setField('pfee', +e.target.value)} />
            </div>
          </div>

          <div className="card-grid" style={{ marginBottom: 0 }}>
            <div className="field">
              <label className="tooltip-wrap">
                {t('EMI.emi_cash_discount')}
                <span className="tooltip-text">Discount you give up by choosing EMI over full payment</span>
              </label>
              <input type="number" min={0} value={form.cashDiscount} onChange={e => setField('cashDiscount', +e.target.value)} />
            </div>
            <div className="field">
              <label className="tooltip-wrap">
                {t('EMI.emi_no_cost_discount')}
                <span className="tooltip-text">Hidden discount baked into "No-Cost" EMI pricing</span>
              </label>
              <input type="number" min={0} value={form.noCostDiscount} onChange={e => setField('noCostDiscount', +e.target.value)} />
            </div>
          </div>

          {error && (
            <div className="alert alert-red animate-bounce-in">
              <AlertTriangle size={16} /> {error}
            </div>
          )}

          <button className="btn btn-primary" onClick={runAudit} disabled={loading}
            style={{ width: '100%', justifyContent: 'center' }}>
            {loading ? <><span className="btn-spinner" /> {t('COMMON.loading')}</> : (
              <><Receipt size={16} /> {t('EMI.emi_calculate')}</>
            )}
          </button>
        </div>

        {/* Results */}
        <div>
          {result ? (
            <div className="result-appear">
              {/* True Cost Big Number */}
              <div className="card animate-bounce-in" style={{ textAlign: 'center', padding: 'var(--spacing-6)' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4 }}>
                  {t('EMI.emi_true_cost')}
                </div>
                <div className="verdict-icon" style={{ fontSize: 40, fontWeight: 800, color: 'var(--error)', marginBottom: 4 }}>
                  {fmt(result.true_effective_outlay)}
                </div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  {t('EMI.emi_effective')}
                </div>
              </div>

              {/* Stats Grid */}
              <div className="card animate-fade-in-up stagger-2" style={{ marginTop: 'var(--spacing-4)' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-3)' }}>
                  <div className="stat-box">
                    <div className="stat-label">{t('EMI.emi_monthly')}</div>
                    <div className="stat-value" style={{ fontSize: 20, color: 'var(--primary)' }}>{fmt(result.monthly_emi)}</div>
                  </div>
                  <div className="stat-box">
                    <div className="stat-label">{t('EMI.emi_total')}</div>
                    <div className="stat-value" style={{ fontSize: 20 }}>{fmt(result.total_payable)}</div>
                  </div>
                  <div className="stat-box">
                    <div className="stat-label">{t('EMI.emi_total_interest')}</div>
                    <div className="stat-value" style={{ fontSize: 20, color: 'var(--warning)' }}>{fmt(result.total_interest)}</div>
                  </div>
                  <div className="stat-box">
                    <div className="stat-label">{t('EMI.emi_hidden')}</div>
                    <div className="stat-value" style={{ fontSize: 20, color: 'var(--error)' }}>{fmt(result.total_hidden_charges)}</div>
                  </div>
                </div>
              </div>

              {/* EMI Schedule */}
              {result.schedule && result.schedule.length > 0 && (
                <div className="card animate-fade-in-up stagger-3" style={{ marginTop: 'var(--spacing-4)', overflowX: 'auto' }}>
                  <div className="card-title">{t('EMI.emi_full_schedule')}</div>
                  <table className="table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>{t('EMI.emi_monthly')}</th>
                        <th>Principal</th>
                        <th>Interest</th>
                        <th>Balance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.schedule.map((row, i) => (
                        <tr key={i}>
                          <td>{row.month || i + 1}</td>
                          <td className="total">{fmt(row.emi)}</td>
                          <td>{fmt(row.principal)}</td>
                          <td className="con">{fmt(row.interest)}</td>
                          <td>{fmt(row.balance)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* GST Section */}
              <div className="card animate-fade-in-up stagger-4" style={{ marginTop: 'var(--spacing-4)' }}>
                <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Shield size={18} color="var(--success)" />
                  {t('EMI.emi_gst_title')}
                </div>

                <div style={{ display: 'flex', gap: 'var(--spacing-3)', alignItems: 'center', marginBottom: 'var(--spacing-3)', flexWrap: 'wrap' }}>
                  <button onClick={() => setShowGST(!showGST)} className="btn" style={{
                    padding: '8px 16px', fontSize: '0.82rem',
                    border: '1px solid var(--border)', background: showGST ? 'rgba(34,197,94,0.1)' : 'transparent',
                    color: showGST ? 'var(--success)' : 'var(--text-muted)',
                  }}>
                    <Receipt size={14} style={{ marginRight: 4 }} />
                    {showGST ? 'GST Breakdown Shown' : 'Show GST Breakdown'}
                  </button>
                </div>

                {showGST && (
                  <div className="gst-section animate-fade-in">
                    <div className="gst-title">
                      <Receipt size={16} />
                      {t('EMI.emi_gst_breakdown') || 'GST Calculation'}
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-3)', marginBottom: 'var(--spacing-3)' }}>
                      <div className="field" style={{ marginBottom: 0 }}>
                        <label>{t('EMI.emi_gst_rate')}</label>
                        <select value={gstRate} onChange={e => setGstRate(+e.target.value)}>
                          <option value={5}>5%</option>
                          <option value={12}>12%</option>
                          <option value={18}>18%</option>
                          <option value={28}>28%</option>
                        </select>
                      </div>
                      <div className="field" style={{ marginBottom: 0 }}>
                        <label>{t('EMI.emi_gst_claim') || 'Are you a business?'}</label>
                        <select value={isBusiness ? 'yes' : 'no'} onChange={e => setIsBusiness(e.target.value === 'yes')}>
                          <option value="no">No — Individual buyer</option>
                          <option value="yes">Yes — Registered business (ITC)</option>
                        </select>
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 'var(--spacing-3)' }}>
                      <div className="stat-box">
                        <div className="stat-label">{t('EMI.emi_gst_amount')}</div>
                        <div className="gst-amount">{fmt(gstAmount)}</div>
                      </div>
                      <div className="stat-box">
                        <div className="stat-label">{t('EMI.emi_gst_return')}</div>
                        <div className="gst-amount">{isBusiness ? fmt(gstReturn) : '--'}</div>
                      </div>
                      <div className="stat-box">
                        <div className="stat-label">{t('EMI.emi_gst_total_after')}</div>
                        <div className="gst-amount">{isBusiness ? fmt(effectiveAfterGST) : fmt(result.true_effective_outlay)}</div>
                      </div>
                    </div>

                    <div style={{ marginTop: 'var(--spacing-3)', padding: 'var(--spacing-3)', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                      <Info size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
                      {t('EMI.emi_gst_note')}
                      {isBusiness && (
                        <div style={{ marginTop: 4, color: 'var(--success)', fontWeight: 600 }}>
                          {t('EMI.emi_saving')} {fmt(gstReturn)} on GST returns
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Advice */}
              {result.advice && (
                <div className="card animate-fade-in-up stagger-5" style={{ marginTop: 'var(--spacing-4)' }}>
                  <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Banknote size={18} color="var(--primary)" />
                    {t('EMI.emi_advice')}
                  </div>
                  <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.7 }}>
                    {result.advice}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="card" style={{
              minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexDirection: 'column', gap: 12, color: 'var(--text-muted)',
            }}>
              <Receipt size={48} strokeWidth={1} />
              <div style={{ fontWeight: 600 }}>{t('EMI.emi_subtitle')}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
