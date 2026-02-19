#!/usr/bin/env python3
"""
Scheduler for running the scraper every 15 minutes during business hours.
Runs Monday-Friday, 8:30 AM - 5:00 PM.
"""

import time
import subprocess
import sys
from datetime import datetime, time as dt_time, timedelta
from pathlib import Path

SCRAPER_SCRIPT = Path(__file__).parent / "scraper.py"
INTERVAL_MINUTES = 30
INTERVAL_SECONDS = INTERVAL_MINUTES * 60

# Business hours configuration
BUSINESS_START_HOUR = 8
BUSINESS_START_MINUTE = 30
BUSINESS_END_HOUR = 17  # 5:00 PM
BUSINESS_END_MINUTE = 0


def is_business_hours() -> bool:
    """Check if current time is within business hours (Mon-Fri, 8:30 AM - 5:00 PM)."""
    now = datetime.now()
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    if now.weekday() >= 5:  # Saturday (5) or Sunday (6)
        return False
    
    # Check if it's within business hours
    current_time = now.time()
    start_time = dt_time(BUSINESS_START_HOUR, BUSINESS_START_MINUTE)
    end_time = dt_time(BUSINESS_END_HOUR, BUSINESS_END_MINUTE)
    
    return start_time <= current_time < end_time


def run_scraper():
    """Run the scraper script."""
    try:
        result = subprocess.run(
            [sys.executable, str(SCRAPER_SCRIPT)],
            cwd=SCRAPER_SCRIPT.parent,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running scraper: {e}", file=sys.stderr)
        return False


def get_next_business_time() -> datetime:
    """Calculate the next time the scraper should run."""
    now = datetime.now()
    
    # If it's currently business hours, run in 15 minutes
    if is_business_hours():
        return now.replace(second=0, microsecond=0) + timedelta(minutes=INTERVAL_MINUTES)
    
    # Otherwise, find next business day and time
    next_run = now.replace(hour=BUSINESS_START_HOUR, minute=BUSINESS_START_MINUTE, second=0, microsecond=0)
    
    # If we've passed business hours today, start tomorrow
    if now.time() >= dt_time(BUSINESS_END_HOUR, BUSINESS_END_MINUTE):
        next_run += timedelta(days=1)
    
    # Skip weekends
    while next_run.weekday() >= 5:
        next_run += timedelta(days=1)
    
    return next_run


def main():
    """Main scheduler loop."""
    print("Microsoft Job Scraper Scheduler")
    print("=" * 40)
    print(f"Schedule: Monday-Friday, {BUSINESS_START_HOUR}:{BUSINESS_START_MINUTE:02d} AM - {BUSINESS_END_HOUR}:{BUSINESS_END_MINUTE:02d} PM")
    print(f"Interval: Every {INTERVAL_MINUTES} minutes")
    print("Press Ctrl+C to stop.\n")
    
    # Run immediately if within business hours
    if is_business_hours():
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Within business hours. Running scraper...")
        run_scraper()
    else:
        next_run = get_next_business_time()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Outside business hours.")
        print(f"Next run scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Main loop
    try:
        while True:
            # Sleep for the interval
            time.sleep(INTERVAL_SECONDS)
            
            # Check if we're in business hours before running
            if is_business_hours():
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running scraper...")
                run_scraper()
            else:
                next_run = get_next_business_time()
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Outside business hours. Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                
    except KeyboardInterrupt:
        print("\nScheduler stopped.")


if __name__ == "__main__":
    main()
