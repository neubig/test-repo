export interface MigrationStats {
  timestamp: string;
  scan_path: string;
  summary: {
    total_files: number;
    clean_files: number;
    files_with_issues: number;
    total_issues: number;
    progress_percentage: number;
  };
  issues_by_type: Record<string, number>;
  issues_by_severity: Record<string, number>;
  top_problematic_files: Array<{
    file: string;
    issues: number;
  }>;
}

export interface Comparison {
  progress_percentage?: {
    old: number;
    new: number;
    change: number;
  };
  total_issues?: {
    old: number;
    new: number;
    change: number;
  };
  clean_files?: {
    old: number;
    new: number;
    change: number;
  };
}

export interface StatsData {
  stats: MigrationStats;
  comparison?: Comparison | null;
}
