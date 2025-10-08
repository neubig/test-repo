import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { MigrationStats } from '../types';
import './IssueCharts.css';

interface IssueChartsProps {
  stats: MigrationStats;
}

const COLORS: Record<string, string> = {
  critical: '#991b1b',
  error: '#ef4444',
  warning: '#f59e0b',
  info: '#3b82f6',
  low: '#6b7280'
};

export function IssueCharts({ stats }: IssueChartsProps) {
  const issueTypesData = Object.entries(stats.issues_by_type)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  const severityData = Object.entries(stats.issues_by_severity)
    .map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value,
      color: COLORS[name.toLowerCase()] || '#6b7280'
    }))
    .filter(item => item.value > 0)
    .sort((a, b) => b.value - a.value);

  return (
    <div className="issue-charts">
      <div className="chart-container">
        <h3>Top Issue Types</h3>
        {issueTypesData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={issueTypesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="no-data">No issues found - migration complete! 🎉</div>
        )}
      </div>

      <div className="chart-container">
        <h3>Issues by Severity</h3>
        {severityData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={severityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {severityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="no-data">No issues by severity</div>
        )}
      </div>
    </div>
  );
}
