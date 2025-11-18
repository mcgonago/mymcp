# DevStack Disk Cleanup Automation

**Purpose**: Prevent DevStack VM from filling up disk space (recurring issue with logs)

**Status**: ✅ Implemented on `192.168.122.140` (stack@laptopserver2)

---

## Quick Summary

**What was done:**
1. Created automatic cleanup script: `/usr/local/bin/devstack-cleanup.sh`
2. Configured permanent log size limits (journal, syslog)
3. Scheduled daily cron job (runs at 2 AM)

**Result**: Disk space automatically maintained, won't hit 100% anymore

---

## The Problem

DevStack VMs accumulate logs quickly from OpenStack services:
- **Systemd journal logs**: Can grow to 1-2GB
- **Syslog**: Can grow to 600MB+
- **Service logs**: Nova, Neutron, Keystone, etc. all log continuously

Without cleanup, disk reaches 100%, causing:
- ❌ Apache/Horizon fails to start
- ❌ OpenStack services fail
- ❌ Can't log in or run commands

---

## Solution Components

### 1. Cleanup Script

**Location**: `/usr/local/bin/devstack-cleanup.sh`

**What it does:**
- Vacuums journal logs (keeps last 200MB)
- Deletes old compressed logs (older than 7 days)
- Deletes old rotated logs (older than 14 days)
- Truncates syslog if over 200MB
- Cleans apt cache
- Removes old DevStack logs (older than 30 days)
- Logs all actions to `/var/log/devstack-cleanup.log`
- Alerts if disk still over 90%

**Script contents:**
```bash
#!/bin/bash
# DevStack Disk Cleanup Script
# Runs automatically to prevent disk from filling up

LOG_FILE=/var/log/devstack-cleanup.log
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Starting DevStack cleanup" >> $LOG_FILE

# Check disk usage before cleanup
BEFORE=$(df -h / | grep -v Filesystem | awk '{print $5}')
echo "[$DATE] Disk usage before: $BEFORE" >> $LOG_FILE

# Clean journal logs (keep last 200MB)
echo "[$DATE] Cleaning journal logs..." >> $LOG_FILE
sudo journalctl --vacuum-size=200M >> $LOG_FILE 2>&1

# Clean old compressed logs (older than 7 days)
echo "[$DATE] Cleaning old compressed logs..." >> $LOG_FILE
sudo find /var/log -name '*.gz' -mtime +7 -delete 2>> $LOG_FILE

# Clean old log files (older than 14 days)
echo "[$DATE] Cleaning old .log.1, .log.2, etc files..." >> $LOG_FILE
sudo find /var/log -name '*.log.[0-9]*' -mtime +14 -delete 2>> $LOG_FILE

# Truncate large syslog if over 200MB
SYSLOG_SIZE=$(du -m /var/log/syslog 2>/dev/null | cut -f1)
if [ "$SYSLOG_SIZE" -gt 200 ]; then
    echo "[$DATE] Truncating large syslog (${SYSLOG_SIZE}MB)..." >> $LOG_FILE
    sudo truncate -s 100M /var/log/syslog
fi

# Clean apt cache
echo "[$DATE] Cleaning apt cache..." >> $LOG_FILE
sudo apt-get clean >> $LOG_FILE 2>&1

# Clean old DevStack logs (keep last 30 days)
if [ -d /opt/stack/logs ]; then
    echo "[$DATE] Cleaning old DevStack logs..." >> $LOG_FILE
    find /opt/stack/logs -name '*.log' -mtime +30 -delete 2>> $LOG_FILE
fi

# Check disk usage after cleanup
AFTER=$(df -h / | grep -v Filesystem | awk '{print $5}')
echo "[$DATE] Disk usage after: $AFTER" >> $LOG_FILE

# Alert if disk still over 90%
USAGE=$(df / | grep -v Filesystem | awk '{print $5}' | sed 's/%//')
if [ "$USAGE" -gt 90 ]; then
    echo "[$DATE] WARNING: Disk usage still high: ${USAGE}%" >> $LOG_FILE
    echo "[$DATE] Manual intervention may be required" >> $LOG_FILE
fi

echo "[$DATE] Cleanup complete" >> $LOG_FILE
echo "----------------------------------------" >> $LOG_FILE
```

