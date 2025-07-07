#!/usr/bin/env python3
"""
Main entry point for the Index Navigator application.
Handles startup, error management, and shutdown.
"""

import tkinter as tk
from pathlib import Path
import sys
import traceback
from datetime import datetime
import logging
from typing import Optional

from dev_gui.gui_controller import GUIController
from utils.logger import LoggerSetup
from dev_gui.gui_error_handler import GUIErrorHandler

class IndexNavigatorApp:
    """Main application class for Index Navigator."""
    
    def __init__(self):
        """Initialize application."""
        self.root: Optional[tk.Tk] = None
        self.controller: Optional[GUIController] = None
        self.error_handler: Optional[GUIErrorHandler] = None
        self.logger = None
        self.setup_logging()

    def setup_logging(self) -> None:
        """Configure application logging."""
        try:
            self.logger = LoggerSetup(
                str(Path.cwd()),
                "IndexNavigator"
            ).get_logger()
            
            # Log application start
            self.logger.info("="*50)
            self.logger.info(f"Application starting at {datetime.now()}")
            self.logger.info("="*50)
            
        except Exception as e:
            print(f"Failed to setup logging: {e}")
            sys.exit(1)

    def initialize_gui(self) -> None:
        """Initialize GUI components."""
        try:
            # Create and configure main window
            self.root = tk.Tk()
            self.root.title("Index Navigator")
            self.root.minsize(900, 700)
            self.root.geometry("900x700")
            
            # Configure grid weights for proper resizing
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_rowconfigure(0, weight=1)
            
            # Initialize error handler
            self.error_handler = GUIErrorHandler()
            
            # Initialize controller
            self.controller = GUIController(self.root)
            
            # Configure window close handler
            self.root.protocol("WM_DELETE_WINDOW", self.handle_shutdown)
            
            self.logger.info("GUI initialization complete")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize GUI: {e}")
            self.show_error_and_exit("Failed to initialize application", e)

    def handle_shutdown(self) -> None:
        """Handle application shutdown."""
        try:
            if self.controller:
                # Check for unsaved changes
                if hasattr(self.controller, 'has_unsaved_changes') and \
                   self.controller.has_unsaved_changes():
                    if not self.confirm_exit():
                        return
                
                # Perform cleanup
                self.controller.shutdown()
            
            # Log shutdown
            if self.logger:
                self.logger.info("="*50)
                self.logger.info(f"Application shutting down at {datetime.now()}")
                self.logger.info("="*50)
            
            # Destroy main window
            if self.root:
                self.root.destroy()
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during shutdown: {e}")
            if self.root:
                self.root.destroy()

    def confirm_exit(self) -> bool:
        """Confirm application exit if there are unsaved changes."""
        return tk.messagebox.askyesno(
            "Confirm Exit",
            "There are unsaved changes. Do you want to exit anyway?"
        )

    def show_error_and_exit(self, message: str, exception: Exception) -> None:
        """Show error message and exit application."""
        error_message = f"{message}\n\nError: {str(exception)}"
        if self.logger:
            self.logger.error(error_message)
            self.logger.error(traceback.format_exc())
            
        # Show error dialog
        tk.messagebox.showerror("Error", error_message)
        
        # Exit application
        if self.root:
            self.root.destroy()
        sys.exit(1)

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Global exception handler."""
        # Log the exception
        if self.logger:
            self.logger.critical(
                "Uncaught exception:",
                exc_info=(exc_type, exc_value, exc_traceback)
            )
        
        # Show error message
        error_message = f"An unexpected error occurred:\n{str(exc_value)}"
        if self.root and self.root.winfo_exists():
            tk.messagebox.showerror("Error", error_message)
            self.root.destroy()
        else:
            print(error_message)

    def setup_exception_handling(self) -> None:
        """Setup global exception handling."""
        sys.excepthook = self.handle_exception

    def run(self) -> None:
        """Run the application."""
        try:
            # Setup exception handling
            self.setup_exception_handling()
            
            # Initialize GUI
            self.initialize_gui()
            
            # Log successful startup
            self.logger.info("Application started successfully")
            
            # Start main event loop
            if self.root:
                self.root.mainloop()
                
        except Exception as e:
            self.show_error_and_exit("Failed to start application", e)
        finally:
            # Ensure proper shutdown
            if self.root and self.root.winfo_exists():
                self.handle_shutdown()

def main():
    """Application entry point."""
    try:
        app = IndexNavigatorApp()
        app.run()
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
