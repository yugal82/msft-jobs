#!/usr/bin/env python3
"""
Alternative scheduler for running the scraper every 15 minutes.
Use this if you prefer not to use cron.
"""

import time
import subprocess
import sys
from pathlib import Path

SCRAPER_SCRIPT = Path(__file__).parent / "scraper.py"
INTERVAL_MINUTES = 15
INTERVAL_SECONDS = INTERVAL_MINUTES * 60


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


def main():
    """Main scheduler loop."""
    print(f"Scheduler started. Running scraper every {INTERVAL_MINUTES} minutes.")
    print("Press Ctrl+C to stop.\n")
    
    # Run immediately on start
    run_scraper()
    
    # Then run every interval
    try:
        while True:
            time.sleep(INTERVAL_SECONDS)
            run_scraper()
    except KeyboardInterrupt:
        print("\nScheduler stopped.")


if __name__ == "__main__":
    main()
