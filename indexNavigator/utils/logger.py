#!/usr/bin/env python3
"""
Logger setup module for the Index Navigator.
Provides centralized logging configuration and management.
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json
import sys
import os
import time
from enum import Enum

class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

class LoggerSetup:
    """Centralized logging configuration for IndexNavigator."""
    
    DEFAULT_CONFIG = {
        "version": 1,
        "log_level": "INFO",
        "max_bytes": 5_242_880,  # 5MB
        "backup_count": 5,
        "file_logging": True,
        "console_logging": True,
        "rotation_interval": "D",  # D for daily
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "detailed_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(pathname)s:%(lineno)d]",
        "retention_days": 30,
        "error_trace": True
    }
    
    def __init__(self, base_path: str, logger_name: str):
        """
        Initialize logger setup.
        
        Args:
            base_path: Base path to indexNavigator directory
            logger_name: Name of the logger instance
        """
        self.base_path = Path(base_path)
        self.logger_name = logger_name
        self.log_dir = self.base_path / "logs"
        self.config_dir = self.base_path / "data" / "config"
        self._ensure_directories()
        self.config = self._load_config()
        self.logger = self._configure_logger()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creating log directories: {e}", file=sys.stderr)
            raise

    def _load_config(self) -> Dict[str, Any]:
        """Load logging configuration from file."""
        config_file = self.config_dir / "logging.json"
        
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                return {**self.DEFAULT_CONFIG, **user_config}
            else:
                # Save default config
                with open(config_file, 'w') as f:
                    json.dump(self.DEFAULT_CONFIG, f, indent=4)
                return dict(self.DEFAULT_CONFIG)
        except Exception as e:
            print(f"Error loading logging config: {e}", file=sys.stderr)
            return dict(self.DEFAULT_CONFIG)

    def _configure_logger(self) -> logging.Logger:
        """Configure and return a logger instance."""
        try:
            # Create logger
            logger = logging.getLogger(self.logger_name)
            logger.setLevel(getattr(logging, self.config["log_level"]))
            
            # Clear any existing handlers
            logger.handlers.clear()
            
            if self.config["file_logging"]:
                # Daily rotating file handler
                daily_handler = self._create_daily_handler()
                logger.addHandler(daily_handler)
                
                # Error file handler
                error_handler = self._create_error_handler()
                logger.addHandler(error_handler)
                
                # Operational logging
                operations_handler = self._create_operations_handler()
                logger.addHandler(operations_handler)
            
            if self.config["console_logging"]:
                # Console handler
                console_handler = self._create_console_handler()
                logger.addHandler(console_handler)
            
            return logger
            
        except Exception as e:
            print(f"Error configuring logger: {e}", file=sys.stderr)
            raise

    def _create_daily_handler(self) -> logging.Handler:
        """Create daily rotating file handler."""
        log_file = self.log_dir / f"{self.logger_name}_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.config["max_bytes"],
            backupCount=self.config["backup_count"],
            encoding='utf-8'
        )
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(self.config["format"]))
        return handler

    def _create_error_handler(self) -> logging.Handler:
        """Create error file handler."""
        error_file = self.log_dir / f"{self.logger_name}_error.log"
        handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=self.config["max_bytes"],
            backupCount=self.config["backup_count"],
            encoding='utf-8'
        )
        handler.setLevel(logging.ERROR)
        handler.setFormatter(logging.Formatter(self.config["detailed_format"]))
        return handler

    def _create_operations_handler(self) -> logging.Handler:
        """Create operations log handler."""
        operations_file = self.log_dir / f"{self.logger_name.lower()}_operations_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.handlers.RotatingFileHandler(
            operations_file,
            maxBytes=self.config["max_bytes"],
            backupCount=self.config["backup_count"],
            encoding='utf-8'
        )
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(self.config["format"]))
        return handler

    def _create_console_handler(self) -> logging.Handler:
        """Create console handler."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(self.config["format"])
        handler.setFormatter(formatter)
        return handler

    def update_log_level(self, level: str) -> None:
        """
        Update logger level.
        
        Args:
            level: New logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        if hasattr(logging, level):
            self.logger.setLevel(getattr(logging, level))
            self.config["log_level"] = level
            
            # Update handlers
            for handler in self.logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(getattr(logging, level))
            
            self.logger.info(f"Log level changed to: {level}")

    def cleanup_old_logs(self, days: Optional[int] = None) -> None:
        """
        Remove log files older than specified days.
        
        Args:
            days: Number of days to keep logs (defaults to config setting)
        """
        try:
            retention_days = days or self.config["retention_days"]
            cutoff = time.time() - (retention_days * 86400)
            
            removed_files = []
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff:
                    log_file.unlink()
                    removed_files.append(log_file.name)
            
            if removed_files:
                self.logger.info(f"Removed old log files: {', '.join(removed_files)}")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {e}")

    def get_logger(self) -> logging.Logger:
        """Return the configured logger instance."""
        return self.logger

    def add_file_handler(self, filename: str, level: str = "INFO") -> None:
        """
        Add a new file handler.
        
        Args:
            filename: Name of log file
            level: Logging level for the handler
        """
        try:
            log_file = self.log_dir / filename
            handler = logging.FileHandler(log_file, encoding='utf-8')
            handler.setLevel(getattr(logging, level))
            handler.setFormatter(logging.Formatter(self.config["format"]))
            self.logger.addHandler(handler)
            self.logger.info(f"Added new log handler: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to add file handler: {e}")

    def rotate_logs(self) -> None:
        """Force rotation of all log files."""
        try:
            for handler in self.logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    handler.doRollover()
            self.logger.info("Log rotation completed")
        except Exception as e:
            self.logger.error(f"Failed to rotate logs: {e}")

def setup_logger(base_path: str, logger_name: str) -> logging.Logger:
    """
    Convenience function to setup and return a logger.
    
    Args:
        base_path: Base path to indexNavigator directory
        logger_name: Name of the logger instance
        
    Returns:
        Configured logger instance
    """
    logger_setup = LoggerSetup(base_path, logger_name)
    return logger_setup.get_logger()

if __name__ == "__main__":
    print("This module is not meant to be run directly.")
