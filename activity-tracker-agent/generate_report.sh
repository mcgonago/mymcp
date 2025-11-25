#!/bin/bash
#
# Quick wrapper to generate activity reports
# Usage: ./generate_report.sh [time_range]
#   time_range: "this week", "last week", "this month", etc.
#   Default: "last week"
#

TIME_RANGE="${1:-last week}"

cd "$(dirname "$0")"

python3 -c "
import sys
sys.path.insert(0, '.')
from server import generate_status_report

result = generate_status_report('$TIME_RANGE')
print(result)
"