### 2. Permanent Log Size Limits

#### Journal Logs
**File**: `/etc/systemd/journald.conf.d/size-limit.conf`

```ini
[Journal]
SystemMaxUse=200M
RuntimeMaxUse=50M
```

**Effect**: Journal logs never exceed 200MB total

#### Syslog Rotation
**File**: `/etc/logrotate.d/rsyslog-devstack`

```
/var/log/syslog
{
    rotate 1
    daily
    maxsize 100M
    missingok
    notifempty
    compress
    delaycompress
    postrotate
        /usr/lib/rsyslog/rsyslog-rotate
    endscript
}
```

**Effect**: Syslog automatically rotates when it hits 100MB

### 3. Cron Job

**Schedule**: Daily at 2:00 AM

**Crontab entry**:
```
# DevStack disk cleanup - runs daily at 2 AM
0 2 * * * /usr/local/bin/devstack-cleanup.sh
```

**Why 2 AM**: Low usage time, won't interfere with development work

---

## Manual Installation Steps

If you need to set this up on another DevStack VM or re-install:

### Step 1: SSH to DevStack VM

```bash
ssh stack@192.168.122.140
# Password: 1xxxxx
```

### Step 2: Create the Cleanup Script

```bash
cat > /tmp/devstack-cleanup.sh << 'EOF'
#!/bin/bash
# DevStack Disk Cleanup Script
# Runs automatically to prevent disk from filling up

LOG_FILE=/var/log/devstack-cleanup.log
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Starting DevStack cleanup" >> $LOG_FILE

# Check disk usage before cleanup
BEFORE=$(df -h / | grep -v Filesystem | awk '{print $5}')
echo "[$DATE] Disk usage before: $BEFORE" >> $LOG_FILE

# Clean journal logs (keep last 200MB)
echo "[$DATE] Cleaning journal logs..." >> $LOG_FILE
sudo journalctl --vacuum-size=200M >> $LOG_FILE 2>&1

# Clean old compressed logs (older than 7 days)
echo "[$DATE] Cleaning old compressed logs..." >> $LOG_FILE
sudo find /var/log -name '*.gz' -mtime +7 -delete 2>> $LOG_FILE

# Clean old log files (older than 14 days)
echo "[$DATE] Cleaning old .log.1, .log.2, etc files..." >> $LOG_FILE
sudo find /var/log -name '*.log.[0-9]*' -mtime +14 -delete 2>> $LOG_FILE

# Truncate large syslog if over 200MB
SYSLOG_SIZE=$(du -m /var/log/syslog 2>/dev/null | cut -f1)
if [ "$SYSLOG_SIZE" -gt 200 ]; then
    echo "[$DATE] Truncating large syslog (${SYSLOG_SIZE}MB)..." >> $LOG_FILE
    sudo truncate -s 100M /var/log/syslog
fi

# Clean apt cache
echo "[$DATE] Cleaning apt cache..." >> $LOG_FILE
sudo apt-get clean >> $LOG_FILE 2>&1

# Clean old DevStack logs (keep last 30 days)
if [ -d /opt/stack/logs ]; then
    echo "[$DATE] Cleaning old DevStack logs..." >> $LOG_FILE
    find /opt/stack/logs -name '*.log' -mtime +30 -delete 2>> $LOG_FILE
fi

# Check disk usage after cleanup
AFTER=$(df -h / | grep -v Filesystem | awk '{print $5}')
echo "[$DATE] Disk usage after: $AFTER" >> $LOG_FILE

# Alert if disk still over 90%
USAGE=$(df / | grep -v Filesystem | awk '{print $5}' | sed 's/%//')
if [ "$USAGE" -gt 90 ]; then
    echo "[$DATE] WARNING: Disk usage still high: ${USAGE}%" >> $LOG_FILE
    echo "[$DATE] Manual intervention may be required" >> $LOG_FILE
fi

echo "[$DATE] Cleanup complete" >> $LOG_FILE
echo "----------------------------------------" >> $LOG_FILE
EOF

# Make executable and move to system location
chmod +x /tmp/devstack-cleanup.sh
sudo mv /tmp/devstack-cleanup.sh /usr/local/bin/
```

