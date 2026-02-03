#!/bin/sh
# This script sets up cron to run the db sync nightly

# Setup cron job to run at 10am UTC every day
echo "0 10 * * * cd /app && python3 app/sync/sync.py >> /app/data/cron.log 2>&1" > /etc/cron.d/xp_sync_cron

# Give execution rights
chmod 0644 /etc/cron.d/xp_sync_cron

# Apply cron job
crontab /etc/cron.d/xp_sync_cron

# Start cron
cron -f