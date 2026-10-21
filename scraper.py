#!/usr/bin/env python3
"""
Microsoft Careers Job Scraper
Fetches job listings from Microsoft Careers API and tracks new openings.
"""

import html
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration
SEARCH_URL = "https://apply.careers.microsoft.com/api/pcsx/search"
SEARCH_PARAMS = {
    'domain': 'microsoft.com',
    'query': 'Software Engineer',
    'location': 'United States',
    'sort_by': 'timestamp',
    'filter_include_remote': 1,
    'filter_seniority': 'Entry',
}
# Unlike the pcsx details endpoint, this one still serves postings after they close.
JOB_DETAILS_URL = "https://apply.careers.microsoft.com/api/apply/v2/jobs/{job_id}"
JOBS_FILE = "jobs.json"
TRACKED_IDS_FILE = "tracked_job_ids.json"
DATA_DIR = Path(__file__).parent

MAX_PAGES = 5  # Safety cap on search pages fetched per run
MAX_LEVEL_LOOKUPS = 20  # Job description fetches per run; the rest wait for the next run
REQUEST_DELAY_SECONDS = 1.5  # Pause between API calls to avoid 429s

# The level sits in the pay transparency sentence of the description, e.g.
# "Software Engineering IC2 - The typical base pay range for this role ..."
LEVEL_PATTERN = re.compile(r'(\S+)\s*[-–—]\s*The (?:typical )?base pay range', re.IGNORECASE)
INTERNSHIP_PATTERN = re.compile(r'base pay range for this internship', re.IGNORECASE)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


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


def create_session() -> requests.Session:
    """Create an HTTP session that backs off and retries on rate limits and server errors."""
    retry = Retry(
        total=5,
        backoff_factor=15,  # Waits 0s, 30s, 60s, 120s, 120s between attempts
        backoff_jitter=10,  # Plus up to 10s random, so retries don't land in lockstep
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=('GET',),
        respect_retry_after_header=True,
        raise_on_status=False,  # Return the last response so callers can tell a 429 from other errors
    )
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=retry))
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    })
    return session


def fetch_jobs(session: requests.Session, tracked_ids: Set[int]) -> List[Dict]:
    """Fetch search results, paging until a page contains no unseen jobs."""
    positions = []
    start = 0
    for page in range(MAX_PAGES):
        if page > 0:
            time.sleep(REQUEST_DELAY_SECONDS)
        try:
            response = session.get(SEARCH_URL, params={**SEARCH_PARAMS, 'start': start}, timeout=30)
            if response.status_code == 429:
                if positions:
                    print("Rate limited while paging; continuing with the pages fetched so far.")
                    break
                # Still throttled after every retry. Nothing is lost by skipping: the
                # same jobs are still listed when the next run comes around.
                print("::warning::Microsoft Careers API is rate limiting (HTTP 429). Skipping this run.")
                sys.exit(0)
            response.raise_for_status()
            data = response.json().get('data', {})
        except requests.RequestException as e:
            print(f"Error fetching jobs: {e}")
            sys.exit(1)

        page_positions = data.get('positions', [])
        positions.extend(page_positions)
        start += len(page_positions)

        # Results are sorted newest first, so a fully seen page means nothing new lies beyond it
        has_unseen = any(p.get('id') not in tracked_ids for p in page_positions)
        if not page_positions or not has_unseen or start >= data.get('count', 0):
            break

    return positions


def extract_level(description_html: str) -> Optional[str]:
    """Extract the job level (e.g. "IC2", or "IC3/IC4" for multi-level postings) from a job description."""
    text = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', description_html)))
    levels = list(dict.fromkeys(LEVEL_PATTERN.findall(text)))
    if levels:
        return '/'.join(levels)
    if INTERNSHIP_PATTERN.search(text):
        return 'Intern'
    return None


def fetch_job_level(session: requests.Session, job_id: int) -> Optional[str]:
    """Fetch a job's description and return its level. Raises RequestException on transient failures."""
    response = session.get(JOB_DETAILS_URL.format(job_id=job_id), params={'domain': 'microsoft.com'}, timeout=30)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return extract_level(response.json().get('job_description') or '')


def fill_missing_levels(session: requests.Session, jobs: List[Dict]) -> int:
    """Set the 'level' field on jobs that don't have one yet, newest first. Returns the number updated."""
    pending = [job for job in reversed(jobs) if 'level' not in job][:MAX_LEVEL_LOOKUPS]
    updated = 0
    for i, job in enumerate(pending):
        if i > 0:
            time.sleep(REQUEST_DELAY_SECONDS)
        try:
            job['level'] = fetch_job_level(session, job['id'])
            updated += 1
        except requests.RequestException as e:
            # Leave 'level' unset so the next run retries this job
            print(f"Error fetching level for job {job['id']}: {e}")
            break
    return updated


def get_tracked_job_ids() -> Set[int]:
    """Load set of previously tracked job IDs."""
    tracked_file = DATA_DIR / TRACKED_IDS_FILE
    data = load_json_file(tracked_file)
    return set(data.get('job_ids', []))


