#!/usr/bin/env python3
"""
Python Syntax Checker
Checks for syntax errors in Python files
"""

import ast
import sys
from pathlib import Path

def check_file_syntax(file_path):
"""Check if a Python file has syntax errors"""
try:
with open(file_path, 'r', encoding='utf-8') as f:
content = f.read()

# Try to parse the file
ast.parse(content, filename=str(file_path))
return True, None
except SyntaxError as e:
return False, f"Syntax Error: {e.msg} at line {e.lineno}"
except Exception as e:
return False, f"Error: {e}"

def main():
"""Check syntax of key files"""
print(" Python Syntax Checker")
print("=" * 30)

# Files to check
files_to_check = [
'core/admin.py',
'emails/__init__.py',
'stockscanner_django/settings.py',
'stockscanner_django/celery.py',
'manage.py',
]

all_good = True

for file_path in files_to_check:
file_obj = Path(file_path)
if file_obj.exists():
print(f" Checking {file_path}...")
is_valid, error = check_file_syntax(file_obj)

if is_valid:
print(f" Syntax OK")
else:
print(f" {error}")
all_good = False
else:
print(f" {file_path} not found")

print("\n" + "=" * 30)
if all_good:
print(" All files have valid syntax!")
return True
else:
print(" Syntax errors found!")
return False

if __name__ == "__main__":
success = main()
sys.exit(0 if success else 1)