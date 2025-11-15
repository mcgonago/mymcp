# Debugging DevStack Keystone Authentication Timeout Issue

## Problem Summary

Horizon is unable to authenticate users against an OpenStack DevStack VM. The authentication request hangs indefinitely without receiving a response from Keystone.

## Symptoms

### Horizon Logs Show:
```
INFO django.server "GET /auth/login/ HTTP/1.1" 200 9187
DEBUG openstack_auth.backend Beginning user authentication
DEBUG openstack_auth.plugin.password Attempting to authenticate for admin
DEBUG keystoneauth.identity.v3.base Making authentication request to http://192.168.122.140/identity/v3/auth/tokens
DEBUG django.utils.autoreload File /usr/lib64/python3.13/netrc.py first seen with mtime 1744120448.0
```

**Note:** The log shows the authentication request being initiated, but there's no response (success or failure).

### User Behavior:
- Login page loads successfully
- After submitting credentials, the page hangs/spins indefinitely
- No error message is displayed

## Investigation Steps

### Step 1: Verify Network Connectivity

Test if the DevStack VM is reachable:

```bash
ping -c 3 192.168.122.140
```

**Expected Output:**
```
PING 192.168.122.140 (192.168.122.140) 56(84) bytes of data.
64 bytes from 192.168.122.140: icmp_seq=1 ttl=64 time=0.356 ms
64 bytes from 192.168.122.140: icmp_seq=2 ttl=64 time=0.231 ms
64 bytes from 192.168.122.140: icmp_seq=3 ttl=64 time=0.324 ms

--- 192.168.122.140 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2081ms
```

✅ **Result:** VM is reachable.

---

### Step 2: Verify Web Server is Running

Test if Apache/web server is responding:

```bash
timeout 5 curl -v http://192.168.122.140/
```

**Expected Output:**
```
< HTTP/1.1 302 Found
< Date: Fri, 07 Nov 2025 18:42:06 GMT
< Server: Apache/2.4.52 (Ubuntu)
< Location: http://192.168.122.140/dashboard/
```

✅ **Result:** Web server is running and responding.

---

### Step 3: Verify Keystone Endpoint is Accessible

Test if the Keystone identity endpoint is responding:

```bash
timeout 5 curl -v http://192.168.122.140/identity/
```

**Expected Output:**
```json
< HTTP/1.1 300 MULTIPLE CHOICES
< Server: Apache/2.4.52 (Ubuntu)
< Content-Type: application/json

{"versions": {"values": [{"id": "v3.14", "status": "stable", "updated": "2020-04-07T00:00:00Z", "links": [{"rel": "self", "href": "http://192.168.122.140/identity/v3/"}], "media-types": [{"base": "application/json", "type": "application/vnd.openstack.identity-v3+json"}]}]}}
```

✅ **Result:** Keystone endpoint is accessible and responding to version requests.

---

### Step 4: Test Authentication Endpoint (THE SMOKING GUN)

Test the actual authentication endpoint that Horizon is trying to use:

```bash
timeout 5 curl -v -X POST http://192.168.122.140/identity/v3/auth/tokens \
  -H "Content-Type: application/json" \
  -d '{
    "auth": {
      "identity": {
        "methods": ["password"],
        "password": {
          "user": {
            "name": "admin",
            "domain": {"name": "Default"},
            "password": "123456"
          }
        }
      },
      "scope": {
        "project": {
          "name": "admin",
          "domain": {"name": "Default"}
        }
      }
    }
  }'
```

**Actual Output:**
```
*   Trying 192.168.122.140:80...
* Connected to 192.168.122.140 (192.168.122.140) port 80
> POST /identity/v3/auth/tokens HTTP/1.1
> Host: 192.168.122.140
> Content-Type: application/json
> Content-Length: 196
> 
* upload completely sent off: 196 bytes
[HANGS FOR 5 SECONDS]
[EXIT CODE: 124 - TIMEOUT]
```

❌ **Result:** The authentication endpoint accepts the connection and receives the data, but **NEVER responds**.

