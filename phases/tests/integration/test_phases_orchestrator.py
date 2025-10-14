"""
Integration tests for the main Phases Orchestrator.
Tests the coordination of all 5 phases in the pipeline.
"""

import unittest
from pathlib import Path
import sys
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from phases.phases_orchestrator import PhasesOrchestrator, create_orchestrator

# Configure logging for tests
logging.basicConfig(level=logging.INFO)


class TestPhasesOrchestrator(unittest.TestCase):
    """Test cases for the main phases orchestrator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = project_root
        self.orchestrator = create_orchestrator(self.project_root)
    
    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes correctly."""
        self.assertIsNotNone(self.orchestrator)
        self.assertEqual(self.orchestrator.project_root, self.project_root)
        self.assertIsNotNone(self.orchestrator.discovery_phase)
        self.assertIsNotNone(self.orchestrator.tui_mapping_phase)
        self.assertIsNotNone(self.orchestrator.collection_phase)
        self.assertIsNotNone(self.orchestrator.validation_phase)
        self.assertIsNotNone(self.orchestrator.export_phase)
    
    def test_execute_single_phase_discovery(self):
        """Test executing Phase 1 (Discovery) individually."""
        context = {}
        result = self.orchestrator.execute_phase(1, context)
        
        self.assertIsNotNone(result)
        self.assertIn('enhanced_defaults_file', result)
        self.assertIn('discovery_summary', result)
    
    def test_execute_single_phase_tui_mapping(self):
        """Test executing Phase 2 (TUI Mapping) individually."""
        # First execute Phase 1 to get required inputs
        context = {}
        phase1_result = self.orchestrator.execute_phase(1, context)
        context.update(phase1_result)
        
        # Now execute Phase 2
        result = self.orchestrator.execute_phase(2, context)
        
        self.assertIsNotNone(result)
        self.assertIn('tui_defaults_file', result)
        self.assertIn('transformation_summary', result)
    
    def test_execute_phases_range(self):
        """Test executing a range of phases (1-2)."""
        result = self.orchestrator.execute_phases_range(1, 2)
        
        self.assertIsNotNone(result)
        self.assertIn('phases_executed', result)
        self.assertEqual(result['phases_executed'], [1, 2])
        self.assertIn('results', result)
        self.assertIn('phase_1', result['results'])
        self.assertIn('phase_2', result['results'])
    
    def test_invalid_phase_number(self):
        """Test that invalid phase numbers raise errors."""
        context = {}
        
        with self.assertRaises(ValueError):
            self.orchestrator.execute_phase(0, context)
        
        with self.assertRaises(ValueError):
            self.orchestrator.execute_phase(6, context)
    
    def test_invalid_phase_range(self):
        """Test that invalid phase ranges raise errors."""
        with self.assertRaises(ValueError):
            self.orchestrator.execute_phases_range(3, 1)  # start > end
        
        with self.assertRaises(ValueError):
            self.orchestrator.execute_phases_range(0, 2)  # invalid start
        
        with self.assertRaises(ValueError):
            self.orchestrator.execute_phases_range(1, 6)  # invalid end


class TestPhasesOrchestrator_Integration(unittest.TestCase):
    """Integration tests for full pipeline execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = project_root
        self.orchestrator = create_orchestrator(self.project_root)
    
    def test_phases_1_and_2_integration(self):
        """Test that Phases 1 and 2 work together correctly."""
        # Execute Phases 1-2
        result = self.orchestrator.execute_phases_range(1, 2)
        
        # Verify Phase 1 outputs
        phase1_result = result['results']['phase_1']
        self.assertIn('enhanced_defaults_file', phase1_result)
        self.assertIn('enhanced_defaults', phase1_result)
        
        # Verify Phase 2 outputs
        phase2_result = result['results']['phase_2']
        self.assertIn('tui_defaults_file', phase2_result)
        self.assertIn('tui_defaults', phase2_result)
        
        # Verify data flow
        enhanced_defaults = phase1_result['enhanced_defaults']
        tui_defaults = phase2_result['tui_defaults']
        
        self.assertIn('defaults', enhanced_defaults)
        self.assertIn('defaults', tui_defaults)
        
        # Verify transformation occurred (enhanced has metadata, tui is flattened)
        self.assertIn('metadata', enhanced_defaults)
        self.assertIsInstance(tui_defaults['defaults'], dict)


if __name__ == '__main__':
    unittest.main()
