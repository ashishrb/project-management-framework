/**
 * Comprehensive Frontend Logging System
 * Provides detailed logging for all frontend modules and functions
 */

class FrontendLogger {
    constructor(moduleName, logLevel = 'INFO') {
        this.moduleName = moduleName;
        this.logLevel = logLevel;
        this.logs = [];
        this.maxLogs = 1000; // Keep last 1000 logs in memory
        this.enableConsoleLogging = true;
        this.enableServerLogging = true;
        this.enableLocalStorage = true;
        
        // Log levels
        this.levels = {
            'DEBUG': 0,
            'INFO': 1,
            'WARN': 2,
            'ERROR': 3,
            'FATAL': 4
        };
        
        this.init();
    }
    
    init() {
        // Set up error handlers
        window.addEventListener('error', (event) => {
            this.log('ERROR', 'Global Error', {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error?.stack
            });
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            this.log('ERROR', 'Unhandled Promise Rejection', {
                reason: event.reason,
                promise: event.promise
            });
        });
        
        // Log page load
        this.log('INFO', 'Module Initialized', {
            module: this.moduleName,
            userAgent: navigator.userAgent,
            url: window.location.href,
            timestamp: new Date().toISOString()
        });
    }
    
    log(level, message, data = null, functionName = null) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            level: level,
            module: this.moduleName,
            function: functionName || this.getCallerFunction(),
            message: message,
            data: data,
            url: window.location.href,
            userAgent: navigator.userAgent
        };
        
        // Add to memory logs
        this.logs.push(logEntry);
        if (this.logs.length > this.maxLogs) {
            this.logs.shift(); // Remove oldest log
        }
        
        // Console logging
        if (this.enableConsoleLogging && this.shouldLog(level)) {
            const consoleMethod = this.getConsoleMethod(level);
            console[consoleMethod](`[${this.moduleName}] ${message}`, data || '');
        }
        
        // Server logging
        if (this.enableServerLogging && this.shouldLog(level)) {
            this.sendToServer(logEntry);
        }
        
        // Local storage logging
        if (this.enableLocalStorage && this.shouldLog(level)) {
            this.saveToLocalStorage(logEntry);
        }
    }
    
    shouldLog(level) {
        return this.levels[level] >= this.levels[this.logLevel];
    }
    
    getConsoleMethod(level) {
        const methods = {
            'DEBUG': 'debug',
            'INFO': 'info',
            'WARN': 'warn',
            'ERROR': 'error',
            'FATAL': 'error'
        };
        return methods[level] || 'log';
    }
    
    getCallerFunction() {
        const stack = new Error().stack;
        const lines = stack.split('\n');
        // Skip the first 3 lines (Error, getCallerFunction, log)
        for (let i = 3; i < lines.length; i++) {
            const line = lines[i];
            if (line.includes('at ') && !line.includes('logging.js')) {
                const match = line.match(/at\s+(\w+)/);
                return match ? match[1] : 'anonymous';
            }
        }
        return 'unknown';
    }
    
    async sendToServer(logEntry) {
        try {
            await fetch('/api/v1/logs/frontend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(logEntry)
            });
        } catch (error) {
            // Don't log this error to avoid infinite loops
            console.warn('Failed to send log to server:', error);
        }
    }
    
    saveToLocalStorage(logEntry) {
        try {
            const key = `frontend_logs_${this.moduleName}`;
            const existingLogs = JSON.parse(localStorage.getItem(key) || '[]');
            existingLogs.push(logEntry);
            
            // Keep only last 100 logs per module
            if (existingLogs.length > 100) {
                existingLogs.splice(0, existingLogs.length - 100);
            }
            
            localStorage.setItem(key, JSON.stringify(existingLogs));
        } catch (error) {
            console.warn('Failed to save log to localStorage:', error);
        }
    }
    
    // Specific logging methods
    logFunctionEntry(functionName, args = [], kwargs = {}) {
        this.log('DEBUG', `ENTER ${functionName}`, {
            args: args,
            kwargs: kwargs
        }, functionName);
    }
    
    logFunctionExit(functionName, result = null, executionTime = null) {
        this.log('DEBUG', `EXIT ${functionName}`, {
            result: result,
            executionTime: executionTime
        }, functionName);
    }
    
    logError(functionName, error, context = {}) {
        this.log('ERROR', `ERROR in ${functionName}`, {
            error: {
                name: error.name,
                message: error.message,
                stack: error.stack
            },
            context: context
        }, functionName);
    }
    
    logApiCall(method, endpoint, statusCode, responseTime, requestData = null, responseData = null) {
        this.log('INFO', `API_CALL ${method} ${endpoint}`, {
            method: method,
            endpoint: endpoint,
            statusCode: statusCode,
            responseTime: responseTime,
            requestData: requestData,
            responseData: responseData
        });
    }
    
    logUserAction(action, component, data = {}) {
        this.log('INFO', `USER_ACTION ${action}`, {
            action: action,
            component: component,
            data: data
        });
    }
    
    logPerformance(operation, duration, details = {}) {
        this.log('INFO', `PERFORMANCE ${operation}`, {
            operation: operation,
            duration: duration,
            details: details
        });
    }
    
    // Utility methods
    getLogs(level = null, functionName = null) {
        let filteredLogs = this.logs;
        
        if (level) {
            filteredLogs = filteredLogs.filter(log => log.level === level);
        }
        
        if (functionName) {
            filteredLogs = filteredLogs.filter(log => log.function === functionName);
        }
        
        return filteredLogs;
    }
    
    exportLogs() {
        return {
            module: this.moduleName,
            exportTime: new Date().toISOString(),
            logs: this.logs,
            summary: this.getLogSummary()
        };
    }
    
    getLogSummary() {
        const summary = {
            totalLogs: this.logs.length,
            levelCounts: {},
            functionCounts: {},
            errorCount: 0,
            recentErrors: []
        };
        
        this.logs.forEach(log => {
            summary.levelCounts[log.level] = (summary.levelCounts[log.level] || 0) + 1;
            summary.functionCounts[log.function] = (summary.functionCounts[log.function] || 0) + 1;
            
            if (log.level === 'ERROR' || log.level === 'FATAL') {
                summary.errorCount++;
                summary.recentErrors.push(log);
            }
        });
        
        // Keep only last 10 errors
        summary.recentErrors = summary.recentErrors.slice(-10);
        
        return summary;
    }
    
    clearLogs() {
        this.logs = [];
        localStorage.removeItem(`frontend_logs_${this.moduleName}`);
    }
}

