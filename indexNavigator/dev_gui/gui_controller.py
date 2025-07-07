#!/usr/bin/env python3
"""
GUI Controller module for Index Navigator.
Handles GUI events and user interactions.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json
from typing import Optional, Dict, Any

from core.index_control import IndexControl
from dev_gui.gui_builder import GUIBuilder
from dev_gui.gui_error_handler import GUIErrorHandler
from utils.logger import LoggerSetup

class GUIController:
    """Controller class for Index Navigator GUI."""
    
    def __init__(self, root: tk.Tk):
        """Initialize GUI controller."""
        self.root = root
        self.logger = LoggerSetup(str(Path.cwd()), "IndexNavigatorGUI").get_logger()
        self.error_handler = GUIErrorHandler()
        self.index_control = None
        self.current_root = None
        self.initialize_components()

    def initialize_components(self) -> None:
        """Initialize all GUI components."""
        try:
            # Initialize GUI builder
            self.gui_builder = GUIBuilder(self.root)
            self.components = self.gui_builder.get_components()
            
            # Setup error handler
            self.error_handler.set_status_label(self.components.status_label)
            
            # Load configuration
            self.config_file = Path.cwd() / "data" / "config" / "gui_config.json"
            self.load_config()
            
            # Bind events
            self.bind_events()
            
            # Setup initial state
            self.update_button_states()
            
        except Exception as e:
            self.error_handler.handle_error('SYSTEM_ERROR', e, show_dialog=True)

    def load_config(self) -> None:
        """Load GUI configuration."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if root_dir := config.get('root_dir'):
                        self.set_root_directory(root_dir, initial=True)
                    
                    # Load other settings
                    self.gui_builder.vars['show_hidden'].set(
                        config.get('show_hidden', False)
                    )
                    self.gui_builder.vars['relative_paths'].set(
                        config.get('use_relative_paths', True)
                    )
                    self.gui_builder.vars['auto_save'].set(
                        config.get('auto_save', True)
                    )
            else:
                self.prompt_root_directory()
                
        except Exception as e:
            self.error_handler.handle_error('CONFIG_LOAD_ERROR', e)
            self.prompt_root_directory()

    def save_config(self) -> None:
        """Save current configuration."""
        try:
            config = {
                'root_dir': str(self.current_root) if self.current_root else None,
                'last_search': self.components.search_entry.get(),
                'show_hidden': self.gui_builder.vars['show_hidden'].get(),
                'use_relative_paths': self.gui_builder.vars['relative_paths'].get(),
                'auto_save': self.gui_builder.vars['auto_save'].get()
            }
            
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
                
        except Exception as e:
            self.error_handler.handle_error('CONFIG_SAVE_ERROR', e)

    def bind_events(self) -> None:
        """Bind all GUI events."""
        try:
            # Root directory selection
            self.components.root_button.configure(
                command=self.select_root_directory
            )
            
            # Index operations
            self.components.update_index_button.configure(
                command=self.update_index
            )
            
            # File operations
            self.components.browse_button.configure(
                command=self.browse_file
            )
            self.components.add_button.configure(
                command=self.add_path
            )
            self.components.remove_button.configure(
                command=self.remove_path
            )
            self.components.lookup_button.configure(
                command=self.lookup_path
            )
            self.components.verify_button.configure(
                command=self.verify_paths
            )
            self.components.clear_button.configure(
                command=self.clear_results
            )
            self.components.save_button.configure(
                command=self.save_index
            )
            self.components.refresh_button.configure(
                command=self.refresh_view
            )
            
            # Search and filter
            self.components.filter_button.configure(
                command=self.apply_filter
            )
            self.components.search_entry.bind(
                '<Return>', 
                lambda e: self.apply_filter()
            )
            
        except Exception as e:
            self.error_handler.handle_error('SYSTEM_ERROR', e, show_dialog=True)

    def select_root_directory(self) -> None:
        """Handle root directory selection."""
        try:
            directory = filedialog.askdirectory(
                title='Select Root Directory',
                mustexist=True
            )
            
            if directory:
                self.set_root_directory(directory)
                
        except Exception as e:
            self.error_handler.handle_error('ROOT_SELECTION_ERROR', e, show_dialog=True)

    def set_root_directory(self, directory: str, initial: bool = False) -> None:
        """Set root directory and initialize components."""
        try:
            directory_path = Path(directory)
            if not directory_path.exists():
                raise FileNotFoundError("Selected directory does not exist")
                
            self.current_root = directory_path
            
            # Update GUI
            self.components.root_entry.configure(state='normal')
            self.components.root_entry.delete(0, tk.END)
            self.components.root_entry.insert(0, str(directory_path))
            self.components.root_entry.configure(state='readonly')
            
            # Initialize index control
            self.index_control = IndexControl(directory_path)
            
            # Update UI state
            self.update_button_states()
            self.save_config()
            
            if not initial:
                self.error_handler.show_success("Root directory updated successfully")
                # Check if index needs update
                if self.index_control.check_index_update():
                    if messagebox.askyesno(
                        "Index Update",
                        "Index needs to be updated. Update now?"
                    ):
                        self.update_index()
                
        except Exception as e:
            self.error_handler.handle_error('ROOT_INVALID', e, show_dialog=True)

    def update_index(self) -> None:
        """Update index by scanning root directory."""
        try:
            if not self.index_control:
                self.error_handler.handle_error('ROOT_NOT_SELECTED', show_dialog=True)
                return
            
            self.components.progress_bar.start()
            self.error_handler.show_status("Scanning directory...", "info")
            
            # Update progress callback
            def update_progress(total: int, indexed: int) -> None:
                self.error_handler.show_status(
                    f"Indexing: {indexed} of {total} files...",
                    "info"
                )
                self.root.update_idletasks()
            
            # Update index
            total_files, indexed_files = self.index_control.update_index(update_progress)
            
            # Update UI
            self.components.progress_bar.stop()
            self.error_handler.show_success(
                f"Index updated: {indexed_files} files indexed out of {total_files}"
            )
            self.refresh_view()
            
        except Exception as e:
            self.components.progress_bar.stop()
            self.error_handler.handle_error('INDEX_UPDATE_ERROR', e, show_dialog=True)

    def update_button_states(self) -> None:
        """Update button states based on current state."""
        has_root = bool(self.current_root) and bool(self.index_control)
        buttons = [
            self.components.add_button,
            self.components.remove_button,
            self.components.lookup_button,
            self.components.verify_button,
            self.components.save_button,
            self.components.refresh_button,
            self.components.browse_button,
            self.components.filter_button,
            self.components.update_index_button
        ]
        for button in buttons:
            button.configure(state='normal' if has_root else 'disabled')

    def browse_file(self) -> None:
        """Handle file browsing."""
        try:
            filename = filedialog.askopenfilename(
                title='Select File',
                initialdir=self.current_root
            )
            
            if filename:
                # Convert to relative path if option is selected
                path = Path(filename)
                if self.gui_builder.vars['relative_paths'].get():
                    try:
                        path = path.relative_to(self.current_root)
                    except ValueError:
                        pass
                        
                self.components.path_entry.delete(0, tk.END)
                self.components.path_entry.insert(0, str(path))
                
        except Exception as e:
            self.error_handler.handle_error('FILE_BROWSE_ERROR', e)

    def add_path(self) -> None:
        """Handle path addition."""
        try:
            key = self.components.key_entry.get().strip()
            path = self.components.path_entry.get().strip()
            module = self.components.module_entry.get().strip()
            
            if not key or not path:
                self.error_handler.handle_error('MISSING_FIELDS', show_dialog=True)
                return
                
            result = self.index_control.add_to_index(key, path, module)
            if result.get('status') == 'SUCCESS':
                self.error_handler.show_success("Path added successfully")
                self.refresh_view()
            else:
                self.error_handler.handle_error('ADD_PATH_ERROR', Exception(result.get('error_message')))
                
        except Exception as e:
            self.error_handler.handle_error('ADD_PATH_ERROR', e)

    def remove_path(self) -> None:
        """Handle path removal."""
        try:
            key = self.components.key_entry.get().strip()
            module = self.components.module_entry.get().strip()
            
            if not key:
                self.error_handler.handle_error('MISSING_KEY', show_dialog=True)
                return
                
            if messagebox.askyesno("Confirm Removal", "Are you sure you want to remove this path?"):
                result = self.index_control.remove_from_index(key, module)
                if result.get('status') == 'SUCCESS':
                    self.error_handler.show_success("Path removed successfully")
                    self.refresh_view()
                else:
                    self.error_handler.handle_error('REMOVE_PATH_ERROR', Exception(result.get('error_message')))
                    
        except Exception as e:
            self.error_handler.handle_error('REMOVE_PATH_ERROR', e)

    def lookup_path(self) -> None:
        """Handle path lookup."""
        try:
            key = self.components.key_entry.get().strip()
            module = self.components.module_entry.get().strip()
            
            if not key:
                self.error_handler.handle_error('MISSING_KEY', show_dialog=True)
                return
                
            result = self.index_control.lookup_path(key, module)
            if result.get('status') == 'SUCCESS':
                path = result.get('path', '')
                self.components.path_entry.delete(0, tk.END)
                self.components.path_entry.insert(0, path)
                self.error_handler.show_success("Path found")
            else:
                self.error_handler.handle_error('PATH_NOT_FOUND', Exception(result.get('error_message')))
                
        except Exception as e:
            self.error_handler.handle_error('LOOKUP_ERROR', e)

    def verify_paths(self) -> None:
        """Handle path verification."""
        try:
            self.components.progress_bar.start()
            self.error_handler.show_status("Verifying paths...", "info")
            
            result = self.index_control.verify_paths()
            stats = self.index_control.get_index_stats()
            
            self.components.progress_bar.stop()
            if result.get('status') == 'SUCCESS':
                self.error_handler.show_success(
                    f"Verification complete: {stats.get('valid_paths', 0)} valid, "
                    f"{stats.get('invalid_paths', 0)} invalid paths"
                )
                self.refresh_view()
            else:
                self.error_handler.handle_error('VERIFY_ERROR', Exception(result.get('error_message')))
                
        except Exception as e:
            self.components.progress_bar.stop()
            self.error_handler.handle_error('VERIFY_ERROR', e)

    def clear_results(self) -> None:
        """Clear results display."""
        try:
            self.components.results_text.delete('1.0', tk.END)
            self.error_handler.show_status("Results cleared", "info")
        except Exception as e:
            self.error_handler.handle_error('CLEAR_ERROR', e)

    def refresh_view(self) -> None:
        """Refresh the results view."""
        try:
            self.components.results_text.delete('1.0', tk.END)
            
            filter_text = self.components.search_entry.get().strip()
            result = self.index_control.list_paths(filter_text if filter_text else None)
            
            if result.get('status') == 'SUCCESS':
                paths = result.get('metadata', {}).get('paths', {})
                for key, path in paths.items():
                    if self.gui_builder.vars['relative_paths'].get():
                        try:
                            path = Path(path).relative_to(self.current_root)
                        except ValueError:
                            pass
                    self.components.results_text.insert(tk.END, f"{key}: {path}\n")
                    
            # Show stats
            stats = self.index_control.get_index_stats()
            self.error_handler.show_status(
                f"Total files: {stats.get('total_files', 0)} | "
                f"Valid: {stats.get('valid_paths', 0)} | "
                f"Invalid: {stats.get('invalid_paths', 0)}",
                "info"
            )
            
        except Exception as e:
            self.error_handler.handle_error('REFRESH_ERROR', e)

    def apply_filter(self) -> None:
        """Apply search filter to results."""
        self.refresh_view()

    def save_index(self) -> None:
        """Save current index."""
        try:
            if self.index_control and self.index_control.save_index():
                self.error_handler.show_success("Index saved successfully")
            else:
                self.error_handler.handle_error('SAVE_ERROR', show_dialog=True)
        except Exception as e:
            self.error_handler.handle_error('SAVE_ERROR', e, show_dialog=True)

    def prompt_root_directory(self) -> None:
        """Prompt user to select root directory."""