#!/usr/bin/env python3
"""
Local Setup Script for Stock Scanner
Using SQLite database and Gmail SMTP
"""

import os
import sys
import subprocess
from pathlib import Path

class LocalSetup:
    """Local setup configuration and utilities"""
    
    def __init__(self, project_path="."):
        self.project_path = Path(project_path)
        
    def print_step(self, message):
        """Print setup step"""
        print(f"\n🔧 {message}")

    def print_success(self, message):
        """Print success message"""
        print(f"✅ {message}")

    def print_error(self, message):
        """Print error message"""
        print(f"❌ {message}")

    def print_warning(self, message):
        """Print warning message"""
        print(f"⚠️ {message}")

    def check_python_version(self):
        """Check if Python version is compatible"""
        self.print_step("Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
            return False
        
        self.print_success(f"Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True

    def setup_virtual_environment(self):
        """Create and activate virtual environment"""
        self.print_step("Setting up virtual environment...")
        
        venv_path = self.project_path / "venv"
        
        if not venv_path.exists():
            try:
                subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
                self.print_success("Virtual environment created")
            except subprocess.CalledProcessError as e:
                self.print_error(f"Failed to create virtual environment: {e}")
                return False
        else:
            self.print_success("Virtual environment already exists")
        
        # Get pip path
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip.exe"
            python_path = venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            pip_path = venv_path / "bin" / "pip"
            python_path = venv_path / "bin" / "python"
        
        self.pip_path = str(pip_path)
        self.python_path = str(python_path)
        
        return True

    def install_requirements(self):
        """Install Python requirements"""
        self.print_step("Installing requirements...")
        
        requirements_file = self.project_path / "requirements_secure.txt"
        
        if not requirements_file.exists():
            self.print_warning("requirements_secure.txt not found, creating basic requirements...")
            self.create_basic_requirements()
        
        try:
            subprocess.run([self.pip_path, 'install', '--upgrade', 'pip'], check=True)
            subprocess.run([self.pip_path, 'install', '-r', str(requirements_file)], check=True)
            self.print_success("Requirements installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to install requirements: {e}")
            return False

    def create_basic_requirements(self):
        """Create basic requirements file"""
        requirements_content = """# Basic requirements for Stock Scanner
Django>=4.2.0,<5.0
yfinance>=0.2.0
requests>=2.31.0
urllib3>=1.26.0
pandas>=2.0.0
numpy>=1.24.0
djangorestframework>=3.14.0
django-cors-headers>=4.3.0
python-dotenv>=1.0.0
whitenoise>=6.5.0
Pillow>=10.0.0
"""
        
        requirements_file = self.project_path / "requirements_secure.txt"
        with open(requirements_file, 'w') as f:
            f.write(requirements_content)
        
        self.print_success("Basic requirements file created")

    def setup_environment_file(self):
        """Create .env file with Gmail and SQLite settings"""
        self.print_step("Setting up environment file...")
        
        env_file = self.project_path / ".env"
        
        if env_file.exists():
            self.print_warning(".env file already exists - not overwriting")
            return True
        
        env_content = """# Local Environment Variables for Stock Scanner

# Django Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True
ADMIN_URL=admin

# Database Configuration (Local SQLite)
DB_TYPE=sqlite3
DB_NAME=stock_scanner.db
DB_PATH=./stock_scanner.db

# Email Configuration (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply.retailtradescanner@gmail.com
EMAIL_HOST_PASSWORD=mzqmvhsjqeqrjmjv
ADMIN_EMAIL=noreply.retailtradescanner@gmail.com

# Site Configuration
SITE_URL=http://localhost:8000
ALLOWED_HOSTS=localhost,127.0.0.1

# Stock API Configuration (yfinance only)
USE_YFINANCE_ONLY=True
STOCK_API_RATE_LIMIT=1.0
YFINANCE_CACHE_DURATION=300
YFINANCE_MAX_RETRIES=3
YFINANCE_TIMEOUT=30

# Security Settings (for local development)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0

# Cache Configuration
CACHE_BACKEND=locmem

# WordPress Integration
WORDPRESS_URL=https://retailtradescan.net
WORDPRESS_API_TIMEOUT=10
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        self.print_success(".env file created")
        return True

    def setup_database(self):
        """Setup SQLite database"""
        self.print_step("Setting up SQLite database...")
        
        try:
            # Run database setup
            subprocess.run([self.python_path, 'database_settings_local.py'], 
                         cwd=str(self.project_path), check=True)
            
            # Run Django migrations
            subprocess.run([self.python_path, 'manage.py', 'makemigrations'], 
                         cwd=str(self.project_path), check=True)
            
            subprocess.run([self.python_path, 'manage.py', 'migrate'], 
                         cwd=str(self.project_path), check=True)
            
            self.print_success("Database setup completed")
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"Database setup failed: {e}")
            return False

    def test_email_configuration(self):
        """Test Gmail email configuration"""
        self.print_step("Testing email configuration...")
        
        try:
            # Import after Django setup
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
            
            import django
            django.setup()
            
            from emails.email_config import test_email_connection
            
            success, message = test_email_connection()
            if success:
                self.print_success(f"Email test: {message}")
            else:
                self.print_warning(f"Email test: {message}")
            
            return success
            
        except Exception as e:
            self.print_warning(f"Email test failed: {e}")
            return False

    def test_yfinance_connection(self):
        """Test yfinance connection"""
        self.print_step("Testing yfinance connection...")
        
        try:
            # Import after Django setup
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
            
            import django
            django.setup()
            
            from stocks.yfinance_config import test_yfinance_connection
            
            success, message = test_yfinance_connection()
            if success:
                self.print_success(f"yfinance test: {message}")
            else:
                self.print_warning(f"yfinance test: {message}")
            
            return success
            
        except Exception as e:
            self.print_warning(f"yfinance test failed: {e}")
            return False

    def create_superuser(self):
        """Create Django superuser"""
        self.print_step("Creating Django superuser...")
        
        print("Please create a superuser account for Django admin:")
        
        try:
            subprocess.run([self.python_path, 'manage.py', 'createsuperuser'], 
                         cwd=str(self.project_path))
            
            self.print_success("Superuser created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_warning(f"Superuser creation failed: {e}")
            return False
        except KeyboardInterrupt:
            self.print_warning("Superuser creation cancelled")
            return False

    def collect_static_files(self):
        """Collect static files"""
        self.print_step("Collecting static files...")
        
        try:
            subprocess.run([self.python_path, 'manage.py', 'collectstatic', '--noinput'], 
                         cwd=str(self.project_path), check=True)
            
            self.print_success("Static files collected")
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"Static files collection failed: {e}")
            return False

    def run_local_setup(self):
        """Run complete local setup process"""
        print("🚀 Stock Scanner Local Setup")
        print("=" * 40)
        print("Using SQLite database and Gmail SMTP")
        print("=" * 40)
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Setup virtual environment
        if not self.setup_virtual_environment():
            return False
        
        # Install requirements
        if not self.install_requirements():
            return False
        
        # Create environment file
        if not self.setup_environment_file():
            return False
        
        # Setup database
        if not self.setup_database():
            return False
        
        # Collect static files
        if not self.collect_static_files():
            return False
        
        # Test configurations
        self.test_email_configuration()
        self.test_yfinance_connection()
        
        # Create superuser (optional)
        create_superuser = input("\nCreate superuser account? (y/n): ").lower().strip()
        if create_superuser in ['y', 'yes']:
            self.create_superuser()
        
        print("\n🎉 Local setup completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Activate virtual environment:")
        if os.name == 'nt':  # Windows
            print("      venv\\Scripts\\activate")
        else:  # Unix/Linux/macOS
            print("      source venv/bin/activate")
        print("   2. Start development server:")
        print("      python manage.py runserver")
        print("   3. Visit: http://localhost:8000")
        print("   4. Admin: http://localhost:8000/admin")
        
        print("\n🔑 Configuration details:")
        print("   📧 Email: Gmail SMTP (noreply.retailtradescanner@gmail.com)")
        print("   🗄️ Database: SQLite (stock_scanner.db)")
        print("   📊 Stocks: yfinance only")
        print("   🌐 WordPress API: Enabled")
        
        return True

def main():
    """Main execution function"""
    setup = LocalSetup()
    success = setup.run_local_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()