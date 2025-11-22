#!/bin/bash
# Script to verify all MCP agent authentication tokens are properly configured
# This is a pre-workshop verification script for attendees

set -e

echo "=================================================="
echo "  MCP Agents Authentication Verification"
echo "=================================================="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

REPO_PATH="$(cd "$(dirname "$0")/.." && pwd)"

echo "Repository path: $REPO_PATH"
echo

# Track overall status
ALL_PASSED=true

# Test 1: OpenDev Review Agent (No Auth Required)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. OpenDev Review Agent"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "$REPO_PATH/opendev-review-agent" ]; then
    echo -e "${RED}✗ opendev-review-agent directory not found${NC}"
    ALL_PASSED=false
else
    cd "$REPO_PATH/opendev-review-agent"
    
    # Check virtual environment
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}⚠ Virtual environment not found${NC}"
        echo -e "${BLUE}  → Run: cd $REPO_PATH/opendev-review-agent && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt${NC}"
        ALL_PASSED=false
    else
        echo -e "${GREEN}✓ Virtual environment exists${NC}"
    fi
    
    # Check server.sh
    if [ ! -f "server.sh" ]; then
        echo -e "${RED}✗ server.sh not found${NC}"
        ALL_PASSED=false
    elif [ ! -x "server.sh" ]; then
        echo -e "${YELLOW}⚠ server.sh is not executable${NC}"
        echo -e "${BLUE}  → Run: chmod +x $REPO_PATH/opendev-review-agent/server.sh${NC}"
        ALL_PASSED=false
    else
        echo -e "${GREEN}✓ server.sh is executable${NC}"
    fi
    
    echo -e "${BLUE}ℹ No authentication required (public API)${NC}"
fi

echo

# Test 2: GitHub Agent
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. GitHub Agent"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "$REPO_PATH/github-agent" ]; then
    echo -e "${RED}✗ github-agent directory not found${NC}"
    ALL_PASSED=false
else
    cd "$REPO_PATH/github-agent"
    
    # Check virtual environment
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}⚠ Virtual environment not found${NC}"
        echo -e "${BLUE}  → Run: cd $REPO_PATH/github-agent && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt${NC}"
        ALL_PASSED=false
    else
        echo -e "${GREEN}✓ Virtual environment exists${NC}"
    fi
    
    # Check .env file
    if [ ! -f ".env" ]; then
        echo -e "${RED}✗ .env file not found${NC}"
        echo -e "${BLUE}  → Run: cp $REPO_PATH/github-agent/example.env $REPO_PATH/github-agent/.env${NC}"
        echo -e "${BLUE}  → Then edit .env and add your GitHub token${NC}"
        ALL_PASSED=false
    else
        echo -e "${GREEN}✓ .env file exists${NC}"
        
        # Check if GITHUB_TOKEN is set (not placeholder) - check only the actual GITHUB_TOKEN= line
        if grep "^GITHUB_TOKEN=" .env 2>/dev/null | grep -q "your_github_token_here"; then
            echo -e "${RED}✗ GITHUB_TOKEN is still a placeholder${NC}"
            echo -e "${BLUE}  → Edit $REPO_PATH/github-agent/.env and add your actual GitHub token${NC}"
            echo -e "${BLUE}  → Get token from: https://github.com/settings/tokens${NC}"
            ALL_PASSED=false
        else
            # Check if GITHUB_TOKEN exists and is not empty
            if grep -q "^GITHUB_TOKEN=.\+" .env 2>/dev/null; then
                echo -e "${GREEN}✓ GITHUB_TOKEN is configured${NC}"
            else
                echo -e "${RED}✗ GITHUB_TOKEN is empty${NC}"
                echo -e "${BLUE}  → Edit $REPO_PATH/github-agent/.env and add your GitHub token${NC}"
                ALL_PASSED=false
            fi
        fi
    fi
    
    # Check server.sh
    if [ ! -f "server.sh" ]; then
        echo -e "${RED}✗ server.sh not found${NC}"
        ALL_PASSED=false
    elif [ ! -x "server.sh" ]; then
        echo -e "${YELLOW}⚠ server.sh is not executable${NC}"
        echo -e "${BLUE}  → Run: chmod +x $REPO_PATH/github-agent/server.sh${NC}"
        ALL_PASSED=false
    else
        echo -e "${GREEN}✓ server.sh is executable${NC}"
    fi