### Step 3: Set Up Journal Size Limit

```bash
sudo mkdir -p /etc/systemd/journald.conf.d/

sudo tee /etc/systemd/journald.conf.d/size-limit.conf > /dev/null << 'EOF'
[Journal]
SystemMaxUse=200M
RuntimeMaxUse=50M
EOF

sudo systemctl restart systemd-journald
```

### Step 4: Set Up Syslog Rotation

```bash
sudo tee /etc/logrotate.d/rsyslog-devstack > /dev/null << 'EOF'
/var/log/syslog
{
    rotate 1
    daily
    maxsize 100M
    missingok
    notifempty
    compress
    delaycompress
    postrotate
        /usr/lib/rsyslog/rsyslog-rotate
    endscript
}
EOF
```

### Step 5: Test the Cleanup Script

```bash
# Run manually to test
sudo /usr/local/bin/devstack-cleanup.sh

# Check the log
sudo tail -20 /var/log/devstack-cleanup.log

# Verify disk space freed
df -h /
```

### Step 6: Install Cron Job

```bash
# Add to root's crontab (needs sudo for cleaning)
(sudo crontab -l 2>/dev/null; echo '# DevStack disk cleanup - runs daily at 2 AM'; echo '0 2 * * * /usr/local/bin/devstack-cleanup.sh') | sudo crontab -

# Verify crontab
sudo crontab -l
```

---

## Verification and Monitoring

### Check if Cron Job is Installed

```bash
ssh stack@192.168.122.140 "sudo crontab -l"
```

**Expected output:**
```
# DevStack disk cleanup - runs daily at 2 AM
0 2 * * * /usr/local/bin/devstack-cleanup.sh
```

### Check Cleanup Logs

```bash
ssh stack@192.168.122.140 "sudo tail -50 /var/log/devstack-cleanup.log"
```

**Expected to see:**
- Daily entries with timestamps
- "Disk usage before" and "Disk usage after"
- Amount of space freed

### Check Current Disk Usage

```bash
ssh stack@192.168.122.140 "df -h /"
```

**Healthy range**: 70-90%
**Warning**: 90-95%
**Critical**: 95-100%

### Manually Run Cleanup (If Needed)

```bash
ssh stack@192.168.122.140 "sudo /usr/local/bin/devstack-cleanup.sh"
```

---

## Troubleshooting

### Disk Still Fills Up Despite Cron Job

**Check if cron is running:**
```bash
ssh stack@192.168.122.140 "sudo systemctl status cron"
```

**Check cleanup log:**
```bash
ssh stack@192.168.122.140 "sudo tail -100 /var/log/devstack-cleanup.log"
```

**Check for large files:**
```bash
ssh stack@192.168.122.140 "sudo du -h --max-depth=2 / 2>/dev/null | grep -E '^[0-9.]+G' | sort -h"
```

### Cron Job Not Running

**Verify crontab:**
```bash
ssh stack@192.168.122.140 "sudo crontab -l"
```

**Check cron logs:**
```bash
ssh stack@192.168.122.140 "sudo grep cleanup /var/log/syslog | tail -20"
```

**Manually test script:**
```bash
ssh stack@192.168.122.140 "sudo /usr/local/bin/devstack-cleanup.sh && sudo tail -20 /var/log/devstack-cleanup.log"
```

### Emergency Cleanup (Disk at 100%)

```bash
ssh stack@192.168.122.140 "
  sudo journalctl --vacuum-size=100M &&
  sudo truncate -s 50M /var/log/syslog &&
  sudo find /var/log -name '*.gz' -delete &&
  sudo find /var/log -name '*.1' -type f -delete &&
  df -h /
"
```

---

## Changing the Schedule

### Current Schedule: Daily at 2 AM

To change frequency or time, edit the crontab:

```bash
ssh stack@192.168.122.140
sudo crontab -e
```

**Cron format**: `minute hour day month weekday command`

