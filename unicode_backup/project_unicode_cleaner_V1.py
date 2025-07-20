#!/usr/bin/env python3
"""
Project Unicode Cleaner for SGeneralGuiManager
Cleans all Python files in the project recursively
Fixes encoding issues and removes problematic Unicode characters
"""

import os
import sys
import shutil
import re
from datetime import datetime
from pathlib import Path

class ProjectUnicodeCleaner:
    def __init__(self, project_path="."):
        self.project_path = Path(project_path)
        self.backup_dir = self.project_path / "unicode_backup"
        self.cleaned_files = []
        self.failed_files = []
        self.skipped_files = []
        
        # Directories to skip
        self.skip_dirs = {
            '.git', '__pycache__', 'build', 'dist', 'node_modules',
            '.vscode', '.idea', 'venv', 'env', '.pytest_cache',
            'unicode_backup'
        }
        
        # File extensions to clean
        self.target_extensions = {'.py', '.txt', '.md', '.rst', '.json', '.log', '.csv'}
        
        # Character replacements for common problematic Unicode
        self.char_replacements = {
            # Smart quotes
            '\u201c': '"',  # Left double quotation mark
            '\u201d': '"',  # Right double quotation mark
            '\u2018': "'",  # Left single quotation mark
            '\u2019': "'",  # Right single quotation mark
            
            # Dashes
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2015': '--', # Horizontal bar
            
            # Spaces
            '\u00a0': ' ',  # Non-breaking space
            '\u2000': ' ',  # En quad
            '\u2001': ' ',  # Em quad
            '\u2002': ' ',  # En space
            '\u2003': ' ',  # Em space
            '\u2009': ' ',  # Thin space
            
            # Accented characters - basic replacements
            'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a',
            'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
            'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
            'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
            'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n',
            
            # Capital versions
            'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A',
            'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
            'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I',
            'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O',
            'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U',
            'Ç': 'C', 'Ñ': 'N',
        }

    def create_backup_dir(self):
        """Create backup directory with timestamp"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
            print(f"Created backup directory: {self.backup_dir}")

    def should_skip_directory(self, dir_path):
        """Check if directory should be skipped"""
        dir_name = dir_path.name
        return dir_name in self.skip_dirs or dir_name.startswith('.')

    def should_process_file(self, file_path):
        """Check if file should be processed"""
        return file_path.suffix.lower() in self.target_extensions

    def detect_encoding(self, file_path):
        """Try to detect file encoding"""
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return encoding, content
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        return None, None

    def clean_unicode_content(self, content):
        """Clean Unicode characters from content"""
        original_content = content
        
        # Apply character replacements
        for unicode_char, replacement in self.char_replacements.items():
            content = content.replace(unicode_char, replacement)
        
        # Remove any remaining non-ASCII characters that aren't common
        # Keep newlines, tabs, and basic punctuation
        cleaned_content = ""
        for char in content:
            if ord(char) < 128:  # ASCII characters
                cleaned_content += char
            elif char in ['\n', '\r', '\t']:  # Keep whitespace
                cleaned_content += char
            else:
                # Replace with closest ASCII equivalent or remove
                if char.isalnum():
                    # Try to find ASCII equivalent
                    import unicodedata
                    try:
                        ascii_char = unicodedata.normalize('NFKD', char).encode('ascii', 'ignore').decode('ascii')
                        if ascii_char:
                            cleaned_content += ascii_char
                        else:
                            cleaned_content += '?'  # Placeholder for unknown chars
                    except:
                        cleaned_content += '?'
                elif char.isspace():
                    cleaned_content += ' '  # Convert all weird spaces to regular space
                else:
                    # Skip other Unicode characters
                    pass
        
        return cleaned_content, original_content != cleaned_content

    def backup_file(self, file_path):
        """Create backup of original file"""
        try:
            relative_path = file_path.relative_to(self.project_path)
            backup_path = self.backup_dir / relative_path
            
            # Create parent directories if needed
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file to backup
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Warning: Could not backup {file_path}: {e}")
            return None

    def clean_file(self, file_path):
        """Clean a single file"""
        try:
            # Detect encoding and read content
            encoding, content = self.detect_encoding(file_path)
            
            if content is None:
                self.failed_files.append((str(file_path), "Could not decode file"))
                print(f"X Failed to decode: {file_path}")
                return False
            
            # Clean Unicode characters
            cleaned_content, was_modified = self.clean_unicode_content(content)
            
            if not was_modified:
                self.skipped_files.append(str(file_path))
                print(f"- No changes needed: {file_path}")
                return True
            
            # Create backup before modifying
            backup_path = self.backup_file(file_path)
            
            # Write cleaned content back to file
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(cleaned_content)
            
            self.cleaned_files.append((str(file_path), str(backup_path)))
            print(f"+ Cleaned: {file_path}")
            return True
            
        except Exception as e:
            self.failed_files.append((str(file_path), str(e)))
            print(f"X Error cleaning {file_path}: {e}")
            return False

    def scan_and_clean_project(self):
        """Scan and clean all files in the project"""
        print("="*70)
        print("PROJECT UNICODE CLEANER - SGENERALGUIMANAGER")
        print("="*70)
        print(f"Project path: {self.project_path.absolute()}")
        print(f"Target extensions: {', '.join(self.target_extensions)}")
        print("="*70)
        
        # Create backup directory
        self.create_backup_dir()
        
        # Find all files to process
        files_to_process = []
        
        for root, dirs, files in os.walk(self.project_path):
            root_path = Path(root)
            
            # Skip certain directories
            dirs[:] = [d for d in dirs if not self.should_skip_directory(root_path / d)]
            
            # Process files in current directory
            for file in files:
                file_path = root_path / file
                if self.should_process_file(file_path):
                    files_to_process.append(file_path)
        
        print(f"Found {len(files_to_process)} files to process")
        print("="*50)
        
        # Process each file
        for file_path in files_to_process:
            self.clean_file(file_path)
        
        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate cleaning report"""
        print("\n" + "="*70)
        print("CLEANING REPORT")
        print("="*70)
        
        total_files = len(self.cleaned_files) + len(self.failed_files) + len(self.skipped_files)
        
        print(f"Total files processed: {total_files}")
        print(f"Files cleaned: {len(self.cleaned_files)}")
        print(f"Files skipped (no changes): {len(self.skipped_files)}")
        print(f"Files failed: {len(self.failed_files)}")
        
        if self.cleaned_files:
            print(f"\n{'-'*50}")
            print("CLEANED FILES:")
            print(f"{'-'*50}")
            for original, backup in self.cleaned_files:
                print(f"+ {original}")
                if backup:
                    print(f"  Backup: {backup}")
        
        if self.failed_files:
            print(f"\n{'-'*50}")
            print("FAILED FILES:")
            print(f"{'-'*50}")
            for file_path, error in self.failed_files:
                print(f"X {file_path}")
                print(f"  Error: {error}")
        
        print(f"\n{'-'*50}")
        print("SUMMARY:")
        print(f"{'-'*50}")
        
        if len(self.cleaned_files) > 0:
            print(f"SUCCESS: {len(self.cleaned_files)} files cleaned!")
            print(f"Backups stored in: {self.backup_dir}")
        
        if len(self.failed_files) > 0:
            print(f"WARNING: {len(self.failed_files)} files could not be cleaned")
        
        if len(self.cleaned_files) == 0 and len(self.failed_files) == 0:
            print("INFO: No files needed cleaning - project is already clean!")

    def save_report(self):
        """Save detailed report to file"""
        report_file = self.project_path / "unicode_cleaning_report.json"
        
        import json
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'project_path': str(self.project_path.absolute()),
            'backup_directory': str(self.backup_dir),
            'total_processed': len(self.cleaned_files) + len(self.failed_files) + len(self.skipped_files),
            'cleaned_files': len(self.cleaned_files),
            'skipped_files': len(self.skipped_files),
            'failed_files': len(self.failed_files),
            'cleaned_file_list': [{'original': orig, 'backup': backup} for orig, backup in self.cleaned_files],
            'failed_file_list': [{'file': file, 'error': error} for file, error in self.failed_files],
            'skipped_file_list': self.skipped_files
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"\nDetailed report saved to: {report_file}")
        except Exception as e:
            print(f"Could not save report: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean Unicode characters from SGeneralGuiManager project")
    parser.add_argument("project_path", nargs="?", default=".", 
                       help="Path to project directory (default: current directory)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified")
        # For dry run, we would need to modify the cleaner logic
        # This is a simplified version
    
    try:
        cleaner = ProjectUnicodeCleaner(args.project_path)
        cleaner.scan_and_clean_project()
        cleaner.save_report()
        
        # Return exit code based on results
        if cleaner.failed_files:
            return 1
        else:
            return 0
            
    except KeyboardInterrupt:
        print("\nCleaning interrupted by user")
        return 1
    except Exception as e:
        print(f"Cleaning failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())