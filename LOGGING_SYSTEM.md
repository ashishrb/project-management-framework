# Comprehensive Logging System

## Overview
This project includes a comprehensive logging system that tracks all modules and functions for easy debugging and error analysis. The system provides detailed logging for both frontend and backend components.

## Features

### Backend Logging (`app/core/logging.py`)
- **Module-specific loggers** for different components
- **Function call tracking** with entry/exit logging
- **API endpoint logging** with request/response details
- **Database query logging** with execution times
- **Error tracking** with detailed context and stack traces
- **Performance monitoring** with execution time tracking
- **Structured logging** with JSON format for easy parsing

### Frontend Logging (`static/js/logging.js`)
- **Module-specific loggers** for dashboard, navigation, API, etc.
- **Function call tracking** with parameters and return values
- **API call logging** with response times and status codes
- **User action tracking** for UI interactions
- **Performance monitoring** for frontend operations
- **Error reporting** with automatic error capture
- **Local storage** for offline log persistence
- **Server logging** for centralized log collection

## Usage

### Backend Logging
```python
from app.core.logging import get_logger, log_function_calls, log_api_endpoint

# Get a logger for your module
logger = get_logger("your_module")

# Log function calls automatically
@log_function_calls("your_module")
def your_function():
    pass

# Log API endpoints
@log_api_endpoint("your_module")
async def your_api_endpoint():
    pass

# Manual logging
logger.log_error("function_name", error, {"context": "data"})
logger.log_api_call("GET", "/endpoint", 200, 0.5)
```

### Frontend Logging
```javascript
// Get a logger for your module
const logger = new FrontendLogger('your_module', 'DEBUG');

// Log function calls
logger.logFunctionEntry('functionName', args, kwargs);
logger.logFunctionExit('functionName', result, executionTime);

// Log errors
logger.logError('functionName', error, context);

// Log API calls
logger.logApiCall('GET', '/endpoint', 200, 0.5, requestData, responseData);

// Log user actions
logger.logUserAction('click', 'button', {buttonId: 'submit'});
```

## Log Analysis Tools

### 1. Log Analyzer (`scripts/analyze_logs.py`)
Analyzes all log files and provides comprehensive error analysis:

```bash
# Analyze all logs
python scripts/analyze_logs.py

# Analyze specific directory
python scripts/analyze_logs.py --logs-dir /path/to/logs

# Export analysis to file
python scripts/analyze_logs.py --output analysis.json

# Verbose output
python scripts/analyze_logs.py --verbose
```

**Output includes:**
- Total error count by module and function
- Performance issue identification
- API error analysis
- Database query performance
- Recommendations for improvements

### 2. Real-time Log Monitor (`scripts/monitor_logs.py`)
Monitors logs in real-time and alerts on critical issues:

```bash
# Start monitoring
python scripts/monitor_logs.py

# Custom threshold
python scripts/monitor_logs.py --threshold 10

# Custom logs directory
python scripts/monitor_logs.py --logs-dir /path/to/logs
```

**Features:**
- Real-time error detection
- Performance issue alerts
- Critical error notifications
- Configurable alert thresholds

## Log Files Structure

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

## Log Format

### Backend Log Format
```
2024-01-15 10:30:45 | ERROR    | api.dashboards | get_all_projects:45 | ERROR in get_all_projects | {"error_type": "DatabaseError", "error_message": "Connection failed", "context": {"query": "SELECT * FROM projects"}}
```

### Frontend Log Format
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "ERROR",
  "module": "dashboard",
  "function": "loadDashboardData",
  "message": "ERROR in loadDashboardData",
  "data": {
    "error": {
      "name": "TypeError",
      "message": "Cannot read property 'data' of undefined",
      "stack": "Error stack trace..."
    },
    "context": {
      "executionTime": 1.234
    }
  }
}
```

## Debugging Dashboard Issues

### 1. Check Log Files
```bash
# View recent errors
tail -f logs/errors.log

# View dashboard-specific logs
tail -f logs/dashboard.log

# View API logs
tail -f logs/api.log
```

### 2. Run Log Analysis
```bash
# Analyze all logs
python scripts/analyze_logs.py --verbose

# Check for specific issues
grep "dashboard" logs/errors.log
grep "loadDashboardData" logs/dashboard.log
```

### 3. Monitor in Real-time
```bash
# Start monitoring
python scripts/monitor_logs.py

# In another terminal, reproduce the issue
# Monitor will show real-time errors
```

## Common Issues and Solutions

### Dashboard Loading Issues
1. **Check API logs**: Look for failed API calls in `logs/api.log`
2. **Check frontend logs**: Look for JavaScript errors in `logs/dashboard.log`
3. **Check database logs**: Look for slow queries in `logs/database.log`

### Performance Issues
1. **Check performance logs**: Look for slow operations
2. **Analyze API response times**: Check for slow API calls
3. **Check database queries**: Look for slow database operations

### Error Patterns
- **Database connection errors**: Check database configuration
- **API timeout errors**: Check network connectivity and API performance
- **Frontend loading errors**: Check JavaScript errors and API responses

## Configuration

### Log Levels
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about program execution
- `WARN`: Warning messages for potential issues
- `ERROR`: Error messages for failed operations
- `FATAL`: Critical errors that cause program termination

### Log Rotation
Logs are automatically rotated when they reach 10MB in size. Old logs are compressed and archived.

### Log Retention
- Error logs: Kept for 30 days
- Debug logs: Kept for 7 days
- Performance logs: Kept for 14 days

## Integration with Monitoring

The logging system integrates with:
- **Application monitoring**: Real-time error tracking
- **Performance monitoring**: Response time tracking
- **User experience monitoring**: Frontend error tracking
- **Database monitoring**: Query performance tracking

## Best Practices

1. **Use appropriate log levels**: Don't log everything as ERROR
2. **Include context**: Always include relevant context in error logs
3. **Monitor regularly**: Use the analysis tools regularly
4. **Set up alerts**: Configure monitoring for critical errors
5. **Review logs**: Regularly review logs for patterns and improvements

## Troubleshooting

### Logs Not Being Created
1. Check if `logs/` directory exists and is writable
2. Check log level configuration
3. Verify logger initialization

### High Log Volume
1. Adjust log levels to reduce verbosity
2. Implement log filtering
3. Consider log sampling for high-frequency events

### Performance Impact
1. Use asynchronous logging where possible
2. Implement log buffering
3. Consider log sampling for performance-critical operations
