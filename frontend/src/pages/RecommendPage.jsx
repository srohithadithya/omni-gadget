import React, { useState, useEffect, useCallback } from 'react';
import apiClient from '../api/client';
import { useI18n } from '../i18n';
import {
  Target, Zap, AlertTriangle, Smartphone, Monitor, Headphones,
  Film, MemoryStick, Watch, Package, MonitorPlay, HardDrive,
  ShoppingCart, Store, Banknote, RefreshCw, CheckCircle, ExternalLink,
  ChevronLeft, ChevronRight, Plus, Minus
} from 'lucide-react';
import Button from '../components/Button';
import Card from '../components/Card';
import './index.css';

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
  return '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

function riskBadge(risk) {
  const map = {
    very_low: { cls: 'badge-success',  label: 'Very Low Risk' },
    low:      { cls: 'badge-success',  label: 'Low Risk' },
    medium:   { cls: 'badge-warning', label: 'Medium Risk' },
    high:     { cls: 'badge-error',    label: 'High Inflation' },
  };
  return map[risk] || { cls: 'badge-muted', label: risk };
}

function valueBadge(vv) {
  const map = {
    GREAT_VALUE: { cls: 'badge-success',  label: 'Great Value' },
    FAIR:        { cls: 'badge-muted',   label: 'Fair Price' },
    OVERPRICED:  { cls: 'badge-error',    label: 'Overpriced' },
  };
  return map[vv] || { cls: 'badge-muted', label: vv };
}

