import { useEffect, useState } from 'react';
import { listReports } from '../api';
import './ReportsList.css';

function scoreColor(score) {
  if (score === null || score === undefined) return 'var(--text-secondary)';
  if (score >= 0.7) return 'var(--accent-red)';
  if (score >= 0.4) return 'var(--accent-amber)';
  return 'var(--accent-green)';
}

function formatTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleString(undefined, {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  });
}

export default function ReportsList({ refreshKey }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    listReports().then((data) => {
      if (!cancelled) {
        setReports(data);
        setLoading(false);
      }
    });
    return () => { cancelled = true; };
  }, [refreshKey]);

  if (loading) return <p className="reports-empty">Loading scan history…</p>;
  if (reports.length === 0) return <p className="reports-empty">No scans yet. Run one above to see it here.</p>;

  return (
    <table className="reports-table">
      <thead>
        <tr>
          <th>File</th>
          <th>Type</th>
          <th>Status</th>
          <th>Risk</th>
          <th>When</th>
        </tr>
      </thead>
      <tbody>
        {reports.map((r) => (
          <tr key={r.scan_id}>
            <td className="reports-table__filename">{r.filename}</td>
            <td className="reports-table__mono">{r.file_type}</td>
            <td className="reports-table__mono">{r.status}</td>
            <td>
              {r.final_score !== null ? (
                <span
                  className="reports-table__score"
                  style={{ color: scoreColor(r.final_score) }}
                >
                  {Math.round(r.final_score * 100)}%
                </span>
              ) : (
                <span className="reports-table__mono">—</span>
              )}
            </td>
            <td className="reports-table__mono">{formatTime(r.created_at)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}