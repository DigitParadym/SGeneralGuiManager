
import os
import sys
import json
import shutil
import datetime
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any

@dataclass
class RunResult:
    '''Class to store the results of a script execution'''
    returncode: int
    stdout: str
    stderr: str

class RunManager:
    def __init__(self, base_dir: str):
        '''Initialize the RunManager with a base directory'''
        self.base_dir = base_dir
        self.srun_dir = os.path.join(base_dir, '.srun')
        self.history_file = os.path.join(self.srun_dir, 'run_history.log')
        
        if not os.path.exists(self.srun_dir):
            os.makedirs(self.srun_dir)
            
        if not os.path.exists(self.history_file):
            self._initialize_history_file()

    def _initialize_history_file(self) -> None:
        '''Initialize the history file with default structure'''
        initial_content = {
            "initialized": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "version": "1.0",
            "entries": []
        }
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(initial_content, f, indent=2)

    def set_history_file(self, file_path: str) -> Tuple[bool, str]:
        '''Set or create a new history file'''
        try:
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            self.history_file = file_path
            if not os.path.exists(file_path):
                self._initialize_history_file()
                return True, f"Created new history file: {file_path}"
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                if not isinstance(content, dict) or 'entries' not in content:
                    return False, "Invalid history file format"
            except json.JSONDecodeError:
                return False, "Invalid JSON format in history file"
            
            return True, f"Using existing history file: {file_path}"
            
        except Exception as e:
            return False, f"Error setting history file: {str(e)}"

    def run_script(self, 
                   script_path: str, 
                   script_args: str = "", 
                   use_venv: bool = False, 
                   history_file_name: str = "run_history.log",
                   include_content: bool = True, 
                   modular_files: Optional[List[str]] = None,
                   discussions: str = "") -> RunResult:
        '''Execute a Python script and record its execution in history'''
        try:
            if not os.path.exists(script_path):
                return RunResult(-1, "", f"Script not found: {script_path}")

            if modular_files:
                for file in modular_files:
                    if not os.path.exists(file):
                        return RunResult(-1, "", f"Modular file not found: {file}")

            if use_venv:
                venv_paths = [
                    os.path.join(self.srun_dir, 'venv', 'Scripts', 'python'),
                    os.path.join(self.srun_dir, 'venv', 'bin', 'python')
                ]
                python_path = next((p for p in venv_paths if os.path.exists(p)), None)
                if not python_path:
                    return RunResult(-1, "", "Virtual environment not found")
            else:
                python_path = sys.executable

            cmd = [python_path, script_path]
            if script_args:
                cmd.extend(script_args.split())

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            stdout, stderr = process.communicate()
            
            entry = {
                "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "script_path": script_path,
                "execution": {
                    "returncode": process.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "args": script_args,
                    "venv": use_venv
                }
            }

            if include_content:
                try:
                    with open(script_path, 'r', encoding='utf-8') as f:
                        entry["script_content"] = f.read()
                except Exception as e:
                    entry["script_content_error"] = f"Error reading script: {str(e)}"

            if modular_files:
                entry["modular_files"] = modular_files
                if include_content:
                    entry["modular_contents"] = {}
                    for file in modular_files:
                        try:
                            with open(file, 'r', encoding='utf-8') as f:
                                entry["modular_contents"][file] = f.read()
                        except Exception as e:
                            entry["modular_contents"][file] = f"Error reading file: {str(e)}"

            if discussions:
                entry["discussions"] = discussions

            self._write_history_entry(entry)
            
            return RunResult(process.returncode, stdout, stderr)
            
        except Exception as e:
            return RunResult(-1, "", str(e))

    def _write_history_entry(self, entry: Dict[str, Any]) -> None:
        '''Write an entry to the history file'''
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {"initialized": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                "version": "1.0", "entries": []}
            else:
                data = {"initialized": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "version": "1.0", "entries": []}
            
            data["entries"].append(entry)
            self._safe_write_json(data)
                
        except Exception as e:
            print(f"Error writing history: {str(e)}")

    def _safe_write_json(self, data: Dict) -> None:
        '''Safely write JSON data with backup'''
        backup_path = self.history_file + '.bak'
        try:
            if os.path.exists(self.history_file):
                shutil.copy2(self.history_file, backup_path)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            if os.path.exists(backup_path):
                os.remove(backup_path)
                
        except Exception as write_error:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, self.history_file)
            raise write_error

    def get_history_entries(self) -> List[Dict[str, Any]]:
        '''Get raw history entries for parsing'''
        try:
            if not os.path.exists(self.history_file):
                return []
                
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data["entries"]
            
        except Exception as e:
            print(f"Error reading history entries: {str(e)}")
            return []

    def get_history(self) -> str:
        '''Get formatted history content as string'''
        try:
            if not os.path.exists(self.history_file):
                return ""
                
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            lines = []
            for entry in data["entries"]:
                lines.append(f"=== Run at {entry['timestamp']} ===")
                lines.append(f"Script: {entry['script_path']}")
                
                if entry.get('modular_files'):
                    lines.append("Modular Files: " + ", ".join(entry['modular_files']))
                
                if entry.get('discussions'):
                    lines.append("\nDiscussions & Plans:\n" + entry['discussions'])
                
                if 'execution' in entry:
                    if entry['execution'].get('args'):
                        lines.append(f"\nArguments: {entry['execution']['args']}")
                    if entry['execution'].get('venv'):
                        lines.append("Virtual Environment: Enabled")
                    
                    if entry['execution'].get('stdout'):
                        lines.append("\nOutput:\n" + entry['execution']['stdout'])
                    if entry['execution'].get('stderr'):
                        lines.append("\nErrors:\n" + entry['execution']['stderr'])
                
                lines.append("\n" + "="*50 + "\n")
            
            return "\n".join(lines)
            
        except Exception as e:
            return f"Error reading history: {str(e)}"

    def backup_history(self, backup_name: Optional[str] = None) -> Tuple[bool, str]:
        '''Create a backup of the history file'''
        try:
            if not os.path.exists(self.history_file):
                return False, "No history file to backup"
            
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = backup_name or f"history_backup_{timestamp}.log"
            backup_path = os.path.join(self.srun_dir, backup_name)
            
            shutil.copy2(self.history_file, backup_path)
            return True, f"Backup created: {backup_path}"
            
        except Exception as e:
            return False, f"Backup failed: {str(e)}"

    def clear_history(self) -> Tuple[bool, str]:
        '''Clear the history file while creating a backup'''
        try:
            success, message = self.backup_history()
            if not success:
                return False, f"Failed to backup before clearing: {message}"
            
            self._initialize_history_file()
            return True, f"History cleared. {message}"
            
        except Exception as e:
            return False, f"Failed to clear history: {str(e)}"
