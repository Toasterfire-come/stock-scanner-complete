#!/bin/bash
set -e  # Exit on any error

echo "🚀 Starting deployment from main branch..."
echo ""

# Change to repository root
cd "$(dirname "$0")/.."

# Store current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📌 Current branch: $CURRENT_BRANCH"

# Stash any local changes
echo "💾 Stashing local changes..."
git stash

# Checkout main branch
echo "🔄 Switching to main branch..."
git checkout main

# Pull latest changes from main
echo "⬇️  Pulling latest changes from main..."
git pull origin main

# Go back to frontend directory
cd frontend

# Install dependencies if package.json changed
echo "📦 Checking dependencies..."
npm install

# Build the production bundle
echo "🔨 Building production bundle..."
DISABLE_ESLINT_PLUGIN=true GENERATE_SOURCEMAP=false npm run build

# Deploy to SFTP
echo "📤 Deploying to SFTP server..."
if [ -f "deploy.lftp" ]; then
    lftp -f deploy.lftp
    echo "✅ Deployment completed successfully!"
else
    echo "❌ deploy.lftp not found!"
    exit 1
fi

# Return to original branch
cd ..
echo "🔄 Returning to branch: $CURRENT_BRANCH"
git checkout "$CURRENT_BRANCH"

# Restore stashed changes
echo "💾 Restoring stashed changes..."
git stash pop || echo "No changes to restore"

echo ""
echo "✨ All done! Site deployed from main branch."
