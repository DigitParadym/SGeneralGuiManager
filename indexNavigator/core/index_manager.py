#!/usr/bin/env python3
"""
Index Manager module for the Index Navigator.
Manages the mapping between keys and file paths, providing a high-level interface
for path indexing operations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Union, List, Tuple, Any
from datetime import datetime

from utils.logger import LoggerSetup
from utils.formatter import ResponseFormatter
from .data_manager import DataManager
from .navigator_core import NavigatorCore

class IndexManager:
    """Core class for managing file path indexing and lookups."""
    
    def __init__(self, base_path: Union[str, Path]):
        """
        Initialize IndexManager.
        
        Args:
            base_path: Base path to indexNavigator directory
        """
        self.base_path = Path(base_path)
        self.setup_components()

    def setup_components(self) -> None:
        """Setup manager components."""
        try:
            # Initialize logger
            self.logger = LoggerSetup(str(self.base_path), "IndexManager").get_logger()
            
            # Initialize components
            self.data_manager = DataManager(self.base_path)
            self.navigator = NavigatorCore(self.base_path)
            self.formatter = ResponseFormatter()
            
            # Set paths
            self.index_path = self.data_manager.get_data_path('indexes', 'paths.json')
            
            self.logger.info("Index manager components initialized successfully")
            
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Failed to setup components: {e}")
            raise RuntimeError(f"Failed to initialize IndexManager: {e}")

    def get_path(self, target_file: str, module_folder: Optional[str] = None) -> Dict[str, Any]:
        """
        Get file path from index.
        
        Args:
            target_file: Name of file to locate
            module_folder: Optional module folder name
            
        Returns:
            Dict containing status and path information
        """
        try:
            self.logger.info(f"Path request - File: {target_file}, Module: {module_folder or 'Not specified'}")
            
            # Try module-specific path first if module provided
            if module_folder:
                module_key = f"{module_folder}/{target_file}"
                result = self.navigator.get_path(module_key)
                if self.formatter.is_success(result):
                    return result
            
            # Try general path lookup
            result = self.navigator.get_path(target_file)
            if self.formatter.is_success(result):
                return result
            
            # Path not found
            return self.formatter.format_not_found(target_file, module_folder)
            
        except Exception as e:
            self.logger.error(f"Error during path lookup: {e}", exc_info=True)
            return self.formatter.format_error(str(e), "LOOKUP_FAILED")

    def update_path(self, file_key: str, file_path: str, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Update or add a path to the index.
        
        Args:
            file_key: Key for indexing
            file_path: Actual file path to store
            module: Optional module name
            
        Returns:
            Dict containing operation status and details
        """
        try:
            # Verify the path exists
            verify_result = self.navigator.verify_path(file_path)
            if not self.formatter.is_success(verify_result):
                return verify_result
            
            # Add/update the path
            result = self.navigator.add_path(file_key, file_path, module)
            
            if self.formatter.is_success(result):
                self.logger.info(f"Updated path for key: {file_key}")
                return self.formatter.format_success(file_path)
            else:
                return result
            
        except Exception as e:
            self.logger.error(f"Error updating path: {e}", exc_info=True)
            return self.formatter.format_error(str(e), "UPDATE_FAILED", path=file_path)

    def remove_path(self, file_key: str, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Remove a path from the index.
        
        Args:
            file_key: Key to remove from index
            module: Optional module name
            
        Returns:
            Dict containing operation status and details
        """
        try:
            result = self.navigator.remove_path(file_key, module)
            
            if self.formatter.is_success(result):
                self.logger.info(f"Removed path for key: {file_key}")
                return result
            else:
                return result
            
        except Exception as e:
            self.logger.error(f"Error removing path: {e}", exc_info=True)
            return self.formatter.format_error(str(e), "REMOVE_FAILED")

    def verify_paths(self) -> Dict[str, Any]:
        """
        Verify all paths in index exist.
        
        Returns:
            Dict containing verification results
        """
        try:
            result = self.navigator.verify_paths()
            
            if self.formatter.is_success(result):
                self.logger.info("Path verification completed")
                return result
            else:
                return result
            
        except Exception as e:
            self.logger.error(f"Error verifying paths: {e}", exc_info=True)
            return self.formatter.format_error(str(e), "VERIFICATION_FAILED")

    def cleanup_invalid(self) -> Dict[str, Any]:
        """
        Remove invalid paths from index.
        
        Returns:
            Dict containing cleanup results
        """
        try:
            result = self.navigator.cleanup_invalid()
            
            if self.formatter.is_success(result):
                self.logger.info("Invalid paths cleaned up")
                return result
            else:
                return result
            
        except Exception as e:
            self.logger.error(f"Error cleaning up invalid paths: {e}", exc_info=True)
            return self.formatter.format_error(str(e), "CLEANUP_FAILED")

    def list_paths(self, module: Optional[str] = None) -> Dict[str, Any]:
        """
        List all paths in index.
        
        Args:
            module: Optional module name to filter by
            
        Returns:
            Dict containing paths list
        """
        try:
            paths = self.navigator.list_paths(module)
            return self.formatter.format_success(
                "Paths retrieved successfully",
                metadata={"paths": paths}
            )
            
        except Exception as e:
            self.logger.error(f"Error listing paths: {e}", exc_info=True)
            return self.formatter.format_error(str(e), "LIST_FAILED")

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get index metadata.
        
        Returns:
            Dict containing metadata
        """
        try:
            result = self.navigator.get_metadata()
            
            if self.formatter.is_success(result):
                self.logger.info("Metadata retrieved successfully")
                return result
            else:
                return result
            
        except Exception as e:
            self.logger.error(f"Error getting metadata: {e}", exc_info=True)
            return self.formatter.format_error(str(e), "METADATA_FAILED")

    def save_index(self) -> bool:
        """
        Save current index state.
        
        Returns:
            bool indicating success
        """
        try:
            result = self.navigator.save_index()
            return self.formatter.is_success(result)
        except Exception as e:
            self.logger.error(f"Error saving index: {e}", exc_info=True)
            return False

    def initialize(self) -> bool:
        """
        Initialize the index manager.
        
        Returns:
            bool indicating success
        """
        try:
            # Initialize components
            if not self.data_manager.initialize():
                raise RuntimeError("Failed to initialize DataManager")
                
            if not self.navigator.initialize():
                raise RuntimeError("Failed to initialize NavigatorCore")
            
            self.logger.info("Index manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize IndexManager: {e}", exc_info=True)
            return False

    def shutdown(self) -> None:
        """Clean shutdown of index manager."""
        try:
            self.navigator.shutdown()
            self.logger.info("Index manager shutdown complete")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}", exc_info=True)

if __name__ == "__main__":
    print("This module is not meant to be run directly.")
