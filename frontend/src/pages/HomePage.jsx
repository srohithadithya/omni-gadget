import React from 'react';
import { useNavigate } from 'react-router-dom';

const FEATURES = [
  {
    icon: '🔋', title: 'Device Diagnosis',
    desc: 'Calculate your device\'s Useful Remaining Life (URL) score based on battery health, storage wear, and age.',
    path: '/diagnose', badge: 'Module 6',
  },
  {
    icon: '🎯', title: 'Smart Recommendations',
    desc: 'Get requirement-matched gadget suggestions with pros/cons, chipflation risk ratings, and refurbished alternatives.',
    path: '/recommend', badge: 'Module 3 & 4',
  },
  {
    icon: '💳', title: 'EMI Hidden Fee Audit',
    desc: 'Expose what "No-Cost EMI" actually costs — processing fees, 18% GST on interest, and forgone cash discounts.',
    path: '/emi-audit', badge: 'Module 7',
  },
  {
    icon: '📈', title: 'Chipflation Index',
    desc: 'Real-time Buy vs Hold Decision Index based on upstream DRAM/NAND component inflation data.',
    path: '/chipflation', badge: 'Module 2',
  },
];

const STATS = [
  { label: 'Device Categories', value: '6', sub: 'Mobile, Laptop, Audio, Video, Memory, Wearable' },
  { label: 'Products in DB', value: '20+', sub: 'With live chipflation risk ratings' },
  { label: 'Hidden Fee Types', value: '4', sub: 'Processing fee, GST on interest, forgone discounts' },
  { label: 'Sale Events Tracked', value: '8', sub: 'Diwali, Big Billion, Prime Day + more' },
];

