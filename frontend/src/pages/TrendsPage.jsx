import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import TrendBarChart from '../components/TrendBarChart';

function barColor(pct) {
  if (pct >= 70) return '#22c55e';
  if (pct >= 40) return '#eab308';
  return '#ef4444';
}

function TrendArrow({ direction }) {
  if (direction === 'up') return <span style={{ color: '#ef4444', fontSize: 18 }}>📈</span>;
  if (direction === 'down') return <span style={{ color: '#22c55e', fontSize: 18 }}>📉</span>;
  return <span style={{ color: '#eab308', fontSize: 18 }}>➡️</span>;
}

export default function TrendsPage() {
  const [popular, setPopular] = useState(null);
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [popRes, trendRes] = await Promise.allSettled([
          apiClient.popular(),
          apiClient.trends(),
        ]);
        if (popRes.status === 'fulfilled') setPopular(popRes.value.data);
        if (trendRes.status === 'fulfilled') setTrends(trendRes.value.data);
        // If both failed
        if (popRes.status === 'rejected' && trendRes.status === 'rejected') {
          const msg = popRes.reason?.response?.data?.detail || popRes.reason?.message || 'Failed to load data';
          setError(msg);
        }
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const popularProducts = popular?.products || popular || [];
  const trendData = trends || {};
  const categoryDI = trendData?.category_avg_di || trendData?.category_di || [];
  const chipflationTrend = trendData?.chipflation_trend || trendData?.chipflation || null;
  const recentInsights = trendData?.insights || trendData?.recent_insights || [];

  // Compute max value for DI bar chart
  const maxDI = categoryDI.length > 0
    ? Math.max(...categoryDI.map(c => c.avg_di || c.value || 0), 1)
    : 100;

  return (
    <div>
      <div className="page-header">
        <h1>📊 Market Trends</h1>
        <p>Popular products, average Decision Index scores by category, and chipflation direction</p>
      </div>

      {loading ? (
        <div className="card" style={{ minHeight: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, color: 'var(--text-muted)' }}>
          <span className="btn-spinner" style={{ borderColor: 'rgba(251,191,36,.3)', borderTopColor: '#fbbf24' }} />
          Loading market data…
        </div>
      ) : error ? (
        <div className="alert alert-red">
          <span className="alert-icon">⚠️</span>
          <div><strong>Error:</strong> {error}</div>
        </div>
      ) : (
        <>
          {/* Chipflation trend direction */}
          {chipflationTrend && (
            <>
              <div className="section-divider">Chipflation Trend Direction</div>
              <div className="card" style={{
                background: 'linear-gradient(135deg, rgba(251,191,36,.08), rgba(217,119,6,.04))',
                border: '1px solid rgba(251,191,36,.2)',
                marginBottom: 20,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
                  <TrendArrow direction={chipflationTrend.direction || 'up'} />
                  <div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 2 }}>Current Trend</div>
                    <div style={{ fontSize: 18, fontWeight: 700, color: '#fbbf24' }}>
                      {chipflationTrend.label || chipflationTrend.direction?.toUpperCase() || 'MONITORING'}
                    </div>
                  </div>
                  {chipflationTrend.delta && (
                    <div style={{ marginLeft: 'auto' }}>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Monthly Change</div>
                      <div style={{ fontSize: 20, fontWeight: 800, color: chipflationTrend.delta > 0 ? '#ef4444' : '#22c55e' }}>
                        {chipflationTrend.delta > 0 ? '+' : ''}{chipflationTrend.delta}%
                      </div>
                    </div>
                  )}
                  {chipflationTrend.summary && (
                    <div style={{ flex: '1 1 100%', fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6, marginTop: 4 }}>
                      {chipflationTrend.summary}
                    </div>
                  )}
                </div>
              </div>
            </>
          )}

          {/* Average DI Score by Category — Recharts bar chart */}
          {categoryDI.length > 0 && (
            <>
              <div className="section-divider">Average Decision Index by Category</div>
              <div className="card" style={{ marginBottom: 20 }}>
                <div className="card-title">Decision Index Score Distribution</div>
                <TrendBarChart 
                  data={categoryDI.map(cat => ({
                    name: cat.category || cat.name || `Category ${catDI.indexOf(cat)+1}`,
                    value: cat.avg_di || cat.value || 0,
                  }))} 
                  maxValue={maxDI}
                />
              </div>
            </>
          )}

          {/* Popular Products */}
          {popularProducts.length > 0 && (
            <>
              <div className="section-divider">Popular Products</div>
              <div className="card-grid" style={{ marginBottom: 20 }}>
                {popularProducts.map((p, i) => (
                  <div key={p.id || p.name || i} className="product-card" style={{
                    borderColor: 'rgba(251,191,36,.15)',
                  }}>
                    <div className="product-header">
                      <div>
                        <div className="product-name">{p.name || p.product_name}</div>
                        {p.brand && <div className="product-brand">{p.brand}</div>}
                      </div>
                      {p.chipflation_risk && (
                        <span className={`badge ${p.chipflation_risk === 'HIGH' ? 'badge-red' : p.chipflation_risk === 'MEDIUM' ? 'badge-yellow' : 'badge-green'}`}
                          style={{ fontSize: 10 }}>
                          {p.chipflation_risk}
                        </span>
                      )}
                    </div>
                    {p.price != null && (
                      <div className="product-price">₹{Number(p.price).toLocaleString('en-IN')}</div>
                    )}
                    {p.di_score != null && (
                      <div style={{ marginTop: 6 }}>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Decision Index</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{ flex: 1, height: 6, background: 'var(--border)', borderRadius: 99, overflow: 'hidden' }}>
                            <div style={{
                              height: '100%', borderRadius: 99,
                              width: `${Math.min(p.di_score, 100)}%`,
                              background: barColor(p.di_score),
                            }} />
                          </div>
                          <span style={{ fontSize: 12, fontWeight: 700, color: barColor(p.di_score) }}>{p.di_score}</span>
                        </div>
                      </div>
                    )}
                    {p.category && (
                      <div style={{ marginTop: 8 }}>
                        <span className="tag" style={{ fontSize: 10 }}>{p.category}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Insights */}
          {recentInsights.length > 0 && (
            <>
              <div className="section-divider">Market Insights</div>
              <div className="card" style={{
                background: 'linear-gradient(135deg, rgba(99,102,241,.06), rgba(168,85,247,.04))',
                border: '1px solid rgba(99,102,241,.15)',
              }}>
                {recentInsights.map((ins, i) => (
                  <div key={i} style={{ padding: '10px 0', borderBottom: i < recentInsights.length - 1 ? '1px solid var(--border)' : 'none' }}>
                    <div style={{ fontSize: 13, color: 'var(--text)', lineHeight: 1.6 }}>
                      {typeof ins === 'string' ? ins : ins.text || ins.description || JSON.stringify(ins)}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Fallback empty state */}
          {!chipflationTrend && categoryDI.length === 0 && popularProducts.length === 0 && recentInsights.length === 0 && (
            <div className="card" style={{ minHeight: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 12, color: 'var(--text-muted)' }}>
              <div style={{ fontSize: 48 }}>📊</div>
              <div style={{ fontWeight: 600 }}>No market data available yet</div>
              <div style={{ fontSize: 13 }}>Trends will populate once enough decisions have been processed.</div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
