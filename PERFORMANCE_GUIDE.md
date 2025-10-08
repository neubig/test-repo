# Performance Benchmark Guide

## Overview

The Performance Benchmark tool helps you quantify the performance improvements from migrating Python 2 code to Python 3. It compares execution time and provides detailed metrics to demonstrate the value of migration.

## Why Benchmark Performance?

- **Demonstrate ROI**: Show concrete performance improvements to stakeholders
- **Catch Regressions**: Identify performance issues before they reach production
- **Guide Optimization**: Highlight which modules benefited most from Python 3
- **Track Progress**: Monitor performance improvements over time
- **Make Informed Decisions**: Use data to prioritize migration efforts

## Quick Start

### Basic Usage

Benchmark a single file:
```bash
./py2to3 bench src/fixer.py
```

Benchmark an entire directory:
```bash
./py2to3 bench src/
```

### Save Report to File

```bash
./py2to3 bench src/ --output performance_report.txt
```

### JSON Output for CI/CD

```bash
./py2to3 bench src/ --format json --output performance.json
```

## Command Options

```bash
./py2to3 bench [PATH] [OPTIONS]
```

### Arguments

- `path` - File or directory to benchmark (default: src)

### Options

- `-i, --iterations NUM` - Number of iterations per benchmark (default: 100)
  - Higher values provide more accurate results but take longer
  - Recommended: 100-1000 for reliable measurements

- `-t, --timeout SEC` - Timeout per file in seconds (default: 30)
  - Prevents benchmarks from hanging on problematic code
  - Adjust based on your codebase complexity

- `-o, --output FILE` - Save report to file
  - Text format by default
  - Use with `--format json` for machine-readable output

- `-f, --format FORMAT` - Output format: `text` or `json` (default: text)
  - `text`: Human-readable report with summaries
  - `json`: Structured data for automation and CI/CD

- `--python2 CMD` - Python 2 command (default: python2)
  - Use if Python 2 is installed with a different name
  - Example: `--python2 python2.7`

- `--python3 CMD` - Python 3 command (default: python3)
  - Use if Python 3 is installed with a different name
  - Example: `--python3 python3.9`

## Understanding Results

### Summary Metrics

The benchmark report includes:

- **Total files benchmarked**: Number of Python files analyzed
- **Successfully completed**: Benchmarks that completed without errors
- **Errors**: Files that couldn't be benchmarked
- **Average speedup**: Mean performance improvement across all files
- **Performance improvements**: Files where Python 3 is faster (>5% improvement)
- **Performance regressions**: Files where Python 3 is slower (>5% slower)

### Interpreting Speedup

- **Speedup > 1.05x**: Python 3 is significantly faster (>5% improvement)
  - ✓ Great result! Highlight these improvements to stakeholders
  
- **Speedup 0.95x - 1.05x**: Similar performance (within 5%)
  - ○ No significant change - focus on other benefits
  
- **Speedup < 0.95x**: Python 3 is slower (>5% regression)
  - ✗ Investigate these cases - may need optimization

### Performance Change Percentage

Shows the relative performance difference:
- **Positive %**: Python 3 is faster (improvement)
- **Negative %**: Python 3 is slower (regression)
- **Example**: +25% means Python 3 is 25% faster

## Common Use Cases

### 1. Initial Assessment

Before starting migration, benchmark your Python 2 code to establish baselines:

```bash
# Benchmark current Python 2 code
./py2to3 bench src/ --iterations 1000 --output baseline_py2.txt

# Save metrics for comparison later
./py2to3 bench src/ --format json --output baseline_py2.json
```

### 2. Track Migration Progress

Benchmark after each migration phase:

```bash
# After fixing imports
./py2to3 bench src/ --output after_imports.txt

# After fixing syntax
./py2to3 bench src/ --output after_syntax.txt

# Final benchmark
./py2to3 bench src/ --output final_performance.txt
```

### 3. Identify Performance Gains

Focus on modules with significant improvements:

