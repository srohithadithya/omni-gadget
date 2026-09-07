import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Smartphone,
  Laptop,
  Headphones,
  Watch,
  Activity as ActivityIcon,
  Target as TargetIcon,
  CreditCard as CreditCardIcon,
  TrendingUp as TrendingUpIcon,
} from 'lucide-react';

const STATS = [
  { label: 'Device Categories', value: '6', icon: Smartphone, bg: 'bg-blue-50' },
  { label: 'Products in DB', value: '20+', icon: Laptop, bg: 'bg-green-50' },
  { label: 'Hidden Fee Types', value: '4', icon: Headphones, bg: 'bg-purple-50' },
  { label: 'Sale Events Tracked', value: '8', icon: Watch, bg: 'bg-orange-50' },
];

const FEATURES = [
  {
    icon: ActivityIcon,
    title: 'Device Diagnosis',
    desc: "Calculate your device's Useful Remaining Life (URL) score based on battery health, storage wear, and age.",
    path: '/diagnose',
  },
  {
    icon: TargetIcon,
    title: 'Smart Recommendations',
    desc: 'Get requirement-matched gadget suggestions with pros/cons, chipflation risk ratings, and refurbished alternatives.',
    path: '/recommend',
  },
  {
    icon: CreditCardIcon,
    title: 'EMI Hidden Fee Audit',
    desc: 'Expose what \"No-Cost EMI\" actually costs — processing fees, 18% GST on interest, and forgone cash discounts.',
    path: '/emi-audit',
  },
  {
    icon: TrendingUpIcon,
    title: 'Chipflation Index',
    desc: 'Real-time Buy vs Hold Decision Index based on upstream DRAM/NAND component inflation data.',
    path: '/chipflation',
  },
];

const CHIPFLATION_DATA = [
  { component: 'LPDDR5X (Mobile RAM)', risk: 'HIGH', mom: '+4.2%', yoy: '+18.5%', impact: 'Price inflation passed to consumers' },
  { component: 'DDR5 SO-DIMM (Laptop)', risk: 'HIGH', mom: '+3.8%', yoy: '+22.1%', impact: 'Price inflation passed to consumers' },
  { component: '3D NAND TLC (Storage)', risk: 'HIGH', mom: '+5.1%', yoy: '+24.3%', impact: 'Price inflation passed to consumers' },
  { component: 'HBM3E (AI Enterprise)', risk: 'CRITICAL', mom: '+2.1%', yoy: '+41.0%', impact: 'Enterprise-focused, limited consumer impact' },
  { component: 'Bluetooth SoC (Audio)', risk: 'STABLE', mom: '+0.4%', yoy: '+2.1%', impact: 'Stable — good time to buy' },
  { component: 'Micro-AMOLED (Wearable)', risk: 'LOW', mom: '+0.8%', yoy: '+4.3%', impact: 'Minor impact, monitor' },
];

