#!/usr/bin/env python3
"""Preview and test individual flows."""

import argparse
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the engine
sys.path.append(str(Path(__file__).parent.parent))

try:
    from engine.flow_engine import FlowEngine
    import questionary
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the ui_flow_designer directory")
    print("and that questionary is installed: pip install questionary")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Preview configuration flows')
    parser.add_argument('--flow', required=True, help='Flow ID to preview')
    parser.add_argument('--step', help='Specific step to preview')
    parser.add_argument('--context', help='JSON string with context data')
    
    args = parser.parse_args()
    
    # Determine flows directory
    flows_dir = Path(__file__).parent.parent / "flows"
    engine = FlowEngine(flows_dir=str(flows_dir))
    
    try:
        if args.step:
            # Preview single step (would need additional implementation)
            questionary.print(f"Single step preview not yet implemented", style="bold yellow")
        else:
            # Preview entire flow
            questionary.print(f"🔍 Previewing flow: {args.flow}", style="bold blue")
            
            # Basic context for testing
            context = {
                'proxy': {'domain': 'example.com'},
                'discovered_data': {}
            }
            
            try:
                result = engine.execute_flow(args.flow, context)
                questionary.print("\n✅ Flow completed successfully!", style="bold green")
                questionary.print(f"📋 Results:", style="bold")
                for key, value in result.items():
                    questionary.print(f"   {key}: {value}")
                    
            except KeyboardInterrupt:
                questionary.print("\n⚠️ Flow cancelled by user", style="bold yellow")
            except Exception as e:
                questionary.print(f"\n❌ Flow failed: {e}", style="bold red")
                raise
                
    except FileNotFoundError as e:
        questionary.print(f"❌ {e}", style="bold red")
        questionary.print(f"Available flows in {flows_dir}:", style="dim")
        if flows_dir.exists():
            for flow_file in flows_dir.glob("*.yml"):
                questionary.print(f"   - {flow_file.stem}")
        sys.exit(1)
    except Exception as e:
        questionary.print(f"❌ Error: {e}", style="bold red")
        sys.exit(1)


if __name__ == '__main__':
    main()