#!/bin/bash
#
# ask_me.sh - Automated Ask Generation for AI-Assisted Development
#
# This script generates formatted "ask" prompts by substituting placeholders
# in templates with values from YAML key files.
#
# Usage:
#   ./ask_me.sh <template-type> <key-file>
#
# Examples:
#   ./ask_me.sh analysis_doc_create askme/keys/fix_chevron_id.yaml
#   ./ask_me.sh code_review_response askme/keys/review_comment_css_gap.yaml
#
# Template types:
#   - analysis_doc_create
#   - code_implement_workspace
#   - code_review_response
#   - investigate_patterns
#   - phase_done
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="${SCRIPT_DIR}/askme/templates"
KEYS_DIR="${SCRIPT_DIR}/askme/keys"

# Function to print usage
usage() {
    echo "Usage: $0 <template-type> <key-file>"
    echo ""
    echo "Template types:"
    echo "  analysis_doc_create        - Create analysis document with investigation"
    echo "  code_implement_workspace   - Implement code changes in workspace"
    echo "  code_review_response       - Respond to code review comment"
    echo "  investigate_patterns       - Investigate framework patterns/best practices"
    echo "  phase_done                 - Wrap-up questions and phase transition"
    echo ""
    echo "Examples:"
    echo "  $0 analysis_doc_create askme/keys/example_fix_chevron_id.yaml"
    echo "  $0 code_review_response askme/keys/example_review_comment_css_gap.yaml"
    echo "  $0 phase_done askme/keys/example_phase_done_gerrit_topic.yaml"
    echo ""
    echo "Available templates:"
    ls -1 "${TEMPLATES_DIR}"/*.template 2>/dev/null | sed 's/.*\//  - /' | sed 's/.template$//' || echo "  (none found)"
    echo ""
    echo "Available key files:"
    ls -1 "${KEYS_DIR}"/*.yaml 2>/dev/null | sed 's/.*\//  - /' || echo "  (none found)"
    exit 1
}

# Function to print error and exit
error() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

# Function to print info
info() {
    echo -e "${BLUE}$1${NC}"
}

# Function to print success
success() {
    echo -e "${GREEN}$1${NC}"
}

# Function to print warning
warn() {
    echo -e "${YELLOW}$1${NC}"
}

# Check arguments
if [ $# -ne 2 ]; then
    usage
fi

TEMPLATE_TYPE="$1"
KEY_FILE="$2"

# Resolve key file path (support both relative and absolute)
if [[ "$KEY_FILE" = /* ]]; then
    KEY_FILE_PATH="$KEY_FILE"
else
    KEY_FILE_PATH="${SCRIPT_DIR}/${KEY_FILE}"
fi

# Check if template exists
TEMPLATE_FILE="${TEMPLATES_DIR}/${TEMPLATE_TYPE}.template"
if [ ! -f "$TEMPLATE_FILE" ]; then
    error "Template '${TEMPLATE_TYPE}' not found at: ${TEMPLATE_FILE}"
fi

# Check if key file exists
if [ ! -f "$KEY_FILE_PATH" ]; then
    error "Key file not found at: ${KEY_FILE_PATH}"
fi

info "📝 Generating ask from:"
echo "   Template: ${TEMPLATE_TYPE}.template"
echo "   Key file: ${KEY_FILE}"
echo ""

# Check if yq is installed (YAML parser)
if ! command -v yq &> /dev/null; then
    warn "⚠️  yq is not installed. Using Python as fallback..."
    
    # Python-based YAML parser fallback
    PYTHON_PARSER=$(cat <<'EOF'
import sys
import yaml
import re

# Read YAML file
with open(sys.argv[1], 'r') as f:
    data = yaml.safe_load(f)

# Read template file
with open(sys.argv[2], 'r') as f:
    template = f.read()

# Function to replace placeholders
def replace_placeholder(match):
    key = match.group(1)
    # Convert placeholder name to YAML key (lowercase, underscores)
    yaml_key = key.lower()
    
    if yaml_key in data:
        value = data[yaml_key]
        # Handle multiline values
        if isinstance(value, str) and '\n' in value:
            # For multiline strings, preserve formatting
            return value
        return str(value)
    else:
        # Keep placeholder if no value found
        return match.group(0)

# Replace all placeholders
result = re.sub(r'\{([A-Z_]+)\}', replace_placeholder, template)

print(result)
EOF
)
    
    # Check if Python and PyYAML are available
    if ! python3 -c "import yaml" 2>/dev/null; then
        error "Neither yq nor Python with PyYAML is installed. Please install one of them:
  - yq: https://github.com/mikefarah/yq
  - PyYAML: pip install pyyaml"
    fi
    
    # Use Python parser
    python3 -c "$PYTHON_PARSER" "$KEY_FILE_PATH" "$TEMPLATE_FILE"
    
else
    # Use yq (faster and more robust)
    
    # Read template
    TEMPLATE_CONTENT=$(cat "$TEMPLATE_FILE")
    
    # Get all keys from YAML file
    YAML_KEYS=$(yq eval 'keys | .[]' "$KEY_FILE_PATH")
    
    # Replace each placeholder
    RESULT="$TEMPLATE_CONTENT"
    
    while IFS= read -r key; do
        if [ -n "$key" ] && [ "$key" != "type" ]; then
            # Get value from YAML
            value=$(yq eval ".${key}" "$KEY_FILE_PATH")
            
            # Convert key to uppercase with underscores for placeholder
            placeholder=$(echo "$key" | tr '[:lower:]' '[:upper:]')
            
            # Replace placeholder in result
            # Use a temporary file to handle multiline values correctly
            echo "$RESULT" | awk -v placeholder="{${placeholder}}" -v value="$value" '
            {
                if (index($0, placeholder) > 0) {
                    sub(placeholder, value)
                }
                print
            }' > /tmp/ask_me_tmp_$$
            
            RESULT=$(cat /tmp/ask_me_tmp_$$)
            rm -f /tmp/ask_me_tmp_$$
        fi
    done <<< "$YAML_KEYS"
    
    echo "$RESULT"
fi

echo ""
success "✅ Ask generated successfully!"
info "💡 Copy the output above and paste it to your AI assistant."

