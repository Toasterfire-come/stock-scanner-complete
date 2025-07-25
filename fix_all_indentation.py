#!/usr/bin/env python3
"""
Comprehensive Indentation Fix Script
Fixes all Python indentation issues in the repository
"""

import os
import ast
import re
from pathlib import Path

def fix_python_indentation(file_path):
    """Fix indentation issues in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the original file
        try:
            ast.parse(content)
            print(f"✓ {file_path} - already valid")
            return True
        except SyntaxError:
            pass  # Continue to fix
        
        # Split into lines
        lines = content.split('\n')
        fixed_lines = []
        indent_level = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip empty lines and comments at the start
            if not stripped or stripped.startswith('#'):
                fixed_lines.append(line)
                continue
            
            # Determine expected indentation based on previous lines
            if i > 0:
                prev_line = lines[i-1].strip()
                
                # Increase indent after these patterns
                if (prev_line.endswith(':') or 
                    prev_line.startswith('def ') or 
                    prev_line.startswith('class ') or
                    prev_line.startswith('if ') or
                    prev_line.startswith('elif ') or
                    prev_line.startswith('else:') or
                    prev_line.startswith('try:') or
                    prev_line.startswith('except') or
                    prev_line.startswith('finally:') or
                    prev_line.startswith('for ') or
                    prev_line.startswith('while ') or
                    prev_line.startswith('with ')):
                    indent_level += 1
                
                # Decrease indent for these patterns
                if (stripped.startswith('except') or
                    stripped.startswith('elif ') or
                    stripped.startswith('else:') or
                    stripped.startswith('finally:')):
                    if indent_level > 0:
                        indent_level -= 1
            
            # Apply proper indentation
            if stripped:
                proper_indent = '    ' * indent_level
                fixed_lines.append(proper_indent + stripped)
            else:
                fixed_lines.append('')
        
        # Join back and test
        fixed_content = '\n'.join(fixed_lines)
        
        try:
            ast.parse(fixed_content)
            # Write the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✓ {file_path} - fixed indentation")
            return True
        except SyntaxError as e:
            print(f"✗ {file_path} - could not auto-fix: {e}")
            return False
            
    except Exception as e:
        print(f"✗ {file_path} - error: {e}")
        return False

def manual_fixes():
    """Apply specific manual fixes for known issues"""
    
    # Fix manage.py
    manage_py_content = '''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Configure PyMySQL for Windows MySQL compatibility
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
'''
    
    # Fix stockscanner_django/__init__.py
    init_py_content = '''# projectname/__init__.py
import os

# Only import Celery if explicitly enabled
if os.environ.get('CELERY_ENABLED', 'false').lower() == 'true':
    try:
        from .celery import app as celery_app
        __all__ = ("celery_app",)
    except Exception:
        # If Celery import fails, continue without it
        pass
else:
    # Development mode - no Celery
    pass
'''
    
    # Apply fixes
    fixes = [
        ('manage.py', manage_py_content),
        ('stockscanner_django/__init__.py', init_py_content)
    ]
    
    for file_path, content in fixes:
        if Path(file_path).exists():
            try:
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"✓ {file_path} - manually fixed")
            except Exception as e:
                print(f"✗ {file_path} - manual fix failed: {e}")

def fix_settings_py():
    """Fix specific issues in settings.py"""
    settings_file = Path('stockscanner_django/settings.py')
    if not settings_file.exists():
        return
    
    try:
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # Fix common indentation patterns
        fixes = [
            # Fix try/except blocks
            (r'^try:\n([^\n]+)', r'try:\n    \1'),
            (r'^except ([^:]+):\n([^\n]+)', r'except \1:\n    \2'),
            (r'^from dotenv import load_dotenv\nload_dotenv\(\)', 
             r'    from dotenv import load_dotenv\n    load_dotenv()'),
            
            # Fix if statements
            (r'^if ([^:]+):\n([^\n]+)', r'if \1:\n    \2'),
            (r'^else:\n([^\n]+)', r'else:\n    \1'),
            
            # Fix function calls in if blocks
            (r'if additional_hosts:\nALLOWED_HOSTS\.extend', 
             r'if additional_hosts:\n    ALLOWED_HOSTS.extend')
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Write back
        with open(settings_file, 'w') as f:
            f.write(content)
        
        print("✓ stockscanner_django/settings.py - applied manual fixes")
        
    except Exception as e:
        print(f"✗ stockscanner_django/settings.py - manual fix failed: {e}")

def main():
    """Main function to fix all indentation issues"""
    print("COMPREHENSIVE INDENTATION FIX")
    print("=" * 50)
    
    # Apply manual fixes first
    print("\nApplying manual fixes...")
    manual_fixes()
    fix_settings_py()
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['.git', '__pycache__', '.pytest_cache', 'venv', '.venv']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    print(f"\nFound {len(python_files)} Python files")
    print("\nFixing indentation issues...")
    
    fixed_count = 0
    error_count = 0
    
    for file_path in python_files:
        if fix_python_indentation(file_path):
            fixed_count += 1
        else:
            error_count += 1
    
    print(f"\nSUMMARY:")
    print(f"✓ Fixed/Valid: {fixed_count}")
    print(f"✗ Errors: {error_count}")
    print(f"Total files: {len(python_files)}")
    
    # Test Django after fixes
    print("\nTesting Django configuration...")
    try:
        import subprocess
        result = subprocess.run(['python', 'manage.py', 'check'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ Django configuration is valid!")
        else:
            print(f"✗ Django check failed: {result.stderr}")
    except Exception as e:
        print(f"✗ Django test failed: {e}")

if __name__ == "__main__":
    main()