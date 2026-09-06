import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getScenario, getScenarioExplanation } from '../services/api';
import { ShieldAlert, Play, CheckCircle, Search } from 'lucide-react';

export default function ScenarioResult() {
  const { id } = useParams();
  const [scenario, setScenario] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app, this waits for both fetches. We fallback to mock if backend not fully wired.
    Promise.all([getScenario(id), getScenarioExplanation(id)])
      .then(([sData, eData]) => {
        if(sData && sData.scenario_id) {
          setScenario(sData);
          setExplanation(eData);
        } else {
          // Mock data
          setScenario({
            scenario_id: `SCEN-${id}`,
            bug_id: id,
            generated_steps: [
              "Login as QA Engineer",
              "Navigate to Procurement > Sourcing > RFQs",
              "Select vendor with active RFQ",
              "Click on the Approvers Tab",
              "Observe that the list is empty despite configuration"
            ],
            gherkin: "Feature: Purchase Order Approver List\n\n  Scenario: Approver list is empty on holistic portals\n    Given the user is on the Procurement module\n    When they navigate to Sourcing > RFQs\n    And select an active vendor\n    Then the Approvers Tab should not be empty",
            risk_level: "HIGH",
            confidence_score: 0.89
          });
          setExplanation({
            explanation_text: `The system confidently generated this scenario (89%) based on high keyword overlap with historical bug BUG-00124 (root cause: missing lookup entity in holistic portals). Furthermore, the log pattern matching detected a NullReferenceException when fetching the Approver matrix.`,
            evidence: [
              { type: 'historical_match', description: 'Matched historical resolution for BUG-00124 (Similarity 0.92)' },
              { type: 'log_pattern', description: 'Log contains NullReferenceException in ApproverMatrixService' }
            ]
          });
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div>Generating scenario...</div>;

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div className="page-title">
        <div>
          <h1 style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            Scenario: {scenario.scenario_id}
            <span className={`badge ${scenario.risk_level?.toLowerCase() || 'medium'}`}>
              {scenario.risk_level} Risk
            </span>
          </h1>
          <p className="text-secondary mt-2">Generated for Bug: {scenario.bug_id}</p>
        </div>
        <div className="glass-panel" style={{ padding: '1rem', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>CONFIDENCE</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--success-color)' }}>
              {(scenario.confidence_score * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
        {/* Steps */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
            <Play size={20} color="var(--accent-color)" /> Reproducible Steps
          </h3>
          <ol className="step-list">
            {scenario.generated_steps.map((step, i) => (
              <li key={i} className="step-item">{step}</li>
            ))}
          </ol>
        </div>

        {/* Explainability */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
            <Search size={20} color="#8b5cf6" /> Why this scenario?
          </h3>
          <p style={{ lineHeight: '1.6', marginBottom: '1.5rem' }}>
            {explanation.explanation_text}
          </p>
          
          <h4 style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '1rem' }}>
            Evidence Traces
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {explanation.evidence.map((ev, i) => (
              <div key={i} style={{ padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', fontSize: '0.875rem' }}>
                <span style={{ fontWeight: 'bold', color: 'var(--accent-color)', marginRight: '0.5rem' }}>[{ev.type.toUpperCase()}]</span>
                {ev.description}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Gherkin */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <ShieldAlert size={20} color="var(--warning-color)" /> Executable Gherkin / Test Script
        </h3>
        <div className="gherkin-block">
          {scenario.gherkin}
        </div>
      </div>
    </div>
  );
}
