# Parallel Migration Runner Guide

## Overview

The **Parallel Migration Runner** is a high-performance feature that enables concurrent processing of migration operations across multiple files simultaneously. This dramatically speeds up large codebase migrations by leveraging multi-core processors.

## 🚀 Key Features

- **Multi-core Processing**: Utilizes all available CPU cores for maximum speed
- **Automatic Work Distribution**: Intelligently distributes files across worker processes
- **Progress Tracking**: Real-time progress indicators showing completion status
- **Aggregated Results**: Comprehensive summary of all operations
- **Error Handling**: Graceful error handling with detailed error reporting
- **Flexible Configuration**: Customize worker count and processing options
- **Performance Metrics**: Detailed timing and speedup calculations
- **JSON Export**: Export results for further analysis or CI/CD integration

## Why Use Parallel Processing?

### Performance Benefits

For large codebases, parallel processing can provide significant speedups:

- **2-4 cores**: ~3x faster than serial processing
- **8 cores**: ~6-7x faster than serial processing  
- **16+ cores**: ~10-15x faster than serial processing

### Example Speedup

```bash
# Serial processing: 100 files in 120 seconds
# Parallel (8 cores): 100 files in 18 seconds (~6.7x faster!)
```

## Quick Start

### Basic Usage

Check all files in a directory:
```bash
./py2to3 parallel check src/
```

Fix all files in parallel:
```bash
./py2to3 parallel fix src/ --backup
```

### With Custom Worker Count

```bash
# Use 4 workers
./py2to3 parallel check src/ --workers 4

# Use 8 workers for faster processing
./py2to3 parallel fix src/ --workers 8 --backup
```

## Command Reference

### Check Operation

Check multiple files for Python 3 compatibility in parallel:

```bash
./py2to3 parallel check <path> [options]
```

**Options:**
- `--workers, -w <N>`: Number of worker processes (default: CPU count)
- `--recursive, -r`: Recursively process subdirectories (default: True)
- `--json, -j <FILE>`: Export results as JSON
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Check src directory with all cores
./py2to3 parallel check src/

# Check with 4 workers and export results
./py2to3 parallel check src/ --workers 4 --json results.json

# Check single directory (non-recursive)
./py2to3 parallel check src/ --no-recursive
```

### Fix Operation

Fix multiple files for Python 3 compatibility in parallel:

```bash
./py2to3 parallel fix <path> [options]
```

**Options:**
- `--workers, -w <N>`: Number of worker processes (default: CPU count)
- `--backup, -b`: Create backups before fixing
- `--dry-run`: Preview changes without applying them
- `--recursive, -r`: Recursively process subdirectories (default: True)
- `--json, -j <FILE>`: Export results as JSON
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Fix all files with backup
./py2to3 parallel fix src/ --backup

# Preview fixes without applying
./py2to3 parallel fix src/ --dry-run

# Fix with 4 workers and backup
./py2to3 parallel fix src/ --workers 4 --backup

# Fix and export results
./py2to3 parallel fix src/ --backup --json fixes.json
```

## Output Format

### Progress Output

During execution, you'll see real-time progress:

```
🚀 Starting parallel compatibility check with 8 workers...
📁 Checking 47 files

  [1/47] ✓ src/fixer.py 
  [2/47] ✗ src/core/engine.py (3 issues)
  [3/47] ✓ src/verifier.py 
  ...
```

### Summary Report

After completion, a comprehensive summary is displayed:

```
======================================================================
📊 Parallel Check Summary
======================================================================

⚙️  Configuration:
   Workers: 8
   Total files: 47

📈 Results:
   ✓ Successful: 45
   ✗ Failed: 2
   ⚠️  Total issues: 12

⏱️  Performance:
   Time: 8.45s
   Speed: 5.56 files/second
   Speedup: ~6.7x faster than serial processing

======================================================================
```

## JSON Export Format

The `--json` option exports detailed results:

```json
{
  "total_files": 47,
  "successful": 45,
  "failed": 2,
  "total_issues": 12,
  "elapsed_time": 8.45,
  "files_per_second": 5.56,
  "workers": 8,
  "results": [
    {
      "file": "src/fixer.py",
      "success": true,
      "issues": 0
    },
    {
      "file": "src/core/engine.py",
      "success": true,
      "issues": 3,
      "issue_details": [...]
    }
  ]
}
```

## Use Cases

### 1. Large Codebase Migration

Speed up initial compatibility check:
```bash
# Check 500+ files in minutes instead of hours
./py2to3 parallel check large_project/ --workers 16 --json initial-check.json
```

### 2. Continuous Integration

