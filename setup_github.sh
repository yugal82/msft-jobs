#!/bin/bash
# Setup script for GitHub repository configuration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Microsoft Job Scraper - GitHub Setup"
echo "====================================="
echo ""

# Check if git is initialized
if [ ! -d "$SCRIPT_DIR/.git" ]; then
    echo "Initializing git repository..."
    cd "$SCRIPT_DIR"
    git init
fi

# Check if remote exists
REMOTE_URL=$(git -C "$SCRIPT_DIR" remote get-url origin 2>/dev/null)

if [ -z "$REMOTE_URL" ]; then
    echo "No GitHub remote configured."
    echo ""
    read -p "Enter your GitHub repository URL (e.g., https://github.com/username/repo.git): " REPO_URL
    
    if [ -n "$REPO_URL" ]; then
        git -C "$SCRIPT_DIR" remote add origin "$REPO_URL"
        echo "✓ Remote added: $REPO_URL"
    else
        echo "No URL provided. Skipping remote setup."
        exit 1
    fi
else
    echo "Current remote: $REMOTE_URL"
    read -p "Change remote? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter new GitHub repository URL: " REPO_URL
        if [ -n "$REPO_URL" ]; then
            git -C "$SCRIPT_DIR" remote set-url origin "$REPO_URL"
            echo "✓ Remote updated: $REPO_URL"
        fi
    fi
fi

# Check git credentials
echo ""
echo "Checking git configuration..."
GIT_USER=$(git -C "$SCRIPT_DIR" config user.name)
GIT_EMAIL=$(git -C "$SCRIPT_DIR" config user.email)

if [ -z "$GIT_USER" ] || [ -z "$GIT_EMAIL" ]; then
    echo "Git user not configured."
    read -p "Enter your git username: " USERNAME
    read -p "Enter your git email: " EMAIL
    
    git -C "$SCRIPT_DIR" config user.name "$USERNAME"
    git -C "$SCRIPT_DIR" config user.email "$EMAIL"
    echo "✓ Git user configured"
fi

# Set default branch to main
git -C "$SCRIPT_DIR" branch -M main 2>/dev/null || true

echo ""
echo "GitHub setup complete!"
echo ""
echo "Note: For automatic pushes, ensure you have:"
echo "  1. Push access to the repository"
echo "  2. Git credentials configured (or use SSH keys)"
echo "  3. For HTTPS, consider using a Personal Access Token"
echo ""
