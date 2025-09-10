#!/usr/bin/env python3
"""
Backup and Restore Manager for GenAI Metrics Dashboard
Comprehensive backup and restore procedures for database and application data
"""
import os
import sys
import json
import shutil
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import tarfile
import gzip
import hashlib
import schedule
import time
from dataclasses import dataclass

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config import settings
from app.database import engine, SessionLocal

logger = logging.getLogger(__name__)

@dataclass
class BackupConfig:
    """Backup configuration"""
    backup_dir: str = "./backups"
    retention_days: int = 30
    compression: bool = True
    include_logs: bool = True
    include_uploads: bool = True
    include_chroma_db: bool = True
    database_backup: bool = True
    application_backup: bool = True

class BackupManager:
    """Comprehensive backup and restore manager"""
    
    def __init__(self, config: BackupConfig = None):
        self.config = config or BackupConfig()
        self.backup_dir = Path(self.config.backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.backup_dir / "database").mkdir(exist_ok=True)
        (self.backup_dir / "application").mkdir(exist_ok=True)
        (self.backup_dir / "logs").mkdir(exist_ok=True)
        (self.backup_dir / "metadata").mkdir(exist_ok=True)
    
    def create_backup(self, backup_name: str = None) -> Dict[str, Any]:
        """Create a comprehensive backup"""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_info = {
            "name": backup_name,
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "status": "in_progress"
        }
        
        try:
            logger.info(f"Starting backup: {backup_name}")
            
            # Database backup
            if self.config.database_backup:
                backup_info["components"]["database"] = self._backup_database(backup_name)
            
            # Application backup
            if self.config.application_backup:
                backup_info["components"]["application"] = self._backup_application(backup_name)
            
            # Logs backup
            if self.config.include_logs:
                backup_info["components"]["logs"] = self._backup_logs(backup_name)
            
            # ChromaDB backup
            if self.config.include_chroma_db:
                backup_info["components"]["chroma_db"] = self._backup_chroma_db(backup_name)
            
            # Create backup manifest
            backup_info["manifest"] = self._create_manifest(backup_name)
            backup_info["status"] = "completed"
            
            # Save backup metadata
            self._save_backup_metadata(backup_name, backup_info)
            
            logger.info(f"Backup completed successfully: {backup_name}")
            return backup_info
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            backup_info["status"] = "failed"
            backup_info["error"] = str(e)
            return backup_info
    
    def _backup_database(self, backup_name: str) -> Dict[str, Any]:
        """Backup database using pg_dump"""
        try:
            db_url = settings.DATABASE_URL
            if not db_url.startswith("postgresql://"):
                raise ValueError("Database backup only supported for PostgreSQL")
            
            # Parse database URL
            # Format: postgresql://user:password@host:port/database
            parts = db_url.replace("postgresql://", "").split("/")
            db_name = parts[1]
            auth_host = parts[0].split("@")
            user_pass = auth_host[0].split(":")
            host_port = auth_host[1].split(":")
            
            username = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            host = host_port[0]
            port = host_port[1] if len(host_port) > 1 else "5432"
            
            # Create database backup
            backup_file = self.backup_dir / "database" / f"{backup_name}_database.sql"
            
            # Set password environment variable
            env = os.environ.copy()
            if password:
                env["PGPASSWORD"] = password
            
            # Run pg_dump
            cmd = [
                "pg_dump",
                "-h", host,
                "-p", port,
                "-U", username,
                "-d", db_name,
                "--verbose",
                "--clean",
                "--if-exists",
                "--create",
                "--format=plain"
            ]
            
            with open(backup_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, env=env)
            
            if result.returncode != 0:
                raise Exception(f"pg_dump failed: {result.stderr.decode()}")
            
            # Compress if enabled
            if self.config.compression:
                compressed_file = f"{backup_file}.gz"
                with open(backup_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(backup_file)
                backup_file = Path(compressed_file)
            
            # Calculate file size and checksum
            file_size = backup_file.stat().st_size
            checksum = self._calculate_checksum(backup_file)
            
            return {
                "file": str(backup_file),
                "size_bytes": file_size,
                "checksum": checksum,
                "compressed": self.config.compression,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _backup_application(self, backup_name: str) -> Dict[str, Any]:
        """Backup application files"""
        try:
            app_dir = Path("app")
            backup_file = self.backup_dir / "application" / f"{backup_name}_application.tar"
            
            with tarfile.open(backup_file, 'w') as tar:
                tar.add(app_dir, arcname="app")
                
                # Add configuration files
                config_files = ["requirements.txt", "alembic.ini", "pytest.ini"]
                for config_file in config_files:
                    if os.path.exists(config_file):
                        tar.add(config_file)
            
            # Compress if enabled
            if self.config.compression:
                compressed_file = f"{backup_file}.gz"
                with open(backup_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(backup_file)
                backup_file = Path(compressed_file)
            
            file_size = backup_file.stat().st_size
            checksum = self._calculate_checksum(backup_file)
            
            return {
                "file": str(backup_file),
                "size_bytes": file_size,
                "checksum": checksum,
                "compressed": self.config.compression,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Application backup failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _backup_logs(self, backup_name: str) -> Dict[str, Any]:
        """Backup log files"""
        try:
            logs_dir = Path("logs")
            if not logs_dir.exists():
                return {"status": "skipped", "reason": "No logs directory"}
            
            backup_file = self.backup_dir / "logs" / f"{backup_name}_logs.tar"
            
            with tarfile.open(backup_file, 'w') as tar:
                tar.add(logs_dir, arcname="logs")
            
            # Compress if enabled
            if self.config.compression:
                compressed_file = f"{backup_file}.gz"
                with open(backup_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(backup_file)
                backup_file = Path(compressed_file)
            
            file_size = backup_file.stat().st_size
            checksum = self._calculate_checksum(backup_file)
            
            return {
                "file": str(backup_file),
                "size_bytes": file_size,
                "checksum": checksum,
                "compressed": self.config.compression,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Logs backup failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _backup_chroma_db(self, backup_name: str) -> Dict[str, Any]:
        """Backup ChromaDB"""
        try:
            chroma_dir = Path("chroma_db")
            if not chroma_dir.exists():
                return {"status": "skipped", "reason": "No ChromaDB directory"}
            
            backup_file = self.backup_dir / "chroma_db" / f"{backup_name}_chroma_db.tar"
            
            with tarfile.open(backup_file, 'w') as tar:
                tar.add(chroma_dir, arcname="chroma_db")
            
            # Compress if enabled
            if self.config.compression:
                compressed_file = f"{backup_file}.gz"
                with open(backup_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(backup_file)
                backup_file = Path(compressed_file)
            
            file_size = backup_file.stat().st_size
            checksum = self._calculate_checksum(backup_file)
            
            return {
                "file": str(backup_file),
                "size_bytes": file_size,
                "checksum": checksum,
                "compressed": self.config.compression,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"ChromaDB backup failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _create_manifest(self, backup_name: str) -> Dict[str, Any]:
        """Create backup manifest"""
        manifest = {
            "backup_name": backup_name,
            "timestamp": datetime.now().isoformat(),
            "version": settings.VERSION,
            "components": [],
            "total_size_bytes": 0
        }
        
        # Collect component information
        for component_type in ["database", "application", "logs", "chroma_db"]:
            component_dir = self.backup_dir / component_type
            if component_dir.exists():
                for file_path in component_dir.glob(f"{backup_name}_*"):
                    file_size = file_path.stat().st_size
                    manifest["components"].append({
                        "type": component_type,
                        "file": str(file_path),
                        "size_bytes": file_size
                    })
                    manifest["total_size_bytes"] += file_size
        
        return manifest
    
    def _save_backup_metadata(self, backup_name: str, backup_info: Dict[str, Any]):
        """Save backup metadata"""
        metadata_file = self.backup_dir / "metadata" / f"{backup_name}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(backup_info, f, indent=2)
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        metadata_dir = self.backup_dir / "metadata"
        
        if metadata_dir.exists():
            for metadata_file in metadata_dir.glob("*_metadata.json"):
                try:
                    with open(metadata_file, 'r') as f:
                        backup_info = json.load(f)
                    backups.append(backup_info)
                except Exception as e:
                    logger.error(f"Error reading metadata file {metadata_file}: {e}")
        
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
    
    def restore_backup(self, backup_name: str, components: List[str] = None) -> Dict[str, Any]:
        """Restore from backup"""
        if components is None:
            components = ["database", "application", "logs", "chroma_db"]
        
        restore_info = {
            "backup_name": backup_name,
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "status": "in_progress"
        }
        
        try:
            logger.info(f"Starting restore from backup: {backup_name}")
            
            # Load backup metadata
            metadata_file = self.backup_dir / "metadata" / f"{backup_name}_metadata.json"
            if not metadata_file.exists():
                raise FileNotFoundError(f"Backup metadata not found: {backup_name}")
            
            with open(metadata_file, 'r') as f:
                backup_info = json.load(f)
            
            # Restore components
            for component in components:
                if component in backup_info["components"]:
                    restore_info["components"][component] = self._restore_component(
                        backup_name, component, backup_info["components"][component]
                    )
            
            restore_info["status"] = "completed"
            logger.info(f"Restore completed successfully: {backup_name}")
            return restore_info
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            restore_info["status"] = "failed"
            restore_info["error"] = str(e)
            return restore_info
    
    def _restore_component(self, backup_name: str, component: str, component_info: Dict[str, Any]) -> Dict[str, Any]:
        """Restore a specific component"""
        try:
            if component == "database":
                return self._restore_database(backup_name, component_info)
            elif component == "application":
                return self._restore_application(backup_name, component_info)
            elif component == "logs":
                return self._restore_logs(backup_name, component_info)
            elif component == "chroma_db":
                return self._restore_chroma_db(backup_name, component_info)
            else:
                return {"status": "skipped", "reason": f"Unknown component: {component}"}
                
        except Exception as e:
            logger.error(f"Component restore failed ({component}): {e}")
            return {"status": "failed", "error": str(e)}
    
    def _restore_database(self, backup_name: str, component_info: Dict[str, Any]) -> Dict[str, Any]:
        """Restore database from backup"""
        # This would implement database restoration logic
        # For safety, this is a placeholder
        return {"status": "skipped", "reason": "Database restore requires manual intervention"}
    
    def cleanup_old_backups(self) -> Dict[str, Any]:
        """Clean up old backups based on retention policy"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
            cleaned_backups = []
            
            for backup_info in self.list_backups():
                backup_date = datetime.fromisoformat(backup_info["timestamp"])
                if backup_date < cutoff_date:
                    # Remove backup files
                    for component_type in ["database", "application", "logs", "chroma_db"]:
                        component_dir = self.backup_dir / component_type
                        if component_dir.exists():
                            for file_path in component_dir.glob(f"{backup_info['name']}_*"):
                                file_path.unlink()
                                logger.info(f"Removed old backup file: {file_path}")
                    
                    # Remove metadata
                    metadata_file = self.backup_dir / "metadata" / f"{backup_info['name']}_metadata.json"
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    cleaned_backups.append(backup_info["name"])
            
            return {
                "status": "completed",
                "cleaned_backups": cleaned_backups,
                "retention_days": self.config.retention_days
            }
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return {"status": "failed", "error": str(e)}

def setup_scheduled_backups():
    """Set up scheduled backups"""
    config = BackupConfig()
    backup_manager = BackupManager(config)
    
    # Schedule daily backups at 2 AM
    schedule.every().day.at("02:00").do(backup_manager.create_backup)
    
    # Schedule weekly cleanup
    schedule.every().week.do(backup_manager.cleanup_old_backups)
    
    logger.info("Scheduled backups configured")
    
    # Run scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Backup and Restore Manager")
    parser.add_argument("action", choices=["create", "list", "restore", "cleanup", "schedule"])
    parser.add_argument("--name", help="Backup name")
    parser.add_argument("--components", nargs="+", help="Components to restore")
    parser.add_argument("--retention-days", type=int, default=30, help="Retention days")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    config = BackupConfig(retention_days=args.retention_days)
    backup_manager = BackupManager(config)
    
    if args.action == "create":
        result = backup_manager.create_backup(args.name)
        print(json.dumps(result, indent=2))
    
    elif args.action == "list":
        backups = backup_manager.list_backups()
        print(json.dumps(backups, indent=2))
    
    elif args.action == "restore":
        if not args.name:
            print("Error: --name required for restore")
            sys.exit(1)
        result = backup_manager.restore_backup(args.name, args.components)
        print(json.dumps(result, indent=2))
    
    elif args.action == "cleanup":
        result = backup_manager.cleanup_old_backups()
        print(json.dumps(result, indent=2))
    
    elif args.action == "schedule":
        setup_scheduled_backups()
