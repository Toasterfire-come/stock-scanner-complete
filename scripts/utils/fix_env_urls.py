#!/usr/bin/env python3
"""
Environment URL Fixer
Fixes URL encoding issues in .env file, particularly for special characters in passwords
"""

import re
from urllib.parse import quote_plus
from pathlib import Path

def fix_database_url(url):
    """Fix DATABASE_URL by properly encoding special characters in password"""
    if not url or '://' not in url:
        return url
    
    # Pattern to match: protocol://user:password@host:port/db
    pattern = r'(postgresql://[^:]+:)([^@]+)(@.+)'
    match = re.match(pattern, url)
    
    if match:
        prefix, password, suffix = match.groups()
        
        # Check if password has special characters that need encoding
        special_chars = ['#', '@', ':', '/', '?', '&', '=', '+', ' ']
        needs_encoding = any(char in password for char in special_chars)
        
        if needs_encoding:
            # URL encode the password
            encoded_password = quote_plus(password)
            fixed_url = prefix + encoded_password + suffix
            print(f"🔧 Fixed DATABASE_URL:")
            print(f"   Original password: {password}")
            print(f"   Encoded password:  {encoded_password}")
            return fixed_url
        else:
            print(f"✅ DATABASE_URL password doesn't need encoding")
            return url
    else:
        print(f"⚠️ Could not parse DATABASE_URL format")
        return url

def fix_env_file():
    """Fix .env file URL encoding issues"""
    print("🔧 Environment URL Fixer")
    print("=" * 30)
    
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print("💡 Copy .env.example to .env first")
        return False
    
    # Read current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Process lines
    fixed_lines = []
    changes_made = False
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('DATABASE_URL='):
            # Extract the URL value
            url = line.split('=', 1)[1]
            
            # Fix the URL
            fixed_url = fix_database_url(url)
            
            if fixed_url != url:
                fixed_lines.append(f"DATABASE_URL={fixed_url}\n")
                changes_made = True
                print(f"✅ Fixed DATABASE_URL in .env file")
            else:
                fixed_lines.append(line + '\n')
        else:
            # Keep other lines as-is
            fixed_lines.append(line + '\n' if line else '\n')
    
    # Write back if changes were made
    if changes_made:
        # Backup original file
        backup_file = Path('.env.backup')
        with open(backup_file, 'w') as f:
            with open(env_file, 'r') as original:
                f.write(original.read())
        print(f"💾 Backed up original .env to {backup_file}")
        
        # Write fixed version
        with open(env_file, 'w') as f:
            f.writelines(fixed_lines)
        
        print(f"✅ Fixed .env file saved")
        return True
    else:
        print(f"✅ No changes needed in .env file")
        return True

def test_database_url():
    """Test if DATABASE_URL can be parsed correctly"""
    import os
    from pathlib import Path
    
    # Load .env file
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    database_url = line.split('=', 1)[1].strip()
                    os.environ['DATABASE_URL'] = database_url
                    break
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("⚠️ No DATABASE_URL found in environment")
        return False
    
    print(f"\n🧪 Testing DATABASE_URL parsing...")
    print(f"URL: {database_url}")
    
    try:
        import dj_database_url
        parsed = dj_database_url.parse(database_url)
        print(f"✅ DATABASE_URL parsed successfully:")
        print(f"   Engine: {parsed.get('ENGINE', 'N/A')}")
        print(f"   Host: {parsed.get('HOST', 'N/A')}")
        print(f"   Port: {parsed.get('PORT', 'N/A')}")
        print(f"   Database: {parsed.get('NAME', 'N/A')}")
        print(f"   User: {parsed.get('USER', 'N/A')}")
        return True
    except ImportError:
        print("⚠️ dj_database_url not installed - install with: pip install dj-database-url")
        return False
    except Exception as e:
        print(f"❌ DATABASE_URL parsing failed: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Fixing environment URL encoding issues...\n")
    
    # Fix .env file
    if fix_env_file():
        print("\n" + "=" * 30)
        
        # Test the fixed URL
        test_database_url()
        
        print("\n💡 Next steps:")
        print("   1. python test_django_startup.py")
        print("   2. python run_migrations.py")
        print("   3. python manage.py runserver")
        
        return True
    else:
        print("\n❌ Failed to fix .env file")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)