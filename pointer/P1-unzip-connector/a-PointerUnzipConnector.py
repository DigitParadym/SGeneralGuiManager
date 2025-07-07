import os
import subprocess
import logging
import tkinter as tk
from threading import Thread

# Logging setup
LOG_FILE = os.path.join(os.path.dirname(__file__), "pointer_connector_gui.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DOWNLOADS_FOLDER = os.path.expanduser("~/Downloads")  # Folder to monitor for ZIP files
UNZIP_UTILITY_RELATIVE_PATH = os.path.join("..", "..", "SUnZip", "unzip_utility.py")

def get_latest_zip(folder):
    """
    Find the latest `.zip` file in the specified folder.
    """
    zip_files = [f for f in os.listdir(folder) if f.endswith(".zip")]
    if not zip_files:
        return None
    # Sort files by modified time and return the latest
    zip_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
    return os.path.join(folder, zip_files[0])

def trigger_unzip_utility(zip_path, extract_path, log_callback):
    """
    Trigger the external `unzip_utility.py` script.
    """
    # Resolve relative path for the utility
    base_dir = os.path.dirname(__file__)
    unzip_utility_path = os.path.join(base_dir, UNZIP_UTILITY_RELATIVE_PATH)
    log_callback(f"Triggering external unzip utility for: {zip_path}")
    
    if not os.path.exists(unzip_utility_path):
        log_callback(f"Error: Unzip utility script not found at: {unzip_utility_path}")
        return False

    try:
        # Run the external unzip utility
        result = subprocess.run(
            ["python", unzip_utility_path, zip_path, extract_path],
            capture_output=True,
            text=True,
            check=True
        )
        log_callback("Unzip utility completed successfully.")
        log_callback(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        log_callback(f"Error: Unzip utility failed: {e.stderr}")
    except Exception as e:
        log_callback(f"Error: Unexpected error: {str(e)}")

    return False

class PointerConnectorUnzipGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pointer Connector Unzip")

        # UI Components
        self.run_button = tk.Button(root, text="Run", command=self.run_process)
        self.run_button.pack(pady=10)

        tk.Label(root, text="Logs:").pack(pady=5)
        self.log_text = tk.Text(root, height=15, width=70, state="disabled")
        self.log_text.pack(padx=10, pady=5)

    def append_log(self, message):
        """Append a log message to the log text box."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see(tk.END)

    def run_process(self):
        """Run the unzip and connector processes."""
        # Disable the button during the process
        self.run_button.config(state="disabled")

        def process_thread():
            """Run the unzip and connector processes in a thread."""
            self.append_log(f"Checking for the latest ZIP file in: {DOWNLOADS_FOLDER}")
            latest_zip = get_latest_zip(DOWNLOADS_FOLDER)
            
            if not latest_zip:
                self.append_log("No ZIP files found in the downloads folder.")
                self.run_button.config(state="normal")
                return

            self.append_log(f"Latest ZIP file found: {latest_zip}")
            extract_path = os.path.join(DOWNLOADS_FOLDER, "latest_extracted")
            os.makedirs(extract_path, exist_ok=True)

            if trigger_unzip_utility(latest_zip, extract_path, self.append_log):
                self.append_log("Unzipping successful using unzip utility.")
            else:
                self.append_log("Unzipping failed.")

            # Re-enable the button after the process
            self.run_button.config(state="normal")

        # Start the process in a separate thread
        Thread(target=process_thread).start()

if __name__ == "__main__":
    root = tk.Tk()
    gui = PointerConnectorUnzipGUI(root)
    root.mainloop()
