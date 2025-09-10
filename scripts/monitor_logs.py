#!/usr/bin/env python3
"""
Real-time Log Monitoring Script
Monitors logs in real-time and alerts on critical issues
"""

import os
import time
import json
import re
from datetime import datetime
from collections import defaultdict
import argparse

class LogMonitor:
    def __init__(self, logs_dir: str = "logs", alert_threshold: int = 5):
        self.logs_dir = logs_dir
        self.alert_threshold = alert_threshold
        self.error_counts = defaultdict(int)
        self.last_check = time.time()
        self.monitoring = True
        
        # Error patterns to monitor
        self.critical_patterns = [
            r'ERROR.*database.*connection',
            r'ERROR.*API.*timeout',
            r'ERROR.*frontend.*loading',
            r'FATAL.*',
            r'CRITICAL.*'
        ]
        
        # Performance patterns
        self.performance_patterns = [
            r'response_time.*[5-9]\d+\.\d+',  # > 50 seconds
            r'duration.*[1-9]\d+\.\d+',      # > 10 seconds
            r'execution_time.*[2-9]\d+\.\d+'  # > 20 seconds
        ]
    
    def start_monitoring(self):
        """Start real-time log monitoring"""
        print("🔍 Starting real-time log monitoring...")
        print(f"📁 Monitoring directory: {self.logs_dir}")
        print(f"⚠️  Alert threshold: {self.alert_threshold} errors per minute")
        print("Press Ctrl+C to stop monitoring\n")
        
        try:
            while self.monitoring:
                self._check_logs()
                time.sleep(10)  # Check every 10 seconds
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            self.monitoring = False
    
    def _check_logs(self):
        """Check for new log entries and analyze them"""
        if not os.path.exists(self.logs_dir):
            return
        
        current_time = time.time()
        
        for filename in os.listdir(self.logs_dir):
            if filename.endswith('.log'):
                filepath = os.path.join(self.logs_dir, filename)
                self._analyze_log_file(filepath, current_time)
        
        # Check for alert conditions
        self._check_alerts()
        
        # Reset counters every minute
        if current_time - self.last_check > 60:
            self.error_counts.clear()
            self.last_check = current_time
    
    def _analyze_log_file(self, filepath: str, current_time: float):
        """Analyze a log file for new entries"""
        try:
            # Get file modification time
            file_mtime = os.path.getmtime(filepath)
            
            # Only analyze files modified in the last minute
            if current_time - file_mtime > 60:
                return
            
            with open(filepath, 'r', encoding='utf-8') as f:
                # Read only the last 100 lines to avoid processing old logs
                lines = f.readlines()[-100:]
                
                for line in lines:
                    self._analyze_log_line(line, filepath)
                    
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
    
    def _analyze_log_line(self, line: str, filepath: str):
        """Analyze a single log line"""
        # Check for critical errors
        for pattern in self.critical_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                self._handle_critical_error(line, filepath, pattern)
        
        # Check for performance issues
        for pattern in self.performance_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                self._handle_performance_issue(line, filepath, pattern)
        
        # Check for general errors
        if 'ERROR' in line:
            self._handle_general_error(line, filepath)
    
    def _handle_critical_error(self, line: str, filepath: str, pattern: str):
        """Handle critical error detection"""
        module = os.path.basename(filepath).replace('.log', '')
        self.error_counts[f"{module}_critical"] += 1
        
        print(f"🚨 CRITICAL ERROR DETECTED in {module}")
        print(f"   Pattern: {pattern}")
        print(f"   Line: {line.strip()}")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def _handle_performance_issue(self, line: str, filepath: str, pattern: str):
        """Handle performance issue detection"""
        module = os.path.basename(filepath).replace('.log', '')
        self.error_counts[f"{module}_performance"] += 1
        
        print(f"⚠️  PERFORMANCE ISSUE in {module}")
        print(f"   Pattern: {pattern}")
        print(f"   Line: {line.strip()}")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def _handle_general_error(self, line: str, filepath: str):
        """Handle general error detection"""
        module = os.path.basename(filepath).replace('.log', '')
        self.error_counts[f"{module}_error"] += 1
    
    def _check_alerts(self):
        """Check if alert thresholds have been exceeded"""
        for error_type, count in self.error_counts.items():
            if count >= self.alert_threshold:
                print(f"🚨 ALERT: {error_type} has {count} occurrences in the last minute!")
                print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print()
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.monitoring = False

def main():
    parser = argparse.ArgumentParser(description='Monitor application logs in real-time')
    parser.add_argument('--logs-dir', default='logs', help='Directory containing log files')
    parser.add_argument('--threshold', type=int, default=5, help='Error threshold for alerts')
    
    args = parser.parse_args()
    
    monitor = LogMonitor(args.logs_dir, args.threshold)
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
