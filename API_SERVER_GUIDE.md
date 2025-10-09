# REST API Server Guide

The py2to3 Migration Toolkit now includes a powerful REST API server that exposes all migration features via HTTP endpoints. This enables programmatic access, CI/CD integration, web dashboard development, and third-party tool integration.

## 🚀 Quick Start

### Starting the Server

```bash
# Start with default settings (localhost:5000)
./py2to3 api

# Start on a specific port
./py2to3 api --port 8080

# Start on all interfaces (for remote access)
./py2to3 api --host 0.0.0.0 --port 8080

# Start with debug mode (development only)
./py2to3 api --debug
```

### Installation

The API server requires Flask and Flask-CORS:

```bash
# Install dependencies
pip install flask flask-cors

# Or install all requirements
pip install -r requirements.txt
```

### First API Call

```bash
# Health check
curl http://localhost:5000/api/health

# Get API information
curl http://localhost:5000/api/info
```

## 📡 API Endpoints

### Health & Information

#### `GET /api/health`
Health check endpoint to verify the server is running.

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-01-15T10:30:00.000000",
  "api_version": "1.0.0",
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "toolkit": "py2to3 Migration Toolkit"
  }
}
```

#### `GET /api/info`
Get API version and available endpoints.

**Response:**
```json
{
  "success": true,
  "data": {
    "version": "1.0.0",
    "endpoints": {
      "/api/check": "Run Python 3 compatibility check",
      "/api/fix": "Apply migration fixes",
      ...
    }
  }
}
```

### Migration Operations

#### `POST /api/check`
Run Python 3 compatibility check on code.

**Request:**
```json
{
  "path": "./src"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "path": "./src",
    "issues_found": 5,
    "issues": [
      {
        "file": "src/main.py",
        "line": 10,
        "severity": "HIGH",
        "category": "print_statement",
        "description": "Print statement found"
      }
    ],
    "summary": {...}
  }
}
```

#### `POST /api/fix`
Apply migration fixes to code.

**Request:**
```json
{
  "path": "./src",
  "backup": true,
  "dry_run": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "path": "./src",
    "fixes_applied": 12,
    "dry_run": false,
    "backup_location": "/tmp/py2to3_backups",
    "results": {...}
  }
}
```

#### `POST /api/report`
Generate migration report.

**Request:**
```json
{
  "path": "./src",
  "format": "json"
}
```

**Formats:** `json`, `html`, `text`

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {...},
    "issues": [...],
    "fixes": [...]
  }
}
```

For HTML format, returns the HTML file directly.

### Statistics & Status

#### `GET /api/stats?path=./src`
Get migration statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_files": 25,
    "total_lines": 5000,
    "issues_found": 45,
    "issues_by_severity": {...},
    "issues_by_category": {...}
  }
}
```

#### `GET /api/status?path=./src`
Get overall migration status.

**Response:**
```json
{
  "success": true,
  "data": {
    "migration_status": "in_progress",
    "progress_percentage": 65,
    "files_processed": 15,
    "files_remaining": 10,
    "estimated_completion": "2024-01-20"
  }
}
```

### Backup Management

#### `GET /api/backup/list`
List all available backups.

**Response:**
```json
{
  "success": true,
  "data": {
    "backups": [
      {
        "backup_id": "20240115_103000",
        "created_at": "2024-01-15T10:30:00",
        "files_count": 25,
        "size": "1.5MB",
        "description": "Pre-migration backup"
      }
    ],
    "total": 1
  }
}
```

#### `POST /api/backup/create`
Create a new backup.

**Request:**
```json
{
  "path": "./src",
  "description": "Pre-fix backup"
}
```

#### `POST /api/backup/restore`
Restore from a backup.

**Request:**
```json
{
  "backup_id": "20240115_103000"
}
```

### Code Analysis

#### `POST /api/deps`
Analyze dependencies for Python 3 compatibility.

**Request:**
```json
{
  "path": "./src"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "compatible": ["requests", "flask"],
    "incompatible": ["PIL"],
    "recommendations": {
      "PIL": "Use Pillow instead"
    }
  }
}
```

#### `POST /api/security`
Run security audit on code.

**Request:**
```json
{
  "path": "./src"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "issues_found": 3,
    "issues": [
      {
        "filename": "src/auth.py",
        "line": 45,
        "severity": "HIGH",
        "category": "encoding",
        "description": "Unsafe encoding detected",
        "remediation": "Use UTF-8 encoding"
      }
    ]
  }
}
```

#### `POST /api/quality`
Check code quality.

**Request:**
```json
{
  "path": "./src"
}
```

#### `POST /api/risk`
Analyze migration risks.

**Request:**
```json
{
  "path": "./src"
}
```

### Configuration

#### `GET /api/config`
Get current configuration.

**Response:**
```json
{
  "success": true,
  "data": {
    "backup_enabled": true,
    "auto_fix": false,
    "ignore_patterns": ["*.pyc", "__pycache__"]
  }
}
```

#### `POST /api/config`
Update configuration.

**Request:**
```json
{
  "backup_enabled": true,
  "auto_fix": true
}
```

## 🔧 Usage Examples

### Python Client

```python
import requests

API_BASE = "http://localhost:5000/api"

# Check compatibility
response = requests.post(f"{API_BASE}/check", json={
    "path": "./src"
})
result = response.json()
print(f"Found {result['data']['issues_found']} issues")

