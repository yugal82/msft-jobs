# Microsoft Job Scraper

A Python-based job scraper that monitors Microsoft Careers for new Software Engineer positions (Entry Level) and automatically commits them to a GitHub repository.

## Features

- 🔍 Fetches job listings from Microsoft Careers API every 15 minutes
- 📝 Tracks new job openings and saves them to `jobs.json`
- 🔄 Automatically commits new jobs to git repository
- 📊 Maintains a history of all discovered jobs

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Git Repository (if not already initialized)

```bash
git init
git remote add origin <your-github-repo-url>
```

### 3. Set Up Cron Job

#### Option A: Using crontab (macOS/Linux)

1. Make the script executable:
```bash
chmod +x scraper.py
```

2. Open crontab:
```bash
crontab -e
```

3. Add the following line to run every 15 minutes:
```bash
*/15 * * * * cd /Users/yugalkhanter/Desktop/Yugal\ Work/Projects/Microsoft\ Job\ Scraper && /usr/bin/python3 scraper.py >> scraper.log 2>&1
```

**Note:** Replace the path with your actual project path and ensure the Python path is correct (use `which python3` to find it).

#### Option B: Using Python scheduler (Alternative)

You can also run the scraper continuously using a Python scheduler:

```bash
python3 scheduler.py
```

This will run the scraper every 15 minutes automatically.

### 4. Test the Scraper

Run manually to test:
```bash
python3 scraper.py
```

## Files

- `scraper.py` - Main scraper script
- `jobs.json` - All discovered jobs (tracked in git)
- `tracked_job_ids.json` - List of job IDs that have been seen (not tracked in git)
- `scraper.log` - Cron job logs (if using crontab)

## Configuration

You can modify the API endpoint in `scraper.py`:

```python
API_URL = "https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=Software%20Engineer&location=United%20States&start=0&sort_by=timestamp&filter_include_remote=1&filter_seniority=Entry"
```

Change the query parameters to search for different roles or locations.

## How It Works

1. The scraper fetches jobs from the Microsoft Careers API
2. It compares new job IDs with previously tracked IDs
3. New jobs are added to `jobs.json` with a discovery timestamp
4. Changes are automatically committed to git with a descriptive message
5. The process repeats every 15 minutes via cron

## Troubleshooting

- **Git not committing**: Ensure git is initialized and you have write permissions
- **API errors**: Check your internet connection and API endpoint
- **Cron not running**: Verify the cron job is set up correctly with `crontab -l`
- **Python path issues**: Use `which python3` to find the correct Python path for cron

## License

MIT
