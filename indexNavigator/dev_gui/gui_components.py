#!/usr/bin/env python3
"""
GUI Components module for Index Navigator.
Defines UI component structures, styles, and configurations.
"""

import tkinter as tk
from tkinter import ttk, font
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

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
    update_index_button: ttk.Button
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

class ThemeColors:
    """Color definitions for UI theme."""
    
    # Main colors
    PRIMARY = '#0078D7'
    SECONDARY = '#6C757D'
    SUCCESS = '#4CAF50'
    WARNING = '#FFC107'
    ERROR = '#DC3545'
    INFO = '#17A2B8'
    
    # Background colors
    BG_LIGHT = '#F8F9FA'
    BG_DARK = '#343A40'
    BG_PRIMARY = '#E3F2FD'
    
    # Text colors
    TEXT_DARK = '#212529'
    TEXT_LIGHT = '#F8F9FA'
    TEXT_MUTED = '#6C757D'
    
    # Button colors
    BUTTON_PRIMARY = '#0078D7'
    BUTTON_SUCCESS = '#4CAF50'
    BUTTON_WARNING = '#FFC107'
    BUTTON_ERROR = '#DC3545'
    
    # Border colors
    BORDER_LIGHT = '#DEE2E6'
    BORDER_DARK = '#343A40'

class StyleManager:
    """Manages GUI styles and themes."""
    
    @classmethod
    def configure_styles(cls) -> None:
        """Configure ttk styles and themes."""
        style = ttk.Style()
        
        # Configure fonts
        cls._configure_fonts()
        
        # Configure general styles
        cls._configure_general_styles(style)
        
        # Configure button styles
        cls._configure_button_styles(style)
        
        # Configure label styles
        cls._configure_label_styles(style)
        
        # Configure frame styles
        cls._configure_frame_styles(style)
        
        # Configure entry styles
        cls._configure_entry_styles(style)
        
        # Configure progress bar style
        cls._configure_progress_styles(style)

    @staticmethod
    def _configure_fonts() -> None:
        """Configure default fonts."""
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=10)
        
        text_font = font.nametofont("TkTextFont")
        text_font.configure(size=10, family="Consolas")
        
        fixed_font = font.nametofont("TkFixedFont")
        fixed_font.configure(size=10, family="Consolas")

    @staticmethod
    def _configure_general_styles(style: ttk.Style) -> None:
        """Configure general widget styles."""
        style.configure('.',
                       background=ThemeColors.BG_LIGHT,
                       foreground=ThemeColors.TEXT_DARK,
                       borderwidth=1,
                       relief='flat')

    @staticmethod
    def _configure_button_styles(style: ttk.Style) -> None:
        """Configure button styles."""
        button_base = {
            'padding': 5,
            'relief': 'raised',
            'borderwidth': 1
        }
        
        style.configure('Primary.TButton',
                       **button_base,
                       background=ThemeColors.BUTTON_PRIMARY,
                       foreground=ThemeColors.TEXT_LIGHT)
        
        style.configure('Success.TButton',
                       **button_base,
                       background=ThemeColors.BUTTON_SUCCESS,
                       foreground=ThemeColors.TEXT_LIGHT)
        
        style.configure('Warning.TButton',
                       **button_base,
                       background=ThemeColors.BUTTON_WARNING,
                       foreground=ThemeColors.TEXT_DARK)
        
        style.configure('Error.TButton',
                       **button_base,
                       background=ThemeColors.BUTTON_ERROR,
                       foreground=ThemeColors.TEXT_LIGHT)
        
        style.configure('Action.TButton',
                       **button_base)
        
        style.configure('Critical.TButton',
                       **button_base,
                       foreground=ThemeColors.ERROR)
        
        style.configure('Update.TButton',
                       **button_base,
                       background=ThemeColors.SUCCESS,
                       foreground=ThemeColors.TEXT_LIGHT)

    @staticmethod
    def _configure_label_styles(style: ttk.Style) -> None:
        """Configure label styles."""
        style.configure('Info.TLabel',
                       padding=5,
                       foreground=ThemeColors.INFO)
        
        style.configure('Status.TLabel',
                       padding=5,
                       relief='sunken',
                       background=ThemeColors.BG_LIGHT)
        
        style.configure('Error.TLabel',
                       foreground=ThemeColors.ERROR)
        
        style.configure('Success.TLabel',
                       foreground=ThemeColors.SUCCESS)
        
        style.configure('Warning.TLabel',
                       foreground=ThemeColors.WARNING)
        
        style.configure('Header.TLabel',
                       font=('TkDefaultFont', 10, 'bold'),
                       padding=5)

    @staticmethod
    def _configure_frame_styles(style: ttk.Style) -> None:
        """Configure frame styles."""
        style.configure('Section.TLabelframe',
                       padding=10,
                       relief='solid',
                       borderwidth=1)
        
        style.configure('Section.TLabelframe.Label',
                       font=('TkDefaultFont', 10, 'bold'))

    @staticmethod
    def _configure_entry_styles(style: ttk.Style) -> None:
        """Configure entry styles."""
        style.configure('TEntry',
                       padding=5,
                       relief='solid',
                       borderwidth=1)

    @staticmethod
    def _configure_progress_styles(style: ttk.Style) -> None:
        """Configure progress bar styles."""
        style.configure('Horizontal.TProgressbar',
                       troughcolor=ThemeColors.BG_LIGHT,
                       background=ThemeColors.PRIMARY,
                       thickness=20)

