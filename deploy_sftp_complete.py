#!/usr/bin/env python3
"""
Complete SFTP Deployment Script
Pulls from git, builds the project, and pushes to SFTP server

Usage:
    python deploy_sftp_complete.py [options]

Options:
    --branch BRANCH      Git branch to checkout (default: main)
    --no-pull           Skip git pull
    --no-build          Skip build step
    --build-only        Only build, don't deploy
    --dry-run           Show what would be done without actually doing it

Environment Variables:
    SFTP_HOST           SFTP server hostname (default: access-5018544625.webspace-host.com)
    SFTP_PORT           SFTP server port (default: 22)
    SFTP_USER           SFTP username (default: a1531117)
    SFTP_PASSWORD       SFTP password (required)
    REMOTE_ROOT         Remote directory (default: /)
    BUILD_DIR           Local build directory (default: frontend/build)
    KEEP_REMOTE_ITEMS   Comma-separated list of items to keep on remote (default: .ssh,.htaccess)
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from typing import List, Optional
import paramiko
import stat
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deploy_sftp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
SFTP_CONFIG = {
    'host': os.environ.get('SFTP_HOST', 'access-5018544625.webspace-host.com'),
    'port': int(os.environ.get('SFTP_PORT', '22')),
    'username': os.environ.get('SFTP_USER', 'a1531117'),
    'password': os.environ.get('SFTP_PASSWORD', 'C2rt3rK#2010'),  # Default from user
}

REMOTE_ROOT = os.environ.get('REMOTE_ROOT', '/')
BUILD_DIR = os.environ.get('BUILD_DIR', 'frontend/build')
KEEP_REMOTE_ITEMS = os.environ.get('KEEP_REMOTE_ITEMS', '.ssh,.htaccess').split(',')

class DeploymentError(Exception):
    """Custom exception for deployment errors"""
    pass


class SFTPDeployer:
    """Handles SFTP deployment operations"""

    def __init__(self, config: dict, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.transport = None
        self.sftp = None

    def connect(self):
        """Establish SFTP connection"""
        try:
            logger.info(f"Connecting to {self.config['username']}@{self.config['host']}:{self.config['port']}")
            if self.dry_run:
                logger.info("[DRY RUN] Would connect to SFTP server")
                return

            self.transport = paramiko.Transport((self.config['host'], self.config['port']))
            self.transport.connect(username=self.config['username'], password=self.config['password'])
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            logger.info("SFTP connection established")

        except Exception as e:
            raise DeploymentError(f"Failed to connect to SFTP server: {e}")

    def disconnect(self):
        """Close SFTP connection"""
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()
        logger.info("SFTP connection closed")

    def remove_remote_files(self, remote_path: str, keep_items: List[str]):
        """Remove all files except those in keep_items"""
        logger.info(f"Cleaning remote directory: {remote_path}")
        logger.info(f"Keeping: {', '.join(keep_items)}")

        if self.dry_run:
            logger.info("[DRY RUN] Would clean remote directory")
            return

        try:
            # Ensure remote path exists
            try:
                self.sftp.stat(remote_path)
            except IOError:
                self.sftp.mkdir(remote_path)

            # List and remove items
            removed_count = 0
            for entry in self.sftp.listdir_attr(remote_path):
                if entry.filename in ['.', '..'] or entry.filename in keep_items:
                    continue

                full_path = f"{remote_path.rstrip('/')}/{entry.filename}"

                try:
                    if stat.S_ISDIR(entry.st_mode):
                        self._remove_directory_recursive(full_path)
                        logger.info(f"Removed directory: {full_path}")
                    else:
                        self.sftp.remove(full_path)
                        logger.info(f"Removed file: {full_path}")
                    removed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to remove {full_path}: {e}")

            logger.info(f"Removed {removed_count} items from remote")

        except Exception as e:
            raise DeploymentError(f"Failed to clean remote directory: {e}")

    def _remove_directory_recursive(self, path: str):
        """Recursively remove a directory"""
        try:
            for entry in self.sftp.listdir_attr(path):
                full_path = f"{path.rstrip('/')}/{entry.filename}"
                if stat.S_ISDIR(entry.st_mode):
                    self._remove_directory_recursive(full_path)
                else:
                    self.sftp.remove(full_path)
            self.sftp.rmdir(path)
        except Exception as e:
            logger.warning(f"Error removing directory {path}: {e}")

    def ensure_remote_directory(self, remote_path: str):
        """Ensure a remote directory exists"""
        if self.dry_run:
            return

        parts = remote_path.strip('/').split('/')
        current = ''
        for part in parts:
            if not part:
                continue
            current += '/' + part
            try:
                self.sftp.stat(current)
            except IOError:
                self.sftp.mkdir(current)
                logger.debug(f"Created directory: {current}")

    def upload_directory(self, local_dir: Path, remote_dir: str):
        """Upload entire directory to remote"""
        logger.info(f"Uploading {local_dir} to {remote_dir}")

        if self.dry_run:
            logger.info("[DRY RUN] Would upload directory")
            return

        uploaded_count = 0

        for root, dirs, files in os.walk(local_dir):
            rel_path = os.path.relpath(root, local_dir)
            if rel_path == '.':
                remote_path = remote_dir
            else:
                remote_path = f"{remote_dir.rstrip('/')}/{rel_path}"

            # Ensure remote directory exists
            self.ensure_remote_directory(remote_path)

            # Upload files
            for file in files:
                local_file = Path(root) / file
                remote_file = f"{remote_path.rstrip('/')}/{file}"

                try:
                    self.sftp.put(str(local_file), remote_file)
                    uploaded_count += 1
                    if uploaded_count % 10 == 0:
                        logger.info(f"Uploaded {uploaded_count} files...")
                except Exception as e:
                    logger.error(f"Failed to upload {local_file} to {remote_file}: {e}")

        logger.info(f"Successfully uploaded {uploaded_count} files")


class GitManager:
    """Handles git operations"""

    def __init__(self, repo_path: Path, dry_run: bool = False):
        self.repo_path = repo_path
        self.dry_run = dry_run

    def run_git_command(self, args: List[str]) -> str:
        """Run a git command and return output"""
        cmd = ['git'] + args
        logger.debug(f"Running: {' '.join(cmd)}")

        if self.dry_run and args[0] in ['checkout', 'pull', 'reset']:
            logger.info(f"[DRY RUN] Would run: {' '.join(cmd)}")
            return ""

        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise DeploymentError(f"Git command failed: {e.stderr}")

    def fetch(self):
        """Fetch from remote"""
        logger.info("Fetching from remote...")
        self.run_git_command(['fetch', '--all', '--tags'])

    def checkout_branch(self, branch: str):
        """Checkout a specific branch"""
        logger.info(f"Checking out branch: {branch}")
        self.run_git_command(['checkout', branch])

    def pull(self):
        """Pull latest changes"""
        logger.info("Pulling latest changes...")
        self.run_git_command(['pull', '--ff-only'])

    def get_current_commit(self) -> str:
        """Get current commit hash"""
        return self.run_git_command(['rev-parse', 'HEAD'])

    def get_current_branch(self) -> str:
        """Get current branch name"""
        return self.run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])


class Builder:
    """Handles project building"""

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.frontend_dir = project_root / 'frontend'
        self.dry_run = dry_run

    def build_frontend(self):
        """Build frontend application"""
        logger.info("Building frontend...")

        if self.dry_run:
            logger.info("[DRY RUN] Would build frontend")
            return

        # Check if node_modules exists
        if not (self.frontend_dir / 'node_modules').exists():
            logger.info("node_modules not found, running npm install...")
            self._run_command(['npm', 'install'], self.frontend_dir)

        # Run build
        self._run_command(['npm', 'run', 'build'], self.frontend_dir)
        logger.info("Frontend build completed")

    def _run_command(self, cmd: List[str], cwd: Path):
        """Run a shell command"""
        logger.debug(f"Running: {' '.join(cmd)} in {cwd}")

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                logger.debug(result.stdout)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Command output: {e.stdout}")
            logger.error(f"Command errors: {e.stderr}")
            raise DeploymentError(f"Build command failed: {e.stderr}")


def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(
        description='Deploy stock scanner to SFTP server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--branch', default='main', help='Git branch to deploy')
    parser.add_argument('--no-pull', action='store_true', help='Skip git pull')
    parser.add_argument('--no-build', action='store_true', help='Skip build step')
    parser.add_argument('--build-only', action='store_true', help='Only build, do not deploy')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')

    args = parser.parse_args()

    # Get project root
    project_root = Path(__file__).parent.absolute()
    build_output = project_root / BUILD_DIR

    logger.info("="*70)
    logger.info("SFTP DEPLOYMENT SCRIPT")
    logger.info("="*70)
    logger.info(f"Project root: {project_root}")
    logger.info(f"Build output: {build_output}")
    logger.info(f"Target: {SFTP_CONFIG['username']}@{SFTP_CONFIG['host']}:{REMOTE_ROOT}")
    logger.info(f"Branch: {args.branch}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info("="*70)

    try:
        # Git operations
        if not args.no_pull:
            git_manager = GitManager(project_root, args.dry_run)
            logger.info(f"Current branch: {git_manager.get_current_branch()}")
            logger.info(f"Current commit: {git_manager.get_current_commit()}")

            git_manager.fetch()
            if args.branch != git_manager.get_current_branch():
                git_manager.checkout_branch(args.branch)
            git_manager.pull()

            logger.info(f"Updated to commit: {git_manager.get_current_commit()}")
        else:
            logger.info("Skipping git pull (--no-pull)")

        # Build
        if not args.no_build:
            builder = Builder(project_root, args.dry_run)
            builder.build_frontend()
        else:
            logger.info("Skipping build (--no-build)")

        # Verify build output exists
        if not build_output.exists():
            raise DeploymentError(f"Build output directory not found: {build_output}")

        # Deploy
        if not args.build_only:
            # Validate SFTP credentials
            if not SFTP_CONFIG['password']:
                raise DeploymentError("SFTP_PASSWORD not set")

            deployer = SFTPDeployer(SFTP_CONFIG, args.dry_run)
            deployer.connect()

            try:
                deployer.remove_remote_files(REMOTE_ROOT, KEEP_REMOTE_ITEMS)
                deployer.upload_directory(build_output, REMOTE_ROOT)

                logger.info("="*70)
                logger.info("DEPLOYMENT SUCCESSFUL")
                logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info("="*70)

            finally:
                deployer.disconnect()
        else:
            logger.info("Skipping deployment (--build-only)")

    except DeploymentError as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