fi

echo

# Test 3: GitLab Agent (Optional)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. GitLab Agent (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "$REPO_PATH/gitlab-rh-agent" ]; then
    echo -e "${YELLOW}⚠ gitlab-rh-agent directory not found (optional agent)${NC}"
else
    cd "$REPO_PATH/gitlab-rh-agent"
    
    # Check virtual environment
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}⚠ Virtual environment not found${NC}"
        echo -e "${BLUE}  → Run: cd $REPO_PATH/gitlab-rh-agent && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt${NC}"
    else
        echo -e "${GREEN}✓ Virtual environment exists${NC}"
    fi
    
    # Check .env file
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠ .env file not found${NC}"
        echo -e "${BLUE}  → Run: cp $REPO_PATH/gitlab-rh-agent/example.env $REPO_PATH/gitlab-rh-agent/.env${NC}"
        echo -e "${BLUE}  → Then edit .env and add your GitLab token${NC}"
    else
        echo -e "${GREEN}✓ .env file exists${NC}"
        
        # Check if GITLAB_TOKEN is set (not placeholder) - check only the actual GITLAB_TOKEN= line
        if grep "^GITLAB_TOKEN=" .env 2>/dev/null | grep -q "your_gitlab_token_here"; then
            echo -e "${YELLOW}⚠ GITLAB_TOKEN is still a placeholder${NC}"
            echo -e "${BLUE}  → Edit $REPO_PATH/gitlab-rh-agent/.env and add your actual GitLab token${NC}"
            echo -e "${BLUE}  → Get token from: https://gitlab.cee.redhat.com/-/user_settings/personal_access_tokens${NC}"
        else
            # Check if GITLAB_TOKEN exists and is not empty
            if grep -q "^GITLAB_TOKEN=.\+" .env 2>/dev/null; then
                echo -e "${GREEN}✓ GITLAB_TOKEN is configured${NC}"
            else
                echo -e "${YELLOW}⚠ GITLAB_TOKEN is empty${NC}"
                echo -e "${BLUE}  → Edit $REPO_PATH/gitlab-rh-agent/.env and add your GitLab token${NC}"
            fi
        fi
    fi
    
    # Check server.sh
    if [ ! -f "server.sh" ]; then
        echo -e "${YELLOW}⚠ server.sh not found${NC}"
    elif [ ! -x "server.sh" ]; then
        echo -e "${YELLOW}⚠ server.sh is not executable${NC}"
        echo -e "${BLUE}  → Run: chmod +x $REPO_PATH/gitlab-rh-agent/server.sh${NC}"
    else
        echo -e "${GREEN}✓ server.sh is executable${NC}"
    fi
    
    echo -e "${BLUE}ℹ GitLab agent is optional (for gitlab.cee.redhat.com only)${NC}"
fi

echo

# Test 4: Jira Agent (Optional)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Jira Agent (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "$REPO_PATH/jira-agent" ]; then
    echo -e "${YELLOW}⚠ jira-agent directory not found (optional agent)${NC}"
else
    # Check Podman
    if ! command -v podman &> /dev/null; then
        echo -e "${YELLOW}⚠ Podman is not installed${NC}"
        echo -e "${BLUE}  → Install: sudo dnf install podman (Fedora/RHEL)${NC}"
        echo -e "${BLUE}  →      or: brew install podman (macOS)${NC}"
    else
        echo -e "${GREEN}✓ Podman is installed${NC}"
        
        # Check container image
        if podman images | grep -q "jira-agent"; then
            echo -e "${GREEN}✓ jira-agent container image exists${NC}"
        else
            echo -e "${YELLOW}⚠ jira-agent container image not found${NC}"
            echo -e "${BLUE}  → Run: cd $REPO_PATH/jira-agent && make build${NC}"
        fi
    fi
    
    # Check environment file (note: test-mcp-setup.sh uses ~/.rh-jira-mcp.env)
    JIRA_ENV_FILE=""
    if [ -f "$HOME/.rh-jira-mcp.env" ]; then
        JIRA_ENV_FILE="$HOME/.rh-jira-mcp.env"
    elif [ -f "$HOME/.rh-jira-agent.env" ]; then
        JIRA_ENV_FILE="$HOME/.rh-jira-agent.env"
    fi
    
    if [ -z "$JIRA_ENV_FILE" ]; then
        echo -e "${YELLOW}⚠ ~/.rh-jira-mcp.env not found${NC}"
        echo -e "${BLUE}  → Run: cp $REPO_PATH/jira-agent/example.env ~/.rh-jira-mcp.env${NC}"
        echo -e "${BLUE}  → Then edit ~/.rh-jira-mcp.env and add your Jira credentials${NC}"
    else
        echo -e "${GREEN}✓ $JIRA_ENV_FILE exists${NC}"
        
        # Check if variables are set (not placeholders)
        if grep -q "your_jira_token_here\|AdDy0urJ1r4ToKenHeR3" "$JIRA_ENV_FILE" 2>/dev/null; then
            echo -e "${YELLOW}⚠ JIRA_API_TOKEN is still a placeholder${NC}"
            echo -e "${BLUE}  → Edit $JIRA_ENV_FILE and add your actual Jira API token${NC}"
            echo -e "${BLUE}  → Get token from your Jira profile → Security → API Tokens${NC}"
        else
            # Check if JIRA_API_TOKEN exists and is not empty
            if grep -q "^JIRA_API_TOKEN=.\+" "$JIRA_ENV_FILE" 2>/dev/null; then
                echo -e "${GREEN}✓ JIRA_API_TOKEN is configured${NC}"
            else
                # Check for common mistake: JIRA_TOKEN instead of JIRA_API_TOKEN
                if grep -q "^JIRA_TOKEN=" "$JIRA_ENV_FILE"; then
                    echo -e "${YELLOW}⚠ Found JIRA_TOKEN but should be JIRA_API_TOKEN${NC}"
                    echo -e "${BLUE}  → Edit $JIRA_ENV_FILE and rename JIRA_TOKEN to JIRA_API_TOKEN${NC}"
                else
                    echo -e "${YELLOW}⚠ JIRA_API_TOKEN is empty${NC}"
                    echo -e "${BLUE}  → Edit $JIRA_ENV_FILE and add your Jira API token${NC}"
                fi
            fi
        fi
        
        # Check JIRA_URL
        if grep -q "^JIRA_URL=.\+" "$JIRA_ENV_FILE" 2>/dev/null; then
            echo -e "${GREEN}✓ JIRA_URL is configured${NC}"
        else
            echo -e "${YELLOW}⚠ JIRA_URL is empty${NC}"
            echo -e "${BLUE}  → Edit $JIRA_ENV_FILE and add your Jira URL${NC}"
        fi
    fi
    
    echo -e "${BLUE}ℹ Jira agent is optional (for Jira integration only)${NC}"
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

if [ "$ALL_PASSED" = true ]; then
    echo -e "${GREEN}✅ All required agents are configured correctly!${NC}"
    echo
    echo "Next steps:"
    echo "  1. Run: cd $REPO_PATH && ./test-mcp-setup.sh"
    echo "  2. Verify all agents start successfully"
    echo "  3. You're ready for the workshop!"
    echo
    exit 0
else
    echo -e "${YELLOW}⚠ Some issues were found (see above)${NC}"
    echo
    echo "Please address the issues marked with ✗ or ⚠ above."
    echo
    echo "Required for workshop:"
    echo "  - OpenDev Review Agent (no auth needed)"
    echo "  - GitHub Agent (needs token)"
    echo
    echo "Optional agents:"
    echo "  - GitLab Agent (only if you use gitlab.cee.redhat.com)"
    echo "  - Jira Agent (only if you need Jira integration)"
    echo
    echo "For detailed setup instructions, see:"
    echo "  → workshop/GET_TOKENS.md"
    echo
    echo "After fixing issues, run this script again to verify."
    echo
    exit 1
fi

