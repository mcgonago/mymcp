#!/bin/bash
# Debug script to check Keystone health on the DevStack VM
# Run this ON the DevStack VM (ssh stack@192.168.122.140)

echo "=========================================="
echo "Keystone Health Check (DevStack VM)"
echo "=========================================="
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check 1: Keystone service status
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}[CHECK 1]${NC} Keystone Service Status"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

# Check different possible service names
for SERVICE in devstack@keystone keystone keystone-uwsgi apache2; do
    if systemctl list-units --full -all | grep -q "$SERVICE"; then
        echo -e "\n${YELLOW}Service: $SERVICE${NC}"
        systemctl status "$SERVICE" --no-pager -l | head -20 || echo "  Not found or no permission"
    fi
done
echo ""

# Check 2: Keystone processes
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}[CHECK 2]${NC} Keystone Processes"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
ps aux | grep -i keystone | grep -v grep | head -10
if [ ${PIPESTATUS[1]} -ne 0 ]; then
    echo -e "${RED}No Keystone processes found!${NC}"
fi
echo ""

# Check 3: Apache/uWSGI status
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}[CHECK 3]${NC} Web Server Status"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
systemctl status apache2 --no-pager | head -10 2>/dev/null || echo "Apache2 not found or not using systemd"
echo ""

# Check 4: Database connectivity
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}[CHECK 4]${NC} Database Connectivity"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

# Try to get DB password from keystone.conf
DB_CONNECTION=$(grep -m 1 "^connection" /etc/keystone/keystone.conf 2>/dev/null | cut -d'=' -f2 | tr -d ' ')
if [ -n "$DB_CONNECTION" ]; then
    echo "Database connection string found in config"
    # Check if MySQL/MariaDB is running
    if systemctl is-active mysql >/dev/null 2>&1 || systemctl is-active mariadb >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} MySQL/MariaDB service is running"
        
        # Try to connect (will need password)
        echo "Testing database connection..."
        if mysql -u root -e "SELECT 1;" >/dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} Database connection successful (no password)"
            mysql -u root -e "SHOW DATABASES;" | grep keystone && echo -e "${GREEN}✓${NC} Keystone database exists"
        else
            echo -e "${YELLOW}⚠${NC} Database needs password (try: mysql -u root -p)"
        fi
        
        # Check for active connections
        echo ""
        echo "Active database connections:"
        mysql -u root -e "SHOW PROCESSLIST;" 2>/dev/null | head -10 || echo "  (need password to check)"
    else
        echo -e "${RED}✗${NC} MySQL/MariaDB service is NOT running!"
    fi
else
    echo -e "${YELLOW}⚠${NC} Could not find database connection in /etc/keystone/keystone.conf"
fi
echo ""

# Check 5: System resources
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}[CHECK 5]${NC} System Resources"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo "Memory usage:"
free -h
echo ""
echo "Disk usage:"
df -h / /opt
echo ""
echo "Load average:"
uptime
echo ""

# Check 6: Recent Keystone logs
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}[CHECK 6]${NC} Recent Keystone Logs"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

# Try different log locations
LOG_FOUND=0

if [ -d /opt/stack/logs ]; then
    echo -e "\n${YELLOW}DevStack logs (/opt/stack/logs/):${NC}"
    if [ -f /opt/stack/logs/keystone.log ]; then
        echo "Last 20 lines of keystone.log:"
        tail -20 /opt/stack/logs/keystone.log
        LOG_FOUND=1
    fi
fi

if systemctl list-units --full -all | grep -q "devstack@keystone"; then
    echo -e "\n${YELLOW}Systemd journal for devstack@keystone:${NC}"
    journalctl -u devstack@keystone --no-pager -n 30 --since "10 minutes ago" 2>/dev/null
    LOG_FOUND=1
fi

if [ -f /var/log/apache2/keystone.log ]; then
    echo -e "\n${YELLOW}Apache Keystone log:${NC}"
    tail -20 /var/log/apache2/keystone.log
    LOG_FOUND=1
fi

if [ -f /var/log/apache2/error.log ]; then
    echo -e "\n${YELLOW}Apache error log (recent Keystone errors):${NC}"
    grep -i keystone /var/log/apache2/error.log | tail -10
fi

if [ $LOG_FOUND -eq 0 ]; then
    echo -e "${RED}No Keystone logs found in common locations${NC}"
fi
echo ""

# Check 7: Keystone configuration
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}[CHECK 7]${NC} Keystone Configuration"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

if [ -f /etc/keystone/keystone.conf ]; then
    echo "Key configuration values:"
    echo -e "\n${YELLOW}Token provider:${NC}"
    grep "^token_provider" /etc/keystone/keystone.conf || echo "  (using default)"
    
    echo -e "\n${YELLOW}Database connection:${NC}"
    grep "^connection" /etc/keystone/keystone.conf | sed 's/:[^:]*@/:****@/'
    
    echo -e "\n${YELLOW}Debug mode:${NC}"
    grep "^debug" /etc/keystone/keystone.conf || echo "  debug = False (default)"
    
    echo -e "\n${YELLOW}Fernet keys:${NC}"
    if [ -d /etc/keystone/fernet-keys ]; then
        ls -la /etc/keystone/fernet-keys/ | head -5
        KEY_COUNT=$(ls /etc/keystone/fernet-keys/ | wc -l)
        echo "  Total keys: $KEY_COUNT"
    else
        echo -e "  ${RED}Fernet keys directory not found!${NC}"
    fi
else
    echo -e "${RED}/etc/keystone/keystone.conf not found!${NC}"
fi
echo ""

# Check 8: Test local authentication
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}[CHECK 8]${NC} Local Authentication Test"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo "Testing Keystone from localhost..."

RESPONSE=$(timeout 5 curl -s http://localhost/identity/v3/ 2>&1)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Keystone responding on localhost"
else
    echo -e "${RED}✗${NC} Keystone NOT responding on localhost"
fi
echo ""

# Summary and recommendations
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}SUMMARY AND RECOMMENDATIONS${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""
echo "Common fixes for authentication timeout:"
echo ""
echo "1. Restart Keystone:"
echo "   sudo systemctl restart devstack@keystone"
echo "   # or if using Apache:"
echo "   sudo systemctl restart apache2"
echo ""
echo "2. Check database and restart if needed:"
echo "   sudo systemctl restart mysql"
echo "   sudo systemctl restart mariadb"
echo ""
echo "3. Re-run DevStack (if all else fails):"
echo "   cd /opt/stack/devstack"
echo "   ./unstack.sh && ./stack.sh"
echo ""
echo "4. View live logs:"
echo "   journalctl -u devstack@keystone -f"
echo "   tail -f /opt/stack/logs/keystone.log"
echo ""
echo "5. Enable debug logging:"
echo "   Edit /etc/keystone/keystone.conf"
echo "   Set: debug = true"
echo "   Then restart Keystone"
echo ""


