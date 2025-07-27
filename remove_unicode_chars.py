#!/usr/bin/env python3
"""
Remove Unicode Characters from Python Files
Replaces Unicode symbols with ASCII equivalents to prevent Windows encoding errors
"""

import os
import sys
import re
from pathlib import Path

def get_unicode_replacements():
    """Return mapping of Unicode characters to ASCII equivalents"""
    return {
        # Checkmarks and X marks
        '✅': '[SUCCESS]',
        '❌': '[ERROR]',
        '⚠️': '[WARNING]',
        '⚠': '[WARNING]',
        
        # Arrows and symbols
        '🚀': '[RUN]',
        '🎯': '[TARGET]',
        '🔧': '[CONFIG]',
        '⚙️': '[SETTINGS]',
        '📦': '[INSTALL]',
        '📊': '[STATS]',
        '🧪': '[TEST]',
        '🎛️': '[CONTROL]',
        '⏹️': '[STOP]',
        '⏱️': '[TIME]',
        'ℹ️': '[INFO]',
        '🌐': '[WEB]',
        '💾': '[SAVE]',
        '🔍': '[SEARCH]',
        '📋': '[LIST]',
        '🎉': '[SUCCESS]',
        '💡': '[TIP]',
        '⭐': '[STAR]',
        '🔥': '[HOT]',
        '📈': '[UP]',
        '📉': '[DOWN]',
        '🎁': '[GIFT]',
        '🎪': '[EVENT]',
        
        # Other symbols
        '•': '-',
        '→': '->',
        '←': '<-',
        '↑': '^',
        '↓': 'v',
        '✓': '[OK]',
        '✗': '[FAIL]',
        '⭕': '[NO]',
        '🔴': '[RED]',
        '🟢': '[GREEN]',
        '🟡': '[YELLOW]',
        '🔵': '[BLUE]',
    }

def fix_unicode_in_file(file_path):
    """Remove Unicode characters from a single file"""
    replacements = get_unicode_replacements()
    
    try:
        # Read file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        
        # Apply replacements
        for unicode_char, ascii_replacement in replacements.items():
            if unicode_char in content:
                content = content.replace(unicode_char, ascii_replacement)
                changes_made += 1
        
        # Remove any remaining non-ASCII characters (except newlines, tabs, etc.)
        # This regex keeps printable ASCII chars, newlines, tabs, and carriage returns
        content = re.sub(r'[^\x20-\x7E\n\r\t]', '', content)
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes_made
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Failed to process {file_path}: {e}")
        return 0

def main():
    """Main function to process all Python files"""
    print("UNICODE CHARACTER REMOVAL TOOL")
    print("=" * 50)
    print("Removing Unicode symbols to prevent Windows encoding errors...")
    
    project_root = Path(__file__).parent
    total_files = 0
    total_changes = 0
    
    # Find all Python files
    python_files = list(project_root.rglob("*.py"))
    
    print(f"\n[SCAN] Found {len(python_files)} Python files")
    
    for py_file in python_files:
        if py_file.name == __file__.split('/')[-1]:  # Skip this script
            continue
            
        print(f"[PROCESS] {py_file.relative_to(project_root)}")
        changes = fix_unicode_in_file(py_file)
        
        if changes > 0:
            print(f"  [FIXED] {changes} Unicode characters replaced")
            total_changes += changes
        else:
            print(f"  [CLEAN] No Unicode characters found")
        
        total_files += 1
    
    print(f"\n" + "=" * 50)
    print(f"[COMPLETE] Unicode removal finished")
    print(f"[STATS] Files processed: {total_files}")
    print(f"[STATS] Total changes: {total_changes}")
    
    if total_changes > 0:
        print(f"[SUCCESS] All Unicode characters replaced with ASCII equivalents")
        print(f"[INFO] Files should now work on Windows without encoding errors")
    else:
        print(f"[INFO] No Unicode characters found - files already clean")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[STOP] Process interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Process failed: {e}")
        sys.exit(1)