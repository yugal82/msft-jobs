# Microsoft Job Scraper

A Python-based job scraper that monitors Microsoft Careers for new Software Engineer positions (Entry Level) and automatically commits and pushes them to a GitHub repository.

## Features

- 🔍 Fetches job listings from Microsoft Careers API every 15 minutes
- 📝 Tracks new job openings and saves them to `jobs.json`
- 🔄 Automatically commits new jobs to git repository
- 🚀 Automatically pushes to GitHub repository
- ⏰ Runs during business hours: Monday-Friday, 8:30 AM - 5:00 PM
- 📊 Maintains a history of all discovered jobs

## Quick Setup (Business Hours Operation)

### 1. Install Dependencies

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

### 3. Test the Scraper

Run manually to test:

```bash
python3 scraper.py
```

This will fetch jobs, commit them, and push to GitHub.

### 4. Install Background Service (macOS)

To run the scraper during business hours in the background:

```bash
./install_service.sh
```

This installs a macOS launchd service that:
- Runs automatically on system startup
- Keeps running continuously (restarts if it crashes)
- Checks for new jobs every 15 minutes during business hours
- Schedule: Monday-Friday, 8:30 AM - 5:00 PM
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

3. Add the following line:
```bash
*/15 * * * * cd /Users/yugalkhanter/Desktop/Yugal\ Work/Projects/Microsoft\ Job\ Scraper && /usr/bin/python3 scraper.py >> scraper.log 2>&1
```

**Note:** Replace the path with your actual project path and ensure the Python path is correct (use `which python3` to find it).

**Limitation:** Cron jobs may not run if your computer is asleep. Use the launchd service for reliable background operation.

### Option C: GitHub Actions (Cloud-based)

For true 24x7 operation without keeping your computer on, you can use GitHub Actions. See `github-actions.yml` example (if provided).

## Files

- `scraper.py` - Main scraper script
- `scheduler.py` - Python scheduler for continuous operation
- `jobs.json` - All discovered jobs (tracked in git)
- `tracked_job_ids.json` - List of job IDs that have been seen (not tracked in git)
- `scraper.log` - Service logs
- `com.microsoft.jobscraper.plist` - macOS launchd service configuration
- `install_service.sh` - Service installation script
- `setup_github.sh` - GitHub repository setup script

## Configuration

### Modify API Endpoint

Edit the API URL in `scraper.py`:

```python
API_URL = "https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=Software%20Engineer&location=United%20States&start=0&sort_by=timestamp&filter_include_remote=1&filter_seniority=Entry"
```

Change the query parameters to search for different roles or locations:
- `query` - Job title to search for
- `location` - Location filter
- `filter_seniority` - Experience level (Entry, Mid-Level, Senior, etc.)
- `filter_include_remote` - Include remote jobs (1) or not (0)

### Change Scraping Interval

Edit `scheduler.py`:

```python
INTERVAL_MINUTES = 15  # Change to desired interval
```

## How It Works

1. The scraper fetches jobs from the Microsoft Careers API
2. It compares new job IDs with previously tracked IDs
3. New jobs are added to `jobs.json` with a discovery timestamp
4. Changes are automatically committed to git with a descriptive message
5. Commits are automatically pushed to GitHub
6. The process repeats every 15 minutes during business hours (Monday-Friday, 8:30 AM - 5:00 PM)

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
