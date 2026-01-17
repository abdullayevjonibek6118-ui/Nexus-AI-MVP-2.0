"""
Script to clean up unnecessary files from the project
Removes test files, cache, and temporary files
"""

import os
import shutil

def remove_path(path):
    """Remove file or directory"""
    try:
        if os.path.isfile(path):
            os.remove(path)
            print(f"   ✅ Removed file: {path}")
            return True
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"   ✅ Removed directory: {path}")
            return True
    except Exception as e:
        print(f"   ❌ Error removing {path}: {e}")
    return False

def cleanup():
    """Clean up project files"""
    print("🧹 Cleaning up unnecessary files...\n")
    
    # Files to remove
    files_to_remove = [
        'test_login.py',
        'test_backend_full.py',
        'translate_pages.py',
        'add_vacancy_timestamps.py',
    ]
    
    # Directories to remove
    dirs_to_remove = [
        '.ipynb_checkpoints',
        'frontend/.ipynb_checkpoints',
        'backend/app/__pycache__',
        'backend/app/api/__pycache__',
        'backend/app/core/__pycache__',
        'backend/app/db/__pycache__',
        'backend/app/models/__pycache__',
        'backend/app/schemas/__pycache__',
        'backend/app/services/__pycache__',
    ]
    
    removed_count = 0
    
    print("📁 Removing test files:")
    for file in files_to_remove:
        if remove_path(file):
            removed_count += 1
    
    print("\n📁 Removing cache directories:")
    for dir_path in dirs_to_remove:
        if remove_path(dir_path):
            removed_count += 1
    
    print(f"\n✅ Cleanup complete! Removed {removed_count} items")
    
    # List remaining important files
    print("\n📋 Project structure after cleanup:")
    important_files = [
        'README.md',
        'SECURITY.md',
        'backend/requirements.txt',
        'backend/.env.example',
        'frontend/index.html',
    ]
    
    for file in important_files:
        status = "✅" if os.path.exists(file) else "❌"
        print(f"   {status} {file}")

if __name__ == "__main__":
    cleanup()