# Apply fixes
response = requests.post(f"{API_BASE}/fix", json={
    "path": "./src",
    "backup": True
})
result = response.json()
print(f"Applied {result['data']['fixes_applied']} fixes")

# Generate report
response = requests.post(f"{API_BASE}/report", json={
    "path": "./src",
    "format": "json"
})
report = response.json()
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

const API_BASE = 'http://localhost:5000/api';

// Check compatibility
async function checkCompatibility() {
  const response = await axios.post(`${API_BASE}/check`, {
    path: './src'
  });
  console.log(`Found ${response.data.data.issues_found} issues`);
}

// Apply fixes
async function applyFixes() {
  const response = await axios.post(`${API_BASE}/fix`, {
    path: './src',
    backup: true
  });
  console.log(`Applied ${response.data.data.fixes_applied} fixes`);
}
```

### Bash/curl

```bash
# Check compatibility
curl -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d '{"path": "./src"}'

# Apply fixes
curl -X POST http://localhost:5000/api/fix \
  -H "Content-Type: application/json" \
  -d '{"path": "./src", "backup": true}'

# Get statistics
curl http://localhost:5000/api/stats?path=./src

# Generate HTML report
curl -X POST http://localhost:5000/api/report \
  -H "Content-Type: application/json" \
  -d '{"path": "./src", "format": "html"}' \
  -o report.html
```

## 🔐 Security Considerations

### Network Security

1. **Localhost Only (Default)**: By default, the server binds to `127.0.0.1` (localhost only)
2. **Firewall**: When exposing on `0.0.0.0`, ensure proper firewall rules
3. **Reverse Proxy**: Use nginx or Apache as a reverse proxy for production
4. **HTTPS**: Add SSL/TLS encryption for production deployments

### Authentication

The current version does not include authentication. For production use:

1. Add authentication middleware
2. Use API keys or OAuth
3. Implement rate limiting
4. Add request validation

Example with API key:

```python
from functools import wraps
from flask import request

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.environ.get('API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/check', methods=['POST'])
@require_api_key
def check_compatibility():
    ...
```

### Access Control

- Limit access to trusted networks
- Use environment variables for configuration
- Don't expose sensitive information in responses
- Validate all input paths
- Sanitize user inputs

## 🚀 Deployment

### Development

```bash
./py2to3 api --debug
```

### Production with Gunicorn

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 'src.api_server:app'
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.api_server:app"]
```

### Systemd Service

```ini
[Unit]
Description=py2to3 API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/py2to3
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:5000 src.api_server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔗 Integration Examples

### CI/CD Pipeline (GitHub Actions)

```yaml
name: Migration Check

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Start API Server
        run: |
          pip install flask flask-cors
          ./py2to3 api &
          sleep 5
      
      - name: Check Compatibility
        run: |
          curl -X POST http://localhost:5000/api/check \
            -H "Content-Type: application/json" \
            -d '{"path": "."}' \
            -o results.json
      
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: migration-results
          path: results.json
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    stages {
        stage('Migration Check') {
            steps {
                sh './py2to3 api &'
                sleep 5
                sh '''
                    curl -X POST http://localhost:5000/api/check \
                      -H "Content-Type: application/json" \
                      -d '{"path": "."}' \
                      -o results.json
                '''
            }
        }
    }
}
```

### Web Dashboard Integration

```javascript
// React component example
import React, { useState, useEffect } from 'react';

function MigrationDashboard() {
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    fetch('http://localhost:5000/api/stats?path=./src')
      .then(res => res.json())
      .then(data => setStats(data.data));
  }, []);
  
  if (!stats) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>Migration Progress</h1>
      <p>Issues Found: {stats.issues_found}</p>
      <p>Files Processed: {stats.total_files}</p>
    </div>
  );
}
```

## 📊 Response Format

All API responses follow this standard format:

```json
{
  "success": true|false,
  "timestamp": "ISO 8601 timestamp",
  "api_version": "1.0.0",
  "data": {...},      // Present when success is true
  "error": "message"  // Present when success is false
}
```

### HTTP Status Codes

- `200 OK`: Successful operation
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource or endpoint not found
- `500 Internal Server Error`: Server-side error

## 🛠️ Troubleshooting

### Server Won't Start

```bash
# Check if port is already in use
lsof -i :5000

# Try a different port
./py2to3 api --port 8080
```

### Flask Not Found

```bash
# Install Flask and Flask-CORS
pip install flask flask-cors
```

### CORS Errors

The server has CORS enabled by default. If you still get CORS errors:

1. Check browser console for specific error
2. Verify server is running on correct host/port
3. Check if browser extension is blocking CORS

### Connection Refused

If connecting from another machine:

```bash
# Start server on all interfaces
./py2to3 api --host 0.0.0.0

# Check firewall allows connections
sudo ufw allow 5000
```

## 📚 Additional Resources

- [Main README](README.md) - Overview of the toolkit
- [CLI Guide](CLI_GUIDE.md) - Command-line interface guide
- [Quick Start](QUICK_START.md) - Getting started guide

## 🤝 Contributing

We welcome contributions to improve the API server! Areas for enhancement:

- Authentication and authorization
- Rate limiting
- WebSocket support for real-time updates
- GraphQL endpoint
- API versioning
- Request caching
- Performance optimization

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