```bash
# Benchmark specific high-value modules
./py2to3 bench src/core/ --iterations 500 --output core_performance.txt
./py2to3 bench src/data/ --iterations 500 --output data_performance.txt
```

### 4. CI/CD Integration

Automate performance tracking in your pipeline:

```bash
# Generate JSON report for automated analysis
./py2to3 bench src/ --format json --output performance.json

# Parse results in your CI script
python -c "import json; data = json.load(open('performance.json')); 
           print(f'Average speedup: {data[\"summary\"][\"avg_speedup\"]:.2f}x')"
```

### 5. Compare Python Versions

Test with different Python versions:

```bash
# Compare Python 2.7 vs Python 3.8
./py2to3 bench src/ --python2 python2.7 --python3 python3.8 --output py38_comparison.txt

# Compare Python 2.7 vs Python 3.11 (latest features)
./py2to3 bench src/ --python2 python2.7 --python3 python3.11 --output py311_comparison.txt
```

## Real-World Examples

### Example 1: String Processing Module

```bash
./py2to3 bench src/utils/validators.py --iterations 1000
```

Expected output:
```
================================================================================
                         Performance Benchmark Report                          
================================================================================

SUMMARY
--------------------------------------------------------------------------------
Total files benchmarked: 1
Successfully completed: 1
Errors: 0
Python 2 failures: 0
Python 3 failures: 0

Average speedup: 1.34x
Performance improvements: 1
Performance regressions: 0
✓ Overall: Python 3 is 34.0% faster on average

DETAILED RESULTS
--------------------------------------------------------------------------------

File: src/utils/validators.py
Status: completed
  Python 2 time: 2.1450s
  Python 3 time: 1.6012s
  ✓ Speedup: 1.34x faster (34.0% improvement)

================================================================================
```

**Analysis**: String operations in Python 3 are optimized, resulting in 34% improvement.

### Example 2: Data Processing Pipeline

```bash
./py2to3 bench src/data/ --iterations 500 --output data_benchmark.txt
```

Results might show:
- Dictionary operations: 15% faster in Python 3
- List comprehensions: 20% faster in Python 3
- Iterator usage: 10% faster in Python 3
- Overall: 18% average improvement

### Example 3: Large Codebase

```bash
./py2to3 bench src/ --iterations 200 --timeout 60 --output full_benchmark.txt
```

This helps identify:
- **High-impact wins**: Modules with >50% improvement
- **Optimization targets**: Modules with regressions
- **Overall ROI**: Average improvement across entire codebase

## Troubleshooting

### Python 2 Not Found

**Error**: `Python 2 not found (command: python2)`

**Solution**: Install Python 2.7 or specify the correct command:
```bash
./py2to3 bench src/ --python2 /usr/bin/python2.7
```

### Python 3 Not Found

**Error**: `Python 3 not found (command: python3)`

**Solution**: Install Python 3 or specify the correct command:
```bash
./py2to3 bench src/ --python3 /usr/local/bin/python3.11
```

### Benchmark Timeout

**Error**: `Benchmark timed out after 30 seconds`

**Solution**: Increase timeout for complex code:
```bash
./py2to3 bench src/ --timeout 120
```

Or reduce iterations:
```bash
./py2to3 bench src/ --iterations 50
```

### Import Errors

**Error**: `import_error: No module named 'module_name'`

**Solution**: Ensure dependencies are installed in both Python 2 and 3:
```bash
# Install in Python 2
python2 -m pip install -r requirements.txt

# Install in Python 3
python3 -m pip install -r requirements.txt
```

### Syntax Errors

**Error**: `Syntax error: ...`

**Solution**: The code must be valid Python 2 syntax before benchmarking. Fix syntax issues first:
```bash
./py2to3 check src/
./py2to3 fix src/
```

## Best Practices

### 1. Run Multiple Iterations

More iterations = more reliable results:
```bash
# Quick check (less accurate)
./py2to3 bench src/module.py --iterations 50

# Standard benchmark (balanced)
./py2to3 bench src/module.py --iterations 100

# Precise measurement (more accurate)
./py2to3 bench src/module.py --iterations 1000
```