## Root Cause Analysis

**Keystone is receiving authentication requests but not processing them.**

The issue is NOT with Horizon or network connectivity. The problem is on the DevStack VM:

1. ✅ Network is working
2. ✅ Web server (Apache) is working
3. ✅ Keystone version endpoint is working
4. ❌ **Keystone authentication is HANGING**

### Possible Causes:

1. **Keystone service crashed or stuck**
2. **Database connection issues** - Keystone can't reach MySQL/MariaDB
3. **Database is locked or corrupted**
4. **External auth backend timeout** (LDAP, AD, etc.)
5. **Resource exhaustion** (out of memory, disk full)
6. **Keystone worker processes are deadlocked**

## Solution: Debugging on the DevStack VM

### 1. SSH into DevStack VM

```bash
ssh stack@192.168.122.140
# or
ssh ubuntu@192.168.122.140
```

### 2. Check Keystone Service Status

For systemd-based deployments:

```bash
systemctl status devstack@keystone
systemctl status devstack@keystone-uwsgi
```

**Look for:**
- Active/Inactive status
- Recent errors in the service log
- "Failed to start" or "Exit code" messages

### 3. Check Keystone Logs

DevStack typically logs to several locations:

```bash
# Real-time logs:
sudo journalctl -u devstack@keystone -f --no-pager

# Or check log files directly:
tail -f /var/log/apache2/keystone.log
tail -f /var/log/apache2/keystone-access.log
tail -f /opt/stack/logs/keystone.log

# Check for errors:
grep -i error /opt/stack/logs/keystone.log | tail -20
grep -i exception /opt/stack/logs/keystone.log | tail -20
```

**Look for:**
- Database connection errors: `Lost connection to MySQL`, `Too many connections`
- Timeout errors
- Token provider issues
- Fernet key problems

### 4. Check Database Connectivity

Test if Keystone can connect to the database:

```bash
# Check if MySQL is running:
systemctl status mysql
# or
systemctl status mariadb

# Test database connection:
mysql -u root -p keystone -e "SELECT 1;"

# Check for locked tables or long-running queries:
mysql -u root -p -e "SHOW PROCESSLIST;"
```

**Common database issues:**
- MySQL not running
- Too many connections (check `max_connections`)
- Table locks
- Corrupted tables

### 5. Check System Resources

```bash
# Check memory usage:
free -h
# If swap is being heavily used, you may be out of memory

# Check disk space:
df -h
# Keystone needs space for logs and token storage

# Check if Keystone processes are running:
ps aux | grep keystone

# Check for zombie processes:
ps aux | grep Z
```

### 6. Check Keystone Configuration

```bash
# Check keystone configuration:
cat /etc/keystone/keystone.conf | grep -v '^#' | grep -v '^$'

# Verify token provider:
grep token_provider /etc/keystone/keystone.conf
# Should be: token_provider = fernet

# Check Fernet keys exist:
ls -la /etc/keystone/fernet-keys/
```

### 7. Restart Keystone Service

If you identify the issue, restart Keystone:

```bash
# For systemd:
sudo systemctl restart devstack@keystone

# Or restart all DevStack services:
cd /opt/stack/devstack
./unstack.sh
./stack.sh

# Quick rejoin (if screen session exists):
./rejoin-stack.sh
```

### 8. Test Authentication Again

After restarting, test from your host machine:

```bash
curl -X POST http://192.168.122.140/identity/v3/auth/tokens \
  -H "Content-Type: application/json" \
  -d '{
    "auth": {
      "identity": {
        "methods": ["password"],
        "password": {
          "user": {
            "name": "admin",
            "domain": {"name": "Default"},
            "password": "YOUR_PASSWORD"
          }
        }
      }
    }
  }'
```

**Expected successful response:**
```
HTTP/1.1 201 Created
X-Subject-Token: gAAAAABl...
Content-Type: application/json

{"token": {...}}
```

## Additional Troubleshooting

### Enable More Verbose Logging in Keystone

Edit `/etc/keystone/keystone.conf`:

