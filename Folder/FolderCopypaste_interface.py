import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pyperclip
import json
from datetime import datetime

class CopypasteInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Content Copy Tool - Advanced")
        self.root.geometry("900x700")
        
        # Settings file path
        self.settings_file = os.path.join(os.path.dirname(__file__), 'folder_settings.json')
        
        # File type mode: 0=Python, 1=Web, 2=Doc, 3=Full
        self.file_mode = tk.IntVar(value=0)
        
        # Recursive scan option
        self.recursive_scan = tk.BooleanVar(value=False)
        
        # Load previous settings
        self.load_settings()
        
        self.setup_gui()
        
        # Load last folder path if exists
        self.restore_last_folder()
        
    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    
                # Restore previous settings
                self.last_folder_path = settings.get('last_folder_path', '')
                self.file_mode.set(settings.get('file_mode', 0))
                self.recursive_scan.set(settings.get('recursive_scan', False))
            else:
                # Default settings
                self.last_folder_path = ''
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.last_folder_path = ''
    
    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            settings = {
                'last_folder_path': self.folder_path.get() if hasattr(self, 'folder_path') else '',
                'file_mode': self.file_mode.get(),
                'recursive_scan': self.recursive_scan.get(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Error saving settings: {e}")
        
    def setup_gui(self):
        # Main container
        mainframe = ttk.Frame(self.root, padding="5")
        mainframe.pack(fill=tk.BOTH, expand=True)
        
        # Target Folder Selection
        folder_frame = ttk.LabelFrame(mainframe, text="Target Folder", padding="5")
        folder_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.folder_path = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=60)
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT)
        
        # File Type Selection
        filetype_frame = ttk.LabelFrame(mainframe, text="File Type Mode", padding="5")
        filetype_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Radio buttons for file modes
        modes = [
            ("Python only (.py)", 0),
            ("Web development (.py, .html, .css, .js)", 1),
            ("Documentation (.py, .md, .txt, .rst)", 2),
            ("Full scan (.py, .html, .css, .js, .md, .txt, .rst, .log, .csv, .json)", 3)
        ]
        
        for text, value in modes:
            rb = ttk.Radiobutton(
                filetype_frame, 
                text=text, 
                variable=self.file_mode, 
                value=value,
                command=self.on_settings_change
            )
            rb.pack(anchor=tk.W, padx=5, pady=2)
        
        # Options Frame
        options_frame = ttk.LabelFrame(mainframe, text="Options", padding="5")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Recursive scan checkbox
        recursive_check = ttk.Checkbutton(
            options_frame, 
            text="Recursive scan (includes subdirectories)", 
            variable=self.recursive_scan,
            command=self.on_settings_change
        )
        recursive_check.pack(anchor=tk.W, padx=5, pady=2)
        
        # Status label
        self.status_label = ttk.Label(options_frame, text="Ready - Settings auto-saved", foreground="green")
        self.status_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Content Preview
        preview_frame = ttk.LabelFrame(mainframe, text="Content Preview", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar to preview
        preview_scroll = ttk.Scrollbar(preview_frame)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preview = tk.Text(preview_frame, wrap=tk.WORD, yscrollcommand=preview_scroll.set)
        self.preview.pack(fill=tk.BOTH, expand=True)
        preview_scroll.config(command=self.preview.yview)
        
        # Buttons
        button_frame = ttk.Frame(mainframe)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        copy_btn = ttk.Button(button_frame, text="Copy Content", command=self.copy_to_clipboard)
        copy_btn.pack(side=tk.RIGHT, padx=5)
        
        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_preview)
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        refresh_btn = ttk.Button(button_frame, text="Refresh", command=self.refresh_preview)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Auto-save settings when window closes
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def restore_last_folder(self):
        """Restore the last used folder path"""
        if self.last_folder_path and os.path.exists(self.last_folder_path):
            self.folder_path.set(self.last_folder_path)
            self.status_label.config(text=f"Restored last folder: {os.path.basename(self.last_folder_path)}", foreground="blue")
            # Auto-load content if folder exists
            self.load_content(self.last_folder_path)
        
    def on_settings_change(self):
        """Called when user changes settings - auto-save and refresh"""
        self.save_settings()
        self.refresh_preview()
        
    def on_closing(self):
        """Called when application is closing - save settings"""
        self.save_settings()
        self.root.destroy()

    def get_extensions(self):
        """Get file extensions based on selected mode"""
        mode = self.file_mode.get()
        
        if mode == 0:  # Python only
            return ('.py',)
        elif mode == 1:  # Web development
            return ('.py', '.html', '.htm', '.css', '.js')
        elif mode == 2:  # Documentation
            return ('.py', '.md', '.txt', '.rst')
        elif mode == 3:  # Full scan
            return ('.py', '.html', '.htm', '.css', '.js', '.md', '.txt', '.rst', '.log', '.csv', '.json')
        else:
            return ('.py',)
    
    def browse_folder(self):
        """Open folder browser and load file contents"""
        # Start from last folder if it exists, otherwise use current folder
        initial_dir = self.folder_path.get() if self.folder_path.get() and os.path.exists(self.folder_path.get()) else os.getcwd()
        
        folder = filedialog.askdirectory(title="Select Target Folder", initialdir=initial_dir)
        if folder:
            self.folder_path.set(folder)
            self.save_settings()  # Save immediately when folder changes
            self.load_content(folder)
            
    def load_content(self, folder):
        """Load content of files based on mode and recursive settings"""
        try:
            self.preview.delete(1.0, tk.END)
            self.status_label.config(text="Loading...", foreground="orange")
            self.root.update()
            
            content = []
            files_found = []
            
            # Get extensions based on selected mode
            extensions = self.get_extensions()
            
            # Choose scan method based on recursive option
            if self.recursive_scan.get():
                # Recursive scan with os.walk()
                for root, dirs, files in os.walk(folder):
                    # Skip hidden directories and build directories
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'build', 'dist', 'node_modules']]
                    
                    for file in files:
                        if file.endswith(extensions):
                            file_path = os.path.join(root, file)
                            files_found.append(file_path)
                            
                            try:
                                with open(file_path, 'r') as f:
                                    file_content = f.read()
                                
                                # Calculate relative path for cleaner display
                                relative_path = os.path.relpath(file_path, folder)
                                
                                content.append(f"\n{'='*50}")
                                content.append(f"\nFile: {relative_path}")
                                content.append(f"\n{'='*50}\n")
                                content.append(file_content)
                                content.append("\n")
                                
                            except Exception as e:
                                relative_path = os.path.relpath(file_path, folder)
                                content.append(f"\nError reading {relative_path}: {str(e)}\n")
            else:
                # Simple scan with os.listdir() - current folder only
                files = [f for f in os.listdir(folder) if f.endswith(extensions)]
                
                for file in files:
                    file_path = os.path.join(folder, file)
                    files_found.append(file_path)
                    
                    try:
                        with open(file_path, 'r') as f:
                            file_content = f.read()
                            content.append(f"\n{'='*50}")
                            content.append(f"\nFile: {file}")
                            content.append(f"\n{'='*50}\n")
                            content.append(file_content)
                            content.append("\n")
                    except Exception as e:
                        content.append(f"\nError reading {file}: {str(e)}\n")
            
            final_content = "".join(content)
            self.preview.insert(tk.END, final_content)
            
            # AUTO-COPY: Automatically copy content to clipboard
            if final_content.strip():
                try:
                    pyperclip.copy(final_content)
                    auto_copy_success = True
                except Exception as e:
                    auto_copy_success = False
            else:
                auto_copy_success = False
            
            # Update status with scan info and auto-copy result
            scan_type = "recursive" if self.recursive_scan.get() else "simple"
            mode_names = ["Python", "Web dev", "Documentation", "Full scan"]
            mode_name = mode_names[self.file_mode.get()]
            
            if files_found:
                if auto_copy_success:
                    self.status_label.config(
                        text=f"Auto-copied {len(files_found)} files to clipboard! ({mode_name}, {scan_type})", 
                        foreground="blue"
                    )
                    scan_msg = f"Loaded and auto-copied {len(files_found)} files using {scan_type} {mode_name} mode.\nContent is ready to paste!\nFolder path saved for next session."
                else:
                    self.status_label.config(
                        text=f"Loaded {len(files_found)} files - auto-copy failed ({mode_name}, {scan_type})", 
                        foreground="orange"
                    )
                    scan_msg = f"Loaded {len(files_found)} files using {scan_type} {mode_name} mode.\nAuto-copy failed - use Copy Content button.\nFolder path saved for next session."
                
                messagebox.showinfo("Success", scan_msg)
            else:
                self.status_label.config(text="No eligible files found", foreground="red")
                messagebox.showwarning("Warning", f"No files found with {mode_name} mode in selected location.")
                
        except Exception as e:
            self.status_label.config(text="Error occurred", foreground="red")
            messagebox.showerror("Error", f"Error loading folder contents: {str(e)}")
            
    def refresh_preview(self):
        """Refresh the preview when settings change"""
        if self.folder_path.get():
            self.load_content(self.folder_path.get())
            
    def copy_to_clipboard(self):
        """Copy preview content to clipboard"""
        content = self.preview.get(1.0, tk.END).strip()
        if content:
            try:
                pyperclip.copy(content)
                self.status_label.config(text="Content manually copied to clipboard!", foreground="blue")
                messagebox.showinfo("Success", "Content copied to clipboard!")
            except Exception as e:
                self.status_label.config(text="Manual copy failed", foreground="red")
                messagebox.showerror("Error", f"Error copying to clipboard: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No content to copy")
            
    def clear_preview(self):
        """Clear the preview text"""
        self.preview.delete(1.0, tk.END)
        self.status_label.config(text="Preview cleared", foreground="green")

def main():
    root = tk.Tk()
    app = CopypasteInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()