#!/usr/bin/env python3
"""
Index Control module for Index Navigator.
Handles index management, file scanning, and synchronization operations.
"""

from pathlib import Path
import time
from typing import Dict, Any, Optional, Tuple, List, Callable
from datetime import datetime
import json

from core.index_manager import IndexManager
from utils.logger import LoggerSetup

class IndexControl:
    """Controls index operations and management."""

    def __init__(self, root_path: Optional[Path] = None):
        """
        Initialize index controller.
        
        Args:
            root_path: Optional root directory path for indexing
        """
        self.logger = LoggerSetup(str(Path.cwd()), "IndexControl").get_logger()
        self.root_path = root_path
        self.index_manager = None
        self.last_update_time = None
        self._ignored_patterns = ['.git', '__pycache__', '*.pyc', '.vscode', '.idea']
        if root_path:
            self.initialize_index_manager(root_path)

    def initialize_index_manager(self, root_path: Path) -> None:
        """
        Initialize or reinitialize the index manager.
        
        Args:
            root_path: Root directory path for indexing
        """
        try:
            self.root_path = root_path
            self.index_manager = IndexManager(str(root_path))
            self.logger.info(f"Index manager initialized for {root_path}")
            self._load_index_metadata()
        except Exception as e:
            self.logger.error(f"Failed to initialize index manager: {e}")
            raise

    def _load_index_metadata(self) -> None:
        """Load index metadata from file."""
        try:
            metadata_file = self.root_path / "data" / "metadata" / "index_meta.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    self.last_update_time = metadata.get('last_update')
                    self._ignored_patterns = metadata.get('ignored_patterns', self._ignored_patterns)
        except Exception as e:
            self.logger.error(f"Failed to load index metadata: {e}")

    def _save_index_metadata(self) -> None:
        """Save index metadata to file."""
        try:
            metadata_file = self.root_path / "data" / "metadata" / "index_meta.json"
            metadata_file.parent.mkdir(parents=True, exist_ok=True)
            
            metadata = {
                'last_update': datetime.now().isoformat(),
                'ignored_patterns': self._ignored_patterns,
                'root_path': str(self.root_path),
                'total_files': len(self.index_manager.list_paths().get('metadata', {}).get('paths', {}))
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save index metadata: {e}")

    def check_index_update(self) -> bool:
        """
        Check if index needs to be updated.
        
        Returns:
            bool: True if update needed
        """
        try:
            if not self.root_path:
                return False
                
            # Check if index exists
            index_file = self.root_path / "data" / "indexes" / "paths.json"
            if not index_file.exists():
                self.logger.info("Index file not found - update needed")
                return True
            
            # Check last update time
            last_update = index_file.stat().st_mtime
            current_time = time.time()
            needs_update = (current_time - last_update) > 86400  # 24 hours
            
            if needs_update:
                self.logger.info("Index is older than 24 hours - update needed")
            
            return needs_update
            
        except Exception as e:
            self.logger.error(f"Error checking index update: {e}")
            return True

    def should_ignore_path(self, path: Path) -> bool:
        """
        Check if path should be ignored based on patterns.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path should be ignored
        """
        try:
            path_str = str(path)
            return any(
                ignored in path_str or path_str.endswith(ignored.replace('*', ''))
                for ignored in self._ignored_patterns
            )
        except Exception as e:
            self.logger.error(f"Error checking ignore pattern: {e}")
            return False

    def update_index(self, progress_callback: Optional[Callable[[int, int], None]] = None) -> Tuple[int, int]:
        """
        Update index by scanning root directory.
        
        Args:
            progress_callback: Optional callback for progress updates (total_files, indexed_files)
            
        Returns:
            Tuple[int, int]: (total_files, indexed_files)
        """
        if not self.root_path or not self.index_manager:
            raise ValueError("Root directory not set")
        
        try:
            total_files = 0
            indexed_files = 0
            errors = []
            
            # Get list of all files first
            all_files = [
                f for f in self.root_path.rglob('*')
                if f.is_file() and not self.should_ignore_path(f)
            ]
            total_files = len(all_files)
            
            # Process each file
            for file_path in all_files:
                try:
                    # Create relative path
                    rel_path = file_path.relative_to(self.root_path)
                    # Use path as key (without extension)
                    key = str(rel_path.with_suffix(''))
                    
                    # Add to index
                    result = self.index_manager.update_path(key, str(rel_path))
                    if result.get('status') == 'SUCCESS':
                        indexed_files += 1
                        
                    # Update progress if callback provided
                    if progress_callback:
                        progress_callback(total_files, indexed_files)
                        
                except Exception as e:
                    errors.append((str(file_path), str(e)))
                    self.logger.error(f"Error indexing {file_path}: {e}")

            # Save index and metadata
            self.save_index()
            self._save_index_metadata()
            
            # Log results
            self.logger.info(f"Index update complete: {indexed_files}/{total_files} files indexed")
            if errors:
                self.logger.warning(f"Encountered {len(errors)} errors during indexing")
                for path, error in errors:
                    self.logger.warning(f"- {path}: {error}")
            
            return total_files, indexed_files
            
        except Exception as e:
            self.logger.error(f"Error updating index: {e}")
            raise

    def add_to_index(self, key: str, path: str, module: str = None) -> Dict[str, Any]:
        """
        Add a path to the index.
        
        Args:
            key: Index key
            path: Path to index
            module: Optional module name
            
        Returns:
            Dict containing operation result
        """
        if not self.index_manager:
            raise ValueError("Index manager not initialized")
            
        result = self.index_manager.update_path(key, path, module)
        if result.get('status') == 'SUCCESS':
            self._save_index_metadata()
        return result

    def remove_from_index(self, key: str, module: str = None) -> Dict[str, Any]:
        """
        Remove a path from the index.
        
        Args:
            key: Key to remove
            module: Optional module name
            
        Returns:
            Dict containing operation result
        """
        if not self.index_manager:
            raise ValueError("Index manager not initialized")
            
        result = self.index_manager.remove_path(key, module)
        if result.get('status') == 'SUCCESS':
            self._save_index_metadata()
        return result

    def lookup_path(self, key: str, module: str = None) -> Dict[str, Any]:
        """
        Look up a path in the index.
        
        Args:
            key: Key to look up
            module: Optional module name
            
        Returns:
            Dict containing lookup result
        """
        if not self.index_manager:
            raise ValueError("Index manager not initialized")
        return self.index_manager.get_path(key, module)

    def list_paths(self, filter_pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        List paths in the index, optionally filtered.
        
        Args:
            filter_pattern: Optional pattern to filter paths
            
        Returns:
            Dict containing paths list
        """
        if not self.index_manager:
            raise ValueError("Index manager not initialized")
            
        result = self.index_manager.list_paths()
        
        if filter_pattern and result.get('status') == 'SUCCESS':
            paths = result['metadata']['paths']
            filtered_paths = {
                k: v for k, v in paths.items()
                if filter_pattern.lower() in k.lower() or filter_pattern.lower() in v.lower()
            }
            result['metadata']['paths'] = filtered_paths
            
        return result

    def verify_paths(self) -> Dict[str, Any]:
        """
        Verify all paths in the index exist.
        
        Returns:
            Dict containing verification results
        """
        if not self.index_manager:
            raise ValueError("Index manager not initialized")
            
        return self.index_manager.verify_paths()

    def save_index(self) -> bool:
        """
        Save current index state.
        
        Returns:
            bool: True if save successful
        """
        if not self.index_manager:
            raise ValueError("Index manager not initialized")
            
        success = self.index_manager.save_index()
        if success:
            self._save_index_metadata()
        return success

    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the index.
        
        Returns:
            Dict containing index statistics
        """
        if not self.index_manager:
            raise ValueError("Index manager not initialized")
            
        try:
            verify_result = self.verify_paths()
            paths_result = self.list_paths()
            
            return {
                'total_files': len(paths_result.get('metadata', {}).get('paths', {})),
                'valid_paths': verify_result.get('metadata', {}).get('valid_paths', 0),
                'invalid_paths': verify_result.get('metadata', {}).get('invalid_paths', 0),
                'last_update': self.last_update_time,
                'root_path': str(self.root_path),
                'ignored_patterns': self._ignored_patterns
            }
        except Exception as e:
            self.logger.error(f"Error getting index stats: {e}")
            return {}

    def update_ignored_patterns(self, patterns: List[str]) -> None:
        """
        Update list of ignored patterns.
        
        Args:
            patterns: List of patterns to ignore
        """
        self._ignored_patterns = patterns
        self._save_index_metadata()
        self.logger.info(f"Updated ignored patterns: {patterns}")

    def shutdown(self) -> None:
        """Clean shutdown of index controller."""
        try:
            if self.index_manager:
                self.save_index()
                self.index_manager.shutdown()
            self.logger.info("Index controller shutdown complete")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    print("This module is not meant to be run directly.")
