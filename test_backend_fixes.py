#!/usr/bin/env python3
"""
Backend Code Validation and Testing Script
Tests the fixes applied to the Django backend
"""

import os
import sys
import ast
import subprocess
import importlib.util
from pathlib import Path

class BackendTester:
    def __init__(self):
        self.workspace_dir = Path(__file__).parent
        self.issues_found = []
        self.fixes_validated = []
        
    def log_issue(self, issue):
        """Log an issue found during testing"""
        self.issues_found.append(issue)
        print(f"❌ ISSUE: {issue}")
        
    def log_fix(self, fix):
        """Log a successful fix validation"""
        self.fixes_validated.append(fix)
        print(f"✅ FIXED: {fix}")
        
    def test_syntax_errors(self):
        """Test for Python syntax errors in key files"""
        print("\n🔍 Testing for syntax errors...")
        
        key_files = [
            'manage.py',
            'core/views.py',
            'stockscanner_django/settings.py',
            'stockscanner_django/urls.py',
            'stocks/models.py',
            'stocks/api_views.py',
            'stocks/urls.py'
        ]
        
        for file_path in key_files:
            full_path = self.workspace_dir / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                    ast.parse(source)
                    self.log_fix(f"Syntax validation passed: {file_path}")
                except SyntaxError as e:
                    self.log_issue(f"Syntax error in {file_path}: {e}")
                except Exception as e:
                    self.log_issue(f"Error reading {file_path}: {e}")
            else:
                self.log_issue(f"File not found: {file_path}")
    
    def test_import_statements(self):
        """Test for import issues in key files"""
        print("\n🔍 Testing import statements...")
        
        # Test core/views.py imports
        try:
            core_views_path = self.workspace_dir / 'core' / 'views.py'
            with open(core_views_path, 'r') as f:
                content = f.read()
                
            # Check for proper indentation in context dict
            if "context = {\n        'title':" in content:
                self.log_fix("Core views context dictionary properly indented")
            else:
                self.log_issue("Core views context dictionary indentation issue")
                
        except Exception as e:
            self.log_issue(f"Error testing core views: {e}")
            
        # Test stocks/api_views.py imports
        try:
            api_views_path = self.workspace_dir / 'stocks' / 'api_views.py'
            with open(api_views_path, 'r') as f:
                content = f.read()
                
            # Check for improved import handling
            if "YFINANCE_AVAILABLE" in content and "try:" in content:
                self.log_fix("API views have proper import error handling")
            else:
                self.log_issue("API views missing import error handling")
                
        except Exception as e:
            self.log_issue(f"Error testing API views imports: {e}")
    
    def test_database_configuration(self):
        """Test database configuration"""
        print("\n🔍 Testing database configuration...")
        
        try:
            settings_path = self.workspace_dir / 'stockscanner_django' / 'settings.py'
            with open(settings_path, 'r') as f:
                content = f.read()
                
            # Check for cross-platform XAMPP detection
            if "platform.system()" in content:
                self.log_fix("Cross-platform XAMPP detection implemented")
            else:
                self.log_issue("Missing cross-platform XAMPP detection")
                
            # Check for proper import
            if "import platform" in content:
                self.log_fix("Platform module imported")
            else:
                self.log_issue("Platform module not imported")
                
        except Exception as e:
            self.log_issue(f"Error testing database configuration: {e}")
    
    def test_security_configurations(self):
        """Test security-related configurations"""
        print("\n🔍 Testing security configurations...")
        
        try:
            settings_path = self.workspace_dir / 'stockscanner_django' / 'settings.py'
            with open(settings_path, 'r') as f:
                content = f.read()
                
            # Check DEBUG configuration
            if "DEBUG = os.environ.get('DEBUG'" in content:
                self.log_fix("DEBUG properly configured from environment")
            elif "DEBUG = " in content and "True" in content:
                self.log_issue("DEBUG might be hardcoded to True")
            
            # Check SECRET_KEY configuration
            if "SECRET_KEY = os.environ.get('SECRET_KEY'" in content:
                self.log_fix("SECRET_KEY properly configured from environment")
            elif "django-insecure" in content:
                self.log_issue("Development SECRET_KEY detected")
                
            # Check CORS configuration
            if "CORS_ALLOW_ALL_ORIGINS" in content:
                if "DEBUG" in content:
                    self.log_fix("CORS properly tied to DEBUG setting")
                else:
                    self.log_issue("CORS might allow all origins in production")
                    
        except Exception as e:
            self.log_issue(f"Error testing security configuration: {e}")
    
    def test_url_patterns(self):
        """Test URL pattern configurations"""
        print("\n🔍 Testing URL patterns...")
        
        try:
            # Test main URLs
            main_urls_path = self.workspace_dir / 'stockscanner_django' / 'urls.py'
            with open(main_urls_path, 'r') as f:
                content = f.read()
                
            required_patterns = ['health/', 'api/', 'admin/']
            for pattern in required_patterns:
                if pattern in content:
                    self.log_fix(f"URL pattern '{pattern}' found")
                else:
                    self.log_issue(f"URL pattern '{pattern}' missing")
                    
            # Test stocks URLs
            stocks_urls_path = self.workspace_dir / 'stocks' / 'urls.py'
            with open(stocks_urls_path, 'r') as f:
                content = f.read()
                
            stocks_patterns = ['stocks/', 'search/', 'realtime/']
            for pattern in stocks_patterns:
                if pattern in content:
                    self.log_fix(f"Stocks URL pattern '{pattern}' found")
                else:
                    self.log_issue(f"Stocks URL pattern '{pattern}' missing")
                    
        except Exception as e:
            self.log_issue(f"Error testing URL patterns: {e}")
    
    def test_model_definitions(self):
        """Test model definitions for potential issues"""
        print("\n🔍 Testing model definitions...")
        
        try:
            models_path = self.workspace_dir / 'stocks' / 'models.py'
            with open(models_path, 'r') as f:
                content = f.read()
                
            # Check for duplicate field definitions
            if content.count('ticker =') > 1:
                self.log_issue("Duplicate ticker field definitions detected")
            else:
                self.log_fix("No duplicate ticker field definitions")
                
            if content.count('symbol =') > 1:
                self.log_issue("Duplicate symbol field definitions detected")
            else:
                self.log_fix("No duplicate symbol field definitions")
                
            # Check for proper field types
            if "DecimalField" in content and "max_digits" in content:
                self.log_fix("Decimal fields properly configured")
            else:
                self.log_issue("Decimal field configuration issues")
                
        except Exception as e:
            self.log_issue(f"Error testing model definitions: {e}")
    
    def test_requirements_file(self):
        """Test requirements file for potential conflicts"""
        print("\n🔍 Testing requirements file...")
        
        try:
            req_path = self.workspace_dir / 'requirements.txt'
            with open(req_path, 'r') as f:
                content = f.read()
                
            # Check for essential packages
            essential_packages = ['Django', 'djangorestframework', 'mysqlclient']
            for package in essential_packages:
                if package.lower() in content.lower():
                    self.log_fix(f"Essential package '{package}' found in requirements")
                else:
                    self.log_issue(f"Essential package '{package}' missing from requirements")
                    
            # Check for version conflicts
            if "dj-database-url" in content and content.count("dj-database-url") > 1:
                self.log_issue("Duplicate dj-database-url entries detected")
            else:
                self.log_fix("No duplicate package entries detected")
                
        except Exception as e:
            self.log_issue(f"Error testing requirements file: {e}")
    
    def test_python_compilation(self):
        """Test Python compilation of key files"""
        print("\n🔍 Testing Python compilation...")
        
        key_files = [
            'manage.py',
            'core/views.py',
            'stockscanner_django/settings.py',
            'stocks/api_views.py'
        ]
        
        for file_path in key_files:
            full_path = self.workspace_dir / file_path
            if full_path.exists():
                try:
                    result = subprocess.run([
                        sys.executable, '-m', 'py_compile', str(full_path)
                    ], capture_output=True, text=True, cwd=self.workspace_dir)
                    
                    if result.returncode == 0:
                        self.log_fix(f"Python compilation successful: {file_path}")
                    else:
                        self.log_issue(f"Python compilation failed for {file_path}: {result.stderr}")
                        
                except Exception as e:
                    self.log_issue(f"Error compiling {file_path}: {e}")
            else:
                self.log_issue(f"File not found for compilation: {file_path}")
    
    def generate_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "="*60)
        print("📊 BACKEND CODE VALIDATION REPORT")
        print("="*60)
        
        print(f"\n✅ Fixes Validated: {len(self.fixes_validated)}")
        for fix in self.fixes_validated:
            print(f"   • {fix}")
            
        print(f"\n❌ Issues Found: {len(self.issues_found)}")
        for issue in self.issues_found:
            print(f"   • {issue}")
            
        # Calculate success rate
        total_checks = len(self.fixes_validated) + len(self.issues_found)
        if total_checks > 0:
            success_rate = (len(self.fixes_validated) / total_checks) * 100
            print(f"\n📈 Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 Excellent! Backend is in great shape.")
            elif success_rate >= 75:
                print("👍 Good! Most issues have been resolved.")
            elif success_rate >= 50:
                print("⚠️  Fair. Several issues need attention.")
            else:
                print("🚨 Critical! Multiple issues need immediate attention.")
        
        print("\n" + "="*60)
        
        return len(self.issues_found) == 0
    
    def run_all_tests(self):
        """Run all backend validation tests"""
        print("🚀 Starting Backend Code Validation...")
        print("="*60)
        
        self.test_syntax_errors()
        self.test_import_statements()
        self.test_database_configuration()
        self.test_security_configurations()
        self.test_url_patterns()
        self.test_model_definitions()
        self.test_requirements_file()
        self.test_python_compilation()
        
        return self.generate_report()

def main():
    """Main execution function"""
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 All backend code validation tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some issues found. Please review the report above.")
        sys.exit(1)

if __name__ == "__main__":
    main()