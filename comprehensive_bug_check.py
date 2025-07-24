#!/usr/bin/env python3
"""
Comprehensive Bug Check & Code Quality Assessment
Performs thorough analysis of the Stock Scanner project for bugs, issues, and code quality.

This script checks:
1. Python syntax and imports
2. Django configuration and settings
3. Database connectivity and models
4. File structure and organization
5. Windows batch script syntax
6. Documentation consistency
7. Requirements and dependencies
8. Security vulnerabilities
9. Performance issues
10. Code quality standards

Author: Stock Scanner Project
Version: 2.0.0
"""

import os
import sys
import ast
import re
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Tuple, Any
import importlib.util

class BugChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.suggestions = []
        self.passed_checks = []
        self.project_root = Path.cwd()
        
    def log_issue(self, severity: str, category: str, file_path: str, message: str, line_num: int = None):
        """Log an issue with details"""
        issue = {
            'severity': severity,  # 'critical', 'major', 'minor', 'info'
            'category': category,
            'file': file_path,
            'message': message,
            'line': line_num
        }
        
        if severity == 'critical':
            self.issues.append(issue)
        elif severity == 'major':
            self.warnings.append(issue)
        else:
            self.suggestions.append(issue)
    
    def log_pass(self, check_name: str):
        """Log a passed check"""
        self.passed_checks.append(check_name)
    
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*70}")
        print(f"🔍 {title}")
        print('='*70)
    
    def print_step(self, message: str):
        """Print step message"""
        print(f"\n🔧 {message}")
    
    def print_result(self, message: str, status: str):
        """Print result with status"""
        status_icons = {
            'pass': '✅',
            'fail': '❌', 
            'warn': '⚠️',
            'info': '💡'
        }
        print(f"   {status_icons.get(status, '•')} {message}")

    def check_python_syntax(self):
        """Check Python files for syntax errors"""
        self.print_step("Checking Python syntax and imports...")
        
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip venv and git directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__', '.pytest_cache']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        syntax_errors = 0
        import_errors = 0
        
        for py_file in python_files:
            try:
                # Check syntax
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                try:
                    ast.parse(content)
                    self.log_pass(f"Syntax check: {py_file.name}")
                except SyntaxError as e:
                    self.log_issue('critical', 'syntax', str(py_file), f"Syntax error: {e.msg}", e.lineno)
                    syntax_errors += 1
                
                # Check for common import issues
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    
                    # Check for relative imports that might break
                    if line.startswith('from .') or line.startswith('import .'):
                        if not self._is_in_package(py_file):
                            self.log_issue('major', 'imports', str(py_file), 
                                         f"Relative import outside package: {line}", i)
                    
                    # Check for missing imports
                    if 'django' in line.lower() and 'import' in line:
                        if not self._check_django_available():
                            self.log_issue('major', 'imports', str(py_file),
                                         f"Django import but Django not available: {line}", i)
                    
            except Exception as e:
                self.log_issue('major', 'file_access', str(py_file), f"Could not read file: {e}")
        
        if syntax_errors == 0:
            self.print_result(f"All {len(python_files)} Python files have valid syntax", 'pass')
        else:
            self.print_result(f"{syntax_errors} syntax errors found in Python files", 'fail')
        
        return syntax_errors == 0

    def check_django_configuration(self):
        """Check Django settings and configuration"""
        self.print_step("Checking Django configuration...")
        
        settings_file = self.project_root / 'stockscanner_django' / 'settings.py'
        if not settings_file.exists():
            self.log_issue('critical', 'django', str(settings_file), "Django settings.py not found")
            return False
        
        try:
            with open(settings_file, 'r') as f:
                settings_content = f.read()
            
            # Check for required Django settings
            required_settings = [
                'SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS', 'INSTALLED_APPS',
                'MIDDLEWARE', 'ROOT_URLCONF', 'DATABASES', 'STATIC_URL'
            ]
            
            missing_settings = []
            for setting in required_settings:
                if setting not in settings_content:
                    missing_settings.append(setting)
            
            if missing_settings:
                self.log_issue('critical', 'django', str(settings_file),
                             f"Missing required settings: {', '.join(missing_settings)}")
            else:
                self.log_pass("All required Django settings present")
            
            # Check for security issues
            if 'SECRET_KEY' in settings_content:
                # Look for hardcoded secret key
                secret_match = re.search(r'SECRET_KEY\s*=\s*[\'"]([^\'"]+)[\'"]', settings_content)
                if secret_match:
                    secret = secret_match.group(1)
                    if 'django-insecure' in secret or len(secret) < 50:
                        self.log_issue('major', 'security', str(settings_file),
                                     "Weak or insecure SECRET_KEY detected")
            
            # Check database configuration
            if 'DATABASES' in settings_content:
                if 'sqlite3' in settings_content and 'mysql' in settings_content:
                    self.log_pass("Multiple database backends supported")
                elif 'mysql' in settings_content:
                    self.log_pass("MySQL database configuration found")
                elif 'sqlite3' in settings_content:
                    self.log_issue('info', 'database', str(settings_file),
                                 "Using SQLite - consider MySQL for production")
            
            self.print_result("Django configuration check completed", 'pass')
            return len(missing_settings) == 0
            
        except Exception as e:
            self.log_issue('critical', 'django', str(settings_file), f"Error reading settings: {e}")
            return False

    def check_database_models(self):
        """Check Django models for issues"""
        self.print_step("Checking Django models...")
        
        models_checked = 0
        model_issues = 0
        
        # Check main app models
        apps_to_check = ['stocks', 'core', 'emails', 'news']
        
        for app in apps_to_check:
            models_file = self.project_root / app / 'models.py'
            if models_file.exists():
                try:
                    with open(models_file, 'r') as f:
                        content = f.read()
                    
                    models_checked += 1
                    
                    # Check for common model issues
                    if 'class ' in content and 'models.Model' in content:
                        # Check for missing __str__ methods
                        classes = re.findall(r'class\s+(\w+)\s*\([^)]*models\.Model[^)]*\):', content)
                        for class_name in classes:
                            if f'def __str__(self):' not in content:
                                self.log_issue('minor', 'models', str(models_file),
                                             f"Model {class_name} missing __str__ method")
                        
                        # Check for missing Meta classes with ordering
                        if 'class Meta:' not in content:
                            self.log_issue('minor', 'models', str(models_file),
                                         "Consider adding Meta class with ordering")
                        
                        self.log_pass(f"Models check: {app}")
                    
                except Exception as e:
                    self.log_issue('major', 'models', str(models_file), f"Error checking models: {e}")
                    model_issues += 1
        
        if models_checked > 0:
            self.print_result(f"Checked {models_checked} model files", 'pass')
        else:
            self.print_result("No model files found to check", 'warn')
        
        return model_issues == 0

    def check_requirements_files(self):
        """Check requirements files for issues"""
        self.print_step("Checking requirements and dependencies...")
        
        requirements_files = [
            'requirements.txt',
            'setup/requirements/requirements-minimal.txt',
            'setup/requirements/requirements-windows.txt'
        ]
        
        found_files = 0
        issues_found = 0
        
        for req_file in requirements_files:
            file_path = self.project_root / req_file
            if file_path.exists():
                found_files += 1
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    
                    # Check for version pinning
                    unpinned = []
                    for line in lines:
                        if line.startswith('#') or not line:
                            continue
                        if '==' not in line and '>=' not in line and line.strip():
                            unpinned.append(line)
                    
                    if unpinned:
                        self.log_issue('minor', 'requirements', str(file_path),
                                     f"Unpinned packages: {', '.join(unpinned[:3])}")
                    
                    # Check for essential packages
                    essential = ['django', 'mysqlclient', 'requests']
                    missing = []
                    for pkg in essential:
                        if not any(pkg.lower() in line.lower() for line in lines):
                            missing.append(pkg)
                    
                    if missing and req_file == 'requirements.txt':
                        self.log_issue('major', 'requirements', str(file_path),
                                     f"Missing essential packages: {', '.join(missing)}")
                    else:
                        self.log_pass(f"Requirements check: {req_file}")
                    
                except Exception as e:
                    self.log_issue('major', 'requirements', str(file_path), f"Error reading requirements: {e}")
                    issues_found += 1
        
        if found_files > 0:
            self.print_result(f"Checked {found_files} requirements files", 'pass')
        else:
            self.log_issue('critical', 'requirements', 'requirements.txt', "No requirements files found")
            issues_found += 1
        
        return issues_found == 0

    def check_batch_scripts(self):
        """Check Windows batch scripts for syntax issues"""
        self.print_step("Checking Windows batch scripts...")
        
        batch_files = []
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['.git', 'venv']]
            for file in files:
                if file.endswith('.bat'):
                    batch_files.append(Path(root) / file)
        
        script_issues = 0
        
        for bat_file in batch_files:
            try:
                with open(bat_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                # Check for common batch script issues
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    
                    # Check for missing @echo off
                    if i == 1 and not line.lower().startswith('@echo off'):
                        self.log_issue('minor', 'batch', str(bat_file),
                                     "Consider starting with '@echo off'", i)
                    
                    # Check for unquoted paths with spaces
                    if 'call ' in line and ' ' in line and '"' not in line:
                        if any(word in line for word in ['setup', 'tools', 'scripts']):
                            self.log_issue('minor', 'batch', str(bat_file),
                                         "Consider quoting paths with spaces", i)
                    
                    # Check for error handling
                    if 'if errorlevel' not in content and 'if %errorlevel%' not in content:
                        if bat_file.name in ['START_HERE.bat', 'SIMPLE_START.bat']:
                            self.log_issue('minor', 'batch', str(bat_file),
                                         "Consider adding error handling")
                
                self.log_pass(f"Batch script check: {bat_file.name}")
                
            except Exception as e:
                self.log_issue('major', 'batch', str(bat_file), f"Error reading batch script: {e}")
                script_issues += 1
        
        if len(batch_files) > 0:
            self.print_result(f"Checked {len(batch_files)} batch scripts", 'pass')
        else:
            self.print_result("No batch scripts found", 'info')
        
        return script_issues == 0

    def check_file_structure(self):
        """Check project file structure and organization"""
        self.print_step("Checking project file structure...")
        
        # Check for required directories
        required_dirs = [
            'stockscanner_django',
            'stocks',
            'setup',
            'tools',
            'docs'
        ]
        
        missing_dirs = []
        for dir_name in required_dirs:
            if not (self.project_root / dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self.log_issue('major', 'structure', 'project_root',
                         f"Missing required directories: {', '.join(missing_dirs)}")
        else:
            self.log_pass("All required directories present")
        
        # Check for main entry points
        entry_points = ['START_HERE.bat', 'manage.py', 'requirements.txt']
        missing_entry = []
        for entry in entry_points:
            if not (self.project_root / entry).exists():
                missing_entry.append(entry)
        
        if missing_entry:
            self.log_issue('major', 'structure', 'project_root',
                         f"Missing entry points: {', '.join(missing_entry)}")
        else:
            self.log_pass("All main entry points present")
        
        # Check for clean root directory
        root_files = [f for f in os.listdir(self.project_root) if os.path.isfile(f)]
        script_files = [f for f in root_files if f.endswith(('.py', '.bat')) and f not in ['manage.py', 'START_HERE.bat']]
        
        if len(script_files) > 2:
            self.log_issue('minor', 'structure', 'project_root',
                         f"Root directory has many scripts: {', '.join(script_files[:5])}")
        else:
            self.log_pass("Root directory is clean")
        
        self.print_result("File structure check completed", 'pass')
        return len(missing_dirs) == 0 and len(missing_entry) == 0

    def check_documentation(self):
        """Check documentation completeness and consistency"""
        self.print_step("Checking documentation...")
        
        # Check for main documentation files
        main_docs = [
            'README.md',
            'docs/setup/SIMPLE_SETUP_README.md',
            'docs/production/MYSQL_PRODUCTION_GUIDE.md'
        ]
        
        missing_docs = []
        for doc in main_docs:
            if not (self.project_root / doc).exists():
                missing_docs.append(doc)
        
        if missing_docs:
            self.log_issue('major', 'documentation', 'docs',
                         f"Missing documentation: {', '.join(missing_docs)}")
        else:
            self.log_pass("Main documentation files present")
        
        # Check README content
        readme_path = self.project_root / 'README.md'
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                
                # Check for essential sections
                essential_sections = [
                    'quick start', 'setup', 'installation', 'prerequisites'
                ]
                
                missing_sections = []
                for section in essential_sections:
                    if section.lower() not in readme_content.lower():
                        missing_sections.append(section)
                
                if missing_sections:
                    self.log_issue('minor', 'documentation', str(readme_path),
                                 f"README missing sections: {', '.join(missing_sections)}")
                else:
                    self.log_pass("README has essential sections")
                
                # Check for broken links (basic check)
                if '[' in readme_content and '](' in readme_content:
                    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', readme_content)
                    for link_text, link_url in links:
                        if link_url.startswith('./') or link_url.startswith('../'):
                            # Check if local file exists
                            link_path = self.project_root / link_url.lstrip('./')
                            if not link_path.exists():
                                self.log_issue('minor', 'documentation', str(readme_path),
                                             f"Broken link: {link_url}")
                
            except Exception as e:
                self.log_issue('major', 'documentation', str(readme_path), f"Error reading README: {e}")
        
        self.print_result("Documentation check completed", 'pass')
        return len(missing_docs) == 0

    def check_security_issues(self):
        """Check for common security issues"""
        self.print_step("Checking for security issues...")
        
        security_issues = 0
        
        # Check for hardcoded secrets
        sensitive_patterns = [
            (r'password\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded password'),
            (r'secret_key\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded secret key'),
            (r'api_key\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded API key'),
            (r'token\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded token'),
        ]
        
        python_files = list(self.project_root.glob('**/*.py'))
        
        for py_file in python_files:
            if 'venv' in str(py_file) or '.git' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern, issue_type in sensitive_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        # Skip if it's a placeholder or example
                        if any(word in match.group().lower() for word in ['your-', 'example', 'placeholder', 'change-this']):
                            continue
                        self.log_issue('major', 'security', str(py_file), issue_type, line_num)
                        security_issues += 1
                
            except Exception as e:
                continue
        
        # Check .env file for security
        env_file = self.project_root / '.env'
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    env_content = f.read()
                
                if 'DEBUG=True' in env_content or 'DEBUG=true' in env_content:
                    self.log_issue('major', 'security', str(env_file), "DEBUG=True in .env file")
                    security_issues += 1
                
                if 'ALLOWED_HOSTS=' in env_content:
                    if '*' in env_content:
                        self.log_issue('major', 'security', str(env_file), "ALLOWED_HOSTS allows all hosts")
                        security_issues += 1
                
            except Exception as e:
                pass
        
        if security_issues == 0:
            self.print_result("No obvious security issues found", 'pass')
        else:
            self.print_result(f"Found {security_issues} potential security issues", 'warn')
        
        return security_issues == 0

    def check_performance_issues(self):
        """Check for common performance issues"""
        self.print_step("Checking for performance issues...")
        
        performance_issues = 0
        
        # Check Django settings for performance
        settings_file = self.project_root / 'stockscanner_django' / 'settings.py'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings_content = f.read()
                
                # Check for database connection pooling
                if 'CONN_MAX_AGE' not in settings_content:
                    self.log_issue('minor', 'performance', str(settings_file),
                                 "Consider adding database connection pooling")
                    performance_issues += 1
                
                # Check for caching configuration
                if 'CACHES' not in settings_content:
                    self.log_issue('minor', 'performance', str(settings_file),
                                 "Consider adding caching configuration")
                    performance_issues += 1
                else:
                    self.log_pass("Caching configuration found")
                
                # Check for static files configuration
                if 'STATIC_ROOT' not in settings_content:
                    self.log_issue('minor', 'performance', str(settings_file),
                                 "Consider adding STATIC_ROOT for production")
                    performance_issues += 1
                
            except Exception as e:
                pass
        
        # Check models for potential performance issues
        models_files = list(self.project_root.glob('**/models.py'))
        for models_file in models_files:
            if 'venv' in str(models_file):
                continue
                
            try:
                with open(models_file, 'r') as f:
                    content = f.read()
                
                # Check for missing database indexes
                if 'models.Model' in content and 'db_index=True' not in content:
                    if 'ForeignKey' in content or 'CharField' in content:
                        self.log_issue('minor', 'performance', str(models_file),
                                     "Consider adding database indexes for frequently queried fields")
                        performance_issues += 1
                
            except Exception as e:
                continue
        
        if performance_issues == 0:
            self.print_result("No obvious performance issues found", 'pass')
        else:
            self.print_result(f"Found {performance_issues} potential performance issues", 'info')
        
        return performance_issues == 0

    def test_imports(self):
        """Test if critical imports work"""
        self.print_step("Testing critical imports...")
        
        import_tests = [
            ('django', 'Django framework'),
            ('requests', 'HTTP requests'),
            ('pandas', 'Data processing'),
            ('yfinance', 'Yahoo Finance API')
        ]
        
        failed_imports = 0
        
        for module, description in import_tests:
            try:
                __import__(module)
                self.log_pass(f"Import test: {module}")
            except ImportError:
                self.log_issue('major', 'imports', 'requirements', 
                             f"Cannot import {module} ({description})")
                failed_imports += 1
            except Exception as e:
                self.log_issue('minor', 'imports', 'requirements',
                             f"Import warning for {module}: {e}")
        
        if failed_imports == 0:
            self.print_result("All critical imports successful", 'pass')
        else:
            self.print_result(f"{failed_imports} import failures", 'fail')
        
        return failed_imports == 0

    def _is_in_package(self, file_path: Path) -> bool:
        """Check if file is in a Python package"""
        parent = file_path.parent
        return (parent / '__init__.py').exists()

    def _check_django_available(self) -> bool:
        """Check if Django is available"""
        try:
            import django
            return True
        except ImportError:
            return False

    def generate_report(self):
        """Generate comprehensive bug report"""
        self.print_header("BUG CHECK REPORT")
        
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        total_suggestions = len(self.suggestions)
        total_passed = len(self.passed_checks)
        
        print(f"\n📊 SUMMARY:")
        print(f"   ✅ Passed Checks: {total_passed}")
        print(f"   ❌ Critical Issues: {total_issues}")
        print(f"   ⚠️  Warnings: {total_warnings}")
        print(f"   💡 Suggestions: {total_suggestions}")
        
        if total_issues > 0:
            print(f"\n❌ CRITICAL ISSUES ({total_issues}):")
            for issue in self.issues:
                line_info = f" (line {issue['line']})" if issue['line'] else ""
                print(f"   • {issue['file']}{line_info}: {issue['message']}")
        
        if total_warnings > 0:
            print(f"\n⚠️  WARNINGS ({total_warnings}):")
            for warning in self.warnings:
                line_info = f" (line {warning['line']})" if warning['line'] else ""
                print(f"   • {warning['file']}{line_info}: {warning['message']}")
        
        if total_suggestions > 0:
            print(f"\n💡 SUGGESTIONS ({total_suggestions}):")
            for suggestion in self.suggestions[:10]:  # Show first 10
                line_info = f" (line {suggestion['line']})" if suggestion['line'] else ""
                print(f"   • {suggestion['file']}{line_info}: {suggestion['message']}")
            if len(self.suggestions) > 10:
                print(f"   ... and {len(self.suggestions) - 10} more suggestions")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if total_issues == 0 and total_warnings <= 2:
            print("   🎉 EXCELLENT - Project is in great shape!")
        elif total_issues == 0 and total_warnings <= 5:
            print("   ✅ GOOD - Minor issues to address")
        elif total_issues <= 2:
            print("   ⚠️  FAIR - Some issues need attention")
        else:
            print("   ❌ NEEDS WORK - Critical issues must be fixed")
        
        return total_issues == 0 and total_warnings <= 5

    def run_all_checks(self):
        """Run all bug checks"""
        self.print_header("COMPREHENSIVE BUG CHECK & CODE QUALITY ASSESSMENT")
        print("🎯 Analyzing Stock Scanner project for bugs and issues...")
        print("⏱️  This may take a few minutes...")
        
        checks = [
            ("Python Syntax & Imports", self.check_python_syntax),
            ("Django Configuration", self.check_django_configuration),
            ("Database Models", self.check_database_models),
            ("Requirements Files", self.check_requirements_files),
            ("Batch Scripts", self.check_batch_scripts),
            ("File Structure", self.check_file_structure),
            ("Documentation", self.check_documentation),
            ("Security Issues", self.check_security_issues),
            ("Performance Issues", self.check_performance_issues),
            ("Import Tests", self.test_imports),
        ]
        
        results = {}
        for check_name, check_func in checks:
            try:
                results[check_name] = check_func()
            except Exception as e:
                self.log_issue('critical', 'system', check_name, f"Check failed: {e}")
                results[check_name] = False
        
        # Generate final report
        overall_result = self.generate_report()
        
        print(f"\n🚀 NEXT STEPS:")
        if len(self.issues) > 0:
            print("   1. Fix critical issues first")
            print("   2. Address major warnings")
            print("   3. Re-run bug check: python comprehensive_bug_check.py")
        else:
            print("   1. Address any warnings if desired")
            print("   2. Test the application: START_HERE.bat")
            print("   3. Deploy with confidence!")
        
        return overall_result

def main():
    """Main function"""
    checker = BugChecker()
    
    try:
        success = checker.run_all_checks()
        
        # Save detailed report
        report_file = Path('bug_check_report.json')
        report_data = {
            'issues': checker.issues,
            'warnings': checker.warnings,
            'suggestions': checker.suggestions,
            'passed_checks': checker.passed_checks,
            'overall_result': success
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📋 Detailed report saved to: {report_file}")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️  Bug check interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error during bug check: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)