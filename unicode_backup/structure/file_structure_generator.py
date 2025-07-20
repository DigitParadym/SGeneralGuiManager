
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText


class FileStructureGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("File Structure Viewer")
        # Increased the initial window size to ensure all controls are visible
        self.root.geometry("700x600")

        # Initialize variables
        self.target_folder = tk.StringVar()
        self.structure_content = ""

        # File to save last generated structure
        self.last_map_file = "last_structure.txt"

        # Set up the GUI
        self.setup_gui()

        # Load last structure if available
        self.load_last_map()

    def setup_gui(self):
        # Main frame with padding to prevent controls from sticking to the edges
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Target folder selection
        folder_label = ttk.Label(main_frame, text="Target Folder:")
        folder_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # Reduced width for the target folder entry
        folder_entry = ttk.Entry(main_frame, textvariable=self.target_folder, width=40)
        folder_entry.grid(row=0, column=1, sticky="ew")
        
        browse_button = ttk.Button(main_frame, text="Browse", command=self.browse_folder)
        browse_button.grid(row=0, column=2, padx=(10, 0))

        # Run button to generate structure
        run_button = ttk.Button(main_frame, text="Generate Structure", command=self.generate_structure)
        run_button.grid(row=1, column=0, columnspan=3, pady=(10, 10))

        # Copy to clipboard button
        copy_button = ttk.Button(main_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_button.grid(row=2, column=0, columnspan=3, pady=(0, 10))

        # Structure output display area with an increased width to use the available space
        self.output_text = ScrolledText(main_frame, wrap=tk.WORD, height=20)
        self.output_text.grid(row=3, column=0, columnspan=3, sticky="nsew")

        # Configure grid weights for responsive layout
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

    def browse_folder(self):
        """Browse and select a target folder."""
        folder = filedialog.askdirectory()
        if folder:
            self.target_folder.set(folder)

    def generate_structure(self):
        """Generate a text representation of the file structure."""
        folder = self.target_folder.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        # Include the target folder path as the root of the structure
        self.structure_content = f"{folder}\n" + self.folder_to_text(folder)

        # Display the structure content in the text widget
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, self.structure_content)

        # Save the last generated structure
        self.save_last_map()

    def folder_to_text(self, folder_path, prefix=""):
        """Recursively generate plain text structure with indentation, excluding specific folders and temporary files."""
        structure = ""
        contents = os.listdir(folder_path)
        pointers = ["├── "] * (len(contents) - 1) + ["└── "]
        
        for pointer, item in zip(pointers, contents):
            # Skip 'backups' and '__pycache__' folders, and temporary files (e.g., "a-", "b-", etc.)
            if item in ("backups", "__pycache__") or (len(item) > 2 and item[1] == '-' and 'a' <= item[0] <= 'z'):
                continue

            path = os.path.join(folder_path, item)
            structure += prefix + pointer + item + "\n"
            if os.path.isdir(path):
                extension = "│   " if pointer == "├── " else "    "
                structure += self.folder_to_text(path, prefix=prefix + extension)
        return structure

    def save_last_map(self):
        """Save the generated structure to a file."""
        if self.structure_content:
            try:
                with open(self.last_map_file, "w", encoding="utf-8") as file:
                    file.write(self.structure_content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save last map: {e}")

    def load_last_map(self):
        """Load the last saved structure file and display it."""
        if os.path.exists(self.last_map_file):
            try:
                with open(self.last_map_file, "r", encoding="utf-8") as file:
                    self.structure_content = file.read()
                    self.output_text.insert(tk.END, self.structure_content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load last map: {e}")

    def copy_to_clipboard(self):
        """Copy the structure content to the clipboard."""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.output_text.get(1.0, tk.END))
            self.root.update()  # Update the clipboard
            messagebox.showinfo("Success", "Structure copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {e}")


def main():
    root = tk.Tk()
    app = FileStructureGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
