# Microsoft Job Scraper

A Python-based job scraper that monitors Microsoft Careers for new Software Engineer positions (Entry Level) and automatically commits and pushes them to a GitHub repository.

## Features

- 🔍 Fetches job listings from Microsoft Careers API every 30 minutes
- 📝 Tracks new job openings and saves them to `jobs.json`
- 🏷️ Records each job's level (IC2, IC3, ...) by reading it from the job description
- 🔄 Automatically commits new jobs to git repository
- 🚀 Automatically pushes to GitHub repository
- ☁️ Runs in the cloud via GitHub Actions (no local machine required)
- ⏰ Business hours only: Monday–Friday, 8:30 AM – 5:00 PM Pacific Time (PST/PDT)
- 📊 Maintains a history of all discovered jobs

## Quick Setup (Cloud – Recommended)

### 1. Install Dependencies (for local testing)

```bash
pip install -r requirements.txt
```

### 2. Configure GitHub Repository

Run the setup script to configure your GitHub remote:

```bash
./setup_github.sh
```

This will:
- Initialize git repository (if needed)
- Set up GitHub remote
- Configure git user credentials

**Important:** Ensure you have push access to the repository. For HTTPS authentication, you may need to use a [Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) instead of a password.

### 3. Enable and Verify GitHub Actions (Cloud Execution)

1. Push this repository to GitHub (already configured for `origin`).
2. In the GitHub UI, go to **Settings → Actions → General**:
   - Set **Workflow permissions** to **Read and write permissions**.
3. Go to the **Actions** tab and ensure the **Microsoft Job Scraper** workflow is visible.
4. Optionally click **Run workflow** to trigger a manual run.

The workflow file lives at `.github/workflows/scraper.yml` and will:
- Run on GitHub-hosted runners
- Use Pacific Time (PST/PDT) to determine business hours
- Trigger the scraper every 30 minutes during Mon–Fri, 8:30 AM–5:00 PM PT

### 4. Test the Scraper Locally (Optional)

Run manually to test:

```bash
python3 scraper.py
```

This will fetch jobs, commit them, and push to GitHub (using your local git credentials).

## Local Background Service (Optional, macOS)

To run the scraper during business hours in the background:

```bash
./install_service.sh
```

This installs a macOS launchd service that:
- Runs automatically on system startup
- Keeps running continuously (restarts if it crashes)
- Checks for new jobs every 30 minutes during business hours
- Schedule: Monday–Friday, 8:30 AM – 5:00 PM (local machine time)
- Automatically commits and pushes to GitHub

**Service Management:**
- Check status: `./install_service.sh status`
- Uninstall: `./install_service.sh uninstall`
- View logs: `tail -f scraper.log`

## Alternative Setup Options

### Option A: Python Scheduler (Manual)

Run the scheduler manually (keeps running until stopped):

```bash
python3 scheduler.py
```

Press `Ctrl+C` to stop.

### Option B: Cron Job (Traditional)

1. Make the script executable:
```bash
chmod +x scraper.py
```

2. Open crontab:
```bash
crontab -e
```

3. Add the following lines (every 30 minutes, Mon–Fri, 8:30 AM – 5:00 PM):
```bash
30 8-16 * * 1-5 cd /Users/yugalkhanter/Desktop/Yugal\ Work/Projects/Microsoft\ Job\ Scraper && /usr/bin/python3 scraper.py >> scraper.log 2>&1
0 9-17  * * 1-5 cd /Users/yugalkhanter/Desktop/Yugal\ Work/Projects/Microsoft\ Job\ Scraper && /usr/bin/python3 scraper.py >> scraper.log 2>&1
```

**Note:** Replace the path with your actual project path and ensure the Python path is correct (use `which python3` to find it).

**Limitation:** Cron jobs may not run if your computer is asleep. For a local, always-on setup, use the launchd service above. For truly machine-independent execution, use the GitHub Actions workflow (cloud).

## Files