**Examples:**

| Schedule | Cron Entry | Description |
|----------|------------|-------------|
| Daily at 2 AM | `0 2 * * *` | Current setting |
| Daily at 3 AM | `0 3 * * *` | Run at 3 AM instead |
| Twice daily | `0 2,14 * * *` | Run at 2 AM and 2 PM |
| Every 12 hours | `0 */12 * * *` | Run every 12 hours |
| Weekly (Sunday 2 AM) | `0 2 * * 0` | Run once per week |
| Every 6 hours | `0 */6 * * *` | Run 4 times per day |

### Recommended Schedules by Usage

**Light usage** (testing occasionally):
```
# Weekly cleanup - Sunday at 2 AM
0 2 * * 0 /usr/local/bin/devstack-cleanup.sh
```

**Medium usage** (daily development):
```
# Daily cleanup - 2 AM (CURRENT)
0 2 * * * /usr/local/bin/devstack-cleanup.sh
```

**Heavy usage** (continuous testing):
```
# Twice daily - 2 AM and 2 PM
0 2,14 * * * /usr/local/bin/devstack-cleanup.sh
```

---

## Customizing Cleanup Behavior

Edit the script to adjust retention periods:

```bash
ssh stack@192.168.122.140
sudo vim /usr/local/bin/devstack-cleanup.sh
```

**Adjustable parameters:**

| Parameter | Current Value | Line in Script | Description |
|-----------|---------------|----------------|-------------|
| Journal size limit | 200MB | `journalctl --vacuum-size=200M` | Max journal log size |
| Compressed log age | 7 days | `find ... -mtime +7` | Delete .gz older than this |
| Rotated log age | 14 days | `find ... -mtime +14` | Delete .1, .2, etc. older than this |
| Syslog size trigger | 200MB | `if [ "$SYSLOG_SIZE" -gt 200 ]` | When to truncate syslog |
| Syslog truncate size | 100MB | `truncate -s 100M` | Size after truncation |
| DevStack log age | 30 days | `find ... -mtime +30` | Delete old service logs |

**Example: More aggressive cleanup for small disk:**
```bash
# Change these lines in the script:
journalctl --vacuum-size=100M          # From 200M to 100M
find ... -mtime +3 -delete             # From +7 to +3 days
find ... -mtime +7 -delete             # From +14 to +7 days
if [ "$SYSLOG_SIZE" -gt 100 ]          # From 200 to 100 MB trigger
find ... -mtime +14 -delete            # From +30 to +14 days for DevStack logs
```

---

## Related Documentation

- **DevStack General Troubleshooting**: (Link to your other docs)
- **Horizon Development Setup**: (Link to workspace setup)
- **Review 966349 Development**: `analysis/analysis_new_feature_966349/`
- **Review 967269 (OSPRH-12802)**: `analysis/analysis_new_feature_osprh_12802/`

---

## History

| Date | Event | Result |
|------|-------|--------|
| 2025-11-18 | Initial disk full issue | Disk at 100%, Apache wouldn't start |
| 2025-11-18 | Manual cleanup performed | Freed 2.1GB (100% → 91%) |
| 2025-11-18 | Safeguards installed | Journal limit, syslog rotation configured |
| 2025-11-18 | Cron job created | Automatic daily cleanup at 2 AM |

---

## Quick Reference Commands

```bash
# Check disk usage
ssh stack@192.168.122.140 "df -h /"

# Check cleanup log
ssh stack@192.168.122.140 "sudo tail -50 /var/log/devstack-cleanup.log"

# Run cleanup manually
ssh stack@192.168.122.140 "sudo /usr/local/bin/devstack-cleanup.sh"

# Check cron job
ssh stack@192.168.122.140 "sudo crontab -l"

# Check Apache status
ssh stack@192.168.122.140 "sudo systemctl status apache2"

# Emergency cleanup (disk at 100%)
ssh stack@192.168.122.140 "sudo journalctl --vacuum-size=100M && df -h /"
```

---

**Last Updated**: 2025-11-18  
**Status**: ✅ Active and monitoring  
**Next Review**: Check logs after 1 week to verify cron is running

