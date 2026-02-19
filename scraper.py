#!/usr/bin/env python3
"""
Microsoft Careers Job Scraper
Fetches job listings from Microsoft Careers API and tracks new openings.
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import requests

# Configuration
API_URL = "https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=Software%20Engineer&location=United%20States&start=0&sort_by=timestamp&filter_include_remote=1&filter_seniority=Entry"
JOBS_FILE = "jobs.json"
TRACKED_IDS_FILE = "tracked_job_ids.json"
DATA_DIR = Path(__file__).parent


def load_json_file(filepath: Path) -> Dict:
    """Load JSON data from file, return empty dict if file doesn't exist."""
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {filepath}: {e}")
            return {}
    return {}


def save_json_file(filepath: Path, data: Dict) -> None:
    """Save data to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def fetch_jobs() -> Dict:
    """Fetch jobs from Microsoft Careers API."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching jobs: {e}")
        sys.exit(1)


def get_tracked_job_ids() -> Set[int]:
    """Load set of previously tracked job IDs."""
    tracked_file = DATA_DIR / TRACKED_IDS_FILE
    data = load_json_file(tracked_file)
    return set(data.get('job_ids', []))


def save_tracked_job_ids(job_ids: Set[int]) -> None:
    """Save tracked job IDs to file."""
    tracked_file = DATA_DIR / TRACKED_IDS_FILE
    data = {'job_ids': list(job_ids), 'last_updated': datetime.now().isoformat()}
    save_json_file(tracked_file, data)


def get_new_jobs(api_response: Dict, tracked_ids: Set[int]) -> List[Dict]:
    """Extract new jobs that haven't been tracked before."""
    positions = api_response.get('data', {}).get('positions', [])
    new_jobs = []
    
    for position in positions:
        job_id = position.get('id')
        if job_id and job_id not in tracked_ids:
            new_jobs.append(position)
    
    return new_jobs


def update_jobs_file(new_jobs: List[Dict]) -> bool:
    """Add new jobs to the jobs.json file."""
    jobs_file = DATA_DIR / JOBS_FILE
    all_jobs = load_json_file(jobs_file)
    
    # Initialize structure if needed
    if 'jobs' not in all_jobs:
        all_jobs['jobs'] = []
    
    # Add new jobs with timestamp
    for job in new_jobs:
        job_entry = {
            **job,
            'discovered_at': datetime.now().isoformat()
        }
        all_jobs['jobs'].append(job_entry)
    
    # Update metadata
    all_jobs['last_updated'] = datetime.now().isoformat()
    all_jobs['total_jobs'] = len(all_jobs['jobs'])
    
    save_json_file(jobs_file, all_jobs)
    return len(new_jobs) > 0


def commit_to_git(message: str) -> bool:
    """Commit changes to git repository."""
    try:
        # Check if git repo exists
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=DATA_DIR,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("Not a git repository. Initializing...")
            subprocess.run(['git', 'init'], cwd=DATA_DIR, check=True)
            # Create .gitignore if it doesn't exist
            gitignore = DATA_DIR / '.gitignore'
            if not gitignore.exists():
                with open(gitignore, 'w') as f:
                    f.write("__pycache__/\n*.pyc\n.env\n")
        
        # Stage all changes
        subprocess.run(
            ['git', 'add', '-A'],
            cwd=DATA_DIR,
            check=True
        )
        
        # Check if there are changes to commit
        result = subprocess.run(
            ['git', 'diff', '--cached', '--quiet'],
            cwd=DATA_DIR,
            capture_output=True
        )
        
        if result.returncode == 0:
            print("No changes to commit.")
            return False
        
        # Commit changes
        subprocess.run(
            ['git', 'commit', '-m', message],
            cwd=DATA_DIR,
            check=True
        )
        
        print(f"Successfully committed: {message}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error committing to git: {e}")
        return False
    except FileNotFoundError:
        print("Git is not installed. Skipping git commit.")
        return False


def main():
    """Main scraper function."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting job scraper...")
    
    # Fetch jobs from API
    print("Fetching jobs from API...")
    api_response = fetch_jobs()
    
    # Get tracked job IDs
    tracked_ids = get_tracked_job_ids()
    print(f"Currently tracking {len(tracked_ids)} job IDs")
    
    # Find new jobs
    new_jobs = get_new_jobs(api_response, tracked_ids)
    print(f"Found {len(new_jobs)} new job(s)")
    
    if new_jobs:
        # Update tracked IDs
        new_ids = {job['id'] for job in new_jobs if job.get('id')}
        tracked_ids.update(new_ids)
        save_tracked_job_ids(tracked_ids)
        
        # Save new jobs
        update_jobs_file(new_jobs)
        
        # Print new jobs
        print("\nNew jobs discovered:")
        for job in new_jobs:
            print(f"  - {job.get('name', 'N/A')} (ID: {job.get('id')})")
            print(f"    Locations: {', '.join(job.get('locations', []))}")
            print(f"    URL: https://apply.careers.microsoft.com{job.get('positionUrl', '')}")
        
        # Commit to git
        commit_message = f"Add {len(new_jobs)} new job(s) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        commit_to_git(commit_message)
    else:
        print("No new jobs found.")
    
    print("Scraper completed successfully.\n")


if __name__ == "__main__":
    main()
