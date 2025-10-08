import { useState, useEffect } from 'react';
import type { StatsData } from '../types';
import { StatsSummary } from './StatsSummary';
import { IssueCharts } from './IssueCharts';
import { ProblematicFiles } from './ProblematicFiles';
import './Dashboard.css';

export function Dashboard() {
  const [statsData, setStatsData] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to load from default location
      const response = await fetch('/migration-stats.json');
      
      if (!response.ok) {
        throw new Error('Stats file not found');
      }
      
      const data = await response.json();
      setStatsData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target?.result as string;
        const data = JSON.parse(text);
        setStatsData(data);
        setError(null);
      } catch (err) {
        setError('Invalid JSON file');
      }
    };
    reader.readAsText(file);
  };

  if (loading) {
    return (
      <div className="dashboard loading">
        <div className="loading-spinner"></div>
        <p>Loading migration statistics...</p>
      </div>
    );
  }

  if (error || !statsData) {
    return (
      <div className="dashboard error">
        <div className="error-message">
          <h2>📊 Migration Statistics Dashboard</h2>
          <p className="error-text">
            {error || 'No statistics file found'}
          </p>
          <div className="instructions">
            <h3>How to generate statistics:</h3>
            <ol>
              <li>Run the stats collection command:
                <code>./py2to3 stats collect src/ --format json --output migration-stats.json</code>
              </li>
              <li>Place the <code>migration-stats.json</code> file in the <code>public/</code> directory</li>
              <li>Refresh this page</li>
            </ol>
            <p className="or-text">OR</p>
            <div className="upload-section">
              <label htmlFor="file-upload" className="upload-button">
                Upload Stats File
              </label>
              <input
                id="file-upload"
                type="file"
                accept=".json"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>📊 Python 2 to 3 Migration Dashboard</h1>
        <button onClick={loadStats} className="refresh-button">
          🔄 Refresh
        </button>
      </header>

      <StatsSummary stats={statsData.stats} comparison={statsData.comparison} />
      
      <IssueCharts stats={statsData.stats} />
      
      <ProblematicFiles stats={statsData.stats} />

      <footer className="dashboard-footer">
        <div className="upload-section-small">
          <label htmlFor="file-upload-footer" className="upload-link">
            Upload different stats file
          </label>
          <input
            id="file-upload-footer"
            type="file"
            accept=".json"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
        </div>
      </footer>
    </div>
  );
}
