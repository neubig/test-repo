import type { MigrationStats } from '../types';
import './ProblematicFiles.css';

interface ProblematicFilesProps {
  stats: MigrationStats;
}

export function ProblematicFiles({ stats }: ProblematicFilesProps) {
  const files = stats.top_problematic_files || [];

  if (files.length === 0) {
    return (
      <div className="problematic-files">
        <h3>Most Problematic Files</h3>
        <div className="no-files">No problematic files found! All files are clean. 🎉</div>
      </div>
    );
  }

  return (
    <div className="problematic-files">
      <h3>Most Problematic Files</h3>
      <p className="description">
        Files with the highest number of compatibility issues. Focus on these for maximum impact.
      </p>
      <div className="file-list">
        {files.map((fileInfo, index) => (
          <div key={fileInfo.file} className="file-item">
            <div className="file-rank">{index + 1}</div>
            <div className="file-info">
              <div className="file-path" title={fileInfo.file}>
                {fileInfo.file}
              </div>
              <div className="file-issues">
                <span className="issue-badge">{fileInfo.issues} issue{fileInfo.issues !== 1 ? 's' : ''}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
