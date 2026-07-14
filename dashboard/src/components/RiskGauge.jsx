import './RiskGauge.css';

function getRiskLevel(score) {
  if (score === null || score === undefined) return { label: 'Pending', color: 'var(--text-secondary)' };
  if (score >= 0.7) return { label: 'High Risk', color: 'var(--accent-red)' };
  if (score >= 0.4) return { label: 'Medium Risk', color: 'var(--accent-amber)' };
  return { label: 'Low Risk', color: 'var(--accent-green)' };
}

export default function RiskGauge({ score }) {
  const level = getRiskLevel(score);
  const percent = score !== null && score !== undefined ? Math.round(score * 100) : null;
  const sweepDeg = percent !== null ? (percent / 100) * 360 : 0;

  return (
    <div className="risk-gauge">
      <div
        className="risk-gauge__ring"
        style={{
          '--sweep': `${sweepDeg}deg`,
          '--ring-color': level.color,
        }}
      >
        <div className="risk-gauge__inner">
          <span className="risk-gauge__number">{percent !== null ? `${percent}%` : '—'}</span>
          <span className="risk-gauge__label" style={{ color: level.color }}>{level.label}</span>
        </div>
      </div>
    </div>
  );
}