import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import ttk, filedialog, messagebox
import os

class SCopypastIndividualManager:
    def __init__(self, root):
        self.root = root
        self.root.title("SCopypastIndividual Manager")
        self.root.geometry("900x500")
        self.root.configure(background='#f0f0f0')
        
        # Configure styles for modern look
        self.style = ttk.Style()
        self.style.configure('Header.TLabel', 
                           font=('Segoe UI', 10, 'bold'),
                           background='#f0f0f0')
        self.style.configure('Status.TLabel', 
                           font=('Segoe UI', 9),
                           background='#f0f0f0')
        self.style.configure('File.TFrame', 
                           padding='1',
                           background='#f0f0f0')
        self.style.configure('TEntry',
                           padding=5,
                           relief='flat')
        self.style.configure('TButton',
                           padding=5,
                           relief='flat')
        self.style.configure("Readonly.TEntry", background="white")  # Custom readonly entry style
        
        self.MAX_FILES = 10
        self.file_paths = [""] * self.MAX_FILES
        self.file_labels = []
        self.file_entries = []
        self.browse_buttons = []
        
        self.target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SCopypastIndividual')
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)
        
        self._create_gui()
        
    def _create_gui(self):
        # Main container
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Top control panel
        control_panel = ttk.Frame(container)
        control_panel.pack(fill=tk.X, pady=(0, 5))
        
        # Left side - Target directory
        target_frame = ttk.Frame(control_panel)
        target_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(target_frame, text="Target:", 
                 style='Header.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.target_label = ttk.Entry(target_frame, state='readonly', style="Readonly.TEntry")
        self.target_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Right side - Action buttons
        button_frame = ttk.Frame(control_panel)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="📁 Browse",
                  command=self.browse_target_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="📋 Copy",
                  command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🗑 Clear",
                  command=self.reset_files).pack(side=tk.LEFT, padx=2)
        
        # Files section
        files_frame = ttk.LabelFrame(container, text="Files", padding=2)
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        # Compact headers
        header_frame = ttk.Frame(files_frame)
        header_frame.pack(fill=tk.X, pady=(0, 2))
        
        headers = [
            ("Name", 25),
            ("Path", 55),
            ("Actions", 15)
        ]
        
        for text, width in headers:
            ttk.Label(header_frame, text=text, width=width,
                     style='Header.TLabel').pack(side=tk.LEFT, padx=1)
        
        # Scrollable file list
        self.canvas = tk.Canvas(files_frame, background='#f0f0f0',
                              highlightthickness=0)
        scrollbar = ttk.Scrollbar(files_frame, orient="vertical",
                                command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create initial file rows
        for i in range(self.MAX_FILES):
            self._create_file_row(self.scrollable_frame, i)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Status bar
        self.status_label = ttk.Label(container, text="Ready", 
                                    style='Status.TLabel',
                                    relief='sunken',
                                    anchor='w')
        self.status_label.pack(fill=tk.X, pady=(5, 0))
        
    def _create_file_row(self, parent, index):
        frame = ttk.Frame(parent, style='File.TFrame')
        frame.pack(fill=tk.X, pady=1)
        
        # Name entry
        entry = ttk.Entry(frame, width=30)
        entry.insert(0, f"File {index + 1}")
        entry.pack(side=tk.LEFT, padx=1)
        entry.bind('<FocusIn>', lambda e, idx=index: self._on_entry_click(e, idx))
        entry.bind('<FocusOut>', lambda e, idx=index: self._on_focus_out(e, idx))
        self.file_entries.append(entry)
        
        # File path display
        file_label = ttk.Label(frame, text="No file selected",
                             background='white', relief='sunken',
                             width=55, anchor='w')
        file_label.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        self.file_labels.append(file_label)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side=tk.LEFT, padx=1)
        
        browse_btn = ttk.Button(btn_frame, text="📁",
                              width=3,
                              command=lambda idx=index: self.browse_file(idx))
        browse_btn.pack(side=tk.LEFT, padx=1)
        self.browse_buttons.append(browse_btn)
        
        remove_btn = ttk.Button(btn_frame, text="❌",
                              width=3,
                              command=lambda idx=index: self.remove_file(idx))
        remove_btn.pack(side=tk.LEFT, padx=1)
        remove_btn.pack_forget()
        setattr(frame, 'remove_btn', remove_btn)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def browse_target_folder(self):
        """Select target folder for file browsing"""
        folder = filedialog.askdirectory(
            initialdir=self.target_dir,
            title="Select Target Folder"
        )
        if folder:
            self.target_dir = folder
            self.target_label.configure(state='normal')
            self.target_label.delete(0, tk.END)
            self.target_label.insert(0, self.target_dir)
            self.target_label.configure(state='readonly')
            self.status_label.config(text="Target folder updated")
            
    def _on_entry_click(self, event, index):
        """Clear placeholder text when entry is clicked"""
        if self.file_entries[index].get() == f"File {index + 1}":
            self.file_entries[index].delete(0, tk.END)
            self.file_entries[index].config(foreground='black')
            
    def _on_focus_out(self, event, index):
        """Restore placeholder text if entry is empty"""
        if not self.file_entries[index].get():
            self.file_entries[index].insert(0, f"File {index + 1}")
            self.file_entries[index].config(foreground='gray')
                
    def remove_file(self, index):
        """Remove a file from the selected files"""
        self.file_paths[index] = ""
        self.file_labels[index].config(text="No file selected")
        self.file_entries[index].delete(0, tk.END)
        self._on_focus_out(None, index)  # Restore placeholder
        
        # Hide remove button
        frame = self.file_labels[index].master
        frame.remove_btn.pack_forget()
            
    def browse_file(self, index):
        """Open file dialog and store selected file path"""
        used_slots = len([f for f in self.file_paths if f])
        if used_slots >= self.MAX_FILES and not self.file_paths[index]:
            messagebox.showwarning("File Limit Reached", 
                                 f"Maximum {self.MAX_FILES} files allowed. Please remove a file first.")
            return
            
        file_types = [
            ('Python files', '*.py'),
            ('Log files', '*.log'),
            ('CSV files', '*.csv'),
            ('Text files', '*.txt'),
            ('All files', '*.*')
        ]
        
        try:
            file_path = filedialog.askopenfilename(
                filetypes=file_types,
                title=f"Select File {index + 1}",
                initialdir=self.target_dir
            )
            
            if file_path:
                if file_path in self.file_paths:
                    messagebox.showwarning("Duplicate File", 
                                         "This file is already selected!")
                    return
                    
                self.file_paths[index] = file_path
                self.file_labels[index].config(text=os.path.basename(file_path))
                
                # Update entry with file name without extension if it's still default
                current_entry = self.file_entries[index].get()
                if current_entry == f"File {index + 1}":
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    self.file_entries[index].delete(0, tk.END)
                    self.file_entries[index].insert(0, base_name)
                    self.file_entries[index].config(foreground='black')
                
                # Show remove button
                frame = self.file_labels[index].master
                frame.remove_btn.pack(side=tk.LEFT, padx=1)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting file: {str(e)}")
            
    def copy_to_clipboard(self):
        """Copy contents of all selected files to clipboard"""
        try:
            clipboard_content = []
            selected_files = [(i, f) for i, f in enumerate(self.file_paths) if f]
            
            if not selected_files:
                messagebox.showwarning("Warning", "No files selected to copy!")
                return
                
            for index, file_path in selected_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        root_name = self.file_entries[index].get()
                        if root_name == f"File {index + 1}":
                            root_name = os.path.splitext(os.path.basename(file_path))[0]
                            
                        separator = "=" * (len(root_name) + 8)
                        clipboard_content.append(
                            f"\n{separator}\n=== {root_name} ===\n{separator}\n{content}"
                        )
                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Error reading file {os.path.basename(file_path)}: {str(e)}"
                    )
                    return
            
            if clipboard_content:
                self.root.clipboard_clear()
                self.root.clipboard_append('\n'.join(clipboard_content))
                
                file_count = len(selected_files)
                message = f"Contents of {file_count} file{'s' if file_count > 1 else ''} copied to clipboard!"
                self.status_label.config(text=message)
                messagebox.showinfo("Success", message)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error copying to clipboard: {str(e)}")
            
    def reset_files(self):
        """Clear all selected files and reset labels"""
        selected_count = len([f for f in self.file_paths if f])
        
        if selected_count > 0:
            if messagebox.askyesno("Confirm Clear", 
                                 f"Clear all {selected_count} selected file{'s' if selected_count > 1 else ''}?"):
                self.file_paths = [""] * self.MAX_FILES
                
                for i, label in enumerate(self.file_labels):
                    label.config(text="No file selected")
                    self.file_entries[i].delete(0, tk.END)
                    self._on_focus_out(None, i)  # Restore placeholder
                    
                    # Hide remove button
                    frame = label.master
                    frame.remove_btn.pack_forget()
                    
                self.status_label.config(text="All files cleared")
        else:
            self.status_label.config(text="No files to clear")

def main():
    try:
        root = ThemedTk(theme="arc")  # Using the arc theme for modern look
    except Exception:
        root = tk.Tk()  # Fallback if ThemedTk fails
        ttk.Style().theme_use("clam")  # Default theme as fallback
    app = SCopypastIndividualManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
