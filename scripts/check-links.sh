#!/bin/bash
# Script to check all markdown links in documentation files

# Get script directory and load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# Load mymcp configuration
if [ -f "${BASE_DIR}/.mymcp-config" ]; then
    source "${BASE_DIR}/.mymcp-config"
    BASE_DIR="${MYMCP_REPO_PATH}"
fi

cd "$BASE_DIR"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Checking markdown links in documentation files..."
echo "================================================"
echo ""

# Find all markdown files, excluding venv, .tox, and workspace subdirectories
find . -name "*.md" -type f \
  ! -path "*/venv/*" \
  ! -path "*/.tox/*" \
  ! -path "./workspace/horizon-*/*" \
  | while read -r file; do
    
    # Extract links in format [text](path) or [text](url)
    grep -oP '\[([^\]]+)\]\(([^\)]+)\)' "$file" | while read -r link; do
        # Extract the path/URL from the link
        path=$(echo "$link" | sed -E 's/\[([^\]]+)\]\(([^\)]+)\)/\2/')
        
        # Skip external URLs (http/https)
        if [[ "$path" =~ ^https?:// ]]; then
            continue
        fi
        
        # Skip anchor links
        if [[ "$path" =~ ^# ]]; then
            continue
        fi
        
        # Get the directory of the current file
        file_dir=$(dirname "$file")
        
        # Resolve the full path
        if [[ "$path" =~ ^\/ ]]; then
            # Absolute path
            full_path="$BASE_DIR$path"
        else
            # Relative path
            full_path="$file_dir/$path"
        fi
        
        # Normalize the path (remove .., ., etc.)
        full_path=$(readlink -m "$full_path")
        
        # Check if file/directory exists
        if [ ! -e "$full_path" ]; then
            echo -e "${RED}✗ BROKEN LINK${NC}"
            echo "  File: $file"
            echo "  Link: $path"
            echo "  Expected: $full_path"
            echo ""
        fi
    done
done

echo ""
echo "================================================"
echo "Link check complete!"