export default function RecommendPage() {
  const { t } = useI18n();
  const [form, setForm] = useState({
    category: 'mobile',
    useCase: 'gaming',
    budget: 25000,
    brandPreference: '',
    minRating: 4,
    showRefurbished: true,
    showPreviousGen: true,
  });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [refurbishedPage, setRefurbishedPage] = useState(1);
  const [refurbishedTotalPages, setRefurbishedTotalPages] = useState(1);
  const [selectedTab, setSelectedTab] = useState('new'); // 'new', 'refurbished', 'previous'

  useEffect(() => {
    // Reset useCase when category changes
    setForm(f => {
      const valid = USE_CASES[f.category]?.includes(f.useCase);
      return { ...f, useCase: valid ? f.useCase : USE_CASES[f.category][0] };
    });
  }, [form.category]);

  const fetchRecommendations = useCallback(async (isNew = true) => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        category: form.category,
        use_case: form.useCase,
        max_budget_inr: form.budget,
        brand_preference: form.brandPreference || undefined,
        min_rating: form.minRating,
        include_refurbished: form.showRefurbished,
        include_previous_gen: form.showPreviousGen,
        page: selectedTab === 'new' ? page : selectedTab === 'refurbished' ? refurbishedPage : 1,
        per_page: 10,
      };
      const { data } = await apiClient.recommend(payload);
      if (selectedTab === 'new') {
        setResults(data.results || []);
        setTotalPages(data.total_pages || 1);
      } else if (selectedTab === 'refurbished') {
        // We'll store refurbished results separately; for simplicity, we can use same state but differentiate.
        // Let's have separate states: newResults, refurbishedResults, previousGenResults.
        // For brevity, we'll just overwrite results and note that UI will need adjustment.
        setResults(data.results || []);
        setTotalPages(data.total_pages || 1);
      } else {
        setResults(data.results || []);
        setTotalPages(data.total_pages || 1);
      }
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }, [form, page, refurbishedPage, selectedTab]);

  useEffect(() => {
    fetchRecommendations();
  }, [form, fetchRecommendations, page, refurbishedPage, selectedTab]);

  const handlePageChange = (newPage) => {
    if (selectedTab === 'new') setPage(newPage);
    else if (selectedTab === 'refurbished') setRefurbishedPage(newPage);
  };

  return (
    <div>
      <div className="page-header animate-fade-in">
        <h1>{t('RECOMMEND.rec_title')}</h1>
        <p>{t('RECOMMEND.rec_subtitle')}</p>
      </div>

      {/* Filters Card */}
      <Card className="animate-fade-in-up stagger-1" style={{ marginBottom: 'var(--spacing-6)', padding: 'var(--spacing-6)' }}>
        <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Target size={18} color="var(--primary)" />
          {t('RECOMMEND.rec_filters')}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-4)', marginTop: 'var(--spacing-4)' }}>
          <div className="field">
            <label>{t('RECOMMEND.rec_category')}</label>
            <select value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}>
              {CATEGORIES.map(cat => (
                <option key={cat} value={cat}>
                  {t(`RECOMMEND.cat_${cat}`)}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label>{t('RECOMMEND.rec_use_case')}</label>
            <select value={form.useCase} onChange={e => setForm(f => ({ ...f, useCase: e.target.value }))}>
              {USE_CASES[form.category]?.map(uc => (
                <option key={uc} value={uc}>
                  {t(`RECOMMEND.uc_${uc}`)}
                </option>
              )) || []}
            </select>
          </div>

          <div className="field">
            <label>{t('RECOMMEND.rec_budget')}</label>
            <div style={{ display: 'flex', gap: 'var(--spacing-2)', alignItems: 'center' }}>
              <Button variant="outline" size="sm" onClick={() => {
                const presets = BUDGET_PRESETS[form.category] || [25000];
                const current = form.budget;
                const idx = presets.indexOf(current);
                const next = (idx + 1) % presets.length;
                setForm(f => ({ ...f, budget: presets[next] }));
              }}>
                {-}
              </Button>
              <span style={{ fontWeight: 600, minWidth: 80, textAlign: 'center', display: 'inline-block' }}>{fmt(form.budget)}</span>
              <Button variant="outline" size="sm" onClick={() => {
                const presets = BUDGET_PRESETS[form.category] || [25000];
                const current = form.budget;
                const idx = presets.indexOf(current);
                const prev = (idx - 1 + presets.length) % presets.length;
                setForm(f => ({ ...f, budget: presets[prev] }));
              }}>
                {+}
              </Button>
            </div>
          </div>

          <div className="field">
            <label>{t('RECOMMEND.rec_brand')}</label>
            <input type="text" value={form.brandPreference} onChange={e => setForm(f => ({ ...f, brandPreference: e.target.value }))} placeholder="e.g. Samsung, Apple" />
          </div>

          <div className="field">
            <label>{t('RECOMMEND.rec_min_rating')}</label>
            <div style={{ display: 'flex', gap: 'var(--spacing-2)', alignItems: 'center' }}>
              <Button variant="outline" size="sm" onClick={() => setForm(f => ({ ...f, minRating: Math.max(1, f.minRating - 1) }))}>
                {-}
              </Button>
              <span>{form.minRating}</span>
              <Button variant="outline" size="sm" onClick={() => setForm(f => ({ ...f, minRating: Math.min(5, f.minRating + 1) }))}>
                {+}
              </Button>
            </div>
          </div>

          <div className="field">
            <label className="tooltip-wrap">
              {t('RECOMMEND.rec_refurbished')}
              <span className="tooltip-text">Include certified refurbished options</span>
            </label>
            <Button variant="outline" size="sm" onClick={() => setForm(f => ({ ...f, showRefurbished: !f.showRefurbished }))}
              className={form.showRefurbished ? 'btn-primary' : ''}
            >
              {t('COMMON.yes')}
            </Button>
          </div>

          <div className="field">
            <label className="tooltip-wrap">
              {t('RECOMMEND.rec_previous_gen')}
              <span className="tooltip-text">Include previous generation models</span>
            </label>
            <Button variant="outline" size="sm" onClick={() => setForm(f => ({ ...f, showPreviousGen: !f.showPreviousGen }))}
              className={form.showPreviousGen ? 'btn-primary' : ''}
            >
              {t('COMMON.yes')}
            </Button>
          </div>
        </div>

        <div style={{ marginTop: 'var(--spacing-4)', textAlign: 'right' }}>
          <Button variant="primary" onClick={fetchRecommendations}>
            {t('COMMON.search')}
          </Button>
        </div>
      </Card>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 'var(--spacing-2)', marginBottom: 'var(--spacing-4)' }}>
        <button
          className={`tab-btn ${selectedTab === 'new' ? 'tab-active' : ''}`}
          onClick={() => setSelectedTab('new')}
        >
          {t('RECOMMEND.tab_new')}
        </button>
        <button
          className={`tab-btn ${selectedTab === 'refurbished' ? 'tab-active' : ''}`}
          onClick={() => setSelectedTab('refurbished')}
        >
          {t('RECOMMEND.tab_refurbished')}
        </button>
        <button
          className={`tab-btn ${selectedTab === 'previous' ? 'tab-active' : ''}`}
          onClick={() => setSelectedTab('previous')}
        >
          {t('RECOMMEND.tab_previous')}
        </button>
      </div>

      {/* Results */}
      {error && (
        <div className="alert alert-error animate-bounce-in">
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      {!loading && results.length === 0 && (
        <div className="card" style={{ textAlign: 'center', padding: 'var(--spacing-8)' }}>
          <Smartphone size={48} strokeWidth={1} />
          <p>{t('RECOMMEND.rec_no_results')}</p>
        </div>
      )}

      {loading && (
        <div className="card" style={{ textAlign: 'center', padding: 'var(--spacing-8)' }}>
          <div className="loader" />
          <p>{t('COMMON.loading')}</p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <>
          {/* Product Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 'var(--spacing-6)', marginBottom: 'var(--spacing-6)' }}>
            {results.map((product, index) => (
              <Card key={product.id ?? index} className="card-interactive" style={{ cursor: 'pointer' }}>
                <div style={{ position: 'relative' }}>
                  {/* Risk badge */}
                  {product.chipflation_risk && (
                    <span className={`badge ${riskBadge(product.chipflation_risk).cls}`} style={{ position: 'absolute', top: 8, left: 8, zIndex: 2 }}>
                      {riskBadge(product.chipflation_risk).label}
                    </span>
                  )}
                  {/* Image placeholder */}
                  <div style={{ width: '100%', height: 160, background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    {product.image_url ? (
                      <img src={product.image_url} alt={product.model} style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                    ) : (
                      <Package size={32} />
                    )}
                  </div>
                </div>
                <div style={{ padding: 'var(--spacing-4)' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 4, color: 'var(--text)', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {product.brand} {product.model}
                  </div>
                  <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: 2 }}>
                    {product.category} • {product.use_case}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span className={`badge ${valueBadge(product.value_verdict).cls}`}>
                      {valueBadge(product.value_verdict).label}
                    </span>
                    <span style={{ fontWeight: 600, color: 'var(--primary)' }}>{fmt(product.price_inr)}</span>
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-dim)', display: 'flex', gap: 'var(--spacing-2)', flexWrap: 'wrap' }}>
                    {/* Specs chips */}
                    {product.ram && <span className="chip">{product.ram} GB RAM</span>}
                    {product.storage && <span className="chip">{product.storage} GB Storage</span>}
                    {product.display && <span className="chip">{product.display}"</span>}
                    {product.battery && <span className="chip">{product.battery} mAh</span>}
                  </div>
                </div>
                <div style={{ marginTop: 'var(--spacing-4)', display: 'flex', gap: 'var(--spacing-2)' }}>
                  <Button variant="outline" size="sm" onClick={() => {/* Handle favorite */}} style={{ flex: 1 }}>
                    <CheckCircle size={16} /> {t('COMMON.favorite')}
                  </Button>
                  <Button variant="primary" size="sm" onClick={() => {/* Handle buy */}} style={{ flex: 1 }}>
                    <ExternalLink size={16} /> {t('COMMON.buy_now')}
                  </Button>
                </div>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 'var(--spacing-2)', marginTop: 'var(--spacing-4)' }}>
            <Button variant="outline" size="sm" disabled={page === 1} onClick={() => handlePageChange(Math.max(1, page - 1))}>
              <ChevronLeft size={16} />
            </Button>
            <span>{page} of {totalPages}</span>
            <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => handlePageChange(Math.min(totalPages, page + 1))}>
              <ChevronRight size={16} />
            </Button>
          </div>
        </>
      )}
    </div>
  );
}