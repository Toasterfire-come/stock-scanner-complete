#!/usr/bin/env python3
"""
Repository Cleanup Script
Removes outdated files and keeps only current XAMPP-optimized setup
"""

import os
import shutil
import sys
from pathlib import Path

class RepositoryCleanup:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.removed_files = []
        self.removed_dirs = []
        self.kept_files = []
        
    def should_keep_file(self, file_path):
        """Determine if a file should be kept in the current XAMPP setup"""
        file_name = file_path.name.lower()
        file_str = str(file_path).lower()
        
        # Core Django files - KEEP
        core_django_patterns = [
            'manage.py', 'settings.py', 'urls.py', 'wsgi.py', 'asgi.py',
            'models.py', 'views.py', 'admin.py', 'apps.py', 'tests.py',
            '__init__.py', 'migrations/', 'static/', 'templates/'
        ]
        
        # Current XAMPP setup files - KEEP
        xampp_current_files = [
            'setup_xampp_complete.bat',
            'django_xampp.bat', 
            'xampp_usage_guide.md',
            'start_stock_scheduler.py'
        ]
        
        # Essential project files - KEEP
        essential_files = [
            'requirements.txt', '.gitignore', 'readme.md',
            'api_views.py', 'update_stocks_yfinance.py'
        ]
        
        # Check if file should be kept
        for pattern in core_django_patterns:
            if pattern in file_str:
                return True
                
        for essential in essential_files:
            if essential in file_name:
                return True
                
        for xampp_file in xampp_current_files:
            if xampp_file in file_name:
                return True
                
        return False
    
    def should_remove_file(self, file_path):
        """Determine if a file should be removed"""
        file_name = file_path.name.lower()
        file_str = str(file_path).lower()
        
        # Outdated MySQL setup files - REMOVE
        outdated_mysql_files = [
            'reinstall_mysql_complete.bat',
            'configure_existing_mysql.bat', 
            'install_mysql_and_setup.bat',
            'manual_mysql_setup.bat',
            'install_xampp_alternative.bat',
            'setup_database_complete.bat',
            'fix_database_schema.bat',
            'fix_database_schema.py',
            'fix_mysql_specifically.py',
            'fix_mysql_errors.py',
            'fix_database_completely.py',
            'fix_mysql_only.bat'
        ]
        
        # Outdated setup scripts - REMOVE  
        outdated_setup_files = [
            'setup_system_python.py',
            'setup_database.py',
            'setup_mysql.py',
            'complete_setup.py',
            'setup_gitbash',
            'start_django_gitbash.sh',
            'git_bash_',
            'setup_database.sh'
        ]
        
        # Debug/fix scripts no longer needed - REMOVE
        debug_fix_files = [
            'fix_all_syntax_errors.py',
            'fix_all_indentation.py', 
            'comprehensive_bug_check',
            'remove_unicode_chars.py',
            'mass_file_replacer.py',
            'fix_django_extensions.py',
            'fix_yfinance_indentation.py',
            'final_cleanup_script.py',
            'check_scheduler_status.py'
        ]
        
        # Outdated documentation - REMOVE
        outdated_docs = [
            'main_branch_merge_complete.md',
            'unicode_encoding_fix_complete.md',
            'indentation_fix_complete.md',
            'background_mode_and_mysql_fixes.md',
            'api_functions_fix.md',
            'no_venv_setup_guide.md',
            'django_extensions_fix.md',
            'windows_scheduler_fix.md',
            'git_bash_',
            'start_postgresql.md',
            'security_checklist.md'
        ]
        
        # Backup/temporary files - REMOVE
        temp_backup_files = [
            'cleanup_backup/',
            '__pycache__/',
            '*.log',
            '=1.2.0', '=3.2.0',
            'bug_check_report.json'
        ]
        
        # Windows scheduler variants - REMOVE (keep main one)
        scheduler_variants = [
            'start_stock_scheduler_windows.py',
            'start_background_simple.bat',
            'start_scheduler_background.bat',
            'start_scheduler_system.sh',
            'start_scheduler.bat'
        ]
        
        # Test files that are outdated - REMOVE
        outdated_tests = [
            'test_api_endpoints.py',
            'test_wordpress_integration.py'
        ]
        
        # Small stub files - REMOVE
        if file_path.stat().st_size < 250 and file_name.endswith('.py'):
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            if len(content.strip()) < 50 or 'placeholder' in content.lower():
                return True
        
        # Check all removal patterns
        all_remove_patterns = (
            outdated_mysql_files + outdated_setup_files + debug_fix_files + 
            outdated_docs + scheduler_variants + outdated_tests
        )
        
        for pattern in all_remove_patterns:
            if pattern in file_name or pattern in file_str:
                return True
                
        # Check temp/backup patterns
        for pattern in temp_backup_files:
            if pattern.rstrip('/') in file_str:
                return True
                
        return False
    
    def cleanup_files(self):
        """Remove outdated files and directories"""
        print("🧹 REPOSITORY CLEANUP - REMOVING OUTDATED FILES")
        print("=" * 50)
        
        # Walk through all files
        for file_path in self.root_dir.rglob('*'):
            if file_path.is_file():
                if self.should_remove_file(file_path):
                    try:
                        file_path.unlink()
                        self.removed_files.append(str(file_path.relative_to(self.root_dir)))
                        print(f"❌ Removed: {file_path.relative_to(self.root_dir)}")
                    except Exception as e:
                        print(f"⚠️  Could not remove {file_path}: {e}")
                        
                elif self.should_keep_file(file_path):
                    self.kept_files.append(str(file_path.relative_to(self.root_dir)))
        
        # Remove empty directories
        self.remove_empty_dirs()
        
    def remove_empty_dirs(self):
        """Remove empty directories"""
        print("\n🗂️  REMOVING EMPTY DIRECTORIES")
        print("-" * 30)
        
        # Get all directories, deepest first
        all_dirs = []
        for dir_path in self.root_dir.rglob('*'):
            if dir_path.is_dir() and dir_path.name not in ['.git']:
                all_dirs.append(dir_path)
        
        # Sort by depth (deepest first)
        all_dirs.sort(key=lambda x: len(x.parts), reverse=True)
        
        for dir_path in all_dirs:
            try:
                # Check if directory is empty
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    self.removed_dirs.append(str(dir_path.relative_to(self.root_dir)))
                    print(f"📁 Removed empty dir: {dir_path.relative_to(self.root_dir)}")
            except Exception as e:
                # Directory not empty or permission error
                pass
    
    def create_gitignore_cleanup(self):
        """Update .gitignore to prevent future clutter"""
        gitignore_path = self.root_dir / '.gitignore'
        
        additional_ignores = [
            "",
            "# Cleanup - prevent future clutter",
            "*.log",
            "__pycache__/",
            "*.pyc",
            "*.pyo", 
            "*.pyd",
            ".Python",
            "env/",
            "venv/",
            ".env",
            ".venv",
            "pip-log.txt",
            "pip-delete-this-directory.txt",
            "*.orig",
            "*.bak",
            "*~",
            "*.swp",
            "*.swo",
            ".DS_Store",
            "Thumbs.db",
            "mysql-installer*.msi",
            "xampp-installer*.exe",
            "temp_*.txt",
            "bug_check_report.json"
        ]
        
        if gitignore_path.exists():
            current_content = gitignore_path.read_text()
            new_ignores = []
            for ignore in additional_ignores:
                if ignore and ignore not in current_content:
                    new_ignores.append(ignore)
            
            if new_ignores:
                with open(gitignore_path, 'a') as f:
                    f.write('\n'.join(new_ignores))
                print(f"📝 Updated .gitignore with {len(new_ignores)} new patterns")
    
    def show_summary(self):
        """Show cleanup summary"""
        print("\n" + "=" * 60)
        print("🎯 CLEANUP SUMMARY")
        print("=" * 60)
        
        print(f"✅ Files removed: {len(self.removed_files)}")
        print(f"📁 Directories removed: {len(self.removed_dirs)}")
        print(f"📂 Files kept: {len(self.kept_files)}")
        
        print(f"\n📋 CURRENT XAMPP SETUP FILES KEPT:")
        current_setup_files = [
            'setup_xampp_complete.bat',
            'django_xampp.bat',
            'XAMPP_USAGE_GUIDE.md', 
            'start_stock_scheduler.py',
            'manage.py',
            'stockscanner_django/settings.py'
        ]
        
        for file in current_setup_files:
            if any(file.lower() in kept.lower() for kept in self.kept_files):
                print(f"  ✅ {file}")
        
        print(f"\n🗑️  MAJOR REMOVALS:")
        major_removals = [
            'Old MySQL installers',
            'Outdated setup scripts', 
            'Debug/fix scripts',
            'Unicode/indentation fixes',
            'Git Bash setup files',
            'Backup directories',
            'Temporary files'
        ]
        
        for removal in major_removals:
            print(f"  ❌ {removal}")
            
        print(f"\n📁 CLEAN REPOSITORY STRUCTURE:")
        print("  ✅ Core Django apps (stocks, emails, core, news)")
        print("  ✅ XAMPP integration files")
        print("  ✅ Current documentation")
        print("  ✅ Essential Python files") 
        print("  ✅ Templates and static files")
        
        print(f"\n🎉 Repository cleaned! Now optimized for XAMPP setup only.")

def main():
    """Run the repository cleanup"""
    print("Repository Cleanup for XAMPP Setup")
    print("This will remove outdated files and keep only current XAMPP files")
    
    response = input("\nProceed with cleanup? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Cleanup cancelled.")
        return
    
    cleanup = RepositoryCleanup()
    cleanup.cleanup_files()
    cleanup.create_gitignore_cleanup()
    cleanup.show_summary()
    
    print(f"\n💡 Next steps:")
    print("1. Run: git add .")
    print("2. Run: git commit -m 'Clean repository - remove outdated files'")
    print("3. Run: git push")
    print("4. Use: setup_xampp_complete.bat for fresh installations")

if __name__ == "__main__":
    main()