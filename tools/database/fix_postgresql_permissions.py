#!/usr/bin/env python3
"""
PostgreSQL Permissions Fix Script for Windows
Fixes database user permissions to allow Django migrations.

This script:
1. Connects to PostgreSQL as superuser
2. Grants necessary permissions to Django user
3. Fixes schema permissions
4. Tests the connection

Usage:
    python fix_postgresql_permissions.py

Author: Stock Scanner Project
Version: 1.0.0
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from urllib.parse import urlparse

def get_database_config():
    """Get database configuration from environment or user input"""
    print("🔍 Getting database configuration...")
    
    # Try to get from environment first
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        print("✅ Found DATABASE_URL in environment")
        parsed = urlparse(database_url)
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 5432,
            'database': parsed.path[1:] if parsed.path else 'stockscanner_prod',
            'username': parsed.username or 'stockscanner',
            'password': parsed.password or ''
        }
    
    # Ask user for configuration
    print("📝 Please provide database configuration:")
    config = {
        'host': input("PostgreSQL Host (default: localhost): ").strip() or 'localhost',
        'port': int(input("PostgreSQL Port (default: 5432): ").strip() or '5432'),
        'database': input("Database Name (default: stockscanner_prod): ").strip() or 'stockscanner_prod',
        'username': input("Django Database User (default: stockscanner): ").strip() or 'stockscanner',
    }
    
    return config

def connect_as_superuser(host, port):
    """Connect to PostgreSQL as superuser"""
    print("\n🔐 Connecting to PostgreSQL as superuser...")
    
    # Default password - Windows command prompt input issues workaround
    default_password = "C2rt3rK#2010"
    
    # Common superuser names to try
    superuser_names = ['postgres', 'postgresql', 'admin']
    
    for username in superuser_names:
        try:
            print(f"🔑 Trying username: {username} with default password")
            
            conn = psycopg2.connect(
                host=host,
                port=port,
                database='postgres',  # Connect to default postgres database
                user=username,
                password=default_password
            )
            
            print(f"✅ Connected as {username}")
            return conn, username
            
        except psycopg2.Error as e:
            print(f"❌ Failed to connect as {username}: {e}")
            continue
    
    # If default password doesn't work, try empty password
    print("🔑 Trying with empty password...")
    for username in superuser_names:
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                database='postgres',
                user=username,
                password=""
            )
            print(f"✅ Connected as {username} (no password)")
            return conn, username
        except psycopg2.Error:
            continue
    
    print("❌ Could not connect as any superuser")
    print("💡 Make sure PostgreSQL is running and the password is correct")
    return None, None

def fix_permissions(conn, db_config):
    """Fix database permissions"""
    print(f"\n🔧 Fixing permissions for user '{db_config['username']}'...")
    
    cursor = conn.cursor()
    
    try:
        # Create database if it doesn't exist
        print(f"📄 Creating database '{db_config['database']}' if not exists...")
        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
            [db_config['database']]
        )
        
        if not cursor.fetchone():
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(db_config['database'])
                )
            )
            print(f"✅ Created database '{db_config['database']}'")
        else:
            print(f"✅ Database '{db_config['database']}' already exists")
        
        # Create user if it doesn't exist
        print(f"👤 Creating user '{db_config['username']}' if not exists...")
        cursor.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s",
            [db_config['username']]
        )
        
        if not cursor.fetchone():
            # Use default password for new user
            user_password = "C2rt3rK#2010"
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier(db_config['username'])
                ),
                [user_password]
            )
            print(f"✅ Created user '{db_config['username']}' with default password")
        else:
            print(f"✅ User '{db_config['username']}' already exists")
        
        # Grant database privileges
        print("🔑 Granting database privileges...")
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(db_config['database']),
                sql.Identifier(db_config['username'])
            )
        )
        print("✅ Granted database privileges")
        
        # Grant superuser privileges (needed for Django migrations)
        print("🔑 Granting superuser privileges...")
        cursor.execute(
            sql.SQL("ALTER USER {} CREATEDB").format(
                sql.Identifier(db_config['username'])
            )
        )
        print("✅ Granted CREATEDB privilege")
        
        conn.commit()
        
    except psycopg2.Error as e:
        print(f"❌ Error fixing permissions: {e}")
        conn.rollback()
        return False
    
    finally:
        cursor.close()
    
    return True

def fix_schema_permissions(db_config):
    """Fix schema permissions on the target database"""
    print(f"\n🗄️ Fixing schema permissions on database '{db_config['database']}'...")
    
    # Default password for connection
    default_password = "C2rt3rK#2010"
    
    try:
        # Connect to the target database
        print("🔑 Connecting with default password...")
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user='postgres',  # Use superuser
            password=default_password
        )
        
        cursor = conn.cursor()
        
        # Grant schema permissions
        print("🔑 Granting schema permissions...")
        
        # Grant usage on public schema
        cursor.execute(
            sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(
                sql.Identifier(db_config['username'])
            )
        )
        
        # Grant create on public schema
        cursor.execute(
            sql.SQL("GRANT CREATE ON SCHEMA public TO {}").format(
                sql.Identifier(db_config['username'])
            )
        )
        
        # Grant all on all tables in public schema
        cursor.execute(
            sql.SQL("GRANT ALL ON ALL TABLES IN SCHEMA public TO {}").format(
                sql.Identifier(db_config['username'])
            )
        )
        
        # Grant all on all sequences in public schema
        cursor.execute(
            sql.SQL("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO {}").format(
                sql.Identifier(db_config['username'])
            )
        )
        
        # Set default privileges
        cursor.execute(
            sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {}").format(
                sql.Identifier(db_config['username'])
            )
        )
        
        cursor.execute(
            sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {}").format(
                sql.Identifier(db_config['username'])
            )
        )
        
        conn.commit()
        print("✅ Schema permissions fixed")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error fixing schema permissions: {e}")
        return False

def test_django_connection(db_config):
    """Test Django database connection"""
    print(f"\n🧪 Testing Django database connection...")
    
    # Use default password for Django user
    django_password = "C2rt3rK#2010"
    
    try:
        print("🔑 Testing with default password...")
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['username'],
            password=django_password
        )
        
        cursor = conn.cursor()
        
        # Test basic operations
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ Connected successfully")
        print(f"📊 PostgreSQL version: {version[:50]}...")
        
        # Test table creation permission
        cursor.execute("CREATE TABLE test_permissions (id SERIAL PRIMARY KEY)")
        cursor.execute("DROP TABLE test_permissions")
        print("✅ Table creation/deletion permissions working")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Django connection test failed: {e}")
        return False

def main():
    """Main function"""
    print("🔧 PostgreSQL Permissions Fix for Django")
    print("=" * 50)
    print()
    
    # Get database configuration
    db_config = get_database_config()
    
    print(f"\n📋 Configuration:")
    print(f"   Host: {db_config['host']}")
    print(f"   Port: {db_config['port']}")
    print(f"   Database: {db_config['database']}")
    print(f"   User: {db_config['username']}")
    
    # Connect as superuser
    superuser_conn, superuser_name = connect_as_superuser(db_config['host'], db_config['port'])
    if not superuser_conn:
        print("❌ Cannot proceed without superuser access")
        return False
    
    try:
        # Fix permissions
        if not fix_permissions(superuser_conn, db_config):
            print("❌ Failed to fix basic permissions")
            return False
        
        superuser_conn.close()
        
        # Fix schema permissions
        if not fix_schema_permissions(db_config):
            print("❌ Failed to fix schema permissions")
            return False
        
        # Test Django connection
        if not test_django_connection(db_config):
            print("❌ Django connection test failed")
            return False
        
        # Show next steps
        print("\n" + "=" * 50)
        print("✅ PERMISSIONS FIXED SUCCESSFULLY!")
        print("=" * 50)
        print()
        print("📋 Database Configuration:")
        print(f"   Host: {db_config['host']}")
        print(f"   Database: {db_config['database']}")
        print(f"   Username: {db_config['username']}")
        print(f"   Password: C2rt3rK#2010")
        print()
        print("📋 Next steps:")
        print("1. Update your .env file with these database credentials")
        print("2. Run: python manage.py migrate")
        print("3. Run: python manage.py createsuperuser")
        print("4. Run: python manage.py runserver")
        print()
        print("🎉 Your Django application should now work with PostgreSQL!")
        
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    finally:
        if superuser_conn and not superuser_conn.closed:
            superuser_conn.close()

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ FAILED: Could not fix PostgreSQL permissions")
        input("\nPress Enter to continue...")
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress Enter to continue...")