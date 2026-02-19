# GitHub Actions Setup (Cloud-Based)

## 🚀 Run Without Your Computer!

This setup runs the scraper **entirely on GitHub's servers**, so you don't need to keep your computer on.

## Benefits

- ✅ **No computer needed** - Runs in the cloud
- ✅ **Free** - GitHub Actions free tier: 2,000 minutes/month
- ✅ **Reliable** - Runs automatically, no system maintenance
- ✅ **Business hours** - Configured for Mon-Fri, 8:30 AM - 5:00 PM

## Setup Instructions

### Step 1: Push Workflow File to GitHub

The workflow file is already created at `.github/workflows/scraper.yml`. Just commit and push it:

```bash
git add .github/workflows/scraper.yml
git commit -m "Add GitHub Actions workflow"
git push
```

### Step 2: Configure Timezone

**IMPORTANT:** The workflow uses UTC timezone by default. You need to adjust the cron schedule and time checks based on your timezone.

**Edit `.github/workflows/scraper.yml`:**

1. **Find the cron schedules** (around line 10-12)
2. **Adjust for your timezone:**

   **For EST (UTC-5):**
   - 8:30 AM EST = 13:30 UTC
   - 5:00 PM EST = 22:00 UTC
   - Cron: `'30,45 13-16 * * 1-5'` and `'0,15,30,45 17-21 * * 1-5'`

   **For PST (UTC-8):**
   - 8:30 AM PST = 16:30 UTC
   - 5:00 PM PST = 01:00 UTC (next day)
   - Cron: `'30,45 16-23 * * 1-5'` and `'0,15,30,45 0 * * 2-6'`

3. **Update the time check script** (around line 40-50) to match your timezone

### Step 3: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click **Settings** → **Actions** → **General**
3. Ensure "Allow all actions and reusable workflows" is selected
4. Under "Workflow permissions", select "Read and write permissions"
5. Check "Allow GitHub Actions to create and approve pull requests"

### Step 4: Test the Workflow

1. Go to **Actions** tab in your GitHub repository
2. You should see "Microsoft Job Scraper" workflow
3. Click "Run workflow" to test manually
4. Or wait for the scheduled time

## How It Works

1. **GitHub Actions** runs the workflow on schedule
2. Checks if it's business hours (Mon-Fri, 8:30 AM - 5:00 PM)
3. Runs the scraper script
4. Commits and pushes new jobs automatically
5. No computer needed!

## Monitoring

- View runs: Go to **Actions** tab in your repository
- View logs: Click on any workflow run
- Check commits: New jobs will appear as commits in your repository

## Timezone Reference

Common US timezones:
- **EST (Eastern)**: UTC-5 (or UTC-4 during DST)
- **CST (Central)**: UTC-6 (or UTC-5 during DST)
- **MST (Mountain)**: UTC-7 (or UTC-6 during DST)
- **PST (Pacific)**: UTC-8 (or UTC-7 during DST)

## Limitations

- **Free tier**: 2,000 minutes/month (plenty for this use case)
- **Minimum interval**: GitHub Actions can run as frequently as every 5 minutes
- **Timezone**: Must configure cron schedule in UTC

## Troubleshooting

### Workflow not running
- Check Actions tab for errors
- Verify cron schedule syntax
- Ensure Actions are enabled in repository settings

### Timezone issues
- Double-check UTC conversion
- Test with manual trigger first
- Adjust cron schedule and time checks

### Authentication errors
- GitHub Actions automatically has write access
- No token setup needed (uses `GITHUB_TOKEN`)

## Disable Local Service

If you're using GitHub Actions, you can disable the local service:

```bash
./install_service.sh uninstall
```

Now your scraper runs entirely in the cloud! ☁️
