# dev_gui/gui_error_handler.py
#!/usr/bin/env python3
"""
GUI Error Handler module for Index Navigator.
Handles error management and user feedback.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Dict
import traceback
from utils.logger import LoggerSetup
from pathlib import Path

class GUIErrorHandler:
    """Handles GUI error management and user feedback."""
    
    ERROR_MESSAGES = {
        # Root Directory Errors
        'ROOT_NOT_SELECTED': "No root directory selected. Please select a root directory to continue.",
        'ROOT_NOT_FOUND': "Selected root directory does not exist or is inaccessible.",
        'ROOT_PERMISSION_ERROR': "Permission denied accessing root directory. Please check folder permissions.",
        'ROOT_INVALID': "Invalid root directory. Please select a valid folder.",
        
        # File Operation Errors
        'FILE_NOT_FOUND': "Selected file not found or has been moved.",
        'FILE_PERMISSION_ERROR': "Permission denied accessing file. Please check file permissions.",
        'FILE_INVALID_PATH': "Invalid file path provided.",
        
        # Index Operation Errors
        'INDEX_INIT_ERROR': "Failed to initialize index manager. Please verify root directory.",
        'INDEX_SAVE_ERROR': "Failed to save index. Please check disk space and permissions.",
        'INDEX_LOAD_ERROR': "Failed to load index. The index file may be corrupted.",
        'INDEX_UPDATE_ERROR': "Failed to update index. Please try again.",
        
        # Configuration Errors
        'CONFIG_SAVE_ERROR': "Failed to save configuration. Please check application permissions.",
        'CONFIG_LOAD_ERROR': "Failed to load configuration. Using default settings.",
        'CONFIG_CORRUPT': "Configuration file is corrupted. Resetting to defaults.",
        
        # General Operation Errors
        'OPERATION_CANCELLED': "Operation cancelled by user.",
        'INVALID_INPUT': "Invalid input provided. Please check your entries.",
        'SYSTEM_ERROR': "System error occurred. Please check application logs.",
        
        # Validation Errors
        'MISSING_KEY': "Key field is required.",
        'MISSING_PATH': "Path field is required.",
        'INVALID_MODULE': "Invalid module name provided.",
        'DUPLICATE_KEY': "Key already exists in the index."
    }
    
    def __init__(self):
        """Initialize error handler."""
        self.logger = LoggerSetup(str(Path.cwd()), "GUIErrorHandler").get_logger()
        self.status_label = None

    def set_status_label(self, label: tk.Label) -> None:
        """Set status label for error display."""
        self.status_label = label

    def handle_error(self, error_code: str, exception: Exception = None, 
                    show_dialog: bool = False) -> None:
        """Handle errors with appropriate user feedback."""
        try:
            # Get error message
            message = self.ERROR_MESSAGES.get(error_code, "An unknown error occurred")
            if exception:
                message = f"{message}\nDetails: {str(exception)}"

            # Log error
            self.logger.error(f"Error ({error_code}): {message}")
            if exception:
                self.logger.error(traceback.format_exc())

            # Show error in status bar
            self.show_error(message)

            # Show dialog for critical errors if requested
            if show_dialog:
                messagebox.showerror("Error", message)

        except Exception as e:
            self.logger.critical(f"Error handler failed: {e}")
            messagebox.showerror("Critical Error", "An unexpected error occurred.")

    def show_error(self, message: str) -> None:
        """Display error message in status bar."""
        if self.status_label:
            self.status_label.configure(
                text=message,
                style='Error.TLabel'
            )

    def show_success(self, message: str) -> None:
        """Display success message in status bar."""
        if self.status_label:
            self.status_label.configure(
                text=message,
                style='Success.TLabel'
            )

    def show_status(self, message: str, status_type: str = "info") -> None:
        """Show status message with appropriate styling."""
        if self.status_label:
            style_map = {
                "info": "Info.TLabel",
                "error": "Error.TLabel",
                "success": "Success.TLabel",
                "warning": "Warning.TLabel"
            }
            self.status_label.configure(
                text=message,
                style=style_map.get(status_type, "Info.TLabel")
            )

    def confirm_action(self, title: str, message: str) -> bool:
        """Show confirmation dialog."""
        return messagebox.askyesno(title, message)
