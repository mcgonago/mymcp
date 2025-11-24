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

# Load mymcp configuration
if [ -f "${SCRIPT_DIR}/.mymcp-config" ]; then
    source "${SCRIPT_DIR}/.mymcp-config"
else
    # Fallback defaults if config file doesn't exist
    export MYMCP_REPO_PATH="${SCRIPT_DIR}"
    export MYMCP_WORKSPACE="${MYMCP_REPO_PATH}/workspace"
    export MYMCP_WORKSPACE_PROJECT="${MYMCP_WORKSPACE}/iproject"
fi

# Function to expand path variables in generated output
expand_path_vars() {
    local text="$1"
    # Replace common path placeholders with actual values
    text="${text//<mymcp-repo-path>/${MYMCP_REPO_PATH}}"
    text="${text//\{MYMCP_REPO_PATH\}/${MYMCP_REPO_PATH}}"
    text="${text//\{WORKSPACE_PATH\}/${MYMCP_WORKSPACE}}"
    text="${text//\{WORKSPACE_PROJECT\}/${MYMCP_WORKSPACE_PROJECT}}"
    echo "$text"
}

# Function to substitute template variables in YAML file
substitute_template_vars() {
    local yaml_file="$1"
    local temp_file="/tmp/ask_me_yaml_$$"
    
    # If no template variables, just copy the file
    if [ ${#TEMPLATE_VARS[@]} -eq 0 ]; then
        echo "$yaml_file"
        return
    fi
    
    # Read the YAML file
    local yaml_content=$(cat "$yaml_file")
    
    # Substitute each template variable
    # We support three formats: {{VAR}}, ${VAR}, and {VAR} (but only for template vars)
    for var_name in "${!TEMPLATE_VARS[@]}"; do
        local var_value="${TEMPLATE_VARS[$var_name]}"
        # Escape special characters in var_value for sed
        local escaped_value=$(printf '%s\n' "$var_value" | sed 's/[&/\]/\\&/g')
        
        # Replace {{VAR_NAME}}, ${VAR_NAME}, and {VAR_NAME} (case-insensitive for flexibility)
        yaml_content=$(echo "$yaml_content" | sed "s/{{${var_name}}}/${escaped_value}/g")
        yaml_content=$(echo "$yaml_content" | sed "s/\${${var_name}}/${escaped_value}/g")
        yaml_content=$(echo "$yaml_content" | sed "s/{${var_name}}/${escaped_value}/g")
        
        # Also try lowercase version
        local var_name_lower=$(echo "$var_name" | tr '[:upper:]' '[:lower:]')
        yaml_content=$(echo "$yaml_content" | sed "s/{{${var_name_lower}}}/${escaped_value}/g")
        yaml_content=$(echo "$yaml_content" | sed "s/\${${var_name_lower}}/${escaped_value}/g")
        yaml_content=$(echo "$yaml_content" | sed "s/{${var_name_lower}}/${escaped_value}/g")
    done
    
    # Write to temporary file
    echo "$yaml_content" > "$temp_file"
    echo "$temp_file"
}

# Function to print usage
usage() {
    echo "Usage: $0 <template-type> <key-file> [VAR=value ...]"
    echo ""
    echo "Template types:"
    echo "  analysis_doc_create        - Create analysis document with investigation"
    echo "  code_implement_workspace   - Implement code changes in workspace"
    echo "  code_review_response       - Respond to code review comment"
    echo "  investigate_patterns       - Investigate framework patterns/best practices"
    echo "  phase_done                 - Wrap-up questions and phase transition"
    echo ""
    echo "Template Variables (optional):"
    echo "  You can override variables in the YAML file by passing VAR=value on command line"
    echo ""
    echo "Examples:"
    echo "  # Basic usage"
    echo "  $0 analysis_doc_create askme/keys/example_fix_chevron_id.yaml"
    echo ""
    echo "  # With template variables"
    echo "  $0 analysis_doc_create askme/keys/osprh_template.yaml TICKET_NUMBER=16421"
    echo "  $0 analysis_doc_create askme/keys/osprh_template.yaml TICKET_NUMBER=99999 FEATURE_NAME=\"My Feature\""
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

# Check arguments (minimum 2, but can have more for variable assignments)
if [ $# -lt 2 ]; then
    usage
fi

TEMPLATE_TYPE="$1"
KEY_FILE="$2"

# Parse variable assignments from remaining arguments
shift 2  # Remove first two arguments
declare -A TEMPLATE_VARS
for arg in "$@"; do
    if [[ "$arg" =~ ^([A-Z_][A-Z0-9_]*)=(.*)$ ]]; then
        var_name="${BASH_REMATCH[1]}"
        var_value="${BASH_REMATCH[2]}"
        TEMPLATE_VARS["$var_name"]="$var_value"
        info "   Variable: ${var_name}=${var_value}"
    else
        warn "⚠️  Ignoring invalid variable assignment: $arg"
        warn "    (Must be in format: VAR_NAME=value)"
    fi
done

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

# Substitute template variables in YAML file if any were provided
PROCESSED_KEY_FILE=$(substitute_template_vars "$KEY_FILE_PATH")
if [ "$PROCESSED_KEY_FILE" != "$KEY_FILE_PATH" ]; then
    info "   Applied ${#TEMPLATE_VARS[@]} template variable(s)"
    # Update KEY_FILE_PATH to point to processed file
    KEY_FILE_PATH="$PROCESSED_KEY_FILE"
fi
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
    
    # Use Python parser and expand path variables
    RESULT=$(python3 -c "$PYTHON_PARSER" "$KEY_FILE_PATH" "$TEMPLATE_FILE")
    RESULT=$(expand_path_vars "$RESULT")
    echo "$RESULT"
    
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
    
    # Expand path variables before output
    RESULT=$(expand_path_vars "$RESULT")
    
    echo "$RESULT"
fi

echo ""
success "✅ Ask generated successfully!"
info "💡 Copy the output above and paste it to your AI assistant."

# Cleanup temporary files
if [ -f "/tmp/ask_me_yaml_$$" ]; then
    rm -f "/tmp/ask_me_yaml_$$"
fi

