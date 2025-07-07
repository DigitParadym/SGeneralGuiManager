#!/usr/bin/env python3
"""
Data management module for the Index Navigator.
Handles file operations, data persistence, and cache management.
"""

from pathlib import Path
from typing import Dict, Optional, Union, Any, List
from datetime import datetime
import json
import shutil
import tempfile
from utils.logger import LoggerSetup

class DataManager:
    """Core class for managing data persistence and file operations."""
    
    def __init__(self, root_path: Union[str, Path]):
        """
        Initialize the data manager.
        
        Args:
            root_path: Base path for data storage
        """
        self.root_path = Path(root_path)
        self.setup_components()

    def setup_components(self) -> None:
        """Setup data manager components."""
        try:
            # Initialize logger
            self.logger = LoggerSetup(str(self.root_path), "DataManager").get_logger()
            
            # Setup directory structure
            self.data_path = self.root_path / "data"
            self.cache_path = self.data_path / "cache"
            self.config_path = self.data_path / "config"
            self.index_path = self.data_path / "indexes"
            self.backup_path = self.data_path / "backup"
            
            self._ensure_directories()
            self.logger.info("Data manager components initialized successfully")
            
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Failed to setup components: {e}")
            raise RuntimeError(f"Failed to initialize DataManager: {e}")

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        try:
            directories = [
                self.data_path,
                self.cache_path,
                self.config_path,
                self.index_path,
                self.backup_path
            ]
            
            for dir_path in directories:
                dir_path.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Verified directory: {dir_path}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to create directory structure: {e}")

    def load_json(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load JSON data from file with backup handling.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dict containing loaded data
        """
        try:
            file_path = Path(file_path)
            backup_path = self._get_backup_path(file_path)
            
            # Check if backup should be used
            if self._should_use_backup(file_path, backup_path):
                self.logger.warning(f"Using backup for {file_path.name}")
                return self._load_from_backup(file_path, backup_path)
            
            # Load main file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.logger.info(f"Loaded JSON file: {file_path}")
                return data
                
            self.logger.warning(f"File not found, returning empty dict: {file_path}")
            return {}
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {file_path}: {e}")
            return self._handle_corrupt_file(file_path)
        except Exception as e:
            self.logger.error(f"Failed to load JSON {file_path}: {e}")
            return {}

    def save_json(self, file_path: Union[str, Path], data: Dict[str, Any]) -> bool:
        """
        Save data to JSON file with backup creation.
        
        Args:
            file_path: Path to save JSON file
            data: Data to save
            
        Returns:
            bool indicating success
        """
        try:
            file_path = Path(file_path)
            
            # Create backup of existing file
            if file_path.exists():
                self._create_backup(file_path)
            
            # Use atomic write with temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
            try:
                json.dump(data, temp_file, indent=2)
                temp_file.flush()
                shutil.move(temp_file.name, file_path)
                self.logger.info(f"Successfully saved JSON to {file_path}")
                return True
            finally:
                try:
                    Path(temp_file.name).unlink(missing_ok=True)
                except Exception:
                    pass
                    
        except Exception as e:
            self.logger.error(f"Failed to save JSON {file_path}: {e}")
            return False

    def _get_backup_path(self, file_path: Path) -> Path:
        """Get backup file path for a given file."""
        return self.backup_path / f"{file_path.stem}_backup{file_path.suffix}"

    def _should_use_backup(self, file_path: Path, backup_path: Path) -> bool:
        """
        Determine if backup should be used.
        
        Args:
            file_path: Main file path
            backup_path: Backup file path
            
        Returns:
            bool indicating if backup should be used
        """
        try:
            # If main file doesn't exist but backup does
            if not file_path.exists() and backup_path.exists():
                return True
                
            # If both exist, check if backup is newer
            if file_path.exists() and backup_path.exists():
                return backup_path.stat().st_mtime > file_path.stat().st_mtime
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking backup status: {e}")
            return False

    def _load_from_backup(self, file_path: Path, backup_path: Path) -> Dict[str, Any]:
        """
        Load data from backup file.
        
        Args:
            file_path: Main file path
            backup_path: Backup file path
            
        Returns:
            Dict containing loaded data
        """
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Restore backup to main file
            shutil.copy2(backup_path, file_path)
            self.logger.info(f"Restored {file_path.name} from backup")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to load from backup: {e}")
            return {}

    def _create_backup(self, file_path: Path) -> bool:
        """
        Create backup of a file.
        
        Args:
            file_path: File to backup
            
        Returns:
            bool indicating success
        """
        try:
            backup_path = self._get_backup_path(file_path)
            shutil.copy2(file_path, backup_path)
            self.logger.debug(f"Created backup: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False

    def _handle_corrupt_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Handle corrupt JSON file.
        
        Args:
            file_path: Path to corrupt file
            
        Returns:
            Dict containing recovered data or empty dict
        """
        try:
            # Try to load from backup
            backup_path = self._get_backup_path(file_path)
            if backup_path.exists():
                with open(backup_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.logger.warning(f"Recovered data from backup for {file_path}")
                return data
                
            # Move corrupt file to .corrupt extension
            corrupt_path = file_path.with_suffix('.corrupt')
            shutil.move(file_path, corrupt_path)
            self.logger.error(f"Moved corrupt file to {corrupt_path}")
            return {}
            
        except Exception as e:
            self.logger.error(f"Failed to handle corrupt file: {e}")
            return {}

    def get_data_path(self, *parts: str) -> Path:
        """
        Get path within data directory.
        
        Args:
            *parts: Path components
            
        Returns:
            Path object for requested location
        """
        return self.data_path.joinpath(*parts)

    def clear_cache(self) -> bool:
        """
        Clear cache directory.
        
        Returns:
            bool indicating success
        """
        try:
            for file in self.cache_path.glob('*'):
                if file.is_file():
                    file.unlink()
            self.logger.info("Cache cleared successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            return False

    def cleanup_old_backups(self, days: int = 30) -> List[str]:
        """
        Remove old backup files.
        
        Args:
            days: Age in days for backup removal
            
        Returns:
            List of removed backup files
        """
        try:
            cutoff = datetime.now().timestamp() - (days * 86400)
            removed_files = []
            
            for backup_file in self.backup_path.glob('*_backup.*'):
                if backup_file.stat().st_mtime < cutoff:
                    backup_file.unlink()
                    removed_files.append(str(backup_file))
                    
            self.logger.info(f"Removed {len(removed_files)} old backup files")
            return removed_files
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup backups: {e}")
            return []

    def initialize(self) -> bool:
        """
        Initialize data manager.
        
        Returns:
            bool indicating success
        """
        try:
            self._ensure_directories()
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize DataManager: {e}")
            return False

if __name__ == "__main__":
    print("This module is not meant to be run directly.")
