#!/bin/bash
# Script to verify all MCP agents are properly configured and working

set -e

echo "=================================================="
echo "  MCP Agents Verification Script"
echo "=================================================="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

REPO_PATH="$(cd "$(dirname "$0")" && pwd)"

echo "Repository path: $REPO_PATH"
echo

# Test 1: OpenDev Review Agent
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Testing OpenDev Review Agent"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "$REPO_PATH/opendev-review-agent" ]; then
    echo -e "${RED}✗ opendev-review-agent directory not found${NC}"
    exit 1
fi

cd "$REPO_PATH/opendev-review-agent"

if [ ! -f "server.sh" ]; then
    echo -e "${RED}✗ server.sh not found${NC}"
    exit 1
fi

if [ ! -x "server.sh" ]; then
    echo -e "${RED}✗ server.sh is not executable${NC}"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -q requests fastmcp
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

echo "Testing server startup..."
timeout 3 bash server.sh <<< '{"jsonrpc": "2.0", "method": "exit"}' 2>&1 | head -20 > /tmp/opendev-test.log
if grep -q "FastMCP" /tmp/opendev-test.log; then
    echo -e "${GREEN}✓ OpenDev Review Agent is working${NC}"
else
    echo -e "${RED}✗ OpenDev Review Agent failed to start${NC}"
    cat /tmp/opendev-test.log
    exit 1
fi

echo

# Test 2: GitHub Agent
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Testing GitHub Agent"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "$REPO_PATH/github-agent" ]; then
    echo -e "${RED}✗ github-agent directory not found${NC}"
    exit 1
fi

cd "$REPO_PATH/github-agent"

if [ ! -f "server.sh" ]; then
    echo -e "${RED}✗ server.sh not found${NC}"
    exit 1
fi

if [ ! -x "server.sh" ]; then
    echo -e "${RED}✗ server.sh is not executable${NC}"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -q requests fastmcp PyGithub
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found (GitHub token required for full functionality)${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo "Testing server startup..."
timeout 3 bash server.sh <<< '{"jsonrpc": "2.0", "method": "exit"}' 2>&1 | head -20 > /tmp/github-test.log
if grep -q "FastMCP" /tmp/github-test.log; then
    echo -e "${GREEN}✓ GitHub Agent is working${NC}"
else
    echo -e "${RED}✗ GitHub Agent failed to start${NC}"
    cat /tmp/github-test.log
    exit 1
fi

echo

# Test 3: Jira Agent
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Testing Jira Agent"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "$REPO_PATH/jira-agent" ]; then
    echo -e "${RED}✗ jira-agent directory not found${NC}"
    exit 1
fi

cd "$REPO_PATH/jira-agent"

echo "Checking for Podman..."
if ! command -v podman &> /dev/null; then
    echo -e "${RED}✗ Podman not found. Please install podman.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Podman is installed${NC}"
fi

echo "Checking for container image..."
if podman images | grep -q "jira-agent"; then
    echo -e "${GREEN}✓ jira-agent container image exists${NC}"
else
    echo -e "${YELLOW}⚠ jira-agent container image not found. Building...${NC}"
    make build
fi

if [ ! -f "$HOME/.rh-jira-mcp.env" ]; then
    echo -e "${YELLOW}⚠ ~/.rh-jira-mcp.env not found (required for Jira authentication)${NC}"
else
    echo -e "${GREEN}✓ ~/.rh-jira-mcp.env exists${NC}"
    
    echo "Testing container startup..."
    timeout 5 podman run --rm -i --env-file ~/.rh-jira-mcp.env jira-agent:latest <<< '{"jsonrpc": "2.0", "method": "exit"}' 2>&1 | head -20 > /tmp/jira-test.log
    if grep -q "Starting MCP server" /tmp/jira-test.log; then
        echo -e "${GREEN}✓ Jira Agent is working${NC}"
    else
        echo -e "${RED}✗ Jira Agent failed to start${NC}"
        cat /tmp/jira-test.log
        exit 1
    fi
fi

echo

# Test 4: Cursor Configuration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Checking Cursor Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "$HOME/.cursor/mcp.json" ]; then
    echo -e "${YELLOW}⚠ ~/.cursor/mcp.json not found${NC}"
    echo "  Please configure MCP servers in Cursor settings."
else
    echo -e "${GREEN}✓ ~/.cursor/mcp.json exists${NC}"
    
    echo "Checking agent paths..."
    
    if grep -q "$REPO_PATH/opendev-review-agent/server.sh" "$HOME/.cursor/mcp.json"; then
        echo -e "${GREEN}  ✓ OpenDev agent path configured${NC}"
    else
        echo -e "${YELLOW}  ⚠ OpenDev agent path not found in mcp.json${NC}"
    fi
    
    if grep -q "$REPO_PATH/github-agent/server.sh" "$HOME/.cursor/mcp.json"; then
        echo -e "${GREEN}  ✓ GitHub agent path configured${NC}"
    else
        echo -e "${YELLOW}  ⚠ GitHub agent path not found in mcp.json${NC}"
    fi
    
    if grep -q "jira-agent:latest" "$HOME/.cursor/mcp.json"; then
        echo -e "${GREEN}  ✓ Jira agent image configured${NC}"
    else
        echo -e "${YELLOW}  ⚠ Jira agent not found in mcp.json (looking for jira-agent:latest)${NC}"
    fi
fi

echo
echo "=================================================="
echo -e "${GREEN}✓ All tests completed successfully!${NC}"
echo "=================================================="
echo
echo "Next steps:"
echo "1. Fully quit Cursor (Ctrl+Q) and restart"
echo "2. Test agents in Cursor:"
echo "   - @opendev-reviewer-agent Analyze https://review.opendev.org/c/..."
echo "   - @github-reviewer-agent Review https://github.com/.../pull/..."
echo "   - @jiraMcp Get details for issue ..."
echo

# Cleanup
rm -f /tmp/opendev-test.log /tmp/github-test.log /tmp/jira-test.log


