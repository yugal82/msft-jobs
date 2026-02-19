#!/bin/bash
# Setup script to add cron job for Microsoft Job Scraper
# Schedule: Monday-Friday, 8:30 AM - 5:00 PM, every 30 minutes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)

# Cron format: minute hour day month weekday
# Runs every 30 minutes from 8:30 AM to 5:00 PM
# Monday-Friday only (1-5, where 0=Sunday, 1=Monday, etc.)
# Note: Cron runs at :00 and :30, so we start at 8:30 and end at 17:00
CRON_JOB="30 8-16 * * 1-5 cd \"$SCRIPT_DIR\" && $PYTHON_PATH scraper.py >> scraper.log 2>&1"
CRON_JOB2="0 9-17 * * 1-5 cd \"$SCRIPT_DIR\" && $PYTHON_PATH scraper.py >> scraper.log 2>&1"

echo "Microsoft Job Scraper - Cron Setup"
echo "=================================="
echo ""
echo "Schedule: Monday-Friday, 8:30 AM - 5:00 PM"
echo "Interval: Every 30 minutes"
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