const CHIPFLATION_DATA = [
  { component: 'LPDDR5X (Mobile RAM)', risk: 'HIGH', mom: '+4.2%', yoy: '+18.5%', color: 'red' },
  { component: 'DDR5 SO-DIMM (Laptop)', risk: 'HIGH', mom: '+3.8%', yoy: '+22.1%', color: 'red' },
  { component: '3D NAND TLC (Storage)', risk: 'HIGH', mom: '+5.1%', yoy: '+24.3%', color: 'red' },
  { component: 'HBM3E (AI Enterprise)', risk: 'CRITICAL', mom: '+2.1%', yoy: '+41.0%', color: 'red' },
  { component: 'Bluetooth SoC (Audio)', risk: 'STABLE', mom: '+0.4%', yoy: '+2.1%', color: 'green' },
  { component: 'Micro-AMOLED (Wearable)', risk: 'LOW', mom: '+0.8%', yoy: '+4.3%', color: 'yellow' },
];

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div>
      {/* Hero */}
      <div className="hero">
        <h1>Omni-Gadget <span>AI Decision Engine</span></h1>
        <p>
          Beat chipflation. Know when to buy, when to hold, and what your "No-Cost EMI"
          actually costs. Powered by real supply-chain data, device diagnostics, and
          transparent financial math.
        </p>
        <div className="hero-actions">
          <button className="btn btn-primary" onClick={() => navigate('/diagnose')}>
            🔋 Diagnose My Device
          </button>
          <button className="btn btn-outline" onClick={() => navigate('/recommend')}>
            🎯 Find Best Gadget
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="card-grid four" style={{ marginBottom: 28 }}>
        {STATS.map(s => (
          <div key={s.label} className="stat-box">
            <div className="stat-label">{s.label}</div>
            <div className="stat-value" style={{ fontSize: 28, color: 'var(--primary-light)' }}>{s.value}</div>
            <div className="stat-sub">{s.sub}</div>
          </div>
        ))}
      </div>

      {/* Feature Cards */}
      <div className="section-divider">Core Engines</div>
      <div className="card-grid" style={{ marginBottom: 28 }}>
        {FEATURES.map(f => (
          <div
            key={f.path}
            className="card"
            style={{ cursor: 'pointer', transition: 'border-color .15s' }}
            onClick={() => navigate(f.path)}
            onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--primary)'}
            onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
              <span style={{ fontSize: 28 }}>{f.icon}</span>
              <span className="badge badge-blue" style={{ fontSize: 10 }}>{f.badge}</span>
            </div>
            <h3 style={{ marginBottom: 8, fontSize: 15 }}>{f.title}</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: 13, lineHeight: 1.6 }}>{f.desc}</p>
            <div style={{ marginTop: 14, color: 'var(--primary-light)', fontSize: 12, fontWeight: 600 }}>
              Open →
            </div>
          </div>
        ))}
      </div>

      {/* Chipflation Snapshot */}
      <div className="section-divider">Live Chipflation Snapshot</div>
      <div className="card">
        <div className="card-title">Semiconductor Component Inflation — Sep 2026</div>
        <table className="table">
          <thead>
            <tr>
              <th>Component</th>
              <th>Risk Level</th>
              <th>MoM Growth</th>
              <th>YoY Growth</th>
              <th>Consumer Impact</th>
            </tr>
          </thead>
          <tbody>
            {CHIPFLATION_DATA.map(row => (
              <tr key={row.component}>
                <td>{row.component}</td>
                <td>
                  <span className={`badge badge-${row.color === 'red' ? 'red' : row.color === 'green' ? 'green' : 'yellow'}`}
                    style={{ fontSize: 11 }}>
                    {row.risk}
                  </span>
                </td>
                <td style={{ color: 'var(--danger)', fontWeight: 600 }}>{row.mom}</td>
                <td style={{ color: 'var(--danger)', fontWeight: 600 }}>{row.yoy}</td>
                <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                  {row.color === 'red' ? 'Price inflation passed to consumers' :
                   row.color === 'yellow' ? 'Minor impact, monitor' : 'Stable — good time to buy'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="alert alert-yellow" style={{ marginTop: 16 }}>
          <span className="alert-icon">⚠️</span>
          <div>
            <strong>Chipflation Alert — AI Infrastructure Cycle Active</strong><br />
            TSMC, SK Hynix, and Micron have shifted capacity toward HBM3E and enterprise AI processors.
            Consumer DRAM and NAND flash remain supply-constrained. Laptop and mobile price inflation
            is expected to persist through Q1 2027.
          </div>
        </div>
      </div>

      {/* Sale Calendar Preview */}
      <div className="section-divider">Upcoming Optimal Buy Windows</div>
      <div className="card">
        <div className="card-title">Sale Event Calendar — Best Purchase Windows</div>
        <div className="card-grid three">
          {[
            { name: 'Big Billion Days', date: 'Oct 1–6, 2026', platform: 'Flipkart', discount: '~20%', cats: 'Mobile, Laptop, TV', badge: 'badge-purple' },
            { name: 'Great Indian Festival', date: 'Oct 1–6, 2026', platform: 'Amazon', discount: '~18%', cats: 'Mobile, Laptop, Audio', badge: 'badge-blue' },
            { name: 'Black Friday', date: 'Nov 27–30, 2026', platform: 'All', discount: '~22%', cats: 'Laptop, Mobile, All', badge: 'badge-green' },
          ].map(ev => (
            <div key={ev.name} className="stat-box">
              <div style={{ marginBottom: 8 }}>
                <span className={`badge ${ev.badge}`} style={{ fontSize: 10 }}>{ev.platform}</span>
              </div>
              <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>{ev.name}</div>
              <div style={{ color: 'var(--text-muted)', fontSize: 12, marginBottom: 6 }}>{ev.date}</div>
              <div style={{ color: 'var(--success)', fontWeight: 700, fontSize: 16 }}>{ev.discount} off</div>
              <div style={{ color: 'var(--text-muted)', fontSize: 11, marginTop: 4 }}>{ev.cats}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
