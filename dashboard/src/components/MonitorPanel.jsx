import { useState } from 'react';
import { runMonitor } from '../api';
import IndicatorList from './IndicatorList';
import './MonitorPanel.css';

export default function MonitorPanel({ onMonitorComplete }) {
  const [status, setStatus] = useState('idle'); // idle | running | done | error
  const [result, setResult] = useState(null);

  async function handleRun() {
    setStatus('running');
    try {
      const data = await runMonitor();
      setResult(data);
      setStatus('done');
      if (onMonitorComplete) onMonitorComplete();
    } catch (err) {
      setStatus('error');
    }
  }

  return (
    <div className="monitor-panel">
      <h2>Check running processes</h2>
      <p className="monitor-panel__hint">
        Scans currently running processes on this machine for suspicious behavior.
      </p>

      <button onClick={handleRun} disabled={status === 'running'}>
        {status === 'running' ? 'Scanning system…' : 'Run system check'}
      </button>

      {status === 'error' && (
        <p className="monitor-panel__error">Could not reach the monitor service.</p>
      )}

      {result && (
        <div className="monitor-panel__result">
          <p className="monitor-panel__count">
            <span className="monitor-panel__count-number">{result.processes_inspected}</span>
            {' '}processes inspected
          </p>
          <IndicatorList indicators={result.indicators} />
        </div>
      )}
    </div>
  );
}