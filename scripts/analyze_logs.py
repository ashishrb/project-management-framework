#!/usr/bin/env python3
"""
Comprehensive Log Analysis Tool
Analyzes logs from all modules to identify errors and performance issues
"""

import os
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any
import argparse

class LogAnalyzer:
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = logs_dir
        self.analysis = {
            "summary": {},
            "errors": [],
            "performance_issues": [],
            "api_issues": [],
            "frontend_issues": [],
            "database_issues": [],
            "recommendations": []
        }
    
    def analyze_all_logs(self):
        """Analyze all log files in the logs directory"""
        print("🔍 Starting comprehensive log analysis...")
        
        if not os.path.exists(self.logs_dir):
            print(f"❌ Logs directory '{self.logs_dir}' not found")
            return self.analysis
        
        # Analyze each log file
        for filename in os.listdir(self.logs_dir):
            if filename.endswith('.log'):
                filepath = os.path.join(self.logs_dir, filename)
                print(f"📄 Analyzing {filename}...")
                self._analyze_log_file(filepath)
        
        # Generate summary and recommendations
        self._generate_summary()
        self._generate_recommendations()
        
        return self.analysis
    
    def _analyze_log_file(self, filepath: str):
        """Analyze a single log file"""
        module_name = os.path.basename(filepath).replace('.log', '')
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                self._analyze_log_line(line, module_name, line_num)
                
        except Exception as e:
            print(f"❌ Error analyzing {filepath}: {e}")
    
    def _analyze_log_line(self, line: str, module: str, line_num: int):
        """Analyze a single log line"""
        # Parse log format: timestamp | level | module | function:line | message
        log_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (\w+)\s+\| (\w+)\s+\| ([^|]+) \| (.+)'
        match = re.match(log_pattern, line)
        
        if not match:
            return
        
        timestamp_str, level, log_module, function_info, message = match.groups()
        
        # Parse timestamp
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except:
            timestamp = None
        
        # Analyze based on log level
        if level == 'ERROR':
            self._analyze_error(line, module, function_info, message, timestamp, line_num)
        elif level == 'WARN':
            self._analyze_warning(line, module, function_info, message, timestamp, line_num)
        elif 'API_CALL' in message:
            self._analyze_api_call(line, module, function_info, message, timestamp, line_num)
        elif 'PERFORMANCE' in message:
            self._analyze_performance(line, module, function_info, message, timestamp, line_num)
        elif 'DB_QUERY' in message:
            self._analyze_database_query(line, module, function_info, message, timestamp, line_num)
    
    def _analyze_error(self, line: str, module: str, function: str, message: str, timestamp: datetime, line_num: int):
        """Analyze error logs"""
        error_info = {
            "module": module,
            "function": function,
            "message": message,
            "timestamp": timestamp.isoformat() if timestamp else None,
            "line_number": line_num,
            "raw_line": line.strip()
        }
        
        # Categorize errors
        if 'API' in module or 'api' in module:
            error_info["category"] = "API"
            self.analysis["api_issues"].append(error_info)
        elif 'database' in module or 'db' in module:
            error_info["category"] = "Database"
            self.analysis["database_issues"].append(error_info)
        elif 'frontend' in module or 'dashboard' in module or 'navigation' in module:
            error_info["category"] = "Frontend"
            self.analysis["frontend_issues"].append(error_info)
        else:
            error_info["category"] = "General"
        
        self.analysis["errors"].append(error_info)
    
    def _analyze_warning(self, line: str, module: str, function: str, message: str, timestamp: datetime, line_num: int):
        """Analyze warning logs"""
        # Look for performance warnings
        if 'slow' in message.lower() or 'timeout' in message.lower():
            self.analysis["performance_issues"].append({
                "module": module,
                "function": function,
                "message": message,
                "timestamp": timestamp.isoformat() if timestamp else None,
                "type": "Performance Warning"
            })
    
    def _analyze_api_call(self, line: str, module: str, function: str, message: str, timestamp: datetime, line_num: int):
        """Analyze API call logs"""
        try:
            # Extract JSON data from the message
            json_start = message.find('{')
            if json_start != -1:
                json_data = json.loads(message[json_start:])
                
                # Check for API issues
                status_code = json_data.get('status_code', 200)
                response_time = json_data.get('response_time', 0)
                
                if status_code >= 400:
                    self.analysis["api_issues"].append({
                        "module": module,
                        "function": function,
                        "status_code": status_code,
                        "endpoint": json_data.get('endpoint', 'Unknown'),
                        "response_time": response_time,
                        "timestamp": timestamp.isoformat() if timestamp else None,
                        "type": "API Error"
                    })
                
                if response_time > 5.0:  # More than 5 seconds
                    self.analysis["performance_issues"].append({
                        "module": module,
                        "function": function,
                        "endpoint": json_data.get('endpoint', 'Unknown'),
                        "response_time": response_time,
                        "timestamp": timestamp.isoformat() if timestamp else None,
                        "type": "Slow API Call"
                    })
        except:
            pass
    
    def _analyze_performance(self, line: str, module: str, function: str, message: str, timestamp: datetime, line_num: int):
        """Analyze performance logs"""
        try:
            json_start = message.find('{')
            if json_start != -1:
                json_data = json.loads(message[json_start:])
                
                duration = json_data.get('duration', 0)
                operation = json_data.get('operation', 'Unknown')
                
                if duration > 1.0:  # More than 1 second
                    self.analysis["performance_issues"].append({
                        "module": module,
                        "function": function,
                        "operation": operation,
                        "duration": duration,
                        "timestamp": timestamp.isoformat() if timestamp else None,
                        "type": "Slow Operation"
                    })
        except:
            pass
    
    def _analyze_database_query(self, line: str, module: str, function: str, message: str, timestamp: datetime, line_num: int):
        """Analyze database query logs"""
        try:
            json_start = message.find('{')
            if json_start != -1:
                json_data = json.loads(message[json_start:])
                
                execution_time = json_data.get('execution_time', 0)
                
                if execution_time > 2.0:  # More than 2 seconds
                    self.analysis["database_issues"].append({
                        "module": module,
                        "function": function,
                        "query": json_data.get('query', 'Unknown')[:100],
                        "execution_time": execution_time,
                        "row_count": json_data.get('row_count', 0),
                        "timestamp": timestamp.isoformat() if timestamp else None,
                        "type": "Slow Query"
                    })
        except:
            pass
    
    def _generate_summary(self):
        """Generate analysis summary"""
        self.analysis["summary"] = {
            "total_errors": len(self.analysis["errors"]),
            "api_errors": len(self.analysis["api_issues"]),
            "frontend_errors": len(self.analysis["frontend_issues"]),
            "database_errors": len(self.analysis["database_issues"]),
            "performance_issues": len(self.analysis["performance_issues"]),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Count errors by module
        error_by_module = Counter()
        for error in self.analysis["errors"]:
            error_by_module[error["module"]] += 1
        
        self.analysis["summary"]["errors_by_module"] = dict(error_by_module)
        
        # Count errors by function
        error_by_function = Counter()
        for error in self.analysis["errors"]:
            error_by_function[error["function"]] += 1
        
        self.analysis["summary"]["errors_by_function"] = dict(error_by_function.most_common(10))
    
    def _generate_recommendations(self):
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # API recommendations
        if self.analysis["api_issues"]:
            recommendations.append({
                "category": "API",
                "priority": "High",
                "issue": f"Found {len(self.analysis['api_issues'])} API issues",
                "recommendation": "Review API error handling and implement better retry mechanisms"
            })
        
        # Performance recommendations
        if self.analysis["performance_issues"]:
            recommendations.append({
                "category": "Performance",
                "priority": "Medium",
                "issue": f"Found {len(self.analysis['performance_issues'])} performance issues",
                "recommendation": "Optimize slow operations and consider caching strategies"
            })
        
        # Database recommendations
        if self.analysis["database_issues"]:
            recommendations.append({
                "category": "Database",
                "priority": "High",
                "issue": f"Found {len(self.analysis['database_issues'])} database issues",
                "recommendation": "Optimize slow queries and add database indexes"
            })
        
        # Frontend recommendations
        if self.analysis["frontend_issues"]:
            recommendations.append({
                "category": "Frontend",
                "priority": "Medium",
                "issue": f"Found {len(self.analysis['frontend_issues'])} frontend issues",
                "recommendation": "Improve error handling and user feedback mechanisms"
            })
        
        self.analysis["recommendations"] = recommendations
    
    def export_analysis(self, output_file: str = "log_analysis.json"):
        """Export analysis results to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(self.analysis, f, indent=2)
        print(f"📊 Analysis exported to {output_file}")
    
    def print_summary(self):
        """Print analysis summary to console"""
        summary = self.analysis["summary"]
        
        print("\n" + "="*60)
        print("📊 LOG ANALYSIS SUMMARY")
        print("="*60)
        print(f"Total Errors: {summary['total_errors']}")
        print(f"API Errors: {summary['api_errors']}")
        print(f"Frontend Errors: {summary['frontend_errors']}")
        print(f"Database Errors: {summary['database_errors']}")
        print(f"Performance Issues: {summary['performance_issues']}")
        
        if summary['errors_by_module']:
            print("\n🔍 Errors by Module:")
            for module, count in summary['errors_by_module'].items():
                print(f"  {module}: {count}")
        
        if summary['errors_by_function']:
            print("\n🔍 Top Error Functions:")
            for function, count in summary['errors_by_function']:
                print(f"  {function}: {count}")
        
        if self.analysis["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in self.analysis["recommendations"]:
                print(f"  [{rec['priority']}] {rec['category']}: {rec['recommendation']}")
        
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Analyze application logs')
    parser.add_argument('--logs-dir', default='logs', help='Directory containing log files')
    parser.add_argument('--output', default='log_analysis.json', help='Output file for analysis results')
    parser.add_argument('--verbose', action='store_true', help='Show detailed analysis')
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(args.logs_dir)
    analysis = analyzer.analyze_all_logs()
    
    analyzer.print_summary()
    analyzer.export_analysis(args.output)
    
    if args.verbose:
        print("\n🔍 Detailed Error Analysis:")
        for error in analysis["errors"][:10]:  # Show first 10 errors
            print(f"  [{error['module']}] {error['function']}: {error['message']}")

if __name__ == "__main__":
    main()
