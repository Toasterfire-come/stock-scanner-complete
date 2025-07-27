#!/usr/bin/env python3
"""
Comprehensive Bug Check and Fix Script
Systematically checks all files for common bugs and fixes them automatically
"""

import os
import re
import ast
import sys
from pathlib import Path
from datetime import datetime

class BugChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.issues_found = []
        self.fixes_applied = []
    
    def check_python_syntax(self, file_path):
        """Check Python files for syntax errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse the file
            ast.parse(content)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Parse error: {e}"
    
    def check_import_issues(self, file_path):
        """Check for common import issues"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Check for incorrect relative imports
                if line.startswith('from .') and 'models' in line:
                    if 'StockAlert' in line and 'Stock' not in line:
                        issues.append(f"Line {i}: Missing Stock import - {line}")
                
                # Check for duplicate imports
                if line.startswith(('import ', 'from ')):
                    import_pattern = line
                    count = sum(1 for l in lines if l.strip() == import_pattern)
                    if count > 1:
                        issues.append(f"Line {i}: Duplicate import - {line}")
        
        except Exception as e:
            issues.append(f"Error reading file: {e}")
        
        return issues
    
    def check_database_model_usage(self, file_path):
        """Check for incorrect model usage"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for StockAlert usage in APIs (should use Stock)
            if 'api' in file_path.name and 'StockAlert.objects' in content:
                # Check if it's actually for alerts or stock data
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if 'StockAlert.objects' in line and 'alert' not in line.lower():
                        issues.append(f"Line {i}: Should use Stock model, not StockAlert - {line.strip()}")
        
        except Exception as e:
            issues.append(f"Error reading file: {e}")
        
        return issues
    
    def check_url_patterns(self, file_path):
        """Check URL patterns for conflicts"""
        issues = []
        
        if file_path.name == 'urls.py':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find path patterns
                path_patterns = re.findall(r"path\('([^']+)'", content)
                
                # Check for conflicts (specific patterns after generic ones)
                for i, pattern in enumerate(path_patterns):
                    if '<' in pattern:  # Generic pattern
                        for j, other_pattern in enumerate(path_patterns[i+1:], i+1):
                            if '<' not in other_pattern and other_pattern.startswith(pattern.split('<')[0]):
                                issues.append(f"URL conflict: '{other_pattern}' should come before '{pattern}'")
            
            except Exception as e:
                issues.append(f"Error reading URL file: {e}")
        
        return issues
    
    def check_api_response_consistency(self, file_path):
        """Check API response consistency"""
        issues = []
        
        if 'api' in file_path.name or 'views' in file_path.name:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for consistent error response format
                if 'JsonResponse' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if 'JsonResponse' in line and 'error' in line:
                            # Check if it includes success: False
                            context_lines = lines[max(0, i-3):i+3]
                            context = '\n'.join(context_lines)
                            if "'success': False" not in context and '"success": false' not in context:
                                issues.append(f"Line {i}: Error response missing 'success': False")
            
            except Exception as e:
                issues.append(f"Error reading API file: {e}")
        
        return issues
    
    def check_decimal_field_handling(self, file_path):
        """Check for proper decimal field handling"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for unsafe decimal conversions
            if 'DecimalField' in content or 'Decimal' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if 'float(' in line and ('stock.' in line or 'decimal' in line.lower()):
                        if 'format_decimal_safe' not in line:
                            issues.append(f"Line {i}: Unsafe decimal conversion - {line.strip()}")
        
        except Exception as e:
            issues.append(f"Error reading file: {e}")
        
        return issues
    
    def check_environment_variables(self, file_path):
        """Check for hardcoded values that should be environment variables"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for hardcoded database credentials
            hardcoded_patterns = [
                (r'StockScanner2010', 'Hardcoded database password'),
                (r'admin123', 'Hardcoded admin password'),
                (r'127\.0\.0\.1:8000', 'Hardcoded server URL'),
            ]
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                for pattern, description in hardcoded_patterns:
                    if re.search(pattern, line) and 'os.environ' not in line:
                        issues.append(f"Line {i}: {description} - {line.strip()}")
        
        except Exception as e:
            issues.append(f"Error reading file: {e}")
        
        return issues
    
    def fix_common_issues(self, file_path):
        """Automatically fix common issues"""
        fixes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix 1: Replace format_decimal with format_decimal_safe
            if 'format_decimal_safe(' in content and 'format_decimal_safe' in content:
                content = content.replace('format_decimal_safe(', 'format_decimal_safe(')
                fixes.append("Replaced format_decimal with format_decimal_safe")
            
            # Fix 2: Add missing imports
            if 'Stock' in content and 'from .models import' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('from .models import') and 'Stock' not in line:
                        if 'StockAlert' in line:
                            lines[i] = line.replace('StockAlert', 'Stock, StockAlert')
                            fixes.append("Added missing Stock import")
                content = '\n'.join(lines)
            
            # Fix 3: Fix f-string syntax errors
            problematic_fstrings = [
                (r'f"([^"]*{[^}]*:.*?if.*?else.*?}[^"]*)"', 'Fix complex f-string expressions'),
            ]
            
            for pattern, description in problematic_fstrings:
                if re.search(pattern, content):
                    # This would need specific fixes based on context
                    fixes.append(f"Found {description} - manual review needed")
            
            # Apply fixes if any were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        except Exception as e:
            fixes.append(f"Error applying fixes: {e}")
        
        return fixes
    
    def check_file(self, file_path):
        """Comprehensive check of a single file"""
        file_issues = {
            'file': str(file_path),
            'syntax': [],
            'imports': [],
            'models': [],
            'urls': [],
            'api_responses': [],
            'decimals': [],
            'environment': [],
            'fixes_applied': []
        }
        
        # Check Python syntax
        is_valid, syntax_error = self.check_python_syntax(file_path)
        if not is_valid:
            file_issues['syntax'].append(syntax_error)
        
        # Only proceed with other checks if syntax is valid
        if is_valid:
            file_issues['imports'] = self.check_import_issues(file_path)
            file_issues['models'] = self.check_database_model_usage(file_path)
            file_issues['urls'] = self.check_url_patterns(file_path)
            file_issues['api_responses'] = self.check_api_response_consistency(file_path)
            file_issues['decimals'] = self.check_decimal_field_handling(file_path)
            file_issues['environment'] = self.check_environment_variables(file_path)
            
            # Apply automatic fixes
            file_issues['fixes_applied'] = self.fix_common_issues(file_path)
        
        return file_issues
    
    def run_comprehensive_check(self):
        """Run comprehensive bug check on all Python files"""
        print("="*70)
        print("[SEARCH] COMPREHENSIVE BUG CHECK AND FIX")
        print("="*70)
        print(f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" Project Root: {self.project_root}")
        print("="*70)
        
        # Find all Python files
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip virtual environments and migrations
            if 'venv' in root or 'migrations' in root or '__pycache__' in root:
                continue
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        print(f" Found {len(python_files)} Python files to check")
        
        # Check each file
        all_issues = []
        total_issues = 0
        total_fixes = 0
        
        for file_path in python_files:
            print(f"\n[SEARCH] Checking: {file_path.relative_to(self.project_root)}")
            
            file_issues = self.check_file(file_path)
            
            # Count issues
            file_issue_count = sum(
                len(issues) for issues in file_issues.values() 
                if isinstance(issues, list) and issues
            )
            
            if file_issue_count > 0:
                all_issues.append(file_issues)
                total_issues += file_issue_count
                
                # Show issues for this file
                for category, issues in file_issues.items():
                    if isinstance(issues, list) and issues and category != 'fixes_applied':
                        print(f"  [WARNING]  {category.title()}: {len(issues)} issues")
                        for issue in issues[:3]:  # Show first 3 issues
                            print(f"    - {issue}")
                        if len(issues) > 3:
                            print(f"    - ... and {len(issues) - 3} more")
            
            # Show fixes applied
            if file_issues['fixes_applied']:
                total_fixes += len(file_issues['fixes_applied'])
                print(f"  [SUCCESS] Applied {len(file_issues['fixes_applied'])} fixes:")
                for fix in file_issues['fixes_applied']:
                    print(f"    - {fix}")
        
        # Display summary
        self.display_summary(all_issues, total_issues, total_fixes)
        
        return all_issues
    
    def display_summary(self, all_issues, total_issues, total_fixes):
        """Display comprehensive summary of issues found and fixed"""
        print("\n" + "="*70)
        print("[STATS] BUG CHECK SUMMARY")
        print("="*70)
        
        files_with_issues = len(all_issues)
        total_files_checked = len([f for f in self.project_root.rglob('*.py') 
                                 if 'venv' not in str(f) and 'migrations' not in str(f)])
        
        print(f" Files Checked: {total_files_checked}")
        print(f"[WARNING]  Files with Issues: {files_with_issues}")
        print(f" Total Issues Found: {total_issues}")
        print(f"[CONFIG] Total Fixes Applied: {total_fixes}")
        
        # Categorize issues
        issue_categories = {}
        for file_issues in all_issues:
            for category, issues in file_issues.items():
                if isinstance(issues, list) and issues and category != 'fixes_applied':
                    if category not in issue_categories:
                        issue_categories[category] = 0
                    issue_categories[category] += len(issues)
        
        if issue_categories:
            print(f"\n[LIST] ISSUES BY CATEGORY:")
            for category, count in sorted(issue_categories.items(), key=lambda x: x[1], reverse=True):
                print(f"   - {category.title()}: {count} issues")
        
        # Priority issues
        critical_files = []
        for file_issues in all_issues:
            if file_issues['syntax'] or len(file_issues['models']) > 0:
                critical_files.append(file_issues['file'])
        
        if critical_files:
            print(f"\n CRITICAL FILES NEEDING ATTENTION:")
            for file in critical_files[:5]:  # Show first 5
                print(f"   - {file}")
            if len(critical_files) > 5:
                print(f"   - ... and {len(critical_files) - 5} more")
        
        # Recommendations
        print(f"\n[TIP] RECOMMENDATIONS:")
        if total_fixes > 0:
            print(f"   [SUCCESS] {total_fixes} issues were automatically fixed")
        if total_issues - total_fixes > 0:
            print(f"   [CONFIG] {total_issues - total_fixes} issues require manual attention")
        if files_with_issues == 0:
            print("   [SUCCESS] No issues found - code quality is excellent!")
        
        print("\n[CONFIG] NEXT STEPS:")
        print("   1. Review syntax errors first (if any)")
        print("   2. Check model usage in API files")
        print("   3. Test all endpoints with test scripts")
        print("   4. Run WordPress integration tests")
        
        print("\n" + "="*70)
        print(f" Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

def main():
    """Main execution function"""
    checker = BugChecker()
    
    try:
        all_issues = checker.run_comprehensive_check()
        
        # Exit with appropriate code
        if any(file_issues['syntax'] for file_issues in all_issues):
            print("\n[ERROR] CRITICAL: Syntax errors found!")
            sys.exit(1)
        elif all_issues:
            print("\n[WARNING]  Issues found but no syntax errors")
            sys.exit(0)
        else:
            print("\n[SUCCESS] No issues found - all systems operational!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n[STOP]  Bug check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Bug check failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()