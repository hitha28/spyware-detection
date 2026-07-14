import './IndicatorList.css';

const SEVERITY_ORDER = { critical: 0, high: 1, medium: 2, low: 3 };

export default function IndicatorList({ indicators }) {
  if (!indicators || indicators.length === 0) {
    return <p className="indicator-empty">No indicators flagged for this scan.</p>;
  }

  const sorted = [...indicators].sort(
    (a, b) => (SEVERITY_ORDER[a.severity] ?? 9) - (SEVERITY_ORDER[b.severity] ?? 9)
  );

  return (
    <ul className="indicator-list">
      {sorted.map((ind, i) => (
        <li key={i} className={`indicator indicator--${ind.severity}`}>
          <span className="indicator__severity">{ind.severity}</span>
          <span className="indicator__source">{ind.source}</span>
          <span className="indicator__description">{ind.description}</span>
        </li>
      ))}
    </ul>
  );
}