def save_tracked_job_ids(job_ids: Set[int]) -> None:
    """Save tracked job IDs to file."""
    tracked_file = DATA_DIR / TRACKED_IDS_FILE
    data = {'job_ids': list(job_ids), 'last_updated': utc_now().isoformat(timespec='seconds')}
    save_json_file(tracked_file, data)


def get_new_jobs(positions: List[Dict], tracked_ids: Set[int]) -> List[Dict]:
    """Extract new jobs that haven't been tracked before."""
    new_jobs = []
    seen = set(tracked_ids)

    for position in positions:
        job_id = position.get('id')
        if job_id and job_id not in seen:
            new_jobs.append(position)
            seen.add(job_id)

    return new_jobs


def save_jobs_file(all_jobs: Dict) -> None:
    """Write the jobs file with refreshed metadata."""
    all_jobs['last_updated'] = utc_now().isoformat(timespec='seconds')
    all_jobs['total_jobs'] = len(all_jobs['jobs'])
    save_json_file(DATA_DIR / JOBS_FILE, all_jobs)


def commit_to_git(message: str) -> bool:
    """Commit the data files. Returns False if there was nothing to commit; raises CalledProcessError on failure."""
    subprocess.run(['git', 'add', JOBS_FILE, TRACKED_IDS_FILE], cwd=DATA_DIR, check=True)

    # Check if there are changes to commit
    result = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=DATA_DIR)
    if result.returncode == 0:
        print("No changes to commit.")
        return False

    subprocess.run(['git', 'commit', '-m', message], cwd=DATA_DIR, check=True)
    print(f"Successfully committed: {message}")
    return True


def push_to_github(branch: str = 'main') -> None:
    """Rebase onto the remote branch and push. Raises CalledProcessError on failure."""
    result = subprocess.run(['git', 'remote'], cwd=DATA_DIR, capture_output=True, text=True)
    if 'origin' not in result.stdout.split():
        print("No 'origin' remote configured. Skipping push.")
        return

    # Another runner (cloud or local) may have pushed since we last pulled
    env = {**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
    pull = subprocess.run(['git', 'pull', '--rebase', 'origin', branch], cwd=DATA_DIR, env=env)
    if pull.returncode != 0:
        subprocess.run(['git', 'rebase', '--abort'], cwd=DATA_DIR)
        raise subprocess.CalledProcessError(pull.returncode, pull.args)

    subprocess.run(['git', 'push', 'origin', f'HEAD:{branch}'], cwd=DATA_DIR, check=True, env=env)
    print(f"Successfully pushed to GitHub: {branch}")


def main():
    """Main scraper function."""
    print(f"[{utc_now().strftime('%Y-%m-%d %H:%M:%S UTC')}] Starting job scraper...")
    session = create_session()

    # Get tracked job IDs
    tracked_ids = get_tracked_job_ids()
    print(f"Currently tracking {len(tracked_ids)} job IDs")

    # Fetch jobs from API
    print("Fetching jobs from API...")
    positions = fetch_jobs(session, tracked_ids)

    # Find new jobs
    new_jobs = get_new_jobs(positions, tracked_ids)
    print(f"Found {len(new_jobs)} new job(s)")

    all_jobs = load_json_file(DATA_DIR / JOBS_FILE)
    all_jobs.setdefault('jobs', [])

    discovered_at = utc_now().isoformat(timespec='seconds')
    new_entries = [{**job, 'discovered_at': discovered_at} for job in new_jobs]
    all_jobs['jobs'].extend(new_entries)

    # Levels come from each job's description, which takes an extra request per job
    levels_filled = fill_missing_levels(session, all_jobs['jobs'])
    if levels_filled:
        print(f"Filled in level for {levels_filled} job(s)")

    if not new_jobs and not levels_filled:
        print("No new jobs found.")
        print("Scraper completed successfully.\n")
        return

    if new_jobs:
        tracked_ids.update(job['id'] for job in new_jobs)
        save_tracked_job_ids(tracked_ids)
    save_jobs_file(all_jobs)

    if new_jobs:
        print("\nNew jobs discovered:")
        for job in new_entries:
            print(f"  - {job.get('name', 'N/A')} (ID: {job.get('id')})")
            print(f"    Level: {job.get('level') or 'unknown'}")
            print(f"    Locations: {', '.join(job.get('locations', []))}")
            print(f"    URL: https://apply.careers.microsoft.com{job.get('positionUrl', '')}")

    timestamp = utc_now().strftime('%Y-%m-%d %H:%M:%S UTC')
    if new_jobs:
        commit_message = f"Add {len(new_jobs)} new job(s) - {timestamp}"
    else:
        commit_message = f"Update levels for {levels_filled} job(s) - {timestamp}"

    try:
        if commit_to_git(commit_message):
            push_to_github()
    except FileNotFoundError:
        print("Git is not installed. Skipping git commit.")
    except subprocess.CalledProcessError as e:
        print(f"Error updating GitHub: {e}")
        sys.exit(1)

    print("Scraper completed successfully.\n")


if __name__ == "__main__":
    main()
