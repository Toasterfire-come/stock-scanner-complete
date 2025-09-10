#!/usr/bin/env python
"""
Create Django Superuser Script
Works with Git Bash and non-TTY environments
"""
import os
import sys
import django
from django.contrib.auth import get_user_model

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()


def get_env(name: str, default: str) -> str:
    return os.environ.get(name, default)


def create_superuser():
    """Create a superuser account if it does not exist."""
    User = get_user_model()

    username = get_env('DJANGO_ADMIN_USERNAME', 'admin')
    email = get_env('DJANGO_ADMIN_EMAIL', 'admin@example.com')
    password = get_env('DJANGO_ADMIN_PASSWORD', '')

    try:
        # Check if superuser already exists
        if User.objects.filter(username=username).exists():
            print(f"SUCCESS: Superuser '{username}' already exists!")
            return

        if not password:
            # Generate a strong one-time password if not provided
            import secrets, string
            alphabet = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(secrets.choice(alphabet) for _ in range(20))
            print("INFO: No DJANGO_ADMIN_PASSWORD provided. Generated a strong temporary password.")

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        print("SUCCESS: Superuser created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print("   Password: [hidden]")
        print("   Admin URL: http://127.0.0.1:8000/admin/")

        # Optional: write the generated password to a local file (ignored by git)
        if os.environ.get('WRITE_ADMIN_PASSWORD_TO_FILE', 'false').lower() == 'true':
            with open('.admin_credentials', 'w') as f:
                f.write(f"username={username}\nemail={email}\npassword={password}\n")
            print("INFO: Credentials written to .admin_credentials")

        return user

    except Exception as e:
        print(f"ERROR: Error creating superuser: {e}")
        return None


def show_login_info():
    print("\n" + "=" * 60)
    print("DJANGO ADMIN LOGIN INFORMATION")
    print("=" * 60)
    print("Admin URL: http://127.0.0.1:8000/admin/")
    print("Username: set via DJANGO_ADMIN_USERNAME (default 'admin')")
    print("Password: set via DJANGO_ADMIN_PASSWORD or generated")
    print("Email: set via DJANGO_ADMIN_EMAIL")
    print("=" * 60)
    print("Use environment variables to control credentials.")


if __name__ == '__main__':
    print("Creating Django Superuser...")
    print()
    create_superuser()
    show_login_info()