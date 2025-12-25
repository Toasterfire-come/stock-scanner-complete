#!/usr/bin/env python3
"""
Fix the remaining console.error callback in SecurityProvider.js
"""

from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SECURITY_PROVIDER = SCRIPT_DIR / "src" / "components" / "SecurityProvider.js"

def fix_console_error_callback():
    """Fix the console.error callback"""
    try:
        with open(SECURITY_PROVIDER, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {SECURITY_PROVIDER}: {e}")
        return False

    # Replace the callback
    old_code = '}).catch(console.error);'
    new_code = '}).catch(err => logger.error("CSP violation report failed:", err));'

    if old_code in content:
        content = content.replace(old_code, new_code)
        print(f"Fixed console.error callback in {SECURITY_PROVIDER}")

        try:
            with open(SECURITY_PROVIDER, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing {SECURITY_PROVIDER}: {e}")
            return False
    else:
        print(f"console.error callback not found in {SECURITY_PROVIDER}")
        return False

if __name__ == '__main__':
    success = fix_console_error_callback()
    exit(0 if success else 1)
