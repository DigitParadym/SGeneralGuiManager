#!/usr/bin/env python3
"""
Response formatter module for the Index Navigator.
Provides standardized response formatting for all operations.
"""

from datetime import datetime
from typing import Dict, Optional, Union, Any, TypedDict
from pathlib import Path
from enum import Enum, auto

class ErrorCode(Enum):
    """Standardized error codes for response formatting."""
    PATH_NOT_FOUND = auto()
    PATH_NOT_INDEXED = auto()
    INVALID_PATH = auto()
    UPDATE_FAILED = auto()
    SAVE_FAILED = auto()
    REMOVE_FAILED = auto()
    LOOKUP_FAILED = auto()
    INVALID_KEY = auto()
    SYSTEM_ERROR = auto()
    VERIFICATION_FAILED = auto()
    DATABASE_ERROR = auto()
    CONFIG_ERROR = auto()
    PERMISSION_ERROR = auto()
    INITIALIZATION_FAILED = auto()
    VALIDATION_ERROR = auto()

class ResponseStatus(Enum):
    """Status codes for operation responses."""
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    INFO = "INFO"

class PathResponse(TypedDict):
    """Type definition for path operation responses."""
    status: str
    path: Optional[str]
    error_message: Optional[str]
    error_code: Optional[str]
    timestamp: str
    lookup_source: str
    metadata: Dict[str, Any]

class ResponseFormatter:
    """Formats standardized responses for IndexNavigator operations."""
    
    @staticmethod
    def format_success(
        message: str,
        path: Optional[str] = None,
        lookup_source: str = "index",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PathResponse:
        """
        Format successful operation response.
        
        Args:
            message: Success message
            path: Optional path information
            lookup_source: Source of the operation
            metadata: Optional additional metadata
            
        Returns:
            Formatted success response
        """
        return {
            "status": ResponseStatus.SUCCESS.value,
            "path": str(Path(path)) if path else None,
            "error_message": None,
            "error_code": None,
            "timestamp": datetime.now().isoformat(),
            "lookup_source": lookup_source,
            "metadata": metadata or {}
        }
    
    @staticmethod
    def format_not_found(
        target: str,
        module: Optional[str] = None,
        lookup_source: str = "index",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PathResponse:
        """
        Format not found response.
        
        Args:
            target: Item that wasn't found
            module: Optional module context
            lookup_source: Source of the lookup
            metadata: Optional additional metadata
            
        Returns:
            Formatted not found response
        """
        error_msg = f"Not found: {target}"
        if module:
            error_msg += f" in module: {module}"
            
        return {
            "status": ResponseStatus.NOT_FOUND.value,
            "path": None,
            "error_message": error_msg,
            "error_code": ErrorCode.PATH_NOT_FOUND.name,
            "timestamp": datetime.now().isoformat(),
            "lookup_source": module or lookup_source,
            "metadata": metadata or {}
        }
    
    @staticmethod
    def format_invalid_path(
        path: str,
        identifier: str,
        lookup_source: str = "index",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PathResponse:
        """
        Format invalid path response.
        
        Args:
            path: Invalid file path
            identifier: File identifier
            lookup_source: Source of the lookup
            metadata: Optional additional metadata
            
        Returns:
            Formatted invalid path response
        """
        return {
            "status": ResponseStatus.ERROR.value,
            "path": path,
            "error_message": f"Invalid path for {identifier}: {path}",
            "error_code": ErrorCode.INVALID_PATH.name,
            "timestamp": datetime.now().isoformat(),
            "lookup_source": lookup_source,
            "metadata": metadata or {}
        }
    
    @staticmethod
    def format_error(
        error_message: str,
        error_code: Union[str, ErrorCode],
        lookup_source: str = "index",
        path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PathResponse:
        """
        Format error response.
        
        Args:
            error_message: Description of the error
            error_code: Error identifier
            lookup_source: Source of the operation
            path: Optional path related to the error
            metadata: Optional additional metadata
            
        Returns:
            Formatted error response
        """
        if isinstance(error_code, ErrorCode):
            error_code = error_code.name
            
        return {
            "status": ResponseStatus.ERROR.value,
            "path": str(Path(path)) if path else None,
            "error_message": error_message,
            "error_code": error_code,
            "timestamp": datetime.now().isoformat(),
            "lookup_source": lookup_source,
            "metadata": metadata or {}
        }

    @staticmethod
    def format_warning(
        message: str,
        path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PathResponse:
        """
        Format warning response.
        
        Args:
            message: Warning message
            path: Optional path information
            metadata: Optional additional metadata
            
        Returns:
            Formatted warning response
        """
        return {
            "status": ResponseStatus.WARNING.value,
            "path": str(Path(path)) if path else None,
            "error_message": message,
            "error_code": None,
            "timestamp": datetime.now().isoformat(),
            "lookup_source": "warning",
            "metadata": metadata or {}
        }

    @staticmethod
    def format_info(
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PathResponse:
        """
        Format informational response.
        
        Args:
            message: Info message
            metadata: Optional additional metadata
            
        Returns:
            Formatted info response
        """
        return {
            "status": ResponseStatus.INFO.value,
            "path": None,
            "error_message": None,
            "error_code": None,
            "timestamp": datetime.now().isoformat(),
            "lookup_source": "info",
            "metadata": metadata or {}
        }

    @staticmethod
    def format_validation_error(
        message: str,
        field: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PathResponse:
        """
        Format validation error response.
        
        Args:
            message: Validation error message
            field: Field that failed validation
            metadata: Optional additional metadata
            
        Returns:
            Formatted validation error response
        """
        return {
            "status": ResponseStatus.ERROR.value,
            "path": None,
            "error_message": f"Validation error in {field}: {message}",
            "error_code": ErrorCode.VALIDATION_ERROR.name,
            "timestamp": datetime.now().isoformat(),
            "lookup_source": "validation",
            "metadata": metadata or {}
        }

    @classmethod
    def is_success(cls, response: Dict[str, Any]) -> bool:
        """
        Check if response indicates success.
        
        Args:
            response: Response to check
            
        Returns:
            bool indicating success
        """
        return response.get("status") in (ResponseStatus.SUCCESS.value, ResponseStatus.FOUND.value)

    @classmethod
    def is_error(cls, response: Dict[str, Any]) -> bool:
        """
        Check if response indicates error.
        
        Args:
            response: Response to check
            
        Returns:
            bool indicating error
        """
        return response.get("status") == ResponseStatus.ERROR.value

    @classmethod
    def is_warning(cls, response: Dict[str, Any]) -> bool:
        """
        Check if response indicates warning.
        
        Args:
            response: Response to check
            
        Returns:
            bool indicating warning
        """
        return response.get("status") == ResponseStatus.WARNING.value

    @classmethod
    def get_message(cls, response: Dict[str, Any]) -> Optional[str]:
        """
        Get message from response.
        
        Args:
            response: Response dictionary
            
        Returns:
            Message if present
        """
        if response.get("status") == ResponseStatus.ERROR.value:
            return response.get("error_message")
        return None

    @classmethod
    def get_metadata(cls, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get metadata from response.
        
        Args:
            response: Response dictionary
            
        Returns:
            Metadata dictionary
        """
        return response.get("metadata", {})

if __name__ == "__main__":
    print("This module is not meant to be run directly.")
