# ✅ Cloud Setup Complete!

## What Was Configured

✅ **GitHub Actions workflow** - Runs in the cloud (no computer needed)
✅ **PST/PDT timezone** - Automatically handles Pacific Time
✅ **30-minute interval** - Checks for new jobs every 30 minutes
✅ **Business hours** - Monday-Friday, 8:30 AM - 5:00 PM Pacific Time
✅ **Auto-commit & push** - Automatically commits and pushes new jobs to GitHub

## Schedule

- **Days**: Monday through Friday
- **Time**: 8:30 AM - 5:00 PM Pacific Time (PST/PDT)
- **Interval**: Every 30 minutes
- **Runs**: Automatically on GitHub's servers

## Next Steps

### 1. Enable GitHub Actions (If Not Already Enabled)

1. Go to: https://github.com/yugal82/msft-jobs
2. Click **Settings** → **Actions** → **General**
3. Under "Workflow permissions", select:
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**
4. Click **Save**

### 2. Verify Workflow is Active

1. Go to: https://github.com/yugal82/msft-jobs/actions
2. You should see "Microsoft Job Scraper" workflow
3. It will run automatically on schedule
4. You can also click "Run workflow" to test manually

### 3. Monitor the Scraper

- **View runs**: https://github.com/yugal82/msft-jobs/actions
- **View commits**: New jobs will appear as commits
- **View jobs.json**: Check the file in your repository

## How It Works

1. **GitHub Actions** triggers the workflow every 30 minutes during business hours
2. **Checks timezone** - Verifies it's business hours in Pacific Time
3. **Runs scraper** - Fetches jobs from Microsoft Careers API
4. **Detects new jobs** - Compares with previously tracked jobs
5. **Commits & pushes** - Automatically commits new jobs and pushes to GitHub

## Timezone Handling

The workflow automatically handles:
- **PST (Pacific Standard Time)** - UTC-8
- **PDT (Pacific Daylight Time)** - UTC-7
- Automatically switches between them based on DST

## Testing

To test the workflow manually:

1. Go to: https://github.com/yugal82/msft-jobs/actions
2. Click "Microsoft Job Scraper"
3. Click "Run workflow" → "Run workflow"
4. Watch it execute in real-time

## Troubleshooting

### Workflow Not Running
- Check Actions tab for errors
- Verify Actions are enabled in Settings
- Check workflow file syntax

### Timezone Issues
- The workflow uses Pacific Time automatically
- Check logs to see actual execution times
- Adjust cron schedule if needed (in UTC)

### No Jobs Found
- This is normal if no new jobs are posted
- Check the logs to see API responses
- Verify API endpoint is accessible

## Status

🎉 **Everything is configured and pushed to GitHub!**

The scraper will now run automatically:
- ✅ No computer needed
- ✅ Runs in the cloud
- ✅ PST/PDT timezone configured
- ✅ 30-minute interval
- ✅ Business hours only (Mon-Fri, 8:30 AM - 5:00 PM)

## View Your Scraper

- **Repository**: https://github.com/yugal82/msft-jobs
- **Actions**: https://github.com/yugal82/msft-jobs/actions
- **Jobs File**: https://github.com/yugal82/msft-jobs/blob/main/jobs.json

Your scraper is now running in the cloud! 🚀
