import React from 'react';
import { Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, Bug, List, Activity } from 'lucide-react';

import Dashboard from './pages/Dashboard';
import UploadBug from './pages/UploadBug';
import BugList from './pages/BugList';
import ScenarioResult from './pages/ScenarioResult';

function Sidebar() {
  const navItems = [
    { to: '/', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
    { to: '/upload', icon: <Bug size={20} />, label: 'Report Bug' },
    { to: '/bugs', icon: <List size={20} />, label: 'Bug Reports' },
  ];

  return (
    <aside className="sidebar glass-panel">
      <div className="sidebar-header">
        <Activity className="logo-icon" size={28} />
        <h2 className="logo-text">AutoRepro</h2>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink 
            key={item.to} 
            to={item.to} 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

function App() {
  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<UploadBug />} />
          <Route path="/bugs" element={<BugList />} />
          <Route path="/scenario/:id" element={<ScenarioResult />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
