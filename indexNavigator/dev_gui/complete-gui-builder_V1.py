#!/usr/bin/env python3
"""
GUI Builder module for Index Navigator.
Builds the graphical interface using defined components.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

from .gui_components import UIComponents, StyleManager, ComponentConfig

class GUIBuilder:
    """Builder class for Index Navigator GUI."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the GUI builder."""
        self.root = root
        self.setup_window()
        self.init_variables()
        self.components = self.build_components()

    def setup_window(self) -> None:
        """Configure main window settings"""
        self.root.title("Index Navigator")
        self.root.minsize(*ComponentConfig.WINDOW_MIN_SIZE)
        
        # Configure window grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Setup styles
        StyleManager.configure_styles()

    def init_variables(self) -> None:
        """Initialize tkinter variables"""
        self.vars = {
            'root_path': tk.StringVar(),
            'key': tk.StringVar(),
            'path': tk.StringVar(),
            'module': tk.StringVar(),
            'status': tk.StringVar(),
            'search_filter': tk.StringVar(),
            'show_hidden': tk.BooleanVar(value=ComponentConfig.DEFAULT_VARS['show_hidden']),
            'auto_save': tk.BooleanVar(value=ComponentConfig.DEFAULT_VARS['auto_save']),
            'relative_paths': tk.BooleanVar(value=ComponentConfig.DEFAULT_VARS['relative_paths'])
        }

    def build_components(self) -> UIComponents:
        """Build all UI components"""
        main_frame = self._create_main_frame()
        
        # Create sections
        path_section = self._create_path_section(main_frame)
        operations_section = self._create_operations_section(main_frame)
        results_section = self._create_results_section(main_frame)
        status_section = self._create_status_section(main_frame)
        
        # Configure grid weights
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)  # Results section expands
        
        return UIComponents(
            main_frame=main_frame,
            root_entry=path_section['root_entry'],
            path_entry=path_section['path_entry'],
            module_entry=path_section['module_entry'],
            results_text=results_section['text'],
            status_label=status_section['label'],
            browse_button=path_section['browse_button'],
            root_button=path_section['root_button'],
            update_index_button=operations_section['update_index'],
            add_button=operations_section['add'],
            remove_button=operations_section['remove'],
            lookup_button=operations_section['lookup'],
            verify_button=operations_section['verify'],
            clear_button=operations_section['clear'],
            save_button=operations_section['save'],
            refresh_button=operations_section['refresh'],
            search_entry=results_section['search'],
            filter_button=results_section['filter'],
            progress_bar=status_section['progress']
        )

    def _create_main_frame(self) -> ttk.Frame:
        """Create and configure main frame"""
        frame = ttk.Frame(self.root, padding=ComponentConfig.PADDING)
        frame.grid(row=0, column=0, sticky='nsew')
        return frame

    def _create_path_section(self, parent: ttk.Frame) -> Dict[str, Any]:
        """Create path management section"""
        frame = ttk.LabelFrame(
            parent,
            text="File Management",
            padding=5,
            style='Section.TLabelframe'
        )
        frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        # Root Directory Selection
        root_frame = ttk.Frame(frame)
        root_frame.grid(row=0, column=0, columnspan=4, sticky='ew', pady=(0, 10))
        
        ttk.Label(
            root_frame, 
            text="Root Directory:", 
            style='Header.TLabel'
        ).pack(side='left', padx=(0, 5))
        
        root_entry = ttk.Entry(
            root_frame,
            textvariable=self.vars['root_path'],
            state='readonly',
            width=50
        )
        root_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        root_button = ttk.Button(
            root_frame,
            text="Select Root",
            style='Primary.TButton',
            width=15
        )
        root_button.pack(side='left', padx=(0, 5))
        
        # Separator
        ttk.Separator(frame, orient='horizontal').grid(
            row=1, column=0, columnspan=4, sticky='ew', pady=5
        )
        
        # Key and Module
        ttk.Label(
            frame, 
            text="Key:", 
            style='Header.TLabel'
        ).grid(row=2, column=0, sticky='w')
        key_entry = ttk.Entry(frame, textvariable=self.vars['key'])
        key_entry.grid(row=2, column=1, sticky='ew', padx=5)
        
        ttk.Label(
            frame, 
            text="Module:", 
            style='Header.TLabel'
        ).grid(row=2, column=2, sticky='w')
        module_entry = ttk.Entry(frame, textvariable=self.vars['module'])
        module_entry.grid(row=2, column=3, sticky='ew', padx=5)
        
        # Path Selection
        ttk.Label(
            frame, 
            text="Path:", 
            style='Header.TLabel'
        ).grid(row=3, column=0, sticky='w')
        path_entry = ttk.Entry(frame, textvariable=self.vars['path'])
        path_entry.grid(row=3, column=1, columnspan=2, sticky='ew', padx=5)
        
        browse_button = ttk.Button(
            frame,
            text="Browse File",
            style='Action.TButton'
        )
        browse_button.grid(row=3, column=3, sticky='w', padx=5)
        
        # Options Frame
        options_frame = ttk.Frame(frame)
        options_frame.grid(row=4, column=0, columnspan=4, sticky='ew', pady=(5, 0))
        
        # Path Options
        ttk.Checkbutton(
            options_frame,
            text="Use Relative Paths",
            variable=self.vars['relative_paths']
        ).pack(side='left', padx=5)
        
        # Auto Save Option
        ttk.Checkbutton(
            options_frame,
            text="Auto Save",
            variable=self.vars['auto_save']
        ).pack(side='left', padx=5)
        
        # Configure grid weights
        frame.grid_columnconfigure(1, weight=2)
        frame.grid_columnconfigure(3, weight=1)
        
        return {
            'key_entry': key_entry,
            'path_entry': path_entry,
            'module_entry': module_entry,
            'root_entry': root_entry,
            'browse_button': browse_button,
            'root_button': root_button
        }

    def _create_operations_section(self, parent: ttk.Frame) -> Dict[str, ttk.Button]:
        """Create operations section with buttons"""
        frame = ttk.LabelFrame(
            parent,
            text="Operations",
            padding=5,
            style='Section.TLabelframe'
        )
        frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        
        buttons = {}
        # Create button groups
        button_frames = {
            'left': ttk.Frame(frame),
            'center': ttk.Frame(frame),
            'right': ttk.Frame(frame)
        }
        
        for name, fr in button_frames.items():
            fr.pack(side='left', expand=True, padx=5)
        
        # Create and organize buttons
        for key, text, style in ComponentConfig.OPERATIONS:
            btn = ttk.Button(frame, text=text, style=style)
            btn.pack(side='left', padx=2)
            buttons[key] = btn
            
        return buttons

    def _create_results_section(self, parent: ttk.Frame) -> Dict[str, Any]:
        """Create results display section"""
        frame = ttk.LabelFrame(
            parent,
            text="Results",
            padding=5,
            style='Section.TLabelframe'
        )
        frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        
        # Search Frame
        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        
        ttk.Label(
            search_frame, 
            text="Search:", 
            style='Header.TLabel'
        ).pack(side='left', padx=(0, 5))
        
        search_entry = ttk.Entry(
            search_frame, 
            textvariable=self.vars['search_filter']
        )
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        filter_button = ttk.Button(
            search_frame,
            text="Filter",
            style='Action.TButton'
        )
        filter_button.pack(side='left')
        
        # Show Hidden Option
        ttk.Checkbutton(
            search_frame,
            text="Show Hidden",
            variable=self.vars['show_hidden']
        ).pack(side='left', padx=5)
        
        # Results Text Area
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=1, column=0, sticky='nsew')
        
        # Create text widget with specified configuration
        text_widget = tk.Text(
            text_frame,
            **ComponentConfig.TEXT_CONFIG
        )
        text_widget.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(
            text_frame,
            orient='vertical',
            command=text_widget.yview
        )
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        
        x_scrollbar = ttk.Scrollbar(
            text_frame,
            orient='horizontal',
            command=text_widget.xview
        )
        x_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure text widget scrolling
        text_widget.configure(
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        
        # Configure weights
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        return {
            'text': text_widget,
            'search': search_entry,
            'filter': filter_button
        }

    def _create_status_section(self, parent: ttk.Frame) -> Dict[str, Any]:
        """Create status bar section"""
        frame = ttk.Frame(parent)
        frame.grid(row=3, column=0, sticky='ew', pady=5)
        
        # Status Label
        status_label = ttk.Label(
            frame,
            textvariable=self.vars['status'],
            style='Status.TLabel'
        )
        status_label.pack(side='left', fill='x', expand=True)
        
        # Progress Bar
        progress_bar = ttk.Progressbar(
            frame,
            mode='indeterminate',  # Changed to indeterminate for better UX
            length=100
        )
        progress_bar.pack(side='right', padx=5)
        
        return {
            'label': status_label,
            'progress': progress_bar
        }

    def get_components(self) -> UIComponents:
        """Return all UI components"""
        return self.components

    def get_variables(self) -> Dict[str, Any]:
        """Return all tkinter variables"""
        return self.vars

if __name__ == "__main__":
    print("This module is not meant to be run directly.")
