#!/usr/bin/env python3
"""
Script to add data-testid attributes to React components for E2E testing
"""

import os
import re
from pathlib import Path

# Base directory
FRONTEND_DIR = Path(__file__).parent / "src"

# Mapping of files to their test ID patterns
TEST_ID_PATTERNS = {
    # Auth pages
    "pages/auth/SignIn.js": [
        (r'(<div className="min-h-screen[^>]*)(>)', r'\1 data-testid="signin-page"\2'),
        (r'(<Card className="w-full"[^>]*)(>)', r'\1 data-testid="signin-card"\2'),
        (r'(<CardTitle[^>]*)(>Sign in)', r'\1 data-testid="signin-title"\2'),
        (r'(<CardDescription[^>]*)(>)', r'\1 data-testid="signin-description"\2', 1),
        (r'(<form[^>]*onSubmit={handleSubmit}[^>]*)(>)', r'\1 data-testid="signin-form"\2'),
        (r'(<Alert variant="destructive"[^>]*)(>)', r'\1 data-testid="signin-error-alert"\2'),
        (r'(<AlertDescription)(>)', r'\1 data-testid="signin-error-message"\2', 1),
        (r'(id="username"[^>]*)(placeholder)', r'\1data-testid="username-input" \2'),
        (r'(id="password"[^>]*type=)', r'\1data-testid="password-input" type='),
        (r'(<Button[^>]*type="button"[^>]*onClick={\(\) => setShowPassword[^>]*)(>)', r'\1 data-testid="password-toggle-button"\2'),
        (r'(<Link[^>]*to="/auth/forgot-password"[^>]*)(>)', r'\1 data-testid="forgot-password-link"\2'),
        (r'(<Button[^>]*type="submit"[^>]*)(>)', r'\1 data-testid="signin-submit-button"\2'),
        (r'(<Link[^>]*to="/auth/sign-up"[^>]*)(>)', r'\1 data-testid="signup-link"\2'),
    ],

    # SignUp page
    "pages/auth/SignUp.js": [
        (r'(<div className="min-h-screen[^>]*)(>)', r'\1 data-testid="signup-page"\2'),
        (r'(<Card className="w-full"[^>]*)(>)', r'\1 data-testid="signup-card"\2'),
        (r'(<form[^>]*onSubmit={handleSubmit}[^>]*)(>)', r'\1 data-testid="signup-form"\2'),
        (r'(name="username"[^>]*)(/>)', r'\1 data-testid="signup-username-input"\2'),
        (r'(name="email"[^>]*)(/>)', r'\1 data-testid="signup-email-input"\2'),
        (r'(name="password"[^>]*type="password"[^>]*)(/>)', r'\1 data-testid="signup-password-input"\2'),
        (r'(name="confirm_password"[^>]*)(/>)', r'\1 data-testid="signup-confirm-password-input"\2'),
        (r'(<Button[^>]*type="submit"[^>]*className="w-full"[^>]*)(>)', r'\1 data-testid="signup-submit-button"\2'),
        (r'(<Link[^>]*to="/auth/sign-in"[^>]*)(>)', r'\1 data-testid="signin-link"\2'),
    ],

    # Forgot Password
    "pages/auth/ForgotPassword.jsx": [
        (r'(<div[^>]*className="[^"]*min-h-screen[^"]*"[^>]*)(>)', r'\1 data-testid="forgot-password-page"\2'),
        (r'(<Card[^>]*)(>)', r'\1 data-testid="forgot-password-card"\2', 1),
        (r'(<form[^>]*onSubmit[^>]*)(>)', r'\1 data-testid="forgot-password-form"\2'),
        (r'(type="email"[^>]*)(placeholder)', r'\1data-testid="forgot-password-email-input" \2'),
        (r'(<Button[^>]*type="submit"[^>]*)(>)', r'\1 data-testid="forgot-password-submit-button"\2'),
        (r'(<Link[^>]*to="/auth/sign-in"[^>]*)(>)', r'\1 data-testid="back-to-signin-link"\2'),
    ],

    # Verify Email
    "pages/auth/VerifyEmail.jsx": [
        (r'(<div[^>]*className="[^"]*min-h-screen[^"]*"[^>]*)(>)', r'\1 data-testid="verify-email-page"\2'),
        (r'(<Card[^>]*)(>)', r'\1 data-testid="verify-email-card"\2', 1),
        (r'(<InputOTP[^>]*)(>)', r'\1 data-testid="verification-code-input"\2'),
        (r'(<Button[^>]*onClick={handleVerify}[^>]*)(>)', r'\1 data-testid="verify-button"\2'),
        (r'(<Button[^>]*onClick={handleResend}[^>]*)(>)', r'\1 data-testid="resend-code-button"\2'),
    ],

    # Plan Selection
    "pages/auth/PlanSelection.jsx": [
        (r'(<div[^>]*className="[^"]*min-h-screen[^"]*"[^>]*)(>)', r'\1 data-testid="plan-selection-page"\2'),
        (r'(<Card[^>]*data-plan="bronze"[^>]*)(>)', r'\1 data-testid="bronze-plan-card"\2'),
        (r'(<Card[^>]*data-plan="silver"[^>]*)(>)', r'\1 data-testid="silver-plan-card"\2'),
        (r'(<Card[^>]*data-plan="gold"[^>]*)(>)', r'\1 data-testid="gold-plan-card"\2'),
        (r'(<Card[^>]*data-plan="platinum"[^>]*)(>)', r'\1 data-testid="platinum-plan-card"\2'),
        (r'(<Button[^>]*onClick={.*selectPlan.*bronze[^>]*)(>)', r'\1 data-testid="select-bronze-button"\2'),
        (r'(<Button[^>]*onClick={.*selectPlan.*silver[^>]*)(>)', r'\1 data-testid="select-silver-button"\2'),
        (r'(<Button[^>]*onClick={.*selectPlan.*gold[^>]*)(>)', r'\1 data-testid="select-gold-button"\2'),
        (r'(<Button[^>]*onClick={.*selectPlan.*platinum[^>]*)(>)', r'\1 data-testid="select-platinum-button"\2'),
    ],
}