// Function decorator for automatic logging
function logFunctionCalls(logger) {
    return function(target, propertyKey, descriptor) {
        const originalMethod = descriptor.value;
        
        descriptor.value = function(...args) {
            const functionName = propertyKey;
            const startTime = performance.now();
            
            logger.logFunctionEntry(functionName, args);
            
            try {
                const result = originalMethod.apply(this, args);
                
                // Handle async functions
                if (result instanceof Promise) {
                    return result.then(
                        (resolvedResult) => {
                            const executionTime = performance.now() - startTime;
                            logger.logFunctionExit(functionName, resolvedResult, executionTime);
                            return resolvedResult;
                        },
                        (error) => {
                            const executionTime = performance.now() - startTime;
                            logger.logError(functionName, error, { executionTime });
                            throw error;
                        }
                    );
                } else {
                    const executionTime = performance.now() - startTime;
                    logger.logFunctionExit(functionName, result, executionTime);
                    return result;
                }
            } catch (error) {
                const executionTime = performance.now() - startTime;
                logger.logError(functionName, error, { executionTime });
                throw error;
            }
        };
        
        return descriptor;
    };
}

// Create module-specific loggers
const dashboardLogger = new FrontendLogger('dashboard', 'DEBUG');
const navigationLogger = new FrontendLogger('navigation', 'DEBUG');
const apiLogger = new FrontendLogger('api', 'INFO');
const mainLogger = new FrontendLogger('main', 'INFO');

// Global logging functions
window.FrontendLogger = FrontendLogger;
window.logFunctionCalls = logFunctionCalls;

// Export loggers for global use
window.Loggers = {
    dashboard: dashboardLogger,
    navigation: navigationLogger,
    api: apiLogger,
    main: mainLogger
};

// Global error reporting
window.reportError = function(error, context = {}) {
    mainLogger.logError('Global Error Handler', error, context);
};

// Performance monitoring
window.measurePerformance = function(operation, fn) {
    const startTime = performance.now();
    const result = fn();
    const duration = performance.now() - startTime;
    
    mainLogger.logPerformance(operation, duration);
    return result;
};

// Export all logs for debugging
window.exportAllLogs = function() {
    const allLogs = {
        exportTime: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent,
        modules: {}
    };
    
    Object.keys(window.Loggers).forEach(moduleName => {
        allLogs.modules[moduleName] = window.Loggers[moduleName].exportLogs();
    });
    
    return allLogs;
};

// Initialize logging
document.addEventListener('DOMContentLoaded', function() {
    mainLogger.log('INFO', 'Frontend logging system initialized');
});