```ini
[DEFAULT]
debug = True
verbose = True
```

Then restart Keystone.

### Check Apache/uWSGI Configuration

If Keystone is running behind Apache with uWSGI:

```bash
# Check Apache error logs:
tail -f /var/log/apache2/error.log

# Check uWSGI logs:
tail -f /var/log/uwsgi/keystone.log

# Restart Apache:
sudo systemctl restart apache2
```

### Database Reset (DESTRUCTIVE - Last Resort)

If the database is corrupted:

```bash
# Backup first!
mysqldump -u root -p keystone > keystone_backup.sql

# Drop and recreate:
mysql -u root -p -e "DROP DATABASE keystone;"
mysql -u root -p -e "CREATE DATABASE keystone;"

# Run keystone DB sync:
sudo su -s /bin/bash keystone -c "keystone-manage db_sync"
```

### Network Issues Inside VM

Check if the VM can resolve itself:

```bash
# On the DevStack VM:
curl http://localhost/identity/v3/

# Check loopback:
ip addr show lo

# Check hosts file:
cat /etc/hosts
```

## Horizon-Side Configuration

### Enable HTTP Request Logging in Horizon

To see the full HTTP request/response in Horizon logs, edit `openstack_dashboard/local/local_settings.py`:

```python
LOGGING = {
    # ... existing config ...
    'loggers': {
        # ... existing loggers ...
        'requests': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'urllib3': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

This will show you the actual HTTP error (timeout, connection refused, etc.).

### Increase Request Timeout

If Keystone is just slow (not hung), you can increase the timeout in Horizon.

Check `openstack_dashboard/local/local_settings.py`:

```python
# Add or modify:
OPENSTACK_API_VERSIONS = {
    "identity": 3,
}

# Increase session timeout:
SESSION_TIMEOUT = 3600  # seconds
```

## Quick Reference Commands

### One-Line Health Checks

```bash
# Test Keystone from host:
timeout 5 curl -s http://192.168.122.140/identity/v3/ && echo "OK" || echo "FAILED"

# On DevStack VM - check all services:
systemctl list-units devstack@* --state=running

# Check if Keystone is responding locally:
ssh stack@192.168.122.140 "curl -s http://localhost/identity/v3/ | jq ."