- `scraper.py` - Main scraper script
- `scheduler.py` - Python scheduler for continuous operation
- `jobs.json` - All discovered jobs (tracked in git)
- `tracked_job_ids.json` - Every job ID ever seen (tracked in git so cloud runs remember it; clearing `jobs.json` doesn't re-add old jobs)
- `scraper.log` - Service logs
- `com.microsoft.jobscraper.plist` - macOS launchd service configuration
- `install_service.sh` - Service installation script
- `setup_github.sh` - GitHub repository setup script

## Configuration

### Modify API Endpoint

Edit the search parameters in `scraper.py`:

```python
SEARCH_PARAMS = {
    'domain': 'microsoft.com',
    'query': 'Software Engineer',
    'location': 'United States',
    'sort_by': 'timestamp',
    'filter_include_remote': 1,
    'filter_seniority': 'Entry',
}
```

Change these to search for different roles or locations:
- `query` - Job title to search for
- `location` - Location filter
- `filter_seniority` - Experience level (Entry, Mid-Level, Senior, etc.)
- `filter_include_remote` - Include remote jobs (1) or not (0)

### Change Scraping Interval

Edit `scheduler.py`:

```python
INTERVAL_MINUTES = 30  # Change to desired interval
```

## How It Works

1. The scraper fetches jobs from the Microsoft Careers API, paging until it reaches jobs it has already seen
2. It compares job IDs with previously tracked IDs
3. New jobs are added to `jobs.json` with a discovery timestamp (UTC)
4. For each job without a `level`, it fetches the job description and extracts the level (see below)
5. `jobs.json` and `tracked_job_ids.json` are committed, rebased onto the latest remote, and pushed to GitHub
6. The process repeats every 30 minutes during business hours (Monday-Friday, 8:30 AM - 5:00 PM)

Requests back off and retry automatically when the API rate-limits (HTTP 429). If fetching still fails, or a push fails, the run exits with an error so the failure shows up in the Actions tab.

## Job Level

The search API doesn't return a job's level, so the scraper reads it from the pay transparency sentence in each job description, e.g. *"Software Engineering **IC2** - The typical base pay range for this role across the U.S. is ..."*.

| `level` value | Meaning |
|---|---|
| `"IC2"`, `"IC3"`, ... | Single-level posting |
| `"IC3/IC4"` | Posting open at several levels |
| other codes, e.g. `"ATR-B/ATR-C"` | Non-IC pay scales (e.g. hourly datacenter roles) |
| `"Intern"` | Internship postings |
| `null` | Description has no level, or the posting no longer exists |
| *(field missing)* | Not looked up yet; filled in on a later run |

To stay under the API's rate limit, each run looks up at most 20 levels (`MAX_LEVEL_LOOKUPS`), newest jobs first, so a large backlog is filled in over a few runs.

### Example entry

```json
{
  "id": 1970393557026652,
  "displayJobId": "200060544",
  "name": "Software Engineer",
  "locations": ["United States, Washington, Redmond"],
  "department": "Software Engineering",
  "postedTs": 1792043010,
  "positionUrl": "/careers/job/1970393557026652",
  "discovered_at": "2026-10-15T19:19:24+00:00",
  "level": "IC2"
}
```

## GitHub Authentication

### HTTPS with Personal Access Token (Recommended)

1. Create a [Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with `repo` scope
2. When prompted for password, use the token instead
3. Or configure git credential helper:
```bash
git config --global credential.helper osxkeychain
```

### SSH (Alternative)

1. Set up SSH keys with GitHub
2. Change remote URL to SSH:
```bash
git remote set-url origin git@github.com:username/repo.git
```

## Troubleshooting

### Git Push Fails

- **Authentication failed**: Ensure you have push access and correct credentials
- **Permission denied**: Check repository permissions and authentication method
- **No remote configured**: Run `./setup_github.sh` to configure

### Service Not Running

- Check status: `./install_service.sh status`
- View logs: `tail -f scraper.log`
- Reinstall: `./install_service.sh uninstall` then `./install_service.sh`

### API Errors

- Check your internet connection
- Verify the API endpoint is accessible
- Check if Microsoft Careers API structure has changed

### Python Path Issues

- Find Python path: `which python3`
- Update paths in `com.microsoft.jobscraper.plist` if needed
- Reinstall service after path changes

## Monitoring

- **View recent logs**: `tail -f scraper.log`
- **View errors**: `tail -f scraper.error.log`
- **Check service status**: `./install_service.sh status`
- **View git history**: `git log --oneline`

## License

MIT
