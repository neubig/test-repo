import type { MigrationStats, Comparison } from '../types';
import './StatsSummary.css';

interface StatsSummaryProps {
  stats: MigrationStats;
  comparison?: Comparison | null;
}

export function StatsSummary({ stats, comparison }: StatsSummaryProps) {
  const { summary } = stats;

  return (
    <div className="stats-summary">
      <h2>Migration Progress Summary</h2>
      
      <div className="progress-circle">
        <svg viewBox="0 0 100 100" className="circular-progress">
          <circle
            className="circle-bg"
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="8"
          />
          <circle
            className="circle-progress"
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="#10b981"
            strokeWidth="8"
            strokeDasharray={`${summary.progress_percentage * 2.51327} 251.327`}
            strokeLinecap="round"
            transform="rotate(-90 50 50)"
          />
          <text x="50" y="50" className="progress-text" textAnchor="middle" dominantBaseline="middle">
            <tspan className="progress-value">{summary.progress_percentage.toFixed(1)}%</tspan>
          </text>
        </svg>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Files</div>
          <div className="stat-value">{summary.total_files}</div>
        </div>
        
        <div className="stat-card success">
          <div className="stat-label">Clean Files</div>
          <div className="stat-value">{summary.clean_files}</div>
          {comparison?.clean_files && comparison.clean_files.change !== 0 && (
            <div className={`stat-change ${comparison.clean_files.change > 0 ? 'positive' : 'negative'}`}>
              {comparison.clean_files.change > 0 ? '+' : ''}{comparison.clean_files.change}
            </div>
          )}
        </div>
        
        <div className="stat-card warning">
          <div className="stat-label">Files with Issues</div>
          <div className="stat-value">{summary.files_with_issues}</div>
        </div>
        
        <div className="stat-card danger">
          <div className="stat-label">Total Issues</div>
          <div className="stat-value">{summary.total_issues}</div>
          {comparison?.total_issues && comparison.total_issues.change !== 0 && (
            <div className={`stat-change ${comparison.total_issues.change < 0 ? 'positive' : 'negative'}`}>
              {comparison.total_issues.change > 0 ? '+' : ''}{comparison.total_issues.change}
            </div>
          )}
        </div>
      </div>

      <div className="severity-breakdown">
        <h3>Issues by Severity</h3>
        <div className="severity-grid">
          {Object.entries(stats.issues_by_severity).map(([severity, count]) => (
            <div key={severity} className={`severity-item ${severity}`}>
              <span className="severity-label">{severity.charAt(0).toUpperCase() + severity.slice(1)}</span>
              <span className="severity-count">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {comparison && (
        <div className="comparison-info">
          <h3>Changes Since Last Scan</h3>
          {comparison.progress_percentage && (
            <p className={comparison.progress_percentage.change >= 0 ? 'positive' : 'negative'}>
              Progress: {comparison.progress_percentage.change >= 0 ? '+' : ''}{comparison.progress_percentage.change.toFixed(2)}%
            </p>
          )}
          {comparison.total_issues && (
            <p className={comparison.total_issues.change <= 0 ? 'positive' : 'negative'}>
              Issues: {comparison.total_issues.change > 0 ? '+' : ''}{comparison.total_issues.change}
            </p>
          )}
          {comparison.clean_files && (
            <p className={comparison.clean_files.change >= 0 ? 'positive' : 'negative'}>
              Clean Files: {comparison.clean_files.change >= 0 ? '+' : ''}{comparison.clean_files.change}
            </p>
          )}
        </div>
      )}

      <div className="scan-info">
        <p className="scan-time">
          Last scanned: {new Date(stats.timestamp).toLocaleString()}
        </p>
        <p className="scan-path">Path: {stats.scan_path}</p>
      </div>
    </div>
  );
}