# Quick log check for errors:
ssh stack@192.168.122.140 "sudo journalctl -u devstack@keystone --since '5 minutes ago' | grep -i error"
```

## Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Network | ✅ Working | Ping successful |
| Web Server | ✅ Working | Apache responding |
| Keystone /identity/ | ✅ Working | Version endpoint responds |
| Keystone /auth/tokens | ❌ **HANGING** | **THIS IS THE PROBLEM** |
| Horizon | ✅ Working | Correctly sending auth requests |

**Next Action:** SSH into the DevStack VM and investigate Keystone service, database, and logs to determine why authentication requests hang.

## Common Solutions by Error Type

### "Connection Refused"
- Keystone service is not running
- Wrong port or IP address
- Firewall blocking connection

### "Timeout" (Our Current Issue)
- Keystone is hung/deadlocked
- Database connection timeout
- External auth backend timeout
- Resource exhaustion

### "Connection Reset"
- Keystone crashed while processing request
- uWSGI/Apache worker killed
- Out of memory

### "401 Unauthorized"
- Wrong credentials (but at least Keystone is responding!)
- User disabled or locked
- Domain/project doesn't exist

### "500 Internal Server Error"
- Check Keystone logs for Python traceback
- Database query failure
- Configuration error

---

**Document Created:** 2025-11-07  
**DevStack VM:** 192.168.122.140  
**Keystone Endpoint:** http://192.168.122.140/identity/v3/  
**Issue:** Authentication endpoint timeout

---

## USE CASE: How to Prevent Disk Space Issues in the Future

### Problem: Disk Full Due to Large Log Files

DevStack VMs can experience disk space exhaustion, which can cause service failures, hung authentication, and general system instability. The most common culprit is unrotated log files, particularly `/var/log/syslog`.

---

### Sequence Showing Disk Space Exhaustion

**Initial Check - Disk Full:**

```bash
stack@omcgonag-devstack-ui-pytest-1:~$ df -h
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           794M   79M  715M  10% /run
/dev/vda1        39G   39G     0 100% /
tmpfs           3.9G  100K  3.9G   1% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/vda15      105M  6.1M   99M   6% /boot/efi
tmpfs           3.9G     0  3.9G   0% /run/qemu
tmpfs           512M  123M  390M  24% /opt/stack/data/etcd
tmpfs           794M  4.0K  794M   1% /run/user/1001
```

❌ **Problem:** Root filesystem at 100% capacity!

---

### Quick Emergency Cleanup

**Step 1: Clean journalctl logs**

```bash
sudo journalctl --vacuum-size=100M
sudo rm -rf /var/log/libvirt/*.log*
```

**Step 2: Check disk space again**

```bash
stack@omcgonag-devstack-ui-pytest-1:~$ df -h
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           794M  1.5M  793M   1% /run
/dev/vda1        39G   39G  544M  99% /
tmpfs           3.9G  100K  3.9G   1% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/vda15      105M  6.1M   99M   6% /boot/efi
tmpfs           3.9G     0  3.9G   0% /run/qemu
tmpfs           512M  123M  390M  24% /opt/stack/data/etcd
tmpfs           794M  4.0K  794M   1% /run/user/1001
```

⚠️ **Still Critical:** Only freed 544M, still at 99%!

---

### Manual Fix: Truncate the Massive syslog File

**Identify the problem:**

```bash
stack@omcgonag-devstack-ui-pytest-1:/var/log$ cd /var/log
stack@omcgonag-devstack-ui-pytest-1:/var/log$ du -h syslog
20G	syslog
```

😱 **20GB syslog file!** This is the culprit.

**Truncate the file (safer than deletion):**

```bash
sudo truncate -s 0 /var/log/syslog
```

> **Why truncate instead of rm?**
> - Keeps the file descriptor open for logging processes
> - Prevents permission/ownership issues
> - Logs can continue to be written immediately
> - No need to restart services

**Verify the space is freed:**

```bash
stack@omcgonag-devstack-ui-pytest-1:/var/log$ df -h
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           794M  1.5M  793M   1% /run
/dev/vda1        39G   19G   21G  49% /
tmpfs           3.9G  100K  3.9G   1% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/vda15      105M  6.1M   99M   6% /boot/efi
tmpfs           3.9G     0  3.9G   0% /run/qemu
tmpfs           512M  123M  390M  24% /opt/stack/data/etcd
tmpfs           794M  4.0K  794M   1% /run/user/1001
```

✅ **Success:** Freed 20GB, now at healthy 49% usage!

---

## Automation: Guard Against Syslog Growing Too Large

That 20GB `syslog` size indicates a **failure in log maintenance**. To guard against this log bloat in the future, you need a **two-part strategy**:

1. **Ensure proper log rotation** (the maintenance fix)
2. **Implement filtering rules** to stop applications that spam log files (the root cause fix)

---

### Part 1: Configure Log Rotation (The Maintenance Fix)

You must ensure that the `logrotate` utility is running on a size-based schedule and compressing old files.

**Logrotate configuration locations:**
- Global config: `/etc/logrotate.conf`
- Syslog-specific rules: `/etc/logrotate.d/rsyslog`

#### Check the State File

Verify when the last rotation occurred:

```bash
cat /var/lib/logrotate/status
```

**Look for:**
- When `/var/log/syslog` was last rotated
- If rotation is failing or stalled

---

#### Implement Size-Based Rotation

To prevent any log file from exceeding a specific size, use the `maxsize` directive. This forces rotation even if the scheduled time (e.g., `weekly`) hasn't arrived.

**Edit the rsyslog configuration:**

```bash
sudo vim /etc/logrotate.d/rsyslog
```

**Add or modify the configuration:**

```
/var/log/syslog {
    maxsize 50M       # Forces rotation as soon as the file exceeds 50MB
    weekly            # Regular scheduled rotation
    rotate 4          # Keep 4 old versions
    compress          # Compress rotated files to save space
    delaycompress     # Don't compress most recent old file
    missingok         # Don't error if file is missing
    notifempty        # Don't rotate if file is empty
    postrotate
        # Reload rsyslog after rotation
        /usr/lib/rsyslog/rsyslog-rotate
    endscript
}
```

**Key directives explained:**

| Directive | Purpose |
|-----------|---------|
| `maxsize 50M` | Rotate immediately when file exceeds 50MB (prevents 20GB files!) |
| `weekly` | Also rotate once per week (whichever comes first) |
| `rotate 4` | Keep 4 old versions (syslog.1, syslog.2, syslog.3, syslog.4) |
| `compress` | Compress old logs with gzip (saves ~90% space) |
| `delaycompress` | Keep most recent rotation uncompressed (for easier access) |

**Test the configuration:**

```bash
# Dry-run to check for syntax errors:
sudo logrotate -d /etc/logrotate.d/rsyslog

# Force an immediate rotation (for testing):
sudo logrotate -f /etc/logrotate.d/rsyslog
```

---

### Part 2: Implement Log Suppression (The Root Cause Fix)

Stopping the source of excessive logs is the only long-term fix. You can filter messages based on the program name using `rsyslog`'s property-based filters.

#### Identify the Spamming Program

First, identify which process is generating excessive logs:

```bash
# Show recent log lines with program names:
journalctl -n 100

# Or check syslog directly:
tail -f /var/log/syslog

# Count log entries by program:
sudo awk '{print $5}' /var/log/syslog | sort | uniq -c | sort -rn | head -20
```

**Look for patterns like:**
- Repeated messages every second/millisecond
- Debug messages that shouldn't be in production
- Error loops (same error repeated constantly)

#### Create a Filtering Rule

Once you know the program name (e.g., `spammer-app`), create a custom filter file that runs **before** the default rules.

**Create the filter file:**

```bash
sudo vim /etc/rsyslog.d/01-discard-spam.conf
```

> **Note:** The `01-` prefix ensures this file is processed before `50-default.conf`

**Example filters:**

```
# Discard all messages from a specific program:
:programname, isequal, "spammer-app" stop

# Discard messages containing a specific string:
:msg, contains, "Excessive Debug Info" stop

# Discard messages matching a regex pattern:
:msg, regex, "Connection reset.*peer" stop

# More complex: Only discard if program AND message match:
:programname, isequal, "neutron-server" {
    :msg, contains, "DEBUG pool" stop
}
```

**Common spam sources in OpenStack DevStack:**

```
# Nova spam:
:programname, isequal, "nova-compute" {
    :msg, contains, "Took" stop
}

# Neutron connection spam:
:programname, isequal, "neutron-server" {
    :msg, contains, "Connection pool" stop
}

# Keystone token spam:
:programname, isequal, "keystone" {
    :msg, contains, "Token validation" stop
}
```

**Restart rsyslog to apply changes:**

```bash
sudo systemctl restart rsyslog
```

**Verify the filter is working:**

```bash
# Watch syslog in real-time:
tail -f /var/log/syslog | grep "spammer-app"

# Should see no new messages from the filtered program
```

---

### Part 3: Adjust Systemd Journal Limits (If Applicable)

If the systemd journal itself is allowing too much log traffic before it even reaches `rsyslog`, adjust its rate limits.

**Edit journald configuration:**

```bash
sudo vim /etc/systemd/journald.conf
```

**Configure rate limits:**

```ini
[Journal]
# Limit the rate of messages per service:
RateLimitIntervalSec=30s
RateLimitBurst=50000      # Allow 50,000 messages per 30 seconds per service

# Set hard limits on total journal size:
SystemMaxUse=5G           # Don't use more than 5GB for logs
SystemMaxFileSize=500M    # Each journal file max 500MB
RuntimeMaxUse=512M        # Limit runtime (tmpfs) logs to 512MB

# How long to keep old logs:
MaxRetentionSec=1week     # Delete logs older than 1 week
```

**Restart journald to apply changes:**

```bash
sudo systemctl restart systemd-journald
```

**Verify journal size:**

```bash
journalctl --disk-usage
```

---

## Automated Monitoring Script

Create a monitoring script to alert when logs grow too large:

**Create the script:**

```bash
sudo vim /usr/local/bin/check-log-sizes.sh
```

**Script contents:**

```bash
#!/bin/bash
# Check for oversized log files

THRESHOLD_MB=100
ALERT_EMAIL="admin@example.com"

# Check syslog size
SYSLOG_SIZE=$(du -m /var/log/syslog 2>/dev/null | cut -f1)

if [ "$SYSLOG_SIZE" -gt "$THRESHOLD_MB" ]; then
    echo "WARNING: /var/log/syslog is ${SYSLOG_SIZE}MB (threshold: ${THRESHOLD_MB}MB)"
    
    # Optional: send email alert
    # echo "Syslog size: ${SYSLOG_SIZE}MB" | mail -s "DevStack Log Alert" "$ALERT_EMAIL"
    
    # Optional: auto-rotate
    # sudo logrotate -f /etc/logrotate.d/rsyslog
fi

# Check total disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

if [ "$DISK_USAGE" -gt "80" ]; then
    echo "WARNING: Disk usage is ${DISK_USAGE}% (threshold: 80%)"
fi
```

**Make it executable:**

```bash
sudo chmod +x /usr/local/bin/check-log-sizes.sh
```

**Add to cron to run every hour:**

```bash
sudo crontab -e
```

Add this line:

```
0 * * * * /usr/local/bin/check-log-sizes.sh
```

---

## Quick Reference: Emergency Disk Space Commands

```bash
# Check disk usage:
df -h

# Find largest directories:
sudo du -sh /* | sort -rh | head -10

# Find largest files in /var/log:
sudo du -sh /var/log/* | sort -rh | head -20

# Truncate syslog (emergency):
sudo truncate -s 0 /var/log/syslog

# Clean journalctl logs:
sudo journalctl --vacuum-size=100M
sudo journalctl --vacuum-time=7d

# Force log rotation:
sudo logrotate -f /etc/logrotate.conf

# Clean package cache (Ubuntu):
sudo apt clean
sudo apt autoremove

# Clean old kernels (Ubuntu):
sudo apt autoremove --purge

# Find and delete old compressed logs:
sudo find /var/log -name "*.gz" -mtime +30 -delete
sudo find /var/log -name "*.old" -mtime +30 -delete
```

---

## Prevention Checklist

- [ ] Configure `maxsize` in `/etc/logrotate.d/rsyslog` (set to 50M-100M)
- [ ] Enable log compression in logrotate config
- [ ] Identify and filter spammy log sources in `/etc/rsyslog.d/01-discard-spam.conf`
- [ ] Set systemd journal size limits in `/etc/systemd/journald.conf`
- [ ] Create monitoring script for log sizes
- [ ] Add cron job to run monitoring script
- [ ] Test logrotate with `logrotate -f` command
- [ ] Document which logs are being filtered and why
- [ ] Set calendar reminder to check disk space monthly

---

## Summary: Three-Layer Defense

| Layer | Purpose | Tool | Configuration |
|-------|---------|------|---------------|
| **1. Rotation** | Prevent files from growing unbounded | `logrotate` | `/etc/logrotate.d/rsyslog` with `maxsize 50M` |
| **2. Filtering** | Stop spam at the source | `rsyslog` | `/etc/rsyslog.d/01-discard-spam.conf` |
| **3. Rate Limiting** | Control journal growth | `systemd-journald` | `/etc/systemd/journald.conf` with `SystemMaxUse=5G` |

**Result:** Logs stay manageable, disk space stays available, DevStack stays healthy! ✅

---

**Last Updated:** 2025-11-13  
**Related Issue:** Disk space exhaustion causing service failures


