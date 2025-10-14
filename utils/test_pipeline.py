#!/usr/bin/env python3
"""
Test Full Pipeline with Mock Responses
Execute all 5 phases using pre-defined mock responses for Phase 3.
"""

import sys
import json
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from phases.phases_orchestrator import create_orchestrator


def main():
    """Test full pipeline with mock responses."""
    
    # Load mock responses
    mock_file = project_root / "test_mock_responses.json"
    with open(mock_file, 'r') as f:
        mock_responses = json.load(f)
    
    logger.info("=" * 80)
    logger.info("TESTING FULL PIPELINE WITH MOCK RESPONSES")
    logger.info("=" * 80)
    
    # Create orchestrator
    orchestrator = create_orchestrator(project_root)
    
    # Create initial context with mock responses
    context = {
        'mock_responses': mock_responses,
        'testing_mode': True
    }
    
    try:
        # Execute all phases
        result = orchestrator.execute_all_phases(context)
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ FULL PIPELINE TEST PASSED")
        logger.info("=" * 80)
        
        # Print summary
        logger.info("\nGenerated Artifacts:")
        if 'phase_5_export' in result:
            export_result = result['phase_5_export']
            if 'export_summary' in export_result:
                summary = export_result['export_summary']
                logger.info(f"  Files exported: {summary.get('files_exported', 0)}")
                logger.info(f"  Export directory: {summary.get('export_directory', 'N/A')}")
                if 'files' in summary:
                    for file in summary['files']:
                        logger.info(f"    - {file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ PIPELINE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
