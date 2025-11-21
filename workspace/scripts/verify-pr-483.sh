#!/bin/bash
#
# Verification Script for horizon-operator PR #483
# PR: https://github.com/openstack-k8s-operators/horizon-operator/pull/483
# Change: Removed TLS conditional around "Include conf.d/*.conf" in httpd.conf
# Merged: 2025-08-08
#
# Usage: ./verify-pr-483.sh [namespace-operator] [namespace-openstack]
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default namespaces
NAMESPACE_OPERATOR="${1:-openstack-operators}"
NAMESPACE_OPENSTACK="${2:-openstack}"

# Determine kubectl/oc command
if command -v oc &> /dev/null; then
    K8S_CMD="oc"
elif command -v kubectl &> /dev/null; then
    K8S_CMD="kubectl"
else
    echo -e "${RED}Error: Neither 'oc' nor 'kubectl' found${NC}"
    exit 1
fi

echo "=========================================="
echo "PR #483 Verification Script"
echo "=========================================="
echo ""
echo "What does PR #483 do?"
echo "  - Removes TLS conditional from httpd.conf template"
echo "  - Makes 'Include conf.d/*.conf' ALWAYS execute"
echo "  - Allows custom httpd configs even without TLS"
echo "  - Related to JIRA: OSPRH-18585"
echo ""
echo "Merged: 2025-08-08T17:10:13+00:00"
echo "Commit: 93aa9b8a3a048c19bb9d077e543b1cd5b77c8893"
echo ""
echo "=========================================="
echo ""

# Step 1: Check operator version
echo -e "${BLUE}[1/7] Checking horizon-operator version...${NC}"
OPERATOR_IMAGE=$($K8S_CMD get deployment horizon-operator-controller-manager -n $NAMESPACE_OPERATOR -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null || echo "NOT_FOUND")

if [ "$OPERATOR_IMAGE" == "NOT_FOUND" ]; then
    echo -e "${RED}✗ horizon-operator deployment not found in namespace '$NAMESPACE_OPERATOR'${NC}"
    echo "  Try: $K8S_CMD get deployments -n $NAMESPACE_OPERATOR | grep horizon"
    exit 1
else
    echo -e "${GREEN}✓ Operator Image: $OPERATOR_IMAGE${NC}"
    
    # Extract tag/version
    if [[ "$OPERATOR_IMAGE" =~ :([^:]+)$ ]]; then
        IMAGE_TAG="${BASH_REMATCH[1]}"
        echo "  Tag/Version: $IMAGE_TAG"
    fi
fi
echo ""

# Step 2: Check image build date
echo -e "${BLUE}[2/7] Checking image build date...${NC}"
echo "  PR #483 was merged on: 2025-08-08"
echo "  Images built AFTER this date should include the change"
echo ""
echo "  Checking image metadata..."
$K8S_CMD get deployment horizon-operator-controller-manager -n $NAMESPACE_OPERATOR -o yaml | grep -A 5 "image:" | head -10
echo ""

# Step 3: Check Horizon deployment
echo -e "${BLUE}[3/7] Checking Horizon deployment...${NC}"
HORIZON_POD=$($K8S_CMD get pods -n $NAMESPACE_OPENSTACK -l service=horizon -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "NOT_FOUND")

if [ "$HORIZON_POD" == "NOT_FOUND" ]; then
    echo -e "${YELLOW}⚠ No Horizon pod found in namespace '$NAMESPACE_OPENSTACK'${NC}"
    echo "  Horizon may not be deployed yet"
else
    echo -e "${GREEN}✓ Horizon Pod: $HORIZON_POD${NC}"
    
    # Check pod creation time
    POD_AGE=$($K8S_CMD get pod $HORIZON_POD -n $NAMESPACE_OPENSTACK -o jsonpath='{.metadata.creationTimestamp}')
    echo "  Pod created: $POD_AGE"
    echo "  (Pods created after 2025-08-08 should have the fix)"
fi
echo ""

# Step 4: THE KEY VERIFICATION - Check httpd.conf
echo -e "${BLUE}[4/7] Verifying httpd.conf configuration (THE CRITICAL CHECK)...${NC}"

