#!/usr/bin/env python3
"""
Run Configuration Manager with YAML-driven orchestration.
Reads design_specs/control_flows.yml to determine phase execution order.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add phases directory to path
sys.path.insert(0, str(Path(__file__).parent))

from phases.dynamic_orchestrator import DynamicOrchestrator


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(message)s' if not verbose else '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="OpenProject Configuration Manager (YAML-driven)"
    )
    parser.add_argument(
        '--flow',
        '-f',
        default='main_config_flow',
        help='Flow ID to execute (default: main_config_flow)'
    )
    parser.add_argument(
        '--spec',
        '-s',
        type=Path,
        help='Path to control_flows.yml (default: auto-detect)'
    )
    parser.add_argument(
        '--list-flows',
        '-l',
        action='store_true',
        help='List available flows and exit'
    )
    parser.add_argument(
        '--info',
        '-i',
        action='store_true',
        help='Show flow information and exit (no execution)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--project-root',
        '-p',
        type=Path,
        help='Project root directory (default: current directory parent)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Determine project root
    if args.project_root:
        project_root = args.project_root
    else:
        project_root = Path(__file__).parent
    
    try:
        # Create orchestrator
        orchestrator = DynamicOrchestrator(
            project_root=project_root,
            spec_file=args.spec
        )
        
        # List flows mode
        if args.list_flows:
            print("📋 Available Flows:")
            print("-" * 40)
            flows = orchestrator.list_available_flows()
            for flow_id in flows:
                info = orchestrator.get_flow_info(flow_id)
                status_counts = {}
                for phase in info['phases']:
                    status = phase['status']
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                print(f"\n  {flow_id}")
                print(f"    {info['description']}")
                print(f"    Phases: {info['total_phases']}", end='')
                if status_counts:
                    print(f" ({', '.join(f'{v} {k}' for k, v in status_counts.items())})")
                else:
                    print()
            return 0
        
        # Info mode
        if args.info:
            print("=" * 80)
            print(f"📊 Flow Information: {args.flow}")
            print("=" * 80)
            
            info = orchestrator.get_flow_info(args.flow)
            print(f"\nDescription: {info['description']}")
            print(f"Orchestrator: {info['orchestrator']}")
            print(f"Total Phases: {info['total_phases']}")
            
            print(f"\nPhases:")
            print("-" * 80)
            for phase in info['phases']:
                status_emoji = {
                    'IMPLEMENTED': '✅',
                    'PLANNED': '🚧',
                    'SKIPPED': '⏭️',
                    'IN_PROGRESS': '🔄'
                }.get(phase['status'], '❓')
                
                print(f"\n{status_emoji} {phase['sequence']}. {phase['name']}")
                print(f"   ID: {phase['id']}")
                print(f"   Status: {phase['status']}")
                print(f"   Description: {phase['description']}")
                
                if phase['artifacts_consumed']:
                    print(f"   Consumes: {', '.join(phase['artifacts_consumed'])}")
                if phase['artifacts_produced']:
                    print(f"   Produces: {', '.join(phase['artifacts_produced'])}")
            
            print("\n" + "=" * 80)
            return 0
        
        # Execute the flow
        print("=" * 80)
        print(f"🚀 Executing Flow: {args.flow}")
        print("=" * 80)
        
        result = orchestrator.execute_all_phases(flow_id=args.flow)
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 Execution Summary")
        print("=" * 80)
        print(f"Status: {result['pipeline_status'].upper()}")
        print(f"Flow: {result['flow_id']}")
        print(f"Phases Executed: {result.get('phases_executed', 'N/A')}")
        print(f"Phases Skipped: {result.get('phases_skipped', 0)}")
        
        if result['pipeline_status'] == 'complete':
            print("\n✅ Pipeline completed successfully!")
            return 0
        elif result['pipeline_status'] == 'interrupted':
            print("\n⚠️  Pipeline was interrupted")
            return 130
        else:
            print(f"\n❌ Pipeline failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have design_specs/control_flows.yml in your project")
        return 1
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