Integrate with CI pipelines:
```bash
# Fast compatibility check on every commit
./py2to3 parallel check src/ --json ci-results.json
if [ $? -ne 0 ]; then
  echo "Python 3 compatibility issues detected!"
  exit 1
fi
```

### 3. Batch Fixing

Apply fixes to entire codebase quickly:
```bash
# Fix with backup, then review changes
./py2to3 parallel fix src/ --backup --workers 8
git diff
```

### 4. Pre-Migration Assessment

Quick assessment before starting migration:
```bash
# Dry run to see what would be fixed
./py2to3 parallel fix src/ --dry-run --json assessment.json
```

## Performance Tips

### Optimal Worker Count

The optimal number of workers depends on your system:

- **CPU-bound tasks**: Use number of CPU cores (`multiprocessing.cpu_count()`)
- **I/O-bound tasks**: Can use more workers than cores (1.5x to 2x cores)
- **Memory constraints**: Reduce workers if running out of memory

### When to Use Parallel Processing

✅ **Good for:**
- Large codebases (50+ files)
- Initial compatibility scans
- Batch fixing operations
- CI/CD integration

❌ **Overkill for:**
- Small projects (<10 files)
- Single file operations
- Interactive reviewing

### Benchmarking

To see actual speedup on your system:

```bash
# Time serial check
time ./py2to3 check src/

# Time parallel check  
time ./py2to3 parallel check src/

# Compare times
```

## Programmatic Usage

Use the parallel runner in your own scripts:

```python
from parallel_runner import ParallelMigrationRunner, collect_python_files

# Collect files
files = collect_python_files('src/', recursive=True)

# Create runner with 8 workers
runner = ParallelMigrationRunner(workers=8, verbose=True)

# Check files
summary = runner.check_files(files)
runner.print_summary(summary, operation='check')

# Fix files
summary = runner.fix_files(files, backup=True, dry_run=False)
runner.print_summary(summary, operation='fix')
```

## Troubleshooting

### ImportError or Module Not Found

If you see import errors, ensure the src directory is in your Python path:

```bash
export PYTHONPATH="$PYTHONPATH:/path/to/test-repo/src"
```

### Out of Memory Errors

Reduce the number of workers:

```bash
./py2to3 parallel check src/ --workers 2
```

### Processes Hanging

This can happen with very large files. Try:
1. Reduce worker count
2. Process large files separately
3. Increase system resources

### Unexpected Results

For debugging, use single-threaded mode first:

```bash
# Debug individual files first
./py2to3 check src/problematic_file.py

# Then try parallel
./py2to3 parallel check src/ --verbose
```

## Best Practices

1. **Always use `--backup` when fixing**: Create backups before applying fixes
2. **Use `--dry-run` first**: Preview changes before applying
3. **Export results**: Use `--json` for record-keeping
4. **Start with check**: Run `parallel check` before `parallel fix`
5. **Review changes**: Always review changes after parallel fixing
6. **Test after fixing**: Run your test suite after migration
7. **Incremental approach**: Process subdirectories separately for better control

## Integration with Other Tools

### With Git Integration

```bash
# Create a branch for parallel migration
./py2to3 git create-branch feature/parallel-migration

# Run parallel fixes
./py2to3 parallel fix src/ --backup

# Review and commit
git diff
git add -A
git commit -m "Apply parallel migration fixes"
```

### With Rollback

```bash
# Fix files in parallel
./py2to3 parallel fix src/ --backup

# If something goes wrong, rollback
./py2to3 rollback
```

### With Quality Checks

```bash
# Parallel fix
./py2to3 parallel fix src/ --backup

# Quality check
./py2to3 quality src/

# Lint check
./py2to3 lint src/
```

## FAQ

**Q: Is parallel processing always faster?**
A: For small projects (<10 files), the overhead of creating processes may negate benefits. For 50+ files, you'll see significant speedups.

**Q: Can I use this in CI/CD?**
A: Yes! The `--json` output and exit codes make it perfect for CI/CD integration.

**Q: What about race conditions?**
A: Each file is processed independently with no shared state, so race conditions are not an issue.

**Q: How is this different from `xargs -P`?**
A: This provides aggregated results, progress tracking, error handling, and integration with the migration toolkit.

**Q: Can I parallelize other operations?**
A: Currently supports check and fix. More operations may be added in future versions.

## See Also

- [PERFORMANCE_GUIDE.md](PERFORMANCE_GUIDE.md) - Performance optimization tips
- [CLI_GUIDE.md](CLI_GUIDE.md) - Complete CLI reference
- [QUICK_START.md](QUICK_START.md) - Getting started guide

---

**Speed up your migration with parallel processing! 🚀**
