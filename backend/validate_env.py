#!/usr/bin/env python3
"""
Environment variable validation script.
Ensures all required variables are set before starting the application.
"""
import os
import sys
from pathlib import Path
from typing import List, Dict


class Color:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


REQUIRED_VARS = {
    'backend': {
        'critical': [
            'SECRET_KEY',
            'DB_NAME',
            'DB_USER',
            'DB_HOST',
        ],
        'important': [
            'DB_PASSWORD',  # Required in production
            'PAYPAL_CLIENT_ID',
            'PAYPAL_SECRET',
            'PAYPAL_WEBHOOK_ID',
        ],
        'optional': [
            'DEBUG',
            'ALLOWED_HOSTS',
            'SENTRY_DSN',
            'REDIS_URL',
        ]
    },
    'frontend': {
        'critical': [
            'REACT_APP_BACKEND_URL',
        ],
        'important': [
            'REACT_APP_PAYPAL_CLIENT_ID',
        ],
        'optional': [
            'REACT_APP_GOOGLE_CLIENT_ID',
            'REACT_APP_SENTRY_DSN',
        ]
    }
}


def check_env_file_exists(env_path: Path) -> bool:
    """Check if .env file exists"""
    if not env_path.exists():
        print(f"{Color.RED}✗ {env_path} does not exist{Color.END}")
        return False
    print(f"{Color.GREEN}✓ {env_path} exists{Color.END}")
    return True


def load_env_file(env_path: Path) -> Dict[str, str]:
    """Load environment variables from file"""
    env_vars = {}
    if not env_path.exists():
        return env_vars
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars


def validate_env_vars(env_vars: Dict[str, str], required: Dict[str, List[str]], 
                     env_name: str) -> tuple:
    """
    Validate environment variables.
    
    Returns:
        Tuple of (all_critical_present, warnings, errors)
    """
    warnings = []
    errors = []
    
    print(f"\n{Color.BLUE}Validating {env_name} environment:{Color.END}")
    
    # Check critical variables
    print(f"\n  {Color.BLUE}Critical variables:{Color.END}")
    for var in required.get('critical', []):
        if var in env_vars and env_vars[var]:
            print(f"    {Color.GREEN}✓ {var}{Color.END}")
        else:
            print(f"    {Color.RED}✗ {var} (MISSING){Color.END}")
            errors.append(f"{var} is required")
    
    # Check important variables
    print(f"\n  {Color.BLUE}Important variables:{Color.END}")
    for var in required.get('important', []):
        if var in env_vars and env_vars[var]:
            print(f"    {Color.GREEN}✓ {var}{Color.END}")
        else:
            print(f"    {Color.YELLOW}! {var} (not set){Color.END}")
            warnings.append(f"{var} is recommended")
    
    # Check optional variables
    print(f"\n  {Color.BLUE}Optional variables:{Color.END}")
    for var in required.get('optional', []):
        if var in env_vars and env_vars[var]:
            print(f"    {Color.GREEN}✓ {var}{Color.END}")
        else:
            print(f"    - {var} (optional)")
    
    return (len(errors) == 0, warnings, errors)


def validate_backend():
    """Validate backend environment"""
    backend_env = Path(__file__).parent / '.env'
    
    if not check_env_file_exists(backend_env):
        print(f"\n{Color.YELLOW}💡 Copy .env.example to .env and configure{Color.END}")
        return False
    
    env_vars = load_env_file(backend_env)
    all_ok, warnings, errors = validate_env_vars(
        env_vars, 
        REQUIRED_VARS['backend'],
        'Backend'
    )
    
    # Additional validations
    if 'DEBUG' in env_vars:
        debug_value = env_vars['DEBUG'].lower()
        if debug_value == 'true':
            print(f"\n  {Color.YELLOW}⚠ DEBUG=True (not recommended for production){Color.END}")
    
    if 'SECRET_KEY' in env_vars:
        if env_vars['SECRET_KEY'] == 'django-insecure-development-key':
            print(f"  {Color.RED}⚠ SECRET_KEY is using default insecure value{Color.END}")
            errors.append("SECRET_KEY must be changed from default")
            all_ok = False
    
    return all_ok


def validate_frontend():
    """Validate frontend environment"""
    frontend_env = Path(__file__).parent.parent / 'frontend' / '.env'
    
    if not check_env_file_exists(frontend_env):
        print(f"\n{Color.YELLOW}💡 Copy .env.example to .env and configure{Color.END}")
        return False
    
    env_vars = load_env_file(frontend_env)
    all_ok, warnings, errors = validate_env_vars(
        env_vars,
        REQUIRED_VARS['frontend'],
        'Frontend'
    )
    
    # Additional validations
    if 'REACT_APP_BACKEND_URL' in env_vars:
        backend_url = env_vars['REACT_APP_BACKEND_URL']
        if 'localhost' in backend_url or '127.0.0.1' in backend_url:
            print(f"  {Color.YELLOW}⚠ Backend URL points to localhost{Color.END}")
    
    return all_ok


def main():
    """Main validation function"""
    print(f"{Color.BLUE}{'='*60}{Color.END}")
    print(f"{Color.BLUE}Environment Variable Validation{Color.END}")
    print(f"{Color.BLUE}{'='*60}{Color.END}")
    
    backend_ok = validate_backend()
    frontend_ok = validate_frontend()
    
    print(f"\n{Color.BLUE}{'='*60}{Color.END}")
    print(f"{Color.BLUE}Validation Summary{Color.END}")
    print(f"{Color.BLUE}{'='*60}{Color.END}")
    
    if backend_ok and frontend_ok:
        print(f"{Color.GREEN}✓ All critical environment variables are set{Color.END}")
        print(f"\n{Color.GREEN}Ready to start application!{Color.END}")
        return 0
    else:
        print(f"{Color.RED}✗ Some critical environment variables are missing{Color.END}")
        print(f"\n{Color.YELLOW}Fix the issues above before starting the application{Color.END}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
