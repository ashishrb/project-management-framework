"""
Comprehensive Logging System for GenAI Metrics Dashboard
Provides detailed logging for all modules and functions with easy error tracking
"""

import logging
import os
import json
import traceback
from datetime import datetime
from typing import Any, Dict, Optional, Union
from functools import wraps
import inspect
import sys

class DetailedLogger:
    """Enhanced logger with module and function-specific logging"""
    
    def __init__(self, name: str, log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Configure file handler for detailed logs
        file_handler = logging.FileHandler(f"logs/{name.lower().replace('.', '_')}.log")
        file_handler.setLevel(logging.DEBUG)
        
        # Configure console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(detailed_formatter)
        
        # Add handlers if not already added
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    # Passthrough standard logging methods for compatibility
    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)
    
    def log_function_entry(self, func_name: str, args: tuple = (), kwargs: dict = None):
        """Log function entry with parameters"""
        kwargs = kwargs or {}
        self.logger.debug(f"ENTER {func_name} | args={args} | kwargs={kwargs}")
    
    def log_function_exit(self, func_name: str, result: Any = None, execution_time: float = None):
        """Log function exit with result and execution time"""
        time_info = f" | execution_time={execution_time:.4f}s" if execution_time else ""
        result_info = f" | result={str(result)[:200]}..." if result and len(str(result)) > 200 else f" | result={result}"
        self.logger.debug(f"EXIT {func_name}{time_info}{result_info}")
    
    def log_error(self, func_name: str, error: Exception, context: Dict = None):
        """Log detailed error information"""
        context = context or {}
        error_info = {
            "function": func_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.error(f"ERROR in {func_name} | {json.dumps(error_info, indent=2)}")
        
        # Also log to error-specific file
        self._log_to_error_file(error_info)
    
    def log_api_call(self, method: str, endpoint: str, status_code: int, response_time: float, 
                    request_data: Any = None, response_data: Any = None):
        """Log API call details"""
        api_info = {
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "response_time": response_time,
            "request_data": str(request_data)[:500] if request_data else None,
            "response_data": str(response_data)[:500] if response_data else None,
            "timestamp": datetime.now().isoformat()
        }
        
        level = logging.INFO if 200 <= status_code < 400 else logging.WARNING
        self.logger.log(level, f"API_CALL | {json.dumps(api_info)}")
    
    def log_database_query(self, query: str, params: Dict = None, execution_time: float = None, 
                          row_count: int = None):
        """Log database query details"""
        query_info = {
            "query": query[:200] + "..." if len(query) > 200 else query,
            "params": params,
            "execution_time": execution_time,
            "row_count": row_count,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.debug(f"DB_QUERY | {json.dumps(query_info)}")
    
    def log_frontend_event(self, event_type: str, component: str, data: Dict = None):
        """Log frontend events"""
        event_info = {
            "event_type": event_type,
            "component": component,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"FRONTEND_EVENT | {json.dumps(event_info)}")
    
    def _log_to_error_file(self, error_info: Dict):
        """Log errors to a separate error file for easy analysis"""
        error_file = "logs/errors.log"
        with open(error_file, "a") as f:
            f.write(f"\n{'='*80}\n")
            f.write(json.dumps(error_info, indent=2))
            f.write(f"\n{'='*80}\n")

def log_function_calls(logger_name: str = None):
    """Decorator to automatically log function calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get logger
            if logger_name:
                logger = DetailedLogger(logger_name)
            else:
                # Try to get logger from module name
                module_name = inspect.getmodule(func).__name__
                logger = DetailedLogger(module_name)
            
            # Log function entry
            logger.log_function_entry(func.__name__, args, kwargs)
            
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.log_function_exit(func.__name__, result, execution_time)
                return result
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.log_error(func.__name__, e, {
                    "args": str(args)[:200],
                    "kwargs": str(kwargs)[:200],
                    "execution_time": execution_time
                })
                raise
        return wrapper
    return decorator

def log_api_endpoint(logger_name: str = None):
    """Decorator specifically for API endpoints - simplified version"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Simple logging without async complications
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise
        return wrapper
    return decorator

# Create module-specific loggers
def get_logger(module_name: str) -> DetailedLogger:
    """Get a logger for a specific module"""
    return DetailedLogger(module_name)

# Global loggers for different components
api_logger = get_logger("api")
database_logger = get_logger("database")
frontend_logger = get_logger("frontend")
dashboard_logger = get_logger("dashboard")
navigation_logger = get_logger("navigation")
error_logger = get_logger("errors")

# Log analysis functions
def analyze_logs(log_file: str = None, error_only: bool = False) -> Dict:
    """Analyze logs for patterns and issues"""
    if log_file is None:
        log_file = "logs/errors.log" if error_only else "logs"
    
    analysis = {
        "total_errors": 0,
        "error_types": {},
        "function_errors": {},
        "api_errors": {},
        "recent_errors": [],
        "performance_issues": []
    }
    
    if os.path.isfile(log_file):
        with open(log_file, "r") as f:
            for line in f:
                if "ERROR" in line:
                    analysis["total_errors"] += 1
                    # Parse error details
                    try:
                        error_data = json.loads(line.split("ERROR in ")[1].split(" | ")[1])
                        error_type = error_data.get("error_type", "Unknown")
                        function = error_data.get("function", "Unknown")
                        
                        analysis["error_types"][error_type] = analysis["error_types"].get(error_type, 0) + 1
                        analysis["function_errors"][function] = analysis["function_errors"].get(function, 0) + 1
                        analysis["recent_errors"].append(error_data)
                    except:
                        pass
    
    return analysis

def export_logs_for_debugging(output_file: str = "debug_logs.json"):
    """Export all logs in a structured format for debugging"""
    debug_data = {
        "export_timestamp": datetime.now().isoformat(),
        "log_files": [],
        "error_summary": analyze_logs(error_only=True),
        "recent_activity": []
    }
    
    # Collect all log files
    if os.path.exists("logs"):
        for filename in os.listdir("logs"):
            if filename.endswith(".log"):
                filepath = os.path.join("logs", filename)
                with open(filepath, "r") as f:
                    content = f.read()
                    debug_data["log_files"].append({
                        "filename": filename,
                        "content": content[-10000:]  # Last 10KB
                    })
    
    with open(output_file, "w") as f:
        json.dump(debug_data, f, indent=2)
    
    return debug_data
