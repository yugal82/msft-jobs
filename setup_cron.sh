#!/bin/bash
# Setup script to add cron job for Microsoft Job Scraper

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)
CRON_JOB="*/15 * * * * cd \"$SCRIPT_DIR\" && $PYTHON_PATH scraper.py >> scraper.log 2>&1"

echo "Microsoft Job Scraper - Cron Setup"
echo "=================================="
echo ""
echo "Script directory: $SCRIPT_DIR"
echo "Python path: $PYTHON_PATH"
echo ""
echo "Cron job to be added:"
echo "$CRON_JOB"
echo ""

read -p "Add this cron job? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "scraper.py"; then
        echo "Cron job already exists. Removing old entry..."
        crontab -l 2>/dev/null | grep -v "scraper.py" | crontab -
    fi
    
    # Add new cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✓ Cron job added successfully!"
    echo ""
    echo "Current crontab:"
    crontab -l
else
    echo "Setup cancelled."
fi
