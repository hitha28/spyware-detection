import { useState } from 'react';
import ScanPanel from './components/ScanPanel';
import MonitorPanel from './components/MonitorPanel';
import ReportsList from './components/ReportsList';
import './App.css';

function App() {
  const [refreshKey, setRefreshKey] = useState(0);

  function triggerRefresh() {
    setRefreshKey((k) => k + 1);
  }

  return (
    <div className="app">
      <header className="app__header">
        <div className="app__brand">
          <span className="app__brand-mark" />
          <h1>SpySentinel</h1>
        </div>
        <p className="app__tagline">Spyware & stalkerware detection</p>
      </header>

      <main className="app__main">
        <section className="app__panels">
          <ScanPanel onScanComplete={triggerRefresh} />
          <MonitorPanel onMonitorComplete={triggerRefresh} />
        </section>

        <section className="app__history">
          <h2>Scan history</h2>
          <ReportsList refreshKey={refreshKey} />
        </section>
      </main>
    </div>
  );
}

export default App;