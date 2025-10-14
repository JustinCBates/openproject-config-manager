#!/bin/bash
# Test interactive mode with automated responses

cd /opt/openproject/external/config-manager/phases/phase_3_collection/step_1_collect_user_configuration
source /opt/openproject/venv/bin/activate

# Pipe responses to handle the first few prompts
# This will let us see if the expanded layout works interactively
echo "Testing interactive mode with expanded sublayouts..."
echo ""

# Use timeout to prevent hanging, and provide some automated responses
timeout 30s python collect_user_configuration.py <<EOF

my-openproject
admin@example.com
SecurePass123!
production
EOF

echo ""
echo "Test completed (timed out after first few prompts as expected)"