class ComponentConfig:
    """Configuration constants for components."""
    
    # Window configuration
    WINDOW_MIN_SIZE = (900, 700)
    PADDING = 10
    
    # Button configurations
    OPERATIONS: List[Tuple[str, str, str]] = [
        ('update_index', "Update Index", 'Update.TButton'),
        ('add', "Add Path", 'Primary.TButton'),
        ('remove', "Remove Path", 'Critical.TButton'),
        ('lookup', "Lookup Path", 'Action.TButton'),
        ('verify', "Verify Paths", 'Action.TButton'),
        ('clear', "Clear Results", 'Action.TButton'),
        ('save', "Save Index", 'Primary.TButton'),
        ('refresh', "Refresh", 'Action.TButton')
    ]
    
    # Text widget configuration
    TEXT_CONFIG = {
        'wrap': 'none',
        'font': ('Consolas', 10),
        'background': ThemeColors.BG_LIGHT,
        'foreground': ThemeColors.TEXT_DARK,
        'insertbackground': ThemeColors.TEXT_DARK,
        'selectbackground': ThemeColors.PRIMARY,
        'selectforeground': ThemeColors.TEXT_LIGHT,
        'undo': True,
        'padx': 5,
        'pady': 5
    }
    
    # Entry configurations
    ENTRY_CONFIG = {
        'width': 50,
        'font': ('TkDefaultFont', 10)
    }
    
    # Default variables
    DEFAULT_VARS = {
        'root_path': '',
        'key': '',
        'path': '',
        'module': '',
        'status': '',
        'search_filter': '',
        'show_hidden': False,
        'auto_save': True,
        'relative_paths': True
    }
    
    # Grid configurations
    GRID_CONFIG = {
        'padx': 5,
        'pady': 5,
        'sticky': 'nsew'
    }
    
    # Section configurations
    SECTION_CONFIG = {
        'path': {
            'title': "File Management",
            'padding': 5,
            'columns': 4
        },
        'operations': {
            'title': "Operations",
            'padding': 5,
            'columns': 8
        },
        'results': {
            'title': "Results",
            'padding': 5,
            'columns': 1
        }
    }

    # Status bar configuration
    STATUS_CONFIG = {
        'progress_length': 100,
        'progress_mode': 'indeterminate',
        'status_relief': 'sunken',
        'status_padding': 5
    }

    @classmethod
    def get_section_config(cls, section_name: str) -> Dict[str, Any]:
        """Get configuration for a specific section."""
        return cls.SECTION_CONFIG.get(section_name, {})

if __name__ == "__main__":
    print("This module is not meant to be run directly.")
