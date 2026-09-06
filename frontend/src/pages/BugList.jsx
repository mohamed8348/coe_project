import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getBugs } from '../services/api';

export default function BugList() {
  const [bugs, setBugs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Attempt to fetch from backend, fallback to mock if backend empty
    getBugs().then(data => {
      if (data && data.length > 0) {
        setBugs(data);
      } else {
        // Mock data for preview
        setBugs([
          { bug_id: 'BUG-06253', title: 'requisition price mismatch benchmark dynamic application', module: 'Procurement', severity: 'High', date: '2024-03-12' },
          { bug_id: 'BUG-04685', title: 'vendor contract vendor found harness bricksandclicks architecture', module: 'Procurement', severity: 'Medium', date: '2024-03-14' },
          { bug_id: 'BUG-09954', title: 'Purchase Order approver list empty when morph holistic portals', module: 'Procurement', severity: 'Critical', date: '2024-04-01' },
          { bug_id: 'BUG-04963', title: 'Payment fails to post when streamline cutting-edge networks', module: 'Finance', severity: 'Low', date: '2024-04-05' },
        ]);
      }
      setLoading(false);
    });
  }, []);

  return (
    <div>
      <div className="page-title">
        <h1>Bug Reports</h1>
        <p className="text-secondary">Recent bugs ingested into the system.</p>
      </div>

      <div className="glass-panel table-container">
        {loading ? (
          <div className="p-4 text-center">Loading...</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Bug ID</th>
                <th>Module</th>
                <th>Title</th>
                <th>Severity</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {bugs.map((bug, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 500 }}>{bug.bug_id}</td>
                  <td>{bug.module}</td>
                  <td style={{ maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {bug.title}
                  </td>
                  <td>
                    <span className={`badge ${bug.severity?.toLowerCase()}`}>
                      {bug.severity}
                    </span>
                  </td>
                  <td>
                    <Link to={`/scenario/${bug.bug_id}`} className="btn" style={{ padding: '0.4rem 0.8rem', background: 'rgba(255,255,255,0.1)', color: 'white' }}>
                      View Scenario
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
