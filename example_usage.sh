#!/bin/bash
# Example usage of YAML-driven orchestration

echo "=================================================="
echo "YAML-Driven Phase Orchestration Examples"
echo "=================================================="
echo ""

echo "1. List all available flows:"
echo "   python3 run_dynamic.py --list-flows"
echo ""
python3 run_dynamic.py --list-flows
echo ""

echo "=================================================="
echo "2. Show detailed info about main flow:"
echo "   python3 run_dynamic.py --info"
echo ""
python3 run_dynamic.py --info
echo ""

echo "=================================================="
echo "3. To execute the full pipeline:"
echo "   python3 run_dynamic.py"
echo ""
echo "   (Not running now - would execute all phases)"
echo ""

echo "=================================================="
echo "4. Key Features:"
echo "   ✓ Phases defined in control_flows.yml"
echo "   ✓ Change execution order by editing YAML"
echo "   ✓ Skip phases by setting status: SKIPPED"
echo "   ✓ Track artifacts flow between phases"
echo "=================================================="