### 2. Isolate System Load

For accurate results:
- Close other applications
- Don't run during system updates
- Use dedicated test environment for important benchmarks

### 3. Benchmark Representative Code

Focus on:
- Performance-critical modules
- Frequently executed code paths
- Code with known performance issues
- High-value business logic

### 4. Document Results

Keep records of benchmark results:
```bash
# Create benchmark history
mkdir -p benchmarks/
./py2to3 bench src/ --output benchmarks/$(date +%Y%m%d)_benchmark.txt
```

### 5. Compare Apples to Apples

Ensure fair comparison:
- Same hardware
- Same system load
- Same input data
- Same dependencies versions

## Integration with Other Tools

### Combine with Quality Analysis

```bash
# Check quality before benchmarking
./py2to3 quality src/ --output quality_report.txt

# Run benchmark
./py2to3 bench src/ --output performance_report.txt

# Compare: Are quality improvements also performance improvements?
```

### Combine with Risk Analysis

```bash
# Identify high-risk changes
./py2to3 risk src/ --output risk_report.txt

# Benchmark high-risk modules specifically
./py2to3 bench src/critical_module.py --iterations 1000
```

### Track Progress Over Time

```bash
# Take snapshot before migration
./py2to3 stats snapshot baseline

# Apply fixes
./py2to3 fix src/

# Benchmark after migration
./py2to3 bench src/ --output after_migration.txt

# Compare with baseline
./py2to3 stats compare baseline after_migration
```

## Advanced Usage

### Custom Python Paths

If Python is installed in custom locations:
```bash
./py2to3 bench src/ \
  --python2 /opt/python27/bin/python \
  --python3 /opt/python39/bin/python
```

### Selective Benchmarking

Benchmark specific file patterns:
```bash
# Only benchmark utility files
find src/ -name "utils*.py" -exec ./py2to3 bench {} --output {}.bench \;

# Only benchmark core modules
./py2to3 bench src/core/
```

### Automated Reporting

Create a benchmark script:
```bash
#!/bin/bash
# benchmark_all.sh

echo "Running performance benchmarks..."

./py2to3 bench src/core/ --format json --output reports/core_bench.json
./py2to3 bench src/data/ --format json --output reports/data_bench.json
./py2to3 bench src/web/ --format json --output reports/web_bench.json

# Combine results
python scripts/combine_benchmarks.py reports/*.json > reports/full_report.txt
```

## Performance Tips for Python 3

If benchmarks show regressions, consider:

1. **Use Modern Python 3 Features**
   - f-strings instead of % formatting or .format()
   - Dict comprehensions for dict operations
   - pathlib instead of os.path

2. **Optimize String Operations**
   - Use str.join() for concatenation
   - Use bytes when appropriate
   - Consider unicodedata for complex text

3. **Leverage Built-in Optimizations**
   - Use range() instead of list(range())
   - Use dict.items() (already returns views)
   - Use set operations for membership tests

4. **Profile Slow Code**
   ```bash
   python3 -m cProfile -o profile.stats your_script.py
   python3 -m pstats profile.stats
   ```

## Summary

The Performance Benchmark tool is essential for:
- ✅ **Demonstrating value** - Show concrete improvements to stakeholders
- ✅ **Ensuring quality** - Catch performance regressions early
- ✅ **Guiding decisions** - Prioritize optimization efforts
- ✅ **Tracking progress** - Monitor improvements over time

**Next Steps**:
1. Run initial baseline benchmark
2. Apply Python 2 to 3 fixes
3. Re-run benchmark to measure improvements
4. Document and share results with your team

For more migration tools, see:
- [CLI_GUIDE.md](CLI_GUIDE.md) - Complete CLI documentation
- [QUALITY_GUIDE.md](QUALITY_GUIDE.md) - Code quality analysis
- [RISK_GUIDE.md](RISK_GUIDE.md) - Risk assessment tools
- [CI_CD_GUIDE.md](CI_CD_GUIDE.md) - CI/CD integration

Happy benchmarking! 🚀
