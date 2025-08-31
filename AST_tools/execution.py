#!/usr/bin/env python3
"""
A powerful and safe script to clean up unnecessary files and folders
from the AST_tools project directory.
"""
import os
import shutil
import argparse
from pathlib import Path

# --- Configuration: Define what is considered "unnecessary" ---

# Cache directories to be completely removed.
CACHE_DIRS = [
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
]

# File patterns and suffixes for backup/temporary files.
FILE_PATTERNS_TO_DELETE = [
    "*.bak",
    "*.bak_*",  # <-- ADDED: Catches timestamped backups like .bak_20250829
    "*.backup",
    "*_backup_*.py",
    "*_old.py",
]

# Specific files to delete.
SPECIFIC_FILES_TO_DELETE = [
    "ast_tools.log",
    "ast_tools_previous.log",
    "errors.log",
    "project_files.txt",
]

# Shim files at the root to be deleted (they can be regenerated).
SHIM_FILES_AT_ROOT = [
    "base_transformer.py",
    "base_wrapper.py",
    "professional_file_filter.py",
    "pyupgrade_wrapper.py",
    "ruff_wrapper.py",
    "transformation_loader.py",
]

def find_items_to_clean(root_path: Path):
    """Finds all files and directories matching the cleanup criteria."""
    items_to_delete = []

    # Find all matching items recursively
    for item in root_path.rglob("*"):
        # 1. Check for cache directories
        if item.is_dir() and item.name in CACHE_DIRS:
            items_to_delete.append(item)
            continue

        # 2. Check for file patterns
        if item.is_file():
            for pattern in FILE_PATTERNS_TO_DELETE:
                if item.match(pattern):
                    items_to_delete.append(item)
                    break  # Move to next item once matched
    
    # 3. Check for specific files anywhere in the project
    for file_name in SPECIFIC_FILES_TO_DELETE:
        items_to_delete.extend(root_path.rglob(file_name))

    # 4. Check for shim files only at the project root
    for file_name in SHIM_FILES_AT_ROOT:
        item = root_path / file_name
        if item.exists() and item.is_file():
            items_to_delete.append(item)

    # Return a unique, sorted list
    return sorted(list(set(items_to_delete)))

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Clean unnecessary files from the project directory."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--show",
        action="store_true",
        help="Show which files and folders would be deleted (dry run)."
    )
    group.add_argument(
        "--apply",
        action="store_true",
        help="Permanently delete the unnecessary files and folders."
    )
    args = parser.parse_args()

    project_root = Path('.').resolve()
    items_to_delete = find_items_to_clean(project_root)

    if not items_to_delete:
        print("[OK] Project is already clean. Nothing to do.")
        return

    print("=" * 60)
    if args.show:
        print(f"DRY RUN: The following {len(items_to_delete)} items would be deleted:")
    else:
        print(f"The following {len(items_to_delete)} items will be PERMANENTLY DELETED:")
    print("=" * 60)
    
    for item in items_to_delete:
        item_type = "DIR " if item.is_dir() else "FILE"
        print(f"  [{item_type}] {item.relative_to(project_root)}")
    
    print("=" * 60)

    if args.apply:
        confirm = input("Are you sure you want to continue? (yes/no): ").lower()
        if confirm == 'yes':
            print("\nApplying cleanup...")
            deleted_count = 0
            for item in items_to_delete:
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                        print(f"  [DELETED DIR] {item.relative_to(project_root)}")
                    elif item.is_file():
                        item.unlink()
                        print(f"  [DELETED FILE] {item.relative_to(project_root)}")
                    deleted_count += 1
                except Exception as e:
                    print(f"  [ERROR] Could not delete {item}: {e}")
            print(f"\n[SUCCESS] Cleanup complete. {deleted_count} items were deleted.")
        else:
            print("\nCleanup cancelled.")

if __name__ == "__main__":
    main()