# Dashboard Debugging Guide

## Overview
This guide provides comprehensive steps to debug dashboard loading issues using the implemented logging system.

## Quick Start

### 1. Enable Comprehensive Logging
The logging system is already integrated into the application. Logs will be automatically created in the `logs/` directory.

### 2. Reproduce the Issue
1. Start the application: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
2. Open the dashboard in your browser
3. Reproduce the loading issue

### 3. Analyze Logs
```bash
# Run comprehensive log analysis
python scripts/analyze_logs.py --verbose

# Monitor logs in real-time
python scripts/monitor_logs.py
```

## Step-by-Step Debugging Process

### Step 1: Check Application Status
```bash
# Check if the application is running
curl http://localhost:8000/status

# Check if the dashboard route is accessible
curl http://localhost:8000/dashboard
```

### Step 2: Analyze Backend Logs
```bash
# Check API endpoint logs
tail -f logs/api.log

# Check dashboard-specific logs
tail -f logs/dashboard.log

# Check database logs
tail -f logs/database.log

# Check all errors
tail -f logs/errors.log
```

### Step 3: Analyze Frontend Logs
```bash
# Check frontend logs
tail -f logs/frontend.log

# Check dashboard component logs
tail -f logs/dashboard.log

# Check navigation logs
tail -f logs/navigation.log
```

### Step 4: Run Log Analysis
```bash
# Comprehensive analysis
python scripts/analyze_logs.py --verbose --output debug_analysis.json

# Check specific patterns
grep -i "error" logs/*.log
grep -i "timeout" logs/*.log
grep -i "failed" logs/*.log
```

## Common Issues and Solutions

### Issue 1: Dashboard Template Loading Error
**Symptoms**: "Error Loading View - Failed to load dashboard template"

**Debug Steps**:
1. Check if the dashboard route is accessible:
   ```bash
   curl -I http://localhost:8000/dashboard
   ```

2. Check navigation logs:
   ```bash
   grep "loadViewContent" logs/navigation.log
   ```

3. Check for template errors:
   ```bash
   grep "template" logs/errors.log
   ```

**Solution**: The navigation system has been updated to use correct routes instead of direct template access.

### Issue 2: API Call Failures
**Symptoms**: Dashboard shows fallback data or loading errors

**Debug Steps**:
1. Check API logs:
   ```bash
   grep "API_CALL" logs/api.log
   ```

2. Check specific endpoints:
   ```bash
   curl http://localhost:8000/api/v1/dashboards/all-projects
   curl http://localhost:8000/api/v1/dashboards/genai-metrics
   ```

3. Check for timeout errors:
   ```bash
   grep "timeout" logs/*.log
   ```

**Solution**: The API call system now includes retry logic and better error handling.

### Issue 3: Database Connection Issues
**Symptoms**: Database-related errors in logs

**Debug Steps**:
1. Check database logs:
   ```bash
   grep "DB_QUERY" logs/database.log
   ```

2. Check for connection errors:
   ```bash
   grep "connection" logs/errors.log
   ```

3. Verify database status:
   ```bash
   python scripts/verify_database.py
   ```

### Issue 4: Frontend JavaScript Errors
**Symptoms**: JavaScript errors in browser console or logs

**Debug Steps**:
1. Check frontend logs:
   ```bash
   grep "ERROR" logs/frontend.log
   ```

2. Check dashboard component logs:
   ```bash
   grep "loadDashboardData" logs/dashboard.log
   ```

3. Check for specific function errors:
   ```bash
   grep "functionName" logs/frontend.log
   ```

## Log Analysis Commands

### Basic Analysis
```bash
# Analyze all logs
python scripts/analyze_logs.py

# Analyze with verbose output
python scripts/analyze_logs.py --verbose

# Export analysis to file
python scripts/analyze_logs.py --output analysis.json
```

### Real-time Monitoring
```bash
# Monitor logs in real-time
python scripts/monitor_logs.py

# Monitor with custom threshold
python scripts/monitor_logs.py --threshold 5

# Monitor specific directory
python scripts/monitor_logs.py --logs-dir /path/to/logs
```

### Specific Pattern Searches
```bash
# Find all errors
grep -r "ERROR" logs/

# Find API errors
grep -r "API_CALL.*[4-5][0-9][0-9]" logs/

# Find performance issues
grep -r "PERFORMANCE" logs/

# Find database issues
grep -r "DB_QUERY" logs/
```

## Log File Locations

### Backend Logs
- `logs/api.log` - API endpoint logs
- `logs/database.log` - Database operation logs
- `logs/dashboard.log` - Dashboard-specific logs
- `logs/errors.log` - All error logs (centralized)

### Frontend Logs
- `logs/frontend.log` - Frontend application logs
- `logs/dashboard.log` - Dashboard component logs
- `logs/navigation.log` - Navigation system logs
- `logs/api.log` - Frontend API call logs

## Debugging Checklist

### Before Starting
- [ ] Application is running (`python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`)
- [ ] Database is accessible
- [ ] Logs directory exists (`logs/`)
- [ ] Browser developer tools are open

### During Issue Reproduction
- [ ] Monitor logs in real-time (`python scripts/monitor_logs.py`)
- [ ] Check browser console for JavaScript errors
- [ ] Check network tab for failed requests
- [ ] Note the exact time of the issue

### After Issue Reproduction
- [ ] Run log analysis (`python scripts/analyze_logs.py --verbose`)
- [ ] Check error logs (`tail -f logs/errors.log`)
- [ ] Check specific module logs
- [ ] Export logs for analysis (`python scripts/analyze_logs.py --output debug.json`)

## Advanced Debugging

### Enable Debug Logging
```javascript
// In browser console
window.Loggers.dashboard.setLevel('DEBUG');
window.Loggers.navigation.setLevel('DEBUG');
window.Loggers.api.setLevel('DEBUG');
```

### Export Frontend Logs
```javascript
// In browser console
const allLogs = window.exportAllLogs();
console.log(JSON.stringify(allLogs, null, 2));
```

### Check Log Statistics
```javascript
// In browser console
Object.keys(window.Loggers).forEach(module => {
    const summary = window.Loggers[module].getLogSummary();
    console.log(`${module}:`, summary);
});
```

## Troubleshooting Common Problems

### No Logs Being Created
1. Check if `logs/` directory exists and is writable
2. Check log level configuration
3. Verify logger initialization in code

### High Log Volume
1. Adjust log levels to reduce verbosity
2. Implement log filtering
3. Consider log sampling for high-frequency events

### Performance Impact
1. Use asynchronous logging where possible
2. Implement log buffering
3. Consider log sampling for performance-critical operations

## Getting Help

### Log Analysis Report
When reporting issues, include:
1. Log analysis output (`python scripts/analyze_logs.py --verbose`)
2. Relevant log files from the `logs/` directory
3. Browser console errors
4. Network request failures
5. Steps to reproduce the issue

### Export Debug Information
```bash
# Export comprehensive debug information
python scripts/analyze_logs.py --output debug_report.json --verbose

# Include log files in the report
tar -czf debug_logs.tar.gz logs/ debug_report.json
```

This comprehensive logging system should help identify and resolve dashboard loading issues quickly and efficiently.
