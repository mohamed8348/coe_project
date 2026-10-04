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
    severity: 'HIGH',
    priority: 'P2',
    reporter_role: 'QA Tester'
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...formData,
        report_date: new Date().toISOString(),
        ui_page: 'Dashboard',
        expected_behavior: 'System should work normally',
        actual_behavior: formData.description
      };

      const result = await submitBug(payload);

      navigate(
        `/scenario/${result.scenario_id || result.id || formData.bug_id}`
      );
    } catch (err) {
      console.error(err);
      alert('Submission failed. Check backend logs.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-title">
        <h1>Report a Bug</h1>
        <p className="text-secondary">
          Ingest a new bug report to generate a reproduction scenario.
        </p>
      </div>

      <form className="form-container glass-panel" onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Bug ID</label>
          <input
            className="form-input"
            name="bug_id"
            value={formData.bug_id}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Module</label>
          <select
            className="form-select"
            name="module"
            value={formData.module}
            onChange={handleChange}
          >
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
          <select
            className="form-select"
            name="severity"
            value={formData.severity}
            onChange={handleChange}
          >
            <option>CRITICAL</option>
            <option>HIGH</option>
            <option>MEDIUM</option>
            <option>LOW</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Priority</label>
          <select
            className="form-select"
            name="priority"
            value={formData.priority}
            onChange={handleChange}
          >
            <option>P1</option>
            <option>P2</option>
            <option>P3</option>
            <option>P4</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Title</label>
          <input
            className="form-input"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            placeholder="Short description of the issue"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Description (User Report)</label>
          <textarea
            className="form-textarea"
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
            placeholder="Paste the raw bug report here..."
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? <Cpu className="animate-spin" /> : <Send size={18} />}
          {loading ? 'Processing...' : 'Generate Scenario'}
        </button>
      </form>
    </div>
  );
}