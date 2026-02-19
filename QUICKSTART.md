# Quick Start Guide - Business Hours Operation

## ✅ Current Status

Your scraper is ready! Here's what's configured:

- ✅ GitHub remote: `https://github.com/yugal82/msft-jobs.git`
- ✅ Git repository initialized
- ✅ Scraper tested and working
- ✅ Automatic push to GitHub enabled
- ✅ Business hours schedule: Monday-Friday, 8:30 AM - 5:00 PM

## 🚀 Start Business Hours Operation

### Step 1: Install the Background Service

```bash
cd "/Users/yugalkhanter/Desktop/Yugal Work/Projects/Microsoft Job Scraper"
./install_service.sh
```

This will:
- Install a macOS launchd service
- Start running automatically
- Keep running continuously (even after restart)
- Check for new jobs every 15 minutes during business hours
- Schedule: Monday-Friday, 8:30 AM - 5:00 PM
- Automatically commit and push to GitHub

### Step 2: Verify It's Running

```bash
./install_service.sh status
```

### Step 3: Monitor Logs

```bash
tail -f scraper.log
```

## 📋 What Happens Automatically

During business hours (Monday-Friday, 8:30 AM - 5:00 PM), every 15 minutes the scraper will:

1. ✅ Fetch jobs from Microsoft Careers API
2. ✅ Detect new job openings
3. ✅ Save them to `jobs.json`
4. ✅ Commit changes to git
5. ✅ Push to GitHub automatically

Outside business hours and on weekends, the scraper will wait until the next business day.

## 🔧 Service Management

- **Check status**: `./install_service.sh status`
- **View logs**: `tail -f scraper.log`
- **View errors**: `tail -f scraper.error.log`
- **Uninstall**: `./install_service.sh uninstall`

## 🔐 GitHub Authentication

If push fails due to authentication:

1. **For HTTPS**: Use a Personal Access Token
   - Create token: https://github.com/settings/tokens
   - Use token as password when prompted
   - Or configure: `git config --global credential.helper osxkeychain`

2. **For SSH**: Switch remote to SSH
   ```bash
   git remote set-url origin git@github.com:yugal82/msft-jobs.git
   ```

## 🧪 Test Manually

To test the scraper manually (including push):

```bash
python3 scraper.py
```

## 📊 View Results

- **Local jobs file**: `cat jobs.json`
- **Git history**: `git log --oneline`
- **GitHub**: Visit https://github.com/yugal82/msft-jobs

## ⚠️ Important Notes

1. **Computer must be on**: The service runs on your Mac during business hours. For cloud-based operation, consider GitHub Actions.

2. **Business hours**: The scraper only runs Monday-Friday, 8:30 AM - 5:00 PM. It will automatically skip weekends and after-hours.

3. **Sleep mode**: macOS launchd services continue running even when the computer sleeps (if configured), but network requests require the computer to be awake.

3. **First push**: You may need to push manually once:
   ```bash
   git push -u origin main
   ```

4. **Authentication**: Ensure GitHub credentials are configured for automatic pushes.

## 🎉 You're All Set!

The scraper will now run automatically and push new jobs to your GitHub repository!
