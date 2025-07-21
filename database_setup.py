#!/usr/bin/env python3
"""
Database Setup for Stock Scanner on IONOS Hosting
Supports PostgreSQL (recommended) and MySQL
"""

import os
import sys
import subprocess
import psycopg2
import mysql.connector
from mysql.connector import Error as MySQLError
from psycopg2 import Error as PostgreSQLError

class DatabaseSetup:
    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'postgresql')  # postgresql or mysql
        self.db_name = os.getenv('DB_NAME', 'stock_scanner_db')
        self.db_user = os.getenv('DB_USER', 'stock_scanner_user')
        self.db_password = os.getenv('DB_PASSWORD', '')
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432' if self.db_type == 'postgresql' else '3306')
        
        # Root credentials for database creation
        self.root_user = os.getenv('DB_ROOT_USER', 'postgres' if self.db_type == 'postgresql' else 'root')
        self.root_password = os.getenv('DB_ROOT_PASSWORD', '')

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

    def validate_requirements(self):
        """Validate that required packages are installed"""
        self.print_step("Validating database requirements...")
        
        if self.db_type == 'postgresql':
            try:
                import psycopg2
                self.print_success("PostgreSQL adapter (psycopg2) is available")
            except ImportError:
                self.print_error("psycopg2 not installed. Run: pip install psycopg2-binary")
                return False
        
        elif self.db_type == 'mysql':
            try:
                import mysql.connector
                self.print_success("MySQL connector is available")
            except ImportError:
                self.print_error("mysql-connector-python not installed. Run: pip install mysql-connector-python")
                return False
        
        return True

    def create_postgresql_database(self):
        """Create PostgreSQL database and user"""
        self.print_step("Setting up PostgreSQL database...")
        
        try:
            # Connect as root user
            connection = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.root_user,
                password=self.root_password,
                database='postgres'  # Connect to default database
            )
            connection.autocommit = True
            cursor = connection.cursor()
            
            # Create user if not exists
            cursor.execute(f"""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{self.db_user}') THEN
                        CREATE USER {self.db_user} WITH PASSWORD '{self.db_password}';
                    END IF;
                END
                $$;
            """)
            self.print_success(f"User '{self.db_user}' created/verified")
            
            # Create database if not exists
            cursor.execute(f"""
                SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.db_name}'
            """)
            
            if not cursor.fetchone():
                cursor.execute(f"CREATE DATABASE {self.db_name} OWNER {self.db_user}")
                self.print_success(f"Database '{self.db_name}' created")
            else:
                self.print_success(f"Database '{self.db_name}' already exists")
            
            # Grant privileges
            cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {self.db_name} TO {self.db_user}")
            cursor.execute(f"ALTER USER {self.db_user} CREATEDB")
            self.print_success(f"Privileges granted to '{self.db_user}'")
            
            cursor.close()
            connection.close()
            return True
            
        except PostgreSQLError as e:
            self.print_error(f"PostgreSQL setup error: {e}")
            return False

    def create_mysql_database(self):
        """Create MySQL database and user"""
        self.print_step("Setting up MySQL database...")
        
        try:
            # Connect as root user
            connection = mysql.connector.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.root_user,
                password=self.root_password
            )
            cursor = connection.cursor()
            
            # Create database if not exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
            self.print_success(f"Database '{self.db_name}' created/verified")
            
            # Create user if not exists and grant privileges
            cursor.execute(f"""
                CREATE USER IF NOT EXISTS '{self.db_user}'@'%' IDENTIFIED BY '{self.db_password}'
            """)
            self.print_success(f"User '{self.db_user}' created/verified")
            
            # Grant privileges
            cursor.execute(f"GRANT ALL PRIVILEGES ON {self.db_name}.* TO '{self.db_user}'@'%'")
            cursor.execute("FLUSH PRIVILEGES")
            self.print_success(f"Privileges granted to '{self.db_user}'")
            
            cursor.close()
            connection.close()
            return True
            
        except MySQLError as e:
            self.print_error(f"MySQL setup error: {e}")
            return False

    def test_database_connection(self):
        """Test database connection with application user"""
        self.print_step("Testing database connection...")
        
        try:
            if self.db_type == 'postgresql':
                connection = psycopg2.connect(
                    host=self.db_host,
                    port=self.db_port,
                    user=self.db_user,
                    password=self.db_password,
                    database=self.db_name
                )
            elif self.db_type == 'mysql':
                connection = mysql.connector.connect(
                    host=self.db_host,
                    port=self.db_port,
                    user=self.db_user,
                    password=self.db_password,
                    database=self.db_name
                )
            
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            if result:
                self.print_success("Database connection successful")
                cursor.close()
                connection.close()
                return True
                
        except Exception as e:
            self.print_error(f"Database connection test failed: {e}")
            return False

    def generate_django_settings(self):
        """Generate Django database settings"""
        self.print_step("Generating Django database configuration...")
        
        if self.db_type == 'postgresql':
            engine = 'django.db.backends.postgresql'
        elif self.db_type == 'mysql':
            engine = 'django.db.backends.mysql'
        
        settings_config = f"""
# Database Configuration for IONOS Hosting
DATABASES = {{
    'default': {{
        'ENGINE': '{engine}',
        'NAME': '{self.db_name}',
        'USER': '{self.db_user}',
        'PASSWORD': '{self.db_password}',
        'HOST': '{self.db_host}',
        'PORT': '{self.db_port}',
        'OPTIONS': {{
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }} if '{self.db_type}' == 'mysql' else {{}},
        'CONN_MAX_AGE': 600,  # Connection pooling
        'ATOMIC_REQUESTS': True,  # Database transactions
    }}
}}

# Database connection pooling (recommended for production)
DATABASE_POOL_SETTINGS = {{
    'max_connections': 20,
    'min_connections': 5,
    'connection_lifetime': 3600,  # 1 hour
}}
"""
        
        # Write to file
        with open('database_settings.py', 'w') as f:
            f.write(settings_config)
        
        self.print_success("Django database settings written to database_settings.py")

    def create_env_file(self):
        """Create .env file with database settings"""
        self.print_step("Creating .env file...")
        
        env_content = f"""# Database Configuration
DB_TYPE={self.db_type}
DB_NAME={self.db_name}
DB_USER={self.db_user}
DB_PASSWORD={self.db_password}
DB_HOST={self.db_host}
DB_PORT={self.db_port}

# Email Configuration (IONOS)
EMAIL_HOST=smtp.ionos.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@retailtradescan.net
EMAIL_HOST_PASSWORD=your_email_password_here

# Site Configuration
SITE_URL=https://retailtradescan.net
DEBUG=False
SECRET_KEY=your_secret_key_here

# Stock API Configuration (yfinance only)
USE_YFINANCE_ONLY=True
STOCK_API_RATE_LIMIT=1  # 1 second between requests

# Security Settings
ALLOWED_HOSTS=retailtradescan.net,www.retailtradescan.net
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
"""
        
        env_file = '.env'
        if not os.path.exists(env_file):
            with open(env_file, 'w') as f:
                f.write(env_content)
            self.print_success(".env file created")
        else:
            self.print_warning(".env file already exists - not overwriting")

    def run_django_migrations(self):
        """Run Django migrations"""
        self.print_step("Running Django migrations...")
        
        try:
            # Make migrations
            result = subprocess.run(['python', 'manage.py', 'makemigrations'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.print_success("Migrations created successfully")
            else:
                self.print_warning(f"Make migrations warning: {result.stderr}")
            
            # Run migrations
            result = subprocess.run(['python', 'manage.py', 'migrate'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.print_success("Migrations applied successfully")
                return True
            else:
                self.print_error(f"Migration error: {result.stderr}")
                return False
                
        except Exception as e:
            self.print_error(f"Django migration error: {e}")
            return False

    def create_superuser(self):
        """Create Django superuser"""
        self.print_step("Creating Django superuser...")
        
        username = input("Enter superuser username (admin): ").strip() or "admin"
        email = input("Enter superuser email (admin@retailtradescan.net): ").strip() or "admin@retailtradescan.net"
        
        try:
            result = subprocess.run([
                'python', 'manage.py', 'createsuperuser',
                '--username', username,
                '--email', email,
                '--noinput'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_success(f"Superuser '{username}' created")
            else:
                self.print_warning("Superuser creation failed - you can create one manually later")
                
        except Exception as e:
            self.print_warning(f"Superuser creation error: {e}")

    def optimize_database(self):
        """Optimize database settings for production"""
        self.print_step("Optimizing database for production...")
        
        if self.db_type == 'postgresql':
            self._optimize_postgresql()
        elif self.db_type == 'mysql':
            self._optimize_mysql()

    def _optimize_postgresql(self):
        """PostgreSQL specific optimizations"""
        try:
            connection = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            connection.autocommit = True
            cursor = connection.cursor()
            
            # Create indexes for better performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_stock_ticker ON stocks_stockalert(ticker)",
                "CREATE INDEX IF NOT EXISTS idx_stock_last_update ON stocks_stockalert(last_update)",
                "CREATE INDEX IF NOT EXISTS idx_email_category ON emails_emailsubscription(category)",
                "CREATE INDEX IF NOT EXISTS idx_email_active ON emails_emailsubscription(is_active)",
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            self.print_success("PostgreSQL indexes created")
            cursor.close()
            connection.close()
            
        except Exception as e:
            self.print_warning(f"PostgreSQL optimization warning: {e}")

    def _optimize_mysql(self):
        """MySQL specific optimizations"""
        try:
            connection = mysql.connector.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            cursor = connection.cursor()
            
            # Create indexes for better performance
            indexes = [
                "CREATE INDEX idx_stock_ticker ON stocks_stockalert(ticker)",
                "CREATE INDEX idx_stock_last_update ON stocks_stockalert(last_update)",
                "CREATE INDEX idx_email_category ON emails_emailsubscription(category)",
                "CREATE INDEX idx_email_active ON emails_emailsubscription(is_active)",
            ]
            
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                except MySQLError:
                    pass  # Index might already exist
            
            self.print_success("MySQL indexes created")
            cursor.close()
            connection.close()
            
        except Exception as e:
            self.print_warning(f"MySQL optimization warning: {e}")

    def setup_database(self):
        """Main database setup process"""
        print("🗄️ Stock Scanner Database Setup for IONOS Hosting")
        print("=" * 50)
        
        # Validate requirements
        if not self.validate_requirements():
            return False
        
        # Create database and user
        if self.db_type == 'postgresql':
            success = self.create_postgresql_database()
        elif self.db_type == 'mysql':
            success = self.create_mysql_database()
        else:
            self.print_error(f"Unsupported database type: {self.db_type}")
            return False
        
        if not success:
            return False
        
        # Test connection
        if not self.test_database_connection():
            return False
        
        # Generate Django settings
        self.generate_django_settings()
        
        # Create .env file
        self.create_env_file()
        
        # Run Django migrations
        if not self.run_django_migrations():
            return False
        
        # Optimize database
        self.optimize_database()
        
        # Create superuser
        self.create_superuser()
        
        print("\n🎉 Database setup completed successfully!")
        print(f"   Database: {self.db_name}")
        print(f"   User: {self.db_user}")
        print(f"   Type: {self.db_type}")
        print(f"   Host: {self.db_host}:{self.db_port}")
        print("\n📝 Next steps:")
        print("   1. Update your Django settings.py with database_settings.py content")
        print("   2. Configure your .env file with actual passwords")
        print("   3. Test the application: python manage.py runserver")
        
        return True

def main():
    """Main execution function"""
    setup = DatabaseSetup()
    
    # Interactive setup if no environment variables
    if not os.getenv('DB_PASSWORD'):
        print("🔧 Interactive Database Setup")
        print("=" * 30)
        
        setup.db_type = input("Database type (postgresql/mysql) [postgresql]: ").strip() or 'postgresql'
        setup.db_name = input("Database name [stock_scanner_db]: ").strip() or 'stock_scanner_db'
        setup.db_user = input("Database user [stock_scanner_user]: ").strip() or 'stock_scanner_user'
        setup.db_password = input("Database password: ").strip()
        setup.db_host = input("Database host [localhost]: ").strip() or 'localhost'
        
        if setup.db_type == 'postgresql':
            setup.db_port = input("Database port [5432]: ").strip() or '5432'
            setup.root_user = input("PostgreSQL superuser [postgres]: ").strip() or 'postgres'
        else:
            setup.db_port = input("Database port [3306]: ").strip() or '3306'
            setup.root_user = input("MySQL root user [root]: ").strip() or 'root'
        
        setup.root_password = input(f"{setup.root_user} password: ").strip()
        
        if not setup.db_password:
            print("❌ Database password is required")
            return
    
    # Run setup
    success = setup.setup_database()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()