if [ "$HORIZON_POD" != "NOT_FOUND" ]; then
    echo "  Checking if 'Include conf.d/*.conf' is present..."
    
    HTTPD_CONF=$($K8S_CMD exec -n $NAMESPACE_OPENSTACK $HORIZON_POD -- cat /etc/httpd/conf/httpd.conf 2>/dev/null || echo "FAILED")
    
    if [ "$HTTPD_CONF" == "FAILED" ]; then
        echo -e "${RED}✗ Could not read httpd.conf from pod${NC}"
    else
        # Check for the Include line
        if echo "$HTTPD_CONF" | grep -q "Include conf.d/\*.conf"; then
            echo -e "${GREEN}✓ PASS: 'Include conf.d/*.conf' found in httpd.conf${NC}"
            
            # Check if it's conditional (old version) or unconditional (new version)
            # In the rendered config, the Go template will be gone, so we just verify it exists
            echo ""
            echo "  Full httpd.conf excerpt:"
            echo "  ----------------------------------------"
            echo "$HTTPD_CONF" | grep -B 2 -A 2 "Include conf"
            echo "  ----------------------------------------"
            
        else
            echo -e "${RED}✗ FAIL: 'Include conf.d/*.conf' NOT found in httpd.conf${NC}"
            echo -e "${YELLOW}  This suggests PR #483 is NOT applied${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠ Skipping - No Horizon pod available${NC}"
fi
echo ""

# Step 5: Check if conf.d files are being loaded
echo -e "${BLUE}[5/7] Checking if conf.d/*.conf files are loaded...${NC}"

