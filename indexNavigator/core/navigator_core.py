#!/usr/bin/env python3
"""
Core navigation logic for the Index Navigator.
Provides base functionality for path indexing and lookup.
"""

from pathlib import Path
from typing import Dict, Optional, Union, List, Tuple, Any
from datetime import datetime
import json
import shutil

from utils.logger import LoggerSetup
from utils.formatter import ResponseFormatter
from .data_manager import DataManager

class NavigatorCore:
    """Core class providing navigation and indexing functionality."""
    
    def __init__(self, root_path: Union[str, Path]):
        """
        Initialize NavigatorCore.
        
        Args:
            root_path: Base path for the navigator
        """
        self.root_path = Path(root_path)
        self.setup_components()

    def setup_components(self) -> None:
        """Setup core components."""
        try:
            # Initialize logger
            self.logger = LoggerSetup(str(self.root_path), "NavigatorCore").get_logger()
            
            # Initialize managers and formatters
            self.data_manager = DataManager(self.root_path)
            self.formatter = ResponseFormatter()
            
            # Initialize paths
            self.index_file = self.root_path / "data" / "indexes" / "paths.json"
            self.backup_file = self.index_file.with_suffix('.json.bak')
            
            # Initialize data structures
            self.index = {}
            
            # Ensure directory structure
            self._ensure_directories()
            
            self.logger.info("Navigator core components initialized successfully")
            
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Failed to setup components: {e}")
            raise RuntimeError(f"Failed to initialize NavigatorCore: {e}")

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        try:
            required_dirs = {
                'data': self.root_path / 'data',
                'indexes': self.root_path / 'data' / 'indexes',
                'cache': self.root_path / 'data' / 'cache',
                'config': self.root_path / 'data' / 'config',
                'backup': self.root_path / 'data' / 'backup'
            }
            
            for name, dir_path in required_dirs.items():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Verified directory: {name} at {dir_path}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to create required directories: {e}")

    def load_index(self) -> Dict[str, Any]:
        """
        Load the path index.
        
        Returns:
            Dict containing operation status and loaded index
        """
        try:
            if self.backup_file.exists():
                self._handle_backup_recovery()
                
            if self.index_file.exists():
                self.index = self.data_manager.load_json(self.index_file)
                self.logger.info(f"Index loaded successfully with {len(self.index)} entries")
                return self.formatter.format_success("Index loaded successfully", 
                                                  metadata={"entries": len(self.index)})
            
            self.index = {}
            return self.formatter.format_success("Empty index initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to load index: {e}")
            return self.formatter.format_error(str(e), "LOAD_FAILED")

    def _handle_backup_recovery(self) -> None:
        """Handle backup recovery if needed."""
        try:
            if self.index_file.exists():
                # Compare modification times
                if self.backup_file.stat().st_mtime > self.index_file.stat().st_mtime:
                    self.logger.warning("Backup file is newer than index file")
                    if self._verify_json_file(self.backup_file):
                        shutil.copy2(self.backup_file, self.index_file)
                        self.logger.info("Restored from backup file")
            else:
                # If only backup exists and is valid
                if self._verify_json_file(self.backup_file):
                    shutil.copy2(self.backup_file, self.index_file)
                    self.logger.info("Restored from backup file")
                    
        except Exception as e:
            self.logger.error(f"Backup recovery failed: {e}")

    def _verify_json_file(self, file_path: Path) -> bool:
        """
        Verify if a file is valid JSON.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            bool indicating if file is valid JSON
        """
        try:
            with open(file_path, 'r') as f:
                json.load(f)
            return True
        except Exception:
            return False

    def save_index(self) -> Dict[str, Any]:
        """
        Save the current index.
        
        Returns:
            Dict containing operation status
        """
        try:
            # Create backup of existing file
            if self.index_file.exists():
                shutil.copy2(self.index_file, self.backup_file)
            
            # Save new index
            success = self.data_manager.save_json(self.index_file, self.index)
            
            if success:
                self.logger.info("Index saved successfully")
                return self.formatter.format_success("Index saved successfully")
            
            raise RuntimeError("Failed to save index file")
            
        except Exception as e:
            self.logger.error(f"Failed to save index: {e}")
            return self.formatter.format_error(str(e), "SAVE_FAILED")

    def verify_path(self, path: Union[str, Path]) -> Dict[str, Any]:
        """
        Verify if a path exists.
        
        Args:
            path: Path to verify
            
        Returns:
            Dict containing verification result
        """
        try:
            path_obj = Path(path)
            exists = path_obj.exists()
            
            if exists:
                return self.formatter.format_success(str(path_obj.resolve()))
            
            return self.formatter.format_error(
                f"Path does not exist: {path}",
                "PATH_NOT_FOUND"
            )
            
        except Exception as e:
            self.logger.error(f"Path verification failed: {e}")
            return self.formatter.format_error(str(e), "VERIFICATION_FAILED")

    def add_path(self, key: str, path: str, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a path to the index.
        
        Args:
            key: Index key for the path
            path: Path to add
            module: Optional module context
            
        Returns:
            Dict containing operation status
        """
        try:
            verify_result = self.verify_path(path)
            if not self.formatter.is_success(verify_result):
                return verify_result

            index_key = f"{module}/{key}" if module else key
            self.index[index_key] = str(Path(path).resolve())
            
            save_result = self.save_index()
            if not self.formatter.is_success(save_result):
                return save_result

            return self.formatter.format_success(
                str(Path(path).resolve()),
                metadata={"key": index_key}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to add path: {e}")
            return self.formatter.format_error(str(e), "ADD_FAILED")

    def remove_path(self, key: str, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Remove a path from the index.
        
        Args:
            key: Key to remove
            module: Optional module context
            
        Returns:
            Dict containing operation status
        """
        try:
            index_key = f"{module}/{key}" if module else key
            
            if index_key not in self.index:
                return self.formatter.format_not_found(key, module)

            removed_path = self.index.pop(index_key)
            
            save_result = self.save_index()
            if not self.formatter.is_success(save_result):
                self.index[index_key] = removed_path
                return save_result

            return self.formatter.format_success(
                removed_path,
                metadata={"removed_key": index_key}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to remove path: {e}")
            return self.formatter.format_error(str(e), "REMOVE_FAILED")

    def get_path(self, key: str, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a path from the index.
        
        Args:
            key: Key to lookup
            module: Optional module context
            
        Returns:
            Dict containing lookup result
        """
        try:
            index_key = f"{module}/{key}" if module else key
            
            if path := self.index.get(index_key):
                verify_result = self.verify_path(path)
                if self.formatter.is_success(verify_result):
                    return self.formatter.format_success(path)
                return verify_result
            
            return self.formatter.format_not_found(key, module)
            
        except Exception as e:
            self.logger.error(f"Failed to get path: {e}")
            return self.formatter.format_error(str(e), "LOOKUP_FAILED")

    def verify_paths(self) -> Dict[str, Any]:
        """
        Verify all paths in the index.
        
        Returns:
            Dict containing verification results
        """
        try:
            results = {
                key: (path, Path(path).exists())
                for key, path in self.index.items()
            }
            
            return self.formatter.format_success(
                "Path verification complete",
                metadata={"results": results}
            )
            
        except Exception as e:
            self.logger.error(f"Path verification failed: {e}")
            return self.formatter.format_error(str(e), "VERIFICATION_FAILED")

    def cleanup_invalid(self) -> Dict[str, Any]:
        """
        Remove invalid paths from the index.
        
        Returns:
            Dict containing cleanup results
        """
        try:
            invalid_keys = []
            for key, path in list(self.index.items()):
                if not Path(path).exists():
                    del self.index[key]
                    invalid_keys.append(key)
            
            if invalid_keys:
                save_result = self.save_index()
                if not self.formatter.is_success(save_result):
                    return save_result

            return self.formatter.format_success(
                f"Removed {len(invalid_keys)} invalid paths",
                metadata={"removed_keys": invalid_keys}
            )
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return self.formatter.format_error(str(e), "CLEANUP_FAILED")

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the index.
        
        Returns:
            Dict containing index metadata
        """
        try:
            valid_paths = sum(1 for path in self.index.values() if Path(path).exists())
            
            metadata = {
                "total_paths": len(self.index),
                "valid_paths": valid_paths,
                "invalid_paths": len(self.index) - valid_paths,
                "last_updated": datetime.now().isoformat(),
                "index_file": str(self.index_file),
                "backup_file": str(self.backup_file)
            }
            
            return self.formatter.format_success(
                "Metadata retrieved successfully",
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get metadata: {e}")
            return self.formatter.format_error(str(e), "METADATA_FAILED")

    def initialize(self) -> Dict[str, Any]:
        """
        Initialize the navigator core.
        
        Returns:
            Dict containing initialization status
        """
        try:
            self._ensure_directories()
            load_result = self.load_index()
            
            if not self.formatter.is_success(load_result):
                return load_result
                
            return self.formatter.format_success("Navigator core initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return self.formatter.format_error(str(e), "INIT_FAILED")

    def shutdown(self) -> Dict[str, Any]:
        """
        Clean shutdown of navigator core.
        
        Returns:
            Dict containing shutdown status
        """
        try:
            save_result = self.save_index()
            if not self.formatter.is_success(save_result):
                return save_result
                
            self.logger.info("Navigator core shutdown complete")
            return self.formatter.format_success("Shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown failed: {e}")
            return self.formatter.format_error(str(e), "SHUTDOWN_FAILED")

if __name__ == "__main__":
    print("This module is not meant to be run directly.")
