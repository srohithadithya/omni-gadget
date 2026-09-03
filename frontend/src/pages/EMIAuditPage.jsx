import React, { useState } from 'react';
import apiClient from '../api/client';

function fmt(n) {
  return '₹' + Number(n).toLocaleString('en-IN', { minimumFractionDigits: 2 });
}

const PRESETS = [
  { label: '₹20k Phone', msrp: 20000, discount: 1200, pfee: 199, tenure: 6,  forgone: 800 },
  { label: '₹40k Phone', msrp: 40000, discount: 2500, pfee: 299, tenure: 6,  forgone: 1500 },
  { label: '₹70k Laptop', msrp: 70000, discount: 4500, pfee: 299, tenure: 12, forgone: 2000 },
  { label: '₹1.1L MacBook', msrp: 110000, discount: 7000, pfee: 299, tenure: 12, forgone: 3000 },
  { label: '₹55k TV',   msrp: 55000, discount: 3500, pfee: 299, tenure: 24, forgone: 1500 },
];

export default function EMIAuditPage() {
  const [form, setForm] = useState({
    product_msrp: 40000,
    no_cost_discount: 2500,
    bank_processing_fee: 299,
    tenure_months: 6,
    forgone_cash_discount: 1500,
    exchange_bonus: 0,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [scheduleData, setScheduleData] = useState(null);
  const [scheduleLoading, setScheduleLoading] = useState(false);
  const [scheduleError, setScheduleError] = useState(null);

  function setField(k, v) { setForm(f => ({ ...f, [k]: v })); }

  function applyPreset(p) {
    setForm({
      product_msrp: p.msrp,
      no_cost_discount: p.discount,
      bank_processing_fee: p.pfee,
      tenure_months: p.tenure,
      forgone_cash_discount: p.forgone,
      exchange_bonus: 0,
    });
    setResult(null);
    setScheduleData(null);
  }

  async function run() {
    setLoading(true); setError(null); setScheduleData(null);
    try {
      const { data } = await apiClient.emiAudit(form);
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }

  async function fetchSchedule() {
    setScheduleLoading(true); setScheduleError(null);
    try {
      const { data } = await apiClient.emiSchedule({
        product_msrp: form.product_msrp,
        annual_rate_pct: 0,  // No-Cost EMI
        tenure_months: form.tenure_months,
        no_cost_discount: form.no_cost_discount,
      });
      setScheduleData(data);
    } catch (e) {
      setScheduleError(e.response?.data?.detail || e.message);
    } finally {
      setScheduleLoading(false);
    }
  }

  const recColor = result
    ? result.recommendation === 'EMI_ACCEPTABLE' ? 'alert-green'
    : result.recommendation === 'RECONSIDER_EMI_TENURE' ? 'alert-yellow'
    : 'alert-red'
    : '';

  return (
    <div>
      <div className="page-header">
        <h1>💳 EMI Hidden Fee Audit</h1>
        <p>Module 7 — True-Cost EMI & Hidden Charges Extractor</p>
      </div>

      {/* Presets */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
        {PRESETS.map(p => (
          <button key={p.label} className="btn btn-outline"
            style={{ fontSize: 12, padding: '6px 14px' }}
            onClick={() => applyPreset(p)}>
            {p.label}
          </button>
        ))}
      </div>

      <div className="card-grid">
        {/* Input */}
        <div>
          <div className="card">
            <div className="card-title">EMI Plan Details</div>

            <div className="field">
              <label>Product MSRP (₹)</label>
              <input type="number" min={0}
                value={form.product_msrp}
                onChange={e => setField('product_msrp', +e.target.value)} />
            </div>

            <div className="field">
              <label>Seller's Interest Subsidy — "No-Cost Discount" (₹)</label>
              <input type="number" min={0} placeholder="e.g. 2500"
                value={form.no_cost_discount}
                onChange={e => setField('no_cost_discount', +e.target.value)} />
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                The amount the seller discounts to cover bank interest. 18% GST on this is charged to YOU.
              </span>
            </div>

            <div className="card-grid">
              <div className="field">
                <label>Bank Processing Fee (₹)</label>
                <input type="number" min={0} placeholder="199–299"
                  value={form.bank_processing_fee}
                  onChange={e => setField('bank_processing_fee', +e.target.value)} />
              </div>
              <div className="field">
                <label>EMI Tenure (months)</label>
                <input type="number" min={1} max={60}
                  value={form.tenure_months}
                  onChange={e => setField('tenure_months', +e.target.value)} />
              </div>
            </div>

            <div className="field">
              <label>Forgone UPI / Instant Cash Discount (₹)</label>
              <input type="number" min={0} placeholder="e.g. 1500"
                value={form.forgone_cash_discount}
                onChange={e => setField('forgone_cash_discount', +e.target.value)} />
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Instant discount you lose by choosing EMI over upfront UPI payment.
              </span>
            </div>

            <div className="field">
              <label>Exchange / Trade-in Bonus (₹)</label>
              <input type="number" min={0} placeholder="0"
                value={form.exchange_bonus}
                onChange={e => setField('exchange_bonus', +e.target.value)} />
            </div>

            {error && <div className="alert alert-red"><span className="alert-icon">⚠️</span>{error}</div>}

            <button className="btn btn-primary" onClick={run} disabled={loading}
              style={{ width: '100%', justifyContent: 'center', marginTop: 4 }}>
              {loading ? <><span className="btn-spinner" />Auditing…</> : '🔍 Expose Hidden Charges'}
            </button>
          </div>

          {/* Education card */}
          <div className="card">
            <div className="card-title">How "No-Cost EMI" Hidden Charges Work</div>
            <div style={{ fontSize: 12, lineHeight: 1.9, color: 'var(--text-muted)' }}>
              <div style={{ marginBottom: 6 }}>
                <strong style={{ color: 'var(--text)' }}>1. Bank Processing Fee</strong><br />
                A one-time conversion fee (₹199–₹299) charged to activate the EMI plan.
              </div>
              <div style={{ marginBottom: 6 }}>
                <strong style={{ color: 'var(--text)' }}>2. GST on Processing Fee (18%)</strong><br />
                18% tax is levied on the processing fee itself.
              </div>
              <div style={{ marginBottom: 6 }}>
                <strong style={{ color: 'var(--danger)' }}>3. 18% GST on Interest Component ⚠</strong><br />
                Under No-Cost EMI, the seller discounts the price by the bank's interest amount.
                But the government charges 18% GST on that interest — and the seller does NOT absorb it.
                This comes entirely out of your pocket.
              </div>
              <div>
                <strong style={{ color: 'var(--text)' }}>4. Forgone Instant Discount</strong><br />
                Many sellers offer 5–10% instant off for UPI/Debit payment. Choosing EMI forfeits this entirely.
              </div>
            </div>
          </div>
        </div>

        {/* Results */}
        <div>
          {result ? (
            <>
              {/* Stat summary */}
              <div className="card-grid" style={{ marginBottom: 16 }}>
                <div className="stat-box">
                  <div className="stat-label">Advertised Price</div>
                  <div className="stat-value" style={{ fontSize: 20 }}>{fmt(result.advertised_price)}</div>
                  <div className="stat-sub">what they show you</div>
                </div>
                <div className="stat-box">
                  <div className="stat-label">Hidden Charges</div>
                  <div className="stat-value" style={{ fontSize: 20, color: 'var(--danger)' }}>
                    {fmt(result.total_hidden_charges)}
                  </div>
                  <div className="stat-sub">{result.hidden_charge_pct}% of price</div>
                </div>
                <div className="stat-box">
                  <div className="stat-label">True Outlay</div>
                  <div className="stat-value" style={{ fontSize: 20, color: 'var(--primary-light)' }}>
                    {fmt(result.true_effective_outlay)}
                  </div>
                  <div className="stat-sub">what you actually pay</div>
                </div>
                <div className="stat-box">
                  <div className="stat-label">Monthly EMI</div>
                  <div className="stat-value" style={{ fontSize: 20 }}>{fmt(result.monthly_emi)}</div>
                  <div className="stat-sub">×{form.tenure_months} months</div>
                </div>
              </div>

              {/* Breakdown table */}
              <div className="card">
                <div className="card-title">Hidden Charge Breakdown</div>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Charge</th>
                      <th>Type</th>
                      <th style={{ textAlign: 'right' }}>Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Bank Processing Fee</td>
                      <td><span className="badge badge-yellow" style={{ fontSize: 10 }}>Bank</span></td>
                      <td className="right danger">{fmt(result.breakdown.bank_processing_fee)}</td>
                    </tr>
                    <tr>
                      <td>GST on Processing Fee (18%)</td>
                      <td><span className="badge badge-yellow" style={{ fontSize: 10 }}>Tax</span></td>
                      <td className="right danger">{fmt(result.breakdown.gst_on_processing_fee_18pct)}</td>
                    </tr>
                    <tr>
                      <td>Unrefundable GST on Interest (18%)</td>
                      <td><span className="badge badge-red" style={{ fontSize: 10 }}>Hidden</span></td>
                      <td className="right danger">{fmt(result.breakdown.unrefundable_gst_on_interest_18pct)}</td>
                    </tr>
                    <tr>
                      <td>Forgone Upfront Cash Discount</td>
                      <td><span className="badge badge-red" style={{ fontSize: 10 }}>Opportunity</span></td>
                      <td className="right danger">{fmt(result.breakdown.forgone_upfront_cash_discount)}</td>
                    </tr>
                    {result.breakdown.exchange_bonus_deducted > 0 && (
                      <tr>
                        <td>Exchange Bonus (deducted)</td>
                        <td><span className="badge badge-green" style={{ fontSize: 10 }}>Saving</span></td>
                        <td className="right" style={{ color: 'var(--success)' }}>
                          -{fmt(result.breakdown.exchange_bonus_deducted)}
                        </td>
                      </tr>
                    )}
                    <tr className="total">
                      <td>Total Hidden Surcharges</td>
                      <td></td>
                      <td className="right" style={{ color: 'var(--danger)', fontSize: 15 }}>
                        {fmt(result.total_hidden_charges)}
                      </td>
                    </tr>
                    <tr className="total">
                      <td>True Effective Outlay</td>
                      <td></td>
                      <td className="right" style={{ color: 'var(--primary-light)', fontSize: 15 }}>
                        {fmt(result.true_effective_outlay)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Verdict */}
              <div className={`alert ${recColor}`}>
                <span className="alert-icon">
                  {result.recommendation === 'EMI_ACCEPTABLE' ? '✅'
                    : result.recommendation === 'RECONSIDER_EMI_TENURE' ? '⚠️' : '🔴'}
                </span>
                <div>
                  <strong>{result.recommendation.replace(/_/g, ' ')}</strong><br />
                  {result.advice}
                </div>
              </div>

              {/* Comparison tip */}
              <div className="card" style={{ marginTop: 4 }}>
                <div className="card-title">Upfront vs EMI Comparison</div>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Payment Method</th>
                      <th style={{ textAlign: 'right' }}>You Pay</th>
                      <th style={{ textAlign: 'right' }}>You Save</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>💳 No-Cost EMI ({form.tenure_months}m)</td>
                      <td className="right">{fmt(result.true_effective_outlay)}</td>
                      <td className="right" style={{ color: 'var(--text-muted)' }}>—</td>
                    </tr>
                    <tr>
                      <td>📱 Upfront UPI / Debit</td>
                      <td className="right" style={{ color: 'var(--success)', fontWeight: 700 }}>
                        {fmt(result.advertised_price - form.forgone_cash_discount)}
                      </td>
                      <td className="right" style={{ color: 'var(--success)', fontWeight: 700 }}>
                        {fmt(result.total_hidden_charges)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* View EMI Schedule button */}
              <div className="card" style={{ marginTop: 4 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div className="card-title" style={{ margin: 0 }}>EMI Amortization Schedule</div>
                  <button
                    className="btn btn-primary"
                    onClick={fetchSchedule}
                    disabled={scheduleLoading}
                    style={{ fontSize: 12, padding: '8px 18px' }}
                  >
                    {scheduleLoading ? <><span className="btn-spinner" />Loading…</> : '📅 View EMI Schedule'}
                  </button>
                </div>

                {scheduleError && (
                  <div className="alert alert-red" style={{ marginTop: 12 }}>
                    <span className="alert-icon">⚠️</span>{scheduleError}
                  </div>
                )}

                {scheduleData && (
                  <div style={{ marginTop: 12 }}>
                    {scheduleData.is_no_cost_emi && scheduleData.no_cost_note && (
                      <div className="alert alert-yellow" style={{ marginBottom: 12, fontSize: 12 }}>
                        <span className="alert-icon">ℹ️</span>
                        <div>{scheduleData.no_cost_note}</div>
                      </div>
                    )}

                    <div style={{ overflowX: 'auto' }}>
                      <table className="table">
                        <thead>
                          <tr>
                            <th style={{ textAlign: 'center' }}>Month</th>
                            <th style={{ textAlign: 'right' }}>Opening Balance</th>
                            <th style={{ textAlign: 'right' }}>EMI</th>
                            <th style={{ textAlign: 'right' }}>Principal</th>
                            <th style={{ textAlign: 'right' }}>Interest</th>
                            <th style={{ textAlign: 'right' }}>Closing Balance</th>
                          </tr>
                        </thead>
                        <tbody>
                          {scheduleData.schedule.map(row => (
                            <tr key={row.month}>
                              <td style={{ textAlign: 'center' }}>{row.month}</td>
                              <td className="right">{fmt(row.opening_balance)}</td>
                              <td className="right">{fmt(row.emi)}</td>
                              <td className="right">{fmt(row.principal_component)}</td>
                              <td className="right" style={{ color: row.interest_component > 0 ? 'var(--danger)' : 'var(--text-muted)' }}>
                                {fmt(row.interest_component)}
                              </td>
                              <td className="right">{fmt(row.closing_balance)}</td>
                            </tr>
                          ))}
                          <tr className="total">
                            <td style={{ textAlign: 'center' }}><strong>Total</strong></td>
                            <td></td>
                            <td className="right"><strong>{fmt(scheduleData.schedule.reduce((s, r) => s + r.emi, 0))}</strong></td>
                            <td className="right"><strong>{fmt(scheduleData.totals.total_principal)}</strong></td>
                            <td className="right" style={{ color: scheduleData.totals.total_interest > 0 ? 'var(--danger)' : 'var(--text-muted)' }}>
                              <strong>{fmt(scheduleData.totals.total_interest)}</strong>
                            </td>
                            <td className="right"><strong>{fmt(scheduleData.totals.total_cost)}</strong></td>
                          </tr>
                        </tbody>
                      </table>
                    </div>

                    <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-muted)', display: 'flex', gap: 20 }}>
                      <span>Principal: <strong>{fmt(scheduleData.totals.total_principal)}</strong></span>
                      <span>Interest: <strong>{fmt(scheduleData.totals.total_interest)}</strong></span>
                      <span>GST on Interest (18%): <strong>{fmt(scheduleData.totals.total_gst_on_interest)}</strong></span>
                      <span>Total Cost: <strong style={{ color: 'var(--primary-light)' }}>{fmt(scheduleData.totals.total_cost)}</strong></span>
                    </div>
                  </div>
                )}

                {!scheduleData && !scheduleError && (
                  <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--text-muted)', fontSize: 13 }}>
                    Click "View EMI Schedule" to see the full month-by-month amortization breakdown
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="card" style={{ minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 12, color: 'var(--text-muted)' }}>
              <div style={{ fontSize: 48 }}>💳</div>
              <div style={{ fontWeight: 600 }}>Enter EMI details to expose hidden charges</div>
              <div style={{ fontSize: 12 }}>Use a preset above to start quickly</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
