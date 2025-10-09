# Cache Manager Guide

## Overview

The **Smart Cache Manager** speeds up Python 2 to 3 migration operations by caching expensive computations like AST parsing, pattern matching, and file analysis. This dramatically reduces execution time for repeated operations on the same files.

## Why Use Caching?

Migration workflows often involve:
- Running multiple analysis passes over the same files
- Iteratively fixing and checking code
- Generating reports and statistics multiple times
- Parsing and analyzing dependencies repeatedly

Without caching, these operations can become slow on large codebases. The cache manager provides:

✅ **Automatic caching** - No code changes needed  
✅ **Smart invalidation** - Detects file changes automatically  
✅ **Multiple cache types** - AST, patterns, and analysis results  
✅ **Performance tracking** - Monitor cache hit rates  
✅ **Easy management** - Simple CLI commands  

## Quick Start

### View Cache Statistics

```bash
./py2to3 cache stats
```

This shows:
- Total cache entries and size
- Cache hit rate (higher is better!)
- Number of cached files
- Performance metrics

### Clear Cache

```bash
# Clear all cache
./py2to3 cache clear

# Clear specific cache type
./py2to3 cache clear --type ast
./py2to3 cache clear --type patterns
./py2to3 cache clear --type analysis
```

### List Cached Files

```bash
./py2to3 cache list
```

Shows all files currently in cache with their content hashes.

### Invalidate Specific File

```bash
./py2to3 cache invalidate src/myfile.py
```

Removes all cache entries for a specific file. Useful when you manually edit a file outside the tool.

### Optimize Cache

```bash
# Remove entries older than 7 days (default)
./py2to3 cache optimize

# Remove entries older than 3 days
./py2to3 cache optimize --max-age 3
```

## How It Works

### 1. **Automatic Caching**

The cache manager automatically stores results from:
- **AST Parsing** - Cached in `.py2to3_cache/ast/`
- **Pattern Matching** - Cached in `.py2to3_cache/patterns/`
- **File Analysis** - Cached in `.py2to3_cache/analysis/`

### 2. **Smart Invalidation**

Every cached file has a content hash (MD5). When you access cache:
- Tool checks if file has changed
- If changed, cache is automatically invalidated
- Fresh analysis is performed and re-cached

This ensures you always get accurate results!

### 3. **Performance Tracking**

The cache tracks:
- **Hits** - How many times cache was used successfully
- **Misses** - How many times cache wasn't available
- **Hit Rate** - Percentage of requests served from cache
- **Size** - Total disk space used by cache

## Cache Structure

```
.py2to3_cache/
├── ast/                    # Cached AST trees (pickle format)
├── patterns/               # Cached pattern matches (JSON)
├── analysis/               # Cached analysis results (JSON)
└── metadata/               # Cache metadata and stats
    └── cache_metadata.json
```

## Performance Benefits

### Example Speedup

On a medium-sized codebase (50 files, ~10K lines):

| Operation | Without Cache | With Cache | Speedup |
|-----------|--------------|------------|---------|
| First run | 45s | 45s | - |
| Second run | 45s | 8s | **5.6x faster** |
| Third run | 45s | 7s | **6.4x faster** |

The more files you have, the bigger the speedup!

### When Cache Helps Most

✅ Running multiple commands in succession  
✅ Iterative development and testing  
✅ Generating reports after analysis  
✅ Re-checking code after small fixes  
✅ Running CI/CD pipelines  

### When Cache Doesn't Help

❌ First-time analysis of new files  
❌ After major code changes  
❌ When files change frequently  

## Integration with CLI

The cache manager is automatically used by these commands:

- `./py2to3 check` - Caches AST and analysis
- `./py2to3 fix` - Caches pattern matches
- `./py2to3 stats` - Caches file statistics
- `./py2to3 report` - Uses cached analysis

You don't need to do anything special - caching just works!

## Advanced Usage

### Using Cache in Python Code

```python
from src.cache_manager import CacheManager

# Initialize cache
cache = CacheManager()

# Cache AST
import ast
with open('myfile.py', 'r') as f:
    tree = ast.parse(f.read())
cache.set_ast_cache('myfile.py', tree)

# Retrieve cached AST
cached_tree = cache.get_ast_cache('myfile.py')
if cached_tree:
    print("Using cached AST!")
else:
    print("Cache miss - parsing file...")

# Cache pattern matches
matches = find_print_statements('myfile.py')
cache.set_pattern_cache('myfile.py', 'print_statements', matches)

# Retrieve cached matches
cached_matches = cache.get_pattern_cache('myfile.py', 'print_statements')

# Cache analysis results
analysis = analyze_file('myfile.py')
cache.set_analysis_cache('myfile.py', analysis)

# Retrieve cached analysis
cached_analysis = cache.get_analysis_cache('myfile.py')
```

### Custom Cache Directory

```python
# Use custom cache directory
cache = CacheManager(cache_dir='/tmp/my_cache')
```

### Programmatic Statistics

```python
# Get statistics as dictionary
stats = cache.get_statistics()
print(f"Hit rate: {stats['hit_rate']}%")
print(f"Total size: {stats['total_size_mb']} MB")

# Print formatted statistics
cache.print_statistics()
```

## Configuration

### Cache Location

By default, cache is stored in `.py2to3_cache/` in your project directory.

To change this:

```python
cache = CacheManager(cache_dir='~/.cache/py2to3')
```

### Git Integration

Add to your `.gitignore`:

```
.py2to3_cache/
```

The cache is specific to your local machine and shouldn't be committed.

## Best Practices

### ✅ DO:
- Let the cache grow naturally during development
- Check cache stats periodically to monitor performance
- Clear cache after major refactoring
- Optimize cache weekly to remove old entries
- Include cache commands in your workflow scripts

### ❌ DON'T:
- Commit `.py2to3_cache/` to version control
- Manually edit cache files
- Share cache between different machines
- Keep cache forever (optimize regularly)

## Troubleshooting

### Cache Not Working?

**Problem**: Cache hit rate is 0%

**Solutions**:
1. Check if files are actually being cached:
   ```bash
   ./py2to3 cache list
   ```

2. Ensure cache directory is writable:
   ```bash
   ls -la .py2to3_cache/
   ```

3. Check for file permission issues:
   ```bash
   ./py2to3 cache stats
   ```

### Cache Too Large?

**Problem**: Cache is using too much disk space

**Solutions**:
1. Clear old entries:
   ```bash
   ./py2to3 cache optimize --max-age 3
   ```

2. Clear specific cache types:
   ```bash
   ./py2to3 cache clear --type patterns
   ```

3. Clear everything and start fresh:
   ```bash
   ./py2to3 cache clear --confirm
   ```

### Stale Cache?

**Problem**: Getting outdated results

**Solutions**:
1. Cache should auto-invalidate, but you can force it:
   ```bash
   ./py2to3 cache invalidate src/problem_file.py
   ```

2. Clear all cache:
   ```bash
   ./py2to3 cache clear
   ```

## Performance Tips

### 1. **Warm Up Cache**

Run a full analysis once to populate cache:

```bash
./py2to3 check src/
```

Then subsequent operations will be much faster!

### 2. **Monitor Hit Rate**

A good hit rate is > 60%. Check with:

```bash
./py2to3 cache stats
```

If hit rate is low, files are changing too frequently or cache isn't being used.

### 3. **Regular Maintenance**

Add to your weekly workflow:

```bash
# Remove entries older than 7 days
./py2to3 cache optimize
```

### 4. **CI/CD Integration**

For CI/CD pipelines, start with empty cache:

```bash
./py2to3 cache clear --confirm
./py2to3 check src/
```

This ensures consistent results across builds.

## Examples

### Example 1: Iterative Development

```bash
# First pass - builds cache
./py2to3 check src/
# Takes: 45 seconds

# Fix some issues
vim src/myfile.py

# Second pass - uses cache for unchanged files
./py2to3 check src/
# Takes: 8 seconds (5x faster!)

# Generate report - uses cached analysis
./py2to3 report
# Takes: 2 seconds
```

### Example 2: Monitoring Performance

```bash
# Start migration
./py2to3 wizard

# Check cache performance
./py2to3 cache stats
# Hit Rate: 67.5%
# Total Entries: 150
# Size: 4.2 MB

# List what's cached
./py2to3 cache list
```

### Example 3: Team Workflow

```bash
# Developer A: Initial analysis
./py2to3 check src/ --save
./py2to3 cache stats > cache_report.txt

# Developer B: Clear cache and verify
./py2to3 cache clear
./py2to3 check src/
# Ensures consistent results
```

## Technical Details

### Cache Keys

Cache keys are generated from:
- Relative file path
- First 8 characters of file hash
- Cache type identifier

Example: `src_myfile.py_a3b2c1d4.pkl`

### File Hash Algorithm

- Uses MD5 for fast hashing
- Hashes entire file content
- Stored in metadata for comparison

### Cache Invalidation

Automatic invalidation happens when:
1. File content changes (detected via hash)
2. File is explicitly invalidated
3. Cache is cleared

### Storage Format

- **AST Cache**: Python pickle format (`.pkl`)
- **Pattern Cache**: JSON format (`.json`)
- **Analysis Cache**: JSON format (`.json`)
- **Metadata**: JSON format (`.json`)

## Command Reference

### stats

Show cache statistics

```bash
./py2to3 cache stats [--json]
```

Options:
- `--json` - Output as JSON for scripting

### clear

Clear cache entries

```bash
./py2to3 cache clear [--type TYPE] [--confirm]
```

Options:
- `--type` - Cache type: `ast`, `patterns`, `analysis`, or `all` (default: `all`)
- `--confirm` - Skip confirmation prompt

### list

List all cached files

```bash
./py2to3 cache list
```

Shows filepath and content hash for each cached file.

### invalidate

Invalidate specific file

```bash
./py2to3 cache invalidate FILEPATH
```

Arguments:
- `FILEPATH` - Path to file to invalidate

### optimize

Remove old cache entries

```bash
./py2to3 cache optimize [--max-age DAYS]
```

Options:
- `--max-age` - Remove entries older than N days (default: 7)

## See Also

- [CLI Guide](CLI_GUIDE.md) - Main CLI documentation
- [Quick Start](QUICK_START.md) - Getting started guide
- [Performance Guide](PERFORMANCE_GUIDE.md) - Performance optimization tips
- [Config Guide](CONFIG.md) - Configuration options

## Support

For issues, questions, or suggestions:
1. Check this guide first
2. Run `./py2to3 cache stats` to diagnose issues
3. Try clearing cache: `./py2to3 cache clear`
4. Report bugs with cache statistics included

---

**Pro Tip**: Cache is your friend! Let it work in the background and enjoy faster migration workflows. 🚀
