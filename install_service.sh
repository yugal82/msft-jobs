#!/bin/bash
# Install/uninstall macOS launchd service for Microsoft Job Scraper

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="$SCRIPT_DIR/com.microsoft.jobscraper.plist"
SERVICE_NAME="com.microsoft.jobscraper"
LAUNCHD_PATH="$HOME/Library/LaunchAgents/$SERVICE_NAME.plist"

if [ "$1" == "uninstall" ]; then
    echo "Uninstalling Microsoft Job Scraper service..."
    
    # Stop the service if running
    if launchctl list | grep -q "$SERVICE_NAME"; then
        echo "Stopping service..."
        launchctl unload "$LAUNCHD_PATH" 2>/dev/null || true
    fi
    
    # Remove plist file
    if [ -f "$LAUNCHD_PATH" ]; then
        rm "$LAUNCHD_PATH"
        echo "✓ Service uninstalled successfully"
    else
        echo "Service not found"
    fi
    
elif [ "$1" == "status" ]; then
    echo "Checking service status..."
    if launchctl list | grep -q "$SERVICE_NAME"; then
        echo "✓ Service is running"
        launchctl list | grep "$SERVICE_NAME"
    else
        echo "✗ Service is not running"
    fi
    
else
    echo "Installing Microsoft Job Scraper service..."
    
    # Unload any previous install so the new config takes effect
    launchctl unload "$LAUNCHD_PATH" 2>/dev/null || true

    # Copy plist to LaunchAgents, filling in this machine's Python and project paths
    # (the template in the repo is left untouched)
    PYTHON_PATH=$(which python3)
    mkdir -p "$HOME/Library/LaunchAgents"
    sed -e "s|/usr/bin/python3|$PYTHON_PATH|g" \
        -e "s|/Users/yugalkhanter/Desktop/Yugal Work/Projects/Microsoft Job Scraper|$SCRIPT_DIR|g" \
        "$PLIST_FILE" > "$LAUNCHD_PATH"
    
    # Load the service
    launchctl load "$LAUNCHD_PATH"
    
    echo "✓ Service installed successfully!"
    echo ""
    echo "The scraper will now run during business hours and automatically:"
    echo "  - Schedule: Monday-Friday, 8:30 AM - 5:00 PM"
    echo "  - Check for new jobs every 30 minutes"
    echo "  - Commit new jobs to git"
    echo "  - Push to GitHub automatically"
    echo ""
    echo "To check status: ./install_service.sh status"
    echo "To uninstall: ./install_service.sh uninstall"
    echo "To view logs: tail -f scraper.log"
fi
