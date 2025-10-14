#!/bin/bash
#
# Config Manager - Production Entry Point
# 
# This script is the primary entry point for running the OpenProject configuration
# pipeline. It executes all 5 phases in sequence to generate deployment configuration.
#
# Usage:
#   ./run_config_manager.sh [--verbose] [--mock-responses PATH]
#
# Options:
#   --verbose           Enable verbose logging
#   --mock-responses    Path to JSON file with mock responses (for testing)
#
# Output:
#   All configuration files are written to: phases/outputs/
#     - docker-compose.yml
#     - .env
#     - configuration_manifest.yml
#     - validation_report.yml
#

set -e  # Exit on any error

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Parse arguments
VERBOSE=""
MOCK_RESPONSES=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "OpenProject Configuration Manager"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --verbose           Enable verbose logging"
            echo "  --mock-responses    Path to JSON file with mock responses (for testing)"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Output:"
            echo "  All configuration files are written to: phases/outputs/"
            echo "    - docker-compose.yml"
            echo "    - .env"
            echo "    - configuration_manifest.yml"
            echo "    - validation_report.yml"
            exit 0
            ;;
        --verbose)
            VERBOSE="--verbose"
            shift
            ;;
        --mock-responses)
            MOCK_RESPONSES="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--verbose] [--mock-responses PATH]"
            exit 1
            ;;
    esac
done

# Check Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not found in PATH"
    exit 1
fi

# Check phases_orchestrator.py exists
if [ ! -f "phases/phases_orchestrator.py" ]; then
    echo "ERROR: phases_orchestrator.py not found at: phases/phases_orchestrator.py"
    exit 1
fi

# Run the orchestrator
echo "========================================"
echo "OpenProject Config Manager"
echo "========================================"
echo ""

# Temporarily disable errexit to capture exit code
set +e

if [ -n "$MOCK_RESPONSES" ]; then
    echo "Using mock responses from: $MOCK_RESPONSES"
    python3 -c "
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path.cwd()))
from phases.phases_orchestrator import create_orchestrator

project_root = Path.cwd()

# Load mock responses
with open('$MOCK_RESPONSES', 'r') as f:
    mock_responses = json.load(f)

context = {'mock_responses': mock_responses}
orchestrator = create_orchestrator(project_root)
result = orchestrator.execute_all_phases(context)

print()
print('=' * 80)
print('✅ CONFIGURATION COMPLETE')
print('=' * 80)
print()
print('Generated files in phases/outputs/:')
if 'phase_5_export' in result and 'export_summary' in result['phase_5_export']:
    for file in result['phase_5_export']['export_summary'].get('files', []):
        print(f'  - {file}')
"
    exit_code=$?
else
    echo "Running in production mode (interactive TUI collection)"
    python3 -c "
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from phases.phases_orchestrator import create_orchestrator

project_root = Path.cwd()
orchestrator = create_orchestrator(project_root)
result = orchestrator.execute_all_phases()

print()
print('=' * 80)
print('✅ CONFIGURATION COMPLETE')
print('=' * 80)
print()
print('Generated files in phases/outputs/:')
if 'phase_5_export' in result and 'export_summary' in result['phase_5_export']:
    for file in result['phase_5_export']['export_summary'].get('files', []):
        print(f'  - {file}')
"
    exit_code=$?
fi

# Re-enable errexit
set -e

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "Configuration files are ready for deployment."
    echo "Location: $(pwd)/phases/outputs/"
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "ERROR: Configuration generation failed with exit code: $exit_code"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "💡 Common Issues:"
    echo ""
    echo "1. TUI Form Engine Not Available:"
    echo "   Phase 3 requires interactive user input collection."
    echo "   Solutions:"
    echo "     • Install tui-form-designer: git submodule update --init --recursive"
    echo "     • OR use mock responses for testing:"
    echo "       ./run_config_manager.sh --mock-responses <path-to-file.json>"
    echo ""
    echo "2. Missing Dependencies:"
    echo "   Install required Python packages:"
    echo "     pip install -r requirements.txt"
    echo ""
    exit $exit_code
fi
