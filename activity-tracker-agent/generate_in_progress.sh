#!/usr/bin/env bash
#
# generate_in_progress.sh - Generate current "In Progress" ownership report
#
# Usage:
#   ./generate_in_progress.sh
#
# Generates: ~/Work/mymcp/workspace/iproject/activity/in_progress.md
#

set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Navigate to script directory
cd "$SCRIPT_DIR"

echo "📊 Generating In Progress report..."
echo ""

# Run the Python function
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from server import generate_in_progress_report

result = generate_in_progress_report()
print(result)
EOF

echo ""
echo "✅ Report generated: ~/Work/mymcp/workspace/iproject/activity/in_progress.md"

