# Migration Statistics Dashboard

An interactive web dashboard for visualizing Python 2 to 3 migration progress.

## Features

- **Progress Overview**: Visual representation of migration completion percentage
- **Statistics Summary**: Key metrics including total files, clean files, and issue counts
- **Interactive Charts**: 
  - Bar chart showing top issue types
  - Pie chart showing issue distribution by severity
- **Problematic Files List**: Ranked list of files with the most compatibility issues
- **Comparison Tracking**: View progress changes since the last scan
- **File Upload**: Load stats from any location

## Quick Start

### 1. Generate Statistics

From your project root, run:

```bash
./py2to3 stats collect src/ --format json --output my-vite-app/public/migration-stats.json
```

This will scan your Python code and generate a JSON file with migration statistics.

### 2. Start the Dashboard

```bash
cd my-vite-app
npm install  # First time only
npm run dev
```

The dashboard will open in your browser at `http://localhost:5173`

### 3. View Your Stats

The dashboard will automatically load the stats from the public directory. You can also:

- Click "Refresh" to reload stats after a new scan
- Click "Upload Stats File" to load stats from a different location

## Building for Production

To create an optimized production build:

```bash
npm run build
```

The built files will be in the `dist/` directory. You can serve them with any static file server:

```bash
npm run preview  # Preview the production build
```

## Stats File Format

The dashboard expects a JSON file with the following structure:

```json
{
  "stats": {
    "timestamp": "2024-01-01T12:00:00",
    "scan_path": "src/",
    "summary": {
      "total_files": 100,
      "clean_files": 75,
      "files_with_issues": 25,
      "total_issues": 150,
      "progress_percentage": 75.0,
      "critical_issues": 5,
      "high_issues": 20,
      "medium_issues": 75,
      "low_issues": 50
    },
    "issue_types": {
      "print_statement": 45,
      "unicode_literal": 30,
      "division_operator": 25
    },
    "most_problematic_files": [
      ["src/old_module.py", 25],
      ["src/legacy.py", 18]
    ]
  },
  "comparison": {
    "progress_change": 5.0,
    "issues_resolved": 20,
    "issues_introduced": 0,
    "clean_files_added": 10,
    "previous_scan": "2024-01-01T10:00:00"
  },
  "generated_at": "2024-01-01T12:00:00"
}
```

## Technology Stack

- **React 18**: Modern UI library
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **Recharts**: Responsive charting library
- **CSS3**: Custom styling with modern features

## Development

### Project Structure

```
my-vite-app/
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx       # Main dashboard container
│   │   ├── StatsSummary.tsx    # Statistics overview
│   │   ├── IssueCharts.tsx     # Chart visualizations
│   │   ├── ProblematicFiles.tsx # File list
│   │   └── *.css               # Component styles
│   ├── types.ts                # TypeScript type definitions
│   ├── App.tsx                 # App entry point
│   └── main.tsx                # React entry point
├── public/                     # Static files
│   └── migration-stats.json    # Generated stats file
└── package.json
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Tips

1. **Regular Scans**: Run stats collection regularly to track progress over time
2. **Compare Mode**: Use the `--compare` flag with stats command to see changes
3. **Focus on Critical**: The dashboard highlights critical and high-severity issues
4. **File Upload**: Useful for sharing stats files with team members
5. **Production Deploy**: Deploy the built dashboard to see progress on any device

## Integration with CI/CD

You can generate stats as part of your CI pipeline:

```yaml
# Example GitHub Actions workflow
- name: Generate Migration Stats
  run: |
    ./py2to3 stats collect src/ --format json --output migration-stats.json
    
- name: Upload Stats Artifact
  uses: actions/upload-artifact@v2
  with:
    name: migration-stats
    path: migration-stats.json
```

Then download and view the stats in the dashboard.
