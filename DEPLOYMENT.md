# Deployment Guide

This guide explains how to deploy the stock scanner application to the SFTP server.

## Overview

The deployment process:
1. Pulls latest changes from git repository
2. Builds the frontend application
3. Uploads the built files to SFTP server

## Prerequisites

- Python 3.6+
- pip (Python package manager)
- Node.js and npm (for building frontend)
- Git
- `paramiko` Python library (will be installed automatically)

## Quick Start

### Simple Deployment

The easiest way to deploy:

```bash
./deploy.sh
```

This will:
- Pull from the `main` branch
- Build the frontend
- Deploy to SFTP server

### Custom Branch Deployment

Deploy a specific branch:

```bash
./deploy.sh --branch develop
```

### Dry Run

See what would be done without actually doing it:

```bash
./deploy.sh --dry-run
```

## Advanced Usage

### Using Python Script Directly

For more control, use the Python script directly:

```bash
python3 deploy_sftp_complete.py [options]
```

#### Options

- `--branch BRANCH`: Git branch to deploy (default: main)
- `--no-pull`: Skip git pull step
- `--no-build`: Skip build step (use existing build)
- `--build-only`: Only build, don't deploy to SFTP
- `--dry-run`: Show what would be done without executing

#### Examples

Build only (no deployment):
```bash
python3 deploy_sftp_complete.py --build-only
```

Deploy existing build without pulling/building:
```bash
python3 deploy_sftp_complete.py --no-pull --no-build
```

Deploy specific branch:
```bash
python3 deploy_sftp_complete.py --branch feature/new-ui
```

## Configuration

### SFTP Credentials

Default credentials are configured in the scripts, but can be overridden with environment variables:

```bash
export SFTP_HOST="access-5018544625.webspace-host.com"
export SFTP_PORT="22"
export SFTP_USER="a1531117"
export SFTP_PASSWORD="your-password"
export REMOTE_ROOT="/"
```

### Build Configuration

```bash
export BUILD_DIR="frontend/build"  # Local build output directory
export KEEP_REMOTE_ITEMS=".ssh,.htaccess"  # Items to keep on remote server
```

## Server Information

**SFTP Server Details:**
- Host: `access-5018544625.webspace-host.com`
- Port: `22`
- Protocol: `SFTP + SSH`
- User: `a1531117`
- Password: `C2rt3rK#2010`

## Troubleshooting

### Missing Dependencies

If you get an error about missing Python packages:

```bash
pip3 install paramiko
```

### Build Failures

If the frontend build fails:

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Try building manually:
   ```bash
   npm run build
   ```

### Connection Issues

If you can't connect to SFTP server:

1. Verify credentials are correct
2. Check network connectivity
3. Verify firewall isn't blocking port 22

### Permission Errors

If you get permission errors running scripts:

```bash
chmod +x deploy.sh
chmod +x deploy_sftp_complete.py
```

## Logs

Deployment logs are saved to `deploy_sftp.log` in the project root.

## Market Manager Changes

The market manager has been updated to use Django-integrated stock retrieval instead of the fast proxy-based approach:

- **Old**: `enhanced_stock_retrieval_working.py` with proxies and full ticker list
- **New**: Django management command `python manage.py update_stocks_yfinance --schedule`

This provides better integration with Django's ORM and more reliable database operations.

## CI/CD Integration

To integrate with CI/CD pipelines:

```bash
# Example GitLab CI
deploy:
  script:
    - export SFTP_PASSWORD=$SFTP_PASSWORD_SECRET
    - ./deploy.sh --branch $CI_COMMIT_BRANCH
```

## Safety Features

- Keeps specific files on remote (`.ssh`, `.htaccess`)
- Dry-run mode for testing
- Comprehensive logging
- Error handling and rollback capability

## Support

For issues or questions:
1. Check `deploy_sftp.log` for detailed error messages
2. Run with `--dry-run` to see what would happen
3. Verify all prerequisites are installed
4. Check network connectivity to SFTP server
