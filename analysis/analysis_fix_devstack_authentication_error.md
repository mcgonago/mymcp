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