if [ "$HORIZON_POD" != "NOT_FOUND" ]; then
    echo "  Listing files in /etc/httpd/conf.d/:"
    $K8S_CMD exec -n $NAMESPACE_OPENSTACK $HORIZON_POD -- ls -la /etc/httpd/conf.d/ 2>/dev/null || echo "  Could not list directory"
    echo ""
    
    # Check if ssl.conf exists and what it contains
    echo "  Checking ssl.conf (the file that caused the original issue):"
    SSL_CONF=$($K8S_CMD exec -n $NAMESPACE_OPENSTACK $HORIZON_POD -- cat /etc/httpd/conf.d/ssl.conf 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$SSL_CONF" != "NOT_FOUND" ]; then
        echo "  ssl.conf exists and contains:"
        echo "$SSL_CONF" | head -20
        
        # Check if it has the problematic certificate lines
        if echo "$SSL_CONF" | grep -q "SSLCertificateFile.*localhost.crt"; then
            echo -e "${YELLOW}  ⚠ ssl.conf references localhost.crt (may cause issues if TLS not configured)${NC}"
        fi
    else
        echo "  ssl.conf not found (this is actually better if TLS is disabled)"
    fi
else
    echo -e "${YELLOW}⚠ Skipping - No Horizon pod available${NC}"
fi
echo ""

# Step 6: Check TLS configuration
echo -e "${BLUE}[6/7] Checking Horizon TLS configuration...${NC}"

HORIZON_CR=$($K8S_CMD get horizon -n $NAMESPACE_OPENSTACK -o yaml 2>/dev/null || echo "NOT_FOUND")

if [ "$HORIZON_CR" == "NOT_FOUND" ]; then
    echo -e "${YELLOW}⚠ No Horizon CR found in namespace '$NAMESPACE_OPENSTACK'${NC}"
else
    echo "  Checking if TLS is enabled in Horizon CR..."
    
    if echo "$HORIZON_CR" | grep -q "tls:"; then
        echo -e "${GREEN}✓ TLS configuration found in Horizon CR${NC}"
        echo "$HORIZON_CR" | grep -A 10 "tls:"
    else
        echo -e "${YELLOW}  TLS not configured (running without TLS)${NC}"
        echo -e "${BLUE}  → With PR #483: conf.d/*.conf is STILL loaded (GOOD!)${NC}"
        echo -e "${BLUE}  → Without PR #483: conf.d/*.conf would NOT be loaded (BAD!)${NC}"
    fi
fi
echo ""

# Step 7: Functional verification - Check httpd is working
echo -e "${BLUE}[7/7] Functional verification...${NC}"

if [ "$HORIZON_POD" != "NOT_FOUND" ]; then
    echo "  Checking if httpd is running..."
    HTTPD_PROCESS=$($K8S_CMD exec -n $NAMESPACE_OPENSTACK $HORIZON_POD -- ps aux 2>/dev/null | grep httpd | grep -v grep || echo "NOT_FOUND")
    
    if [ "$HTTPD_PROCESS" != "NOT_FOUND" ]; then
        echo -e "${GREEN}✓ httpd is running${NC}"
        echo "$HTTPD_PROCESS" | head -3
        echo ""
        
        # Check httpd error log for issues with conf.d includes
        echo "  Checking httpd error log for conf.d related issues..."
        ERROR_LOG=$($K8S_CMD exec -n $NAMESPACE_OPENSTACK $HORIZON_POD -- tail -50 /var/log/httpd/error_log 2>/dev/null | grep -i "conf.d" || echo "No conf.d errors found")
        
        if [ "$ERROR_LOG" == "No conf.d errors found" ]; then
            echo -e "${GREEN}✓ No conf.d related errors in httpd log${NC}"
        else
            echo -e "${YELLOW}⚠ Found conf.d related log entries:${NC}"
            echo "$ERROR_LOG"
        fi
    else
        echo -e "${RED}✗ httpd is NOT running${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Skipping - No Horizon pod available${NC}"
fi
echo ""

# Summary
echo "=========================================="
echo -e "${BLUE}VERIFICATION SUMMARY${NC}"
echo "=========================================="
echo ""
echo "PR #483 Changes:"
echo "  - Removes: {{- if .TLS }}"
echo "  - Always includes: conf.d/*.conf"
echo "  - Purpose: Allow httpd configs (like LimitRequestBody) without TLS"
echo ""
echo "Key Verification Points:"
echo ""
echo "1. Image Date:"
if [[ "$OPERATOR_IMAGE" =~ "2025" ]]; then
    echo -e "   ${GREEN}✓ Image appears recent (2025)${NC}"
else
    echo -e "   ${YELLOW}? Check image build date manually${NC}"
fi
echo ""
echo "2. httpd.conf Content:"
echo "   → Check Step [4/7] output above"
echo "   → 'Include conf.d/*.conf' should be present"
echo "   → Should be UNCONDITIONAL (no if/else around it)"
echo ""
echo "3. Behavior without TLS:"
echo "   → With PR #483: conf.d files ARE loaded"
echo "   → Without PR #483: conf.d files are NOT loaded"
echo ""
echo "=========================================="
echo ""
echo "Manual Verification Steps:"
echo ""
echo "1. Check the actual httpd.conf template in the operator:"
echo "   \$ $K8S_CMD exec -n $NAMESPACE_OPERATOR <operator-pod> -- cat /templates/horizon/config/httpd.conf | grep -A 2 -B 2 'conf.d'"
echo ""
echo "2. Verify conf.d files are loaded in running Horizon:"
echo "   \$ $K8S_CMD exec -n $NAMESPACE_OPENSTACK $HORIZON_POD -- httpd -t -D DUMP_INCLUDES 2>&1 | grep conf.d"
echo ""
echo "3. Check if your custom configs in conf.d are working:"
echo "   \$ $K8S_CMD exec -n $NAMESPACE_OPENSTACK $HORIZON_POD -- cat /etc/httpd/conf.d/99-custom.conf"
echo "   \$ $K8S_CMD exec -n $NAMESPACE_OPENSTACK $HORIZON_POD -- httpd -M | grep <your-module>"
echo ""
echo "=========================================="
echo ""

# Exit with appropriate code
if [ "$HORIZON_POD" == "NOT_FOUND" ]; then
    echo -e "${YELLOW}Exit: Partial verification (Horizon not deployed)${NC}"
    exit 2
else
    echo -e "${GREEN}Exit: Verification complete - Review results above${NC}"
    exit 0
fi

