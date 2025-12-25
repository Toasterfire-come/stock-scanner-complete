#!/usr/bin/env python3
"""
Script to replace all console.* statements with logger utility
Handles: console.log, console.error, console.warn, console.info, console.debug
"""

import os
import re
from pathlib import Path

# Counter for tracking changes
changes = {
    'files_processed': 0,
    'files_modified': 0,
    'log_replaced': 0,
    'error_replaced': 0,
    'warn_replaced': 0,
    'info_replaced': 0,
    'debug_replaced': 0
}

def has_logger_import(content):
    """Check if file already imports logger"""
    patterns = [
        r"import\s+logger\s+from\s+['\"].*logger",
        r"import\s+\{\s*logger\s*\}\s+from\s+['\"].*logger",
    ]
    for pattern in patterns:
        if re.search(pattern, content):
            return True
    return False

def add_logger_import(content, filepath):
    """Add logger import at the top of the file"""
    # Determine relative path to logger.js
    file_dir = os.path.dirname(filepath)
    src_dir = os.path.join(os.path.dirname(filepath).split('/src/')[0], 'src')

    # Calculate relative path
    rel_path = os.path.relpath(os.path.join(src_dir, 'lib', 'logger.js'), file_dir)
    if not rel_path.startswith('.'):
        rel_path = './' + rel_path
    rel_path = rel_path.replace('\\', '/')

    # Find the first import statement
    import_match = re.search(r'^import\s+', content, re.MULTILINE)

    if import_match:
        # Add after the first import
        pos = import_match.start()
        logger_import = f"import logger from '{rel_path}';\n"
        content = content[:pos] + logger_import + content[pos:]
    else:
        # Add at the very beginning
        logger_import = f"import logger from '{rel_path}';\n\n"
        content = logger_import + content

    return content

def replace_console_statements(content):
    """Replace all console.* with logger.*"""
    modified = False

    # Replace console.log
    new_content, count = re.subn(r'\bconsole\.log\b', 'logger.info', content)
    if count > 0:
        changes['log_replaced'] += count
        modified = True
        content = new_content

    # Replace console.error
    new_content, count = re.subn(r'\bconsole\.error\b', 'logger.error', content)
    if count > 0:
        changes['error_replaced'] += count
        modified = True
        content = new_content

    # Replace console.warn
    new_content, count = re.subn(r'\bconsole\.warn\b', 'logger.warn', content)
    if count > 0:
        changes['warn_replaced'] += count
        modified = True
        content = new_content

    # Replace console.info
    new_content, count = re.subn(r'\bconsole\.info\b', 'logger.info', content)
    if count > 0:
        changes['info_replaced'] += count
        modified = True
        content = new_content

    # Replace console.debug
    new_content, count = re.subn(r'\bconsole\.debug\b', 'logger.debug', content)
    if count > 0:
        changes['debug_replaced'] += count
        modified = True
        content = new_content

    return content, modified

def process_file(filepath):
    """Process a single file"""
    changes['files_processed'] += 1

    # Skip logger.js itself
    if 'logger.js' in filepath:
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if file has console statements
        if not re.search(r'\bconsole\.(log|error|warn|info|debug)\b', content):
            return

        # Replace console statements
        new_content, modified = replace_console_statements(content)

        if modified:
            # Add logger import if not present
            if not has_logger_import(new_content):
                new_content = add_logger_import(new_content, filepath)

            # Write back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

            changes['files_modified'] += 1
            print(f"✅ Modified: {filepath}")

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")

def main():
    """Main function to process all files"""
    src_dir = Path('src')

    if not src_dir.exists():
        print("❌ src directory not found. Run from frontend directory.")
        return

    print("🔍 Finding JavaScript/JSX files with console statements...")

    # Find all JS/JSX files
    js_files = list(src_dir.rglob('*.js')) + list(src_dir.rglob('*.jsx'))

    print(f"📁 Found {len(js_files)} JavaScript/JSX files")
    print("🔧 Processing files...\n")

    for filepath in js_files:
        process_file(str(filepath))

    print("\n" + "="*60)
    print("📊 SUMMARY:")
    print("="*60)
    print(f"Files processed: {changes['files_processed']}")
    print(f"Files modified: {changes['files_modified']}")
    print(f"console.log → logger.info: {changes['log_replaced']}")
    print(f"console.error → logger.error: {changes['error_replaced']}")
    print(f"console.warn → logger.warn: {changes['warn_replaced']}")
    print(f"console.info → logger.info: {changes['info_replaced']}")
    print(f"console.debug → logger.debug: {changes['debug_replaced']}")
    total = (changes['log_replaced'] + changes['error_replaced'] +
             changes['warn_replaced'] + changes['info_replaced'] +
             changes['debug_replaced'])
    print(f"\nTotal replacements: {total}")
    print("="*60)

    if changes['files_modified'] > 0:
        print("\n✅ All console statements replaced with logger!")
        print("🔍 Verify: grep -r \"console\\.\" src/ --include=\"*.js\" --include=\"*.jsx\"")
    else:
        print("\n✨ No console statements found or all already using logger!")

if __name__ == '__main__':
    main()