def add_test_ids_to_file(file_path, patterns):
    """Add data-testid attributes to a file based on patterns."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes = 0

        for pattern_data in patterns:
            if len(pattern_data) == 2:
                pattern, replacement = pattern_data
                count = 0  # Apply to all matches
            else:
                pattern, replacement, count = pattern_data

            # Skip if test ID already exists
            if 'data-testid' in pattern:
                continue

            if count == 1:
                content, n = re.subn(pattern, replacement, content, count=1)
            else:
                content, n = re.subn(pattern, replacement, content)

            if n > 0:
                changes += n
                print(f"  ✓ Applied pattern (matched {n} times)")

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated {file_path} ({changes} changes)")
            return changes
        else:
            print(f"- No changes needed for {file_path}")
            return 0

    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        return 0
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return 0


def main():
    """Main function to add test IDs across the frontend."""
    total_changes = 0

    print("Adding data-testid attributes for E2E testing...\n")

    for rel_path, patterns in TEST_ID_PATTERNS.items():
        file_path = FRONTEND_DIR / rel_path
        print(f"\nProcessing {rel_path}:")
        changes = add_test_ids_to_file(file_path, patterns)
        total_changes += changes

    print(f"\n{'='*60}")
    print(f"Total changes made: {total_changes}")
    print(f"{'='*60}\n")

    # Count total data-testid attributes
    print("Counting total data-testid attributes...")
    count_cmd = 'grep -r "data-testid" src/ --include="*.jsx" --include="*.js" | wc -l'
    os.system(f'cd {FRONTEND_DIR.parent} && {count_cmd}')


if __name__ == '__main__':
    main()
