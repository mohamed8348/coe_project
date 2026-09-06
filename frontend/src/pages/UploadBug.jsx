import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, Cpu } from 'lucide-react';
import { submitBug } from '../services/api';

export default function UploadBug() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    bug_id: 'BUG-MANUAL-' + Math.floor(Math.random() * 1000),
    title: '',
    description: '',
    module: 'Finance',
    severity: 'High'
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const result = await submitBug(formData);
      // Assuming result returns the generated scenario_id
      navigate(`/scenario/${result.scenario_id || result.id || formData.bug_id}`);
    } catch (err) {
      console.error(err);
      alert("Submission failed. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-title">
        <h1>Report a Bug</h1>
        <p className="text-secondary">Ingest a new bug report to generate a reproduction scenario.</p>
      </div>

      <form className="form-container glass-panel" onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Bug ID</label>
          <input className="form-input" name="bug_id" value={formData.bug_id} onChange={handleChange} required />
        </div>

        <div className="form-group">
          <label className="form-label">Module</label>
          <select className="form-select" name="module" value={formData.module} onChange={handleChange}>
            <option>Finance</option>
            <option>HR</option>
            <option>Payroll</option>
            <option>Procurement</option>
            <option>Inventory</option>
            <option>Manufacturing</option>
            <option>CRM</option>
            <option>Sales</option>
            <option>Compliance</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Severity</label>
          <select className="form-select" name="severity" value={formData.severity} onChange={handleChange}>
            <option>Critical</option>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Title</label>
          <input className="form-input" name="title" value={formData.title} onChange={handleChange} required placeholder="Short description of the issue" />
        </div>

        <div className="form-group">
          <label className="form-label">Description (User Report)</label>
          <textarea 
            className="form-textarea" 
            name="description" 
            value={formData.description} 
            onChange={handleChange} 
            required
            placeholder="Paste the raw, messy user report here..."
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? <Cpu className="animate-spin" /> : <Send size={18} />}
          {loading ? 'Processing...' : 'Generate Scenario'}
        </button>
      </form>
    </div>
  );
}
