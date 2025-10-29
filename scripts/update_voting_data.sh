#!/usr/bin/env bash
set -euo pipefail
echo "🗳️ Updating Swiss Voting Data..."

SCRIPT_DIR="$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P)"
cd "$SCRIPT_DIR"

source ../venv/bin/activate

python extract_voting_data.py
python validate_voting_data.py

echo "✅ Data update finished"
