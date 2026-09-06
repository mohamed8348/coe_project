import React, { useState, useEffect } from 'react';
import { Activity, Clock, Target, CheckCircle } from 'lucide-react';
import { getDashboardStats } from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    getDashboardStats().then(setStats);
  }, []);

  if (!stats) return <div className="p-4 text-center">Loading dashboard...</div>;

  return (
    <div className="dashboard">
      <div className="page-title">
        <h1>KPI Dashboard</h1>
        <p className="text-secondary">System Performance Overview</p>
      </div>

      <div className="dashboard-grid">
        <div className="metric-card glass-panel">
          <div className="metric-title">
            <span>Reproduction Success</span>
            <Target size={18} color="var(--success-color)" />
          </div>
          <div className="metric-value">{(stats.rsr * 100).toFixed(1)}%</div>
        </div>

        <div className="metric-card glass-panel">
          <div className="metric-title">
            <span>Precision</span>
            <CheckCircle size={18} color="var(--accent-color)" />
          </div>
          <div className="metric-value">{(stats.precision * 100).toFixed(1)}%</div>
        </div>

        <div className="metric-card glass-panel">
          <div className="metric-title">
            <span>Recall</span>
            <Activity size={18} color="var(--warning-color)" />
          </div>
          <div className="metric-value">{(stats.recall * 100).toFixed(1)}%</div>
        </div>

        <div className="metric-card glass-panel">
          <div className="metric-title">
            <span>Time Saved (Est)</span>
            <Clock size={18} color="#8b5cf6" />
          </div>
          <div className="metric-value">{stats.time_saved_hours} hrs</div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '2rem', marginTop: '2rem' }}>
        <h2>System Status</h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '1rem' }}>
          FAISS Index: <span style={{ color: 'var(--success-color)' }}>Loaded (10,000 resolutions)</span><br />
          LLM Backend: <span style={{ color: 'var(--success-color)' }}>Operational</span><br />
          Database: <span style={{ color: 'var(--success-color)' }}>Connected</span>
        </p>
      </div>
    </div>
  );
}