const SALE_EVENTS = [
  { name: 'Big Billion Days', date: 'Oct 1–6, 2026', platform: 'Flipkart', discount: '~20%', cats: 'Mobile, Laptop, TV' },
  { name: 'Great Indian Festival', date: 'Oct 1–6, 2026', platform: 'Amazon', discount: '~18%', cats: 'Mobile, Laptop, Audio' },
  { name: 'Black Friday', date: 'Nov 27–30, 2026', platform: 'All', discount: '~22%', cats: 'Laptop, Mobile, All' },
];

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div>
      {/* Hero */}
      <section className="mb-10">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="mb-4">Make smarter gadget decisions</h1>
          <p className="text-muted mb-6">
            Beat chipflation. Know when to buy, when to hold, and what your \"No-Cost EMI\"\n            actually costs. Powered by real supply-chain data, device diagnostics, and\n            transparent financial math.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <button
              className="btn btn-primary"
              onClick={() => navigate('/diagnose')}
            >
              Diagnose Your Device
            </button>
            <button
              className="btn btn-outline"
              onClick={() => navigate('/recommend')}
            >
              Find Best Gadget
            </button>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="mb-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {STATS.map((stat) => (
            <div
              key={stat.label}
              className="card text-center p-6"
            >
              <div className="flex h-10 w-10 items-center justify-center mb-3" style={{ backgroundColor: stat.bg.replace('bg-', '').replace('-50', '') + '20' }}>
                <stat.icon className="h-5 w-5" style={{ color: stat.bg.replace('bg-', '').replace('-50', '') + '600' }} />
              </div>
              <p className="stat-value">{stat.value}</p>
              <p className="stat-label">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="mb-10">
        <div className="mb-6">
          <h2 className="section-divider">Core Engines</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {FEATURES.map((feature) => (
            <div
              key={feature.path}
              className="card p-6 hover:bg-bg-card-hover transition-colors cursor-pointer"
              onClick={() => navigate(feature.path)}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex h-10 w-10 items-center justify-center mb-0" style={{ backgroundColor: 'rgba(217, 119, 6, 0.05)' }}>
                  <feature.icon className="h-5 w-5" style={{ color: 'var(--primary)' }} />
                </div>
              </div>
              <h3 className="mb-3">{feature.title}</h3>
              <p className="text-muted text-sm mb-4">{feature.desc}</p>
              <div className="text-sm text-primary hover:text-primary-hover">
                Learn more →
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Chipflation Snapshot */}
      <section className="mb-10">
        <div className="mb-6">
          <h2 className="section-divider">Live Chipflation Snapshot</h2>
        </div>
        <div class="card">
          <div class="overflow-x-auto">
            <table className="table w-full">
              <thead>
                <tr>
                  <th className="text-left text-muted font-medium text-xs uppercase tracking-wider">Component</th>
                  <th className="text-left text-muted font-medium text-xs uppercase tracking-wider">Risk Level</th>
                  <th className="text-left text-muted font-medium text-xs uppercase tracking-wider">MoM Growth</th>
                  <th className="text-left text-muted font-medium text-xs uppercase tracking-wider">YoY Growth</th>
                  <th className="text-left text-muted font-medium text-xs uppercase tracking-wider">Consumer Impact</th>
                </tr>
              </thead>
              <tbody>
                {CHIPFLATION_DATA.map((row, index) => (
                  <tr key={index} className="border-b border-border hover:bg-bg-card-hover">
                    <td className="p-4 text-sm">{row.component}</td>
                    <td className="p-4 text-sm flex items-center">
                      <span className={`badge badge-${row.risk === 'HIGH' ? 'error' : row.risk === 'CRITICAL' ? 'error' : row.risk === 'STABLE' ? 'success' : 'warning'}`}>
                        {row.risk}
                      </span>
                    </td>
                    <td className="p-4 text-sm font-medium text-danger">{row.mom}</td>
                    <td className="p-4 text-sm font-medium text-danger">{row.yoy}</td>
                    <td className="p-4 text-sm text-muted">{row.impact}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="alert alert-yellow mt-6">
            <span className="alert-icon">⚠️</span>
            <div className="alert-content">
              <strong>Chipflation Alert — AI Infrastructure Cycle Active</strong><br />
              TSMC, SK Hynix, and Micron have shifted capacity toward HBM3E and enterprise AI processors.
              Consumer DRAM and NAND flash remain supply-constrained. Laptop and mobile price inflation
              is expected to persist through Q1 2027.
            </div>
          </div>
        </div>
      </section>

      {/* Sale Calendar Preview */}
      <section className="mb-10">
        <div className="mb-6">
          <h2 className="section-divider">Upcoming Optimal Buy Windows</h2>
        </div>
        <div className="card">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {SALE_EVENTS.map((event) => (
              <div key={event.name} className="text-center p-4">
                <span className="badge badge-outline mb-3">{event.platform}</span>
                <h3 className="mb-2">{event.name}</h3>
                <p className="text-muted text-sm mb-2">{event.date}</p>
                <p className="text-success font-medium mb-2">{event.discount} off</p>
                <p className="text-muted text-sm">{event.cats}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}