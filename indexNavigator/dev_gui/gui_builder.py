#!/usr/bin/env python3
"""
GUI Builder module for the Index Navigator.
Responsible for creating and managing the graphical interface components.
"""

import tkinter as tk
from tkinter import ttk, font
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class UIComponents:
    """Container for UI components"""
    main_frame: ttk.Frame
    root_entry: ttk.Entry
    path_entry: ttk.Entry
    module_entry: ttk.Entry
    results_text: tk.Text
    status_label: ttk.Label
    browse_button: ttk.Button
    root_button: ttk.Button
    add_button: ttk.Button
    remove_button: ttk.Button
    lookup_button: ttk.Button
    verify_button: ttk.Button
    clear_button: ttk.Button
    save_button: ttk.Button
    refresh_button: ttk.Button
    search_entry: ttk.Entry
    filter_button: ttk.Button
    progress_bar: ttk.Progressbar

class GUIBuilder:
    """Builder class for the Index Navigator GUI."""

    WINDOW_MIN_SIZE = (900, 700)
    PADDING = 10
    
    def __init__(self, root: tk.Tk):
        """Initialize the GUI builder."""
        self.root = root
        self.setup_window()
        self.init_variables()
        self.components = self.build_components()

    def setup_window(self) -> None:
        """Configure main window settings"""
        self.root.title("Index Navigator")
        self.root.minsize(*self.WINDOW_MIN_SIZE)
        
        # Configure window grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Setup styles
        self._configure_styles()

    def _configure_styles(self) -> None:
        """Configure ttk styles and themes"""
        style = ttk.Style()
        
        # Configure fonts
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=10)
        
        heading_font = font.Font(family="TkDefaultFont", size=10, weight="bold")
        
        # Style configurations
        style.configure('Primary.TButton',
                       padding=5,
                       font=heading_font)
        
        style.configure('Action.TButton',
                       padding=5)
        
        style.configure('Critical.TButton',
                       padding=5,
                       foreground='red')
        
        style.configure('Info.TLabel',
                       padding=5,
                       font=('TkDefaultFont', 9))
        
        style.configure('Status.TLabel',
                       padding=5,
                       relief='sunken')
        
        style.configure('Error.TLabel',
                       foreground='red')
        
        style.configure('Success.TLabel',
                       foreground='green')
        
        style.configure('Warning.TLabel',
                       foreground='orange')
        
        style.configure('Header.TLabel',
                       font=heading_font,
                       padding=5)
        
        style.configure('Section.TLabelframe',
                       padding=10)
        
        style.configure('Section.TLabelframe.Label',
                       font=heading_font)

    def init_variables(self) -> None:
        """Initialize tkinter variables"""
        self.vars = {
            'root_path': tk.StringVar(),
            'key': tk.StringVar(),
            'path': tk.StringVar(),
            'module': tk.StringVar(),
            'status': tk.StringVar(),
            'search_filter': tk.StringVar(),
            'show_hidden': tk.BooleanVar(value=False),
            'auto_save': tk.BooleanVar(value=True),
            'relative_paths': tk.BooleanVar(value=True)
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
        frame = ttk.Frame(self.root, padding=self.PADDING)
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
        
        ttk.Label(root_frame, text="Root Name:", style='Header.TLabel').pack(side='left', padx=(0, 5))
        
        root_entry = ttk.Entry(
            root_frame,
            textvariable=self.vars['root_path'],
            state='readonly',
            width=50
        )
        root_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        root_button = ttk.Button(
            root_frame,
            text="Select Root Folder",
            style='Primary.TButton',
            width=20
        )
        root_button.pack(side='left', padx=(0, 5))
        
        # Separator
        ttk.Separator(frame, orient='horizontal').grid(
            row=1, column=0, columnspan=4, sticky='ew', pady=5
        )
        
        # Key and Module
        ttk.Label(frame, text="Key:", style='Header.TLabel').grid(row=2, column=0, sticky='w')
        key_entry = ttk.Entry(frame, textvariable=self.vars['key'])
        key_entry.grid(row=2, column=1, sticky='ew', padx=5)
        
        ttk.Label(frame, text="Module:", style='Header.TLabel').grid(row=2, column=2, sticky='w')
        module_entry = ttk.Entry(frame, textvariable=self.vars['module'])
        module_entry.grid(row=2, column=3, sticky='ew', padx=5)
        
        # Path Selection
        ttk.Label(frame, text="Path:", style='Header.TLabel').grid(row=3, column=0, sticky='w')
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
        
        ttk.Checkbutton(
            options_frame,
            text="Use Relative Paths",
            variable=self.vars['relative_paths']
        ).pack(side='left', padx=5)
        
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
        operations = [
            ('add', "Add Path", 'Primary.TButton'),
            ('remove', "Remove Path", 'Critical.TButton'),
            ('lookup', "Lookup Path", 'Action.TButton'),
            ('verify', "Verify Paths", 'Action.TButton'),
            ('clear', "Clear Results", 'Action.TButton'),
            ('save', "Save Index", 'Primary.TButton'),
            ('refresh', "Refresh", 'Action.TButton')
        ]
        
        for i, (key, text, style) in enumerate(operations):
            btn = ttk.Button(frame, text=text, style=style)
            btn.grid(row=0, column=i, padx=2)
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
        
        ttk.Label(search_frame, text="Search:", style='Header.TLabel').pack(side='left', padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.vars['search_filter'])
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        filter_button = ttk.Button(
            search_frame,
            text="Filter",
            style='Action.TButton'
        )
        filter_button.pack(side='left')
        
        # Show Hidden Checkbox
        ttk.Checkbutton(
            search_frame,
            text="Show Hidden",
            variable=self.vars['show_hidden']
        ).pack(side='left', padx=5)
        
        # Results Text Area
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=1, column=0, sticky='nsew')
        
        text_widget = tk.Text(
            text_frame,
            wrap='none',
            font=('Consolas', 10),
            background='white',
            foreground='black',
            insertbackground='black',
            selectbackground='#0078D7',
            selectforeground='white',
            undo=True
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
            mode='determinate',
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

if __name__ == "__main__":
    print("This module is not meant to be run directly.")
