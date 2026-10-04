import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getScenario, getScenarioExplanation } from '../services/api';
import { ShieldAlert, Play, Search } from 'lucide-react';

export default function ScenarioResult() {
  const { id } = useParams();

  const [scenario, setScenario] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const scenarioData = await getScenario(id);

        let explanationData = null;
        try {
          explanationData = await getScenarioExplanation(id);
        } catch (err) {
          console.warn('Explanation API not available:', err);
        }

        if (scenarioData) {
          setScenario(scenarioData);
        } else {
          throw new Error('No scenario data');
        }

        setExplanation(
          explanationData || {
            explanation_text: 'No explanation available.',
            evidence: [
              {
                type: 'fallback',
                description: 'Backend explanation endpoint not available.'
              }
            ]
          }
        );
      } catch (err) {
        console.error(err);

        setScenario({
          scenario_id: `SCEN-${id}`,
          bug_id: id,
          generated_steps: [
            'Login as QA Engineer',
            'Navigate to ERP Module',
            'Perform the action',
            'Observe the issue'
          ],
          gherkin:
            'Feature: Auto Generated Scenario\n\nScenario: Reproduce Bug',
          risk_level: 'MEDIUM',
          confidence_score: 0.85
        });

        setExplanation({
          explanation_text:
            'Fallback scenario generated because backend data was unavailable.',
          evidence: [
            {
              type: 'fallback',
              description: 'Using local fallback data.'
            }
          ]
        });
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [id]);

  if (loading) {
    return <div>Loading scenario...</div>;
  }

  if (!scenario) {
    return <div>Scenario not found.</div>;
  }

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div className="page-title">
        <h1>
          Scenario: {scenario.scenario_id}
        </h1>

        <p>
          Bug ID: {scenario.bug_id}
        </p>

        <p>
          Risk Level: {scenario.risk_level}
        </p>

        <p>
          Confidence:{' '}
          {scenario.confidence_score
            ? (scenario.confidence_score * 100).toFixed(0)
            : 0}
          %
        </p>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '20px'
        }}
      >
        <div className="glass-panel" style={{ padding: '20px' }}>
          <h3>
            <Play size={18} /> Reproduction Steps
          </h3>

          <ol>
            {(scenario.generated_steps || []).map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ol>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <h3>
            <Search size={18} /> Explanation
          </h3>

          <p>
            {explanation?.explanation_text ||
              'No explanation available'}
          </p>

          {(explanation?.evidence || []).map((item, index) => (
            <div key={index}>
              <strong>{item.type}</strong> - {item.description}
            </div>
          ))}
        </div>
      </div>

      <div
        className="glass-panel"
        style={{ padding: '20px', marginTop: '20px' }}
      >
        <h3>
          <ShieldAlert size={18} /> Gherkin Script
        </h3>

        <pre>
          {scenario.gherkin || 'No gherkin available'}
        </pre>
      </div>
    </div>
  );
}