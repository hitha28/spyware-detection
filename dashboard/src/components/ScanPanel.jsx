import { useState } from 'react';
import { scanFile, getReport } from '../api';
import RiskGauge from './RiskGauge';
import IndicatorList from './IndicatorList';
import './ScanPanel.css';

export default function ScanPanel({ onScanComplete }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); // idle | scanning | done | error
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  async function handleScan() {
    if (!file) return;
    setStatus('scanning');
    setResult(null);
    setErrorMsg('');

    try {
      const initial = await scanFile(file);

      if (initial.error) {
        setStatus('error');
        setErrorMsg(initial.message || 'This file type is not supported yet.');
        return;
      }

      const scanId = initial.scan_id;
      pollForResult(scanId);
    } catch (err) {
      setStatus('error');
      setErrorMsg('Could not reach the scan service. Is the API running?');
    }
  }

  function pollForResult(scanId, attempt = 0) {
    if (attempt > 20) {
      setStatus('error');
      setErrorMsg('Scan is taking longer than expected.');
      return;
    }
    setTimeout(async () => {
      const report = await getReport(scanId);
      if (report.status === 'done' || report.status === 'failed') {
        setResult(report);
        setStatus(report.status === 'done' ? 'done' : 'error');
        if (report.status === 'failed') {
          setErrorMsg('This file type could not be analyzed.');
        }
        if (onScanComplete) onScanComplete();
      } else {
        pollForResult(scanId, attempt + 1);
      }
    }, 800);
  }

  return (
    <div className="scan-panel">
      <h2>Scan a file</h2>
      <p className="scan-panel__hint">Upload an APK to check for spyware indicators.</p>

      <div className="scan-panel__upload">
        <input
          type="file"
          id="file-input"
          onChange={(e) => setFile(e.target.files[0])}
          disabled={status === 'scanning'}
        />
        <button onClick={handleScan} disabled={!file || status === 'scanning'}>
          {status === 'scanning' ? 'Scanning…' : 'Scan file'}
        </button>
      </div>

      {status === 'error' && <p className="scan-panel__error">{errorMsg}</p>}

      {result && result.status === 'done' && (
        <div className="scan-panel__result">
          <RiskGauge score={result.final_score} />
          <div className="scan-panel__meta">
            <span>{result.filename}</span>
            <span className="scan-panel__meta-sep">·</span>
            <span>{result.file_type}</span>
          </div>
          <IndicatorList indicators={result.indicators} />
        </div>
      )}
    </div>
  );
}