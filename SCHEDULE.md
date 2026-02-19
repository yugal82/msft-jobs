# Schedule Configuration

## Business Hours Schedule

The scraper runs during the following hours:

- **Days**: Monday through Friday (excluding weekends)
- **Time**: 8:30 AM - 5:00 PM
- **Interval**: Every 15 minutes

## How It Works

The scheduler (`scheduler.py`) continuously runs and checks:
1. If it's a weekday (Monday-Friday)
2. If the current time is between 8:30 AM and 5:00 PM
3. Only runs the scraper if both conditions are met

## Schedule Details

- **First run of day**: 8:30 AM
- **Last run of day**: 4:45 PM (15 minutes before 5:00 PM)
- **Weekends**: Completely skipped (Saturday & Sunday)
- **After hours**: Waits until next business day at 8:30 AM

## Modifying the Schedule

To change the business hours, edit `scheduler.py`:

```python
BUSINESS_START_HOUR = 8      # Start hour (24-hour format)
BUSINESS_START_MINUTE = 30   # Start minute
BUSINESS_END_HOUR = 17       # End hour (5:00 PM = 17)
BUSINESS_END_MINUTE = 0      # End minute
```

To change the interval between checks:

```python
INTERVAL_MINUTES = 15  # Change to desired interval
```

## Testing

Test the schedule logic:

```bash
python3 -c "from scheduler import is_business_hours; print(is_business_hours())"
```

## Service Behavior

When installed as a macOS launchd service:
- The service runs continuously (24x7)
- The scheduler checks every 15 minutes
- Only executes scraper during business hours
- Automatically skips weekends and after-hours

This means the service stays running but only performs actual scraping during business hours.
