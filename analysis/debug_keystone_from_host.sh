#!/bin/bash
# Debug script to test Keystone connectivity from the host machine
# Run this on your local machine (not the DevStack VM)

set -e

DEVSTACK_IP="${1:-192.168.122.140}"
TIMEOUT=5

echo "=========================================="
echo "Keystone Connectivity Debug Script"
echo "=========================================="
echo "Target DevStack: $DEVSTACK_IP"
echo "Timeout: ${TIMEOUT}s"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Network connectivity
echo -e "${YELLOW}[TEST 1]${NC} Testing network connectivity..."
if ping -c 3 -W 2 "$DEVSTACK_IP" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC} - Host is reachable"
else
    echo -e "${RED}✗ FAIL${NC} - Host is NOT reachable"
    exit 1
fi
echo ""

# Test 2: Web server responding
echo -e "${YELLOW}[TEST 2]${NC} Testing web server..."
HTTP_CODE=$(timeout $TIMEOUT curl -s -o /dev/null -w "%{http_code}" "http://$DEVSTACK_IP/" 2>/dev/null || echo "timeout")
if [[ "$HTTP_CODE" == "200" || "$HTTP_CODE" == "302" ]]; then
    echo -e "${GREEN}✓ PASS${NC} - Web server responding (HTTP $HTTP_CODE)"
else
    echo -e "${RED}✗ FAIL${NC} - Web server not responding (HTTP $HTTP_CODE)"
fi
echo ""

# Test 3: Keystone endpoint accessible
echo -e "${YELLOW}[TEST 3]${NC} Testing Keystone endpoint..."
if timeout $TIMEOUT curl -s "http://$DEVSTACK_IP/identity/" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC} - Keystone endpoint accessible"
    VERSION=$(timeout $TIMEOUT curl -s "http://$DEVSTACK_IP/identity/v3/" 2>/dev/null | grep -o '"id":"[^"]*"' | head -1)
    echo "  Version info: $VERSION"
else
    echo -e "${RED}✗ FAIL${NC} - Keystone endpoint NOT accessible"
fi
echo ""

# Test 4: Authentication endpoint (THE CRITICAL TEST)
echo -e "${YELLOW}[TEST 4]${NC} Testing authentication endpoint..."
echo "  Sending authentication request..."

# Create temp file for response
RESPONSE_FILE=$(mktemp)
HTTP_CODE_FILE=$(mktemp)

# Try authentication with timeout
timeout $TIMEOUT curl -s -w "%{http_code}" -o "$RESPONSE_FILE" \
    -X POST "http://$DEVSTACK_IP/identity/v3/auth/tokens" \
    -H "Content-Type: application/json" \
    -d '{
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": "admin",
                        "domain": {"name": "Default"},
                        "password": "PLACEHOLDER"
                    }
                }
            }
        }
    }' > "$HTTP_CODE_FILE" 2>&1

EXIT_CODE=$?
HTTP_CODE=$(cat "$HTTP_CODE_FILE" 2>/dev/null || echo "000")

if [[ $EXIT_CODE -eq 124 ]]; then
    echo -e "${RED}✗ FAIL${NC} - Authentication endpoint TIMEOUT (This is the problem!)"
    echo "  The endpoint accepts connections but never responds."
    echo "  Keystone is likely hung or has database issues."
elif [[ $EXIT_CODE -eq 0 ]]; then
    if [[ "$HTTP_CODE" == "201" ]]; then
        echo -e "${GREEN}✓ PASS${NC} - Authentication working (HTTP 201)"
    elif [[ "$HTTP_CODE" == "401" ]]; then
        echo -e "${YELLOW}⚠ PARTIAL${NC} - Keystone responding but credentials invalid (HTTP 401)"
        echo "  This is actually good - Keystone is working, just need correct password"
    else
        echo -e "${YELLOW}⚠ UNKNOWN${NC} - Got HTTP $HTTP_CODE"
        cat "$RESPONSE_FILE" | head -5
    fi
else
    echo -e "${RED}✗ FAIL${NC} - Connection failed (exit code: $EXIT_CODE)"
fi

# Cleanup
rm -f "$RESPONSE_FILE" "$HTTP_CODE_FILE"
echo ""

# Summary
echo "=========================================="
echo "Summary"
echo "=========================================="
echo "If Test 4 shows TIMEOUT, the problem is on the DevStack VM."
echo "Next steps:"
echo "  1. SSH to the DevStack VM: ssh stack@$DEVSTACK_IP"
echo "  2. Run the VM-side debug script"
echo "  3. Check Keystone logs and service status"
echo ""


