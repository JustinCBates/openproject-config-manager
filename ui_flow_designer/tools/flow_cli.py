#!/usr/bin/env python3
"""
Flow Designer CLI
Command-line interface for all flow design and testing tools.
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Flow Designer CLI - Design, validate, and test YAML flows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s design                    # Interactive flow designer
  %(prog)s validate flows/           # Validate all flows in directory
  %(prog)s test --all                # Test all flows
  %(prog)s test --flow core_config   # Test specific flow
  %(prog)s preview core_config       # Preview flow execution
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Design command
    design_parser = subparsers.add_parser(
        'design', 
        help='Interactive flow designer'
    )
    design_parser.add_argument(
        '--flows-dir',
        default='flows',
        help='Directory containing flow definitions'
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate flow definitions'
    )
    validate_parser.add_argument(
        'path',
        help='Path to flow file or directory'
    )
    validate_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show results for all flows'
    )
    validate_parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Only show summary'
    )
    
    # Test command
    test_parser = subparsers.add_parser(
        'test',
        help='Test flow execution'
    )
    test_parser.add_argument(
        '--flows-dir',
        default='flows',
        help='Directory containing flow definitions'
    )
    test_parser.add_argument(
        '--flow',
        help='Test specific flow by ID'
    )
    test_parser.add_argument(
        '--all',
        action='store_true',
        help='Test all flows'
    )
    test_parser.add_argument(
        '--context',
        choices=['development', 'production'],
        default='development',
        help='Test context to use'
    )
    test_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    test_parser.add_argument(
        '--generate-scenarios',
        help='Generate test scenarios for specified flow'
    )
    
    # Preview command
    preview_parser = subparsers.add_parser(
        'preview',
        help='Preview flow execution interactively'
    )
    preview_parser.add_argument(
        'flow_id',
        help='Flow ID to preview'
    )
    preview_parser.add_argument(
        '--flows-dir',
        default='flows',
        help='Directory containing flow definitions'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Import and run the appropriate tool
    if args.command == 'design':
        from flow_designer import InteractiveFlowDesigner
        designer = InteractiveFlowDesigner(flows_dir=args.flows_dir)
        designer.run()
    
    elif args.command == 'validate':
        from flow_validator import FlowValidator
        path = Path(args.path)
        validator = FlowValidator()
        
        if path.is_file():
            flow_id = path.stem
            errors, warnings = validator.validate_flow_file(path)
            results = {flow_id: (errors, warnings)}
        elif path.is_dir():
            results = validator.validate_directory(path)
        else:
            print(f"❌ Path does not exist: {path}")
            sys.exit(1)
        
        if not args.quiet:
            validator.print_validation_results(results, verbose=args.verbose)
        
        total_errors = sum(len(errors) for errors, warnings in results.values())
        sys.exit(1 if total_errors > 0 else 0)
    
    elif args.command == 'test':
        from flow_tester import FlowTester
        tester = FlowTester(flows_dir=args.flows_dir)
        
        if args.generate_scenarios:
            tester.generate_test_scenarios(args.generate_scenarios)
        elif args.flow:
            result = tester.test_flow(args.flow, verbose=args.verbose)
            sys.exit(0 if result else 1)
        elif args.all:
            results = tester.test_all_flows(context_name=args.context, verbose=args.verbose)
            failed_count = sum(1 for success in results.values() if not success)
            
            print("📊 Test Summary:")
            print(f"   Total flows: {len(results)}")
            print(f"   Passed: {len(results) - failed_count}")
            print(f"   Failed: {failed_count}")
            
            sys.exit(1 if failed_count > 0 else 0)
        else:
            test_parser.print_help()
    
    elif args.command == 'preview':
        from flow_preview import preview_flow
        preview_flow(args.flow_id, flows_dir=args.flows_dir)


if __name__ == "__main__":
    main()