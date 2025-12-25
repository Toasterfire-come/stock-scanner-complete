#!/usr/bin/env python3
"""
Script to replace console.* statements with logger utility
Excludes src/lib/logger.js itself
"""

import os
import re
from pathlib import Path

FRONTEND_DIR = Path("/c/Stock-scanner-project/v2mvp-stock-scanner-complete/stock-scanner-complete/frontend")
SRC_DIR = FRONTEND_DIR / "src"
LOGGER_FILE = SRC_DIR / "lib" / "logger.js"

def calculate_relative_import(file_path):
    """Calculate the relative path to logger.js from the given file"""
    # Get relative path from file to src/lib/logger.js
    file_path = Path(file_path)
    src_path = Path(SRC_DIR)

    # Calculate depth
    try:
        rel_to_src = file_path.relative_to(src_path)
        parts = rel_to_src.parts[:-1]  # Exclude the filename
        depth = len(parts)

        if depth == 0:
            return "./lib/logger"
        else:
            return ("../" * depth) + "lib/logger"
    except ValueError:
        return "@/lib/logger"

def process_file(file_path):
    """Process a single file to replace console statements"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    # Check if file contains console statements
    if not re.search(r'console\.(log|error|warn|info|debug)\(', content):
        return False

    print(f"Processing: {file_path}")

    # Calculate import path
    import_path = calculate_relative_import(file_path)

    # Check if logger import already exists
    has_logger_import = bool(re.search(r'import\s+.*logger.*\s+from', content))

    if not has_logger_import:
        # Find the position to insert the import
        # Look for the last import statement
        import_pattern = r'^import\s+.*?;?\s*$'
        lines = content.split('\n')
        last_import_idx = -1

        for i, line in enumerate(lines):
            if re.match(import_pattern, line.strip()):
                last_import_idx = i

        # Insert the logger import
        import_statement = f"import logger from '{import_path}';"

        if last_import_idx >= 0:
            # Insert after the last import
            lines.insert(last_import_idx + 1, import_statement)
        else:
            # No imports found, add at the beginning
            # Skip any leading comments
            insert_idx = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith('//') and not stripped.startswith('/*') and not stripped.startswith('*'):
                    insert_idx = i
                    break
            lines.insert(insert_idx, import_statement)
            lines.insert(insert_idx + 1, '')  # Add blank line

        content = '\n'.join(lines)

    # Replace console statements
    replacements = [
        (r'console\.log\(', 'logger.info('),
        (r'console\.error\(', 'logger.error('),
        (r'console\.warn\(', 'logger.warn('),
        (r'console\.info\(', 'logger.info('),
        (r'console\.debug\(', 'logger.debug('),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # Write back to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}")
        return False

def main():
    """Main function to process all files"""
    processed_count = 0
    error_count = 0

    # Find all JS/JSX files
    for ext in ['*.js', '*.jsx']:
        for file_path in SRC_DIR.rglob(ext):
            # Skip logger.js itself
            if file_path == LOGGER_FILE:
                continue

            # Skip node_modules and other directories
            if 'node_modules' in str(file_path) or '__tests__' in str(file_path):
                continue

            try:
                if process_file(file_path):
                    processed_count += 1
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                error_count += 1

    print(f"\n[SUCCESS] Processed {processed_count} files")
    if error_count > 0:
        print(f"[ERROR] Errors: {error_count}")

    return processed_count, error_count

if __name__ == '__main__':
    processed, errors = main()
    exit(0 if errors == 0 else 1)
