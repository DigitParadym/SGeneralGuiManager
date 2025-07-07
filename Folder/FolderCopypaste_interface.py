import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pyperclip
from datetime import datetime

class CopypasteInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Content Copy Tool")
        self.root.geometry("800x600")
        
        # File type filter flag
        self.py_only = tk.BooleanVar(value=False)
        
        self.setup_gui()
        
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
        
        # File Type Filter
        filter_frame = ttk.Frame(mainframe)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        py_only_check = ttk.Checkbutton(
            filter_frame, 
            text=".py files only", 
            variable=self.py_only,
            command=self.refresh_preview
        )
        py_only_check.pack(side=tk.LEFT)
        
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
        
    def browse_folder(self):
        """Open folder browser and load file contents"""
        folder = filedialog.askdirectory(title="Select Target Folder")
        if folder:
            self.folder_path.set(folder)
            self.load_content(folder)
            
    def load_content(self, folder):
        """Load content of files based on filter settings"""
        try:
            self.preview.delete(1.0, tk.END)
            content = []
            
            # Determine which file types to include
            extensions = ('.py',) if self.py_only.get() else ('.py', '.log', '.csv')
            
            # Get files with selected extensions
            files = [f for f in os.listdir(folder) if f.endswith(extensions)]
            
            for file in files:
                file_path = os.path.join(folder, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
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
            
            if files:
                messagebox.showinfo("Success", f"Loaded {len(files)} files")
            else:
                messagebox.showwarning("Warning", "No eligible files found in selected folder")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading folder contents: {str(e)}")
            
    def refresh_preview(self):
        """Refresh the preview when filter changes"""
        if self.folder_path.get():
            self.load_content(self.folder_path.get())
            
    def copy_to_clipboard(self):
        """Copy preview content to clipboard"""
        content = self.preview.get(1.0, tk.END).strip()
        if content:
            try:
                pyperclip.copy(content)
                messagebox.showinfo("Success", "Content copied to clipboard!")
            except Exception as e:
                messagebox.showerror("Error", f"Error copying to clipboard: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No content to copy")
            
    def clear_preview(self):
        """Clear the preview text"""
        self.preview.delete(1.0, tk.END)

def main():
    root = tk.Tk()
    app = CopypasteInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()
