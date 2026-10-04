import React, { useState, useEffect } from "react";
import { getBugs } from "../services/api";

export default function BugList() {
  const [bugs, setBugs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBugs();
  }, []);

  const loadBugs = async () => {
    try {
      const data = await getBugs();

      if (Array.isArray(data)) {
        setBugs(data);
      } else {
        setBugs([]);
      }
    } catch (err) {
      console.error(err);
      setBugs([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-title">
        <h1>Bug Reports</h1>
        <p className="text-secondary">
          Submitted bugs available in the system.
        </p>
      </div>

      <div className="glass-panel table-container">
        {loading ? (
          <div style={{ padding: "20px" }}>Loading...</div>
        ) : (
          <table style={{ width: "100%" }}>
            <thead>
              <tr>
                <th>Bug ID</th>
                <th>Module</th>
                <th>Title</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Created Date</th>
              </tr>
            </thead>

            <tbody>
              {bugs.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: "center" }}>
                    No bugs found
                  </td>
                </tr>
              ) : (
                bugs.map((bug, index) => (
                  <tr key={index}>
                    <td>{bug.bug_id}</td>

                    <td>{bug.module}</td>

                    <td>{bug.title}</td>

                    <td>
                      <span
                        className={`badge ${
                          bug.severity
                            ? bug.severity.toLowerCase()
                            : "medium"
                        }`}
                      >
                        {bug.severity}
                      </span>
                    </td>

                    <td>
                      <span
                        style={{
                          color: "#22c55e",
                          fontWeight: "bold",
                        }}
                      >
                        Generated
                      </span>
                    </td>

                    <td>
                      {bug.report_date
                        ? new Date(bug.report_date).toLocaleDateString()
                        : "-"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}