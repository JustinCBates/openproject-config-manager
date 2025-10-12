"""Main CLI entry point for OpenProject Configuration Manager."""

import sys
import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler

from .core.manager import ConfigurationManager
from .ui.console import ConsoleUI


# Setup rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)
console = Console()


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--project-root', '-p', type=click.Path(exists=True, file_okay=False), 
              help='Project root directory')
@click.pass_context
def cli(ctx, verbose, project_root):
    """OpenProject Configuration Manager
    
    Interactive configuration management for Docker Compose projects with 
    intelligent discovery and live validation.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['project_root'] = project_root
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.option('--output', '-o', type=click.Path(), 
              help='Output file path (default: interactive_config.cfg)')
@click.pass_context
def configure(ctx, output):
    """Run the complete 4-phase configuration process."""
    verbose = ctx.obj['verbose']
    project_root = ctx.obj['project_root']
    
    try:
        manager = ConfigurationManager(
            project_root=project_root,
            verbose=verbose
        )
        
        # Run full configuration process
        config_file = manager.run_full_process(output_path=output)
        
        console.print(f"\n[bold green]✓ Configuration complete![/bold green]")
        console.print(f"Configuration saved to: [cyan]{config_file}[/cyan]")
        console.print("\nYou can now use this configuration file with the deployment manager:")
        console.print(f"[dim]deploy-manager --config {config_file}[/dim]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Configuration cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        # Escape the error message to prevent Rich markup issues
        error_msg = str(e).replace('[', '\\[').replace(']', '\\]')
        console.print(f"\n[red]Configuration failed: {error_msg}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), 
              help='Output file path (default: update existing file)')
@click.pass_context
def update(ctx, config_file, output):
    """Update an existing configuration file."""
    verbose = ctx.obj['verbose']
    project_root = ctx.obj['project_root']
    
    try:
        manager = ConfigurationManager(
            project_root=project_root,
            config_file=config_file,
            verbose=verbose
        )
        
        # Load existing configuration
        manager.load_existing_configuration(config_file)
        
        # Run discovery to get current environment
        manager.run_discovery_phase()
        
        # Update configuration
        updated_file = manager.update_configuration()
        
        console.print(f"\n[bold green]✓ Configuration updated![/bold green]")
        console.print(f"Updated configuration saved to: [cyan]{updated_file}[/cyan]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Update cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Update failed: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option('--output-dir', '-o', type=click.Path(), default='output',
              help='Output directory for generated files (default: output)')
@click.option('--flow', '-f', default='openproject_main_config',
              help='Flow name to execute (default: openproject_main_config)')
@click.option('--mock-file', '-m', type=click.Path(exists=True),
              help='JSON file with mock responses for testing')
@click.pass_context
def collect(ctx, output_dir, flow, mock_file):
    """Collect configuration using TUI Form Engine workflows."""
    verbose = ctx.obj['verbose']
    project_root = ctx.obj['project_root']
    
    console = Console()
    
    try:
        # Import the TUI collector
        from .collector.tui_collector import OpenProjectConfigCollector
        
        # Initialize collector
        collector = OpenProjectConfigCollector(
            flows_dir=str(Path(project_root) / "flows"),
            output_dir=output_dir
        )
        
        if mock_file:
            # Test mode with mock responses
            console.print(f"🧪 Testing flow '{flow}' with mock responses from {mock_file}")
            import json
            with open(mock_file) as f:
                mock_responses = json.load(f)
            
            config = collector.test_flow(flow, mock_responses)
            console.print("✅ Test completed successfully!")
            
        else:
            # Interactive mode
            console.print(f"🎯 Starting interactive configuration collection...")
            config = collector.collect_configuration(flow)
        
        console.print(f"\n🎉 Configuration collection complete!")
        console.print(f"📁 Output directory: {output_dir}")
        console.print(f"✅ Ready for deployment!")
        
    except ImportError as e:
        console.print(f"❌ TUI Form Engine not available: {e}")
        console.print("💡 Install with: pip install tui-form-engine")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Configuration collection failed: {e}")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.pass_context
def validate(ctx, config_file):
    """Validate an existing configuration file."""
    verbose = ctx.obj['verbose']
    project_root = ctx.obj['project_root']
    
    try:
        manager = ConfigurationManager(
            project_root=project_root,
            config_file=config_file,
            verbose=verbose
        )
        
        # Load configuration
        configuration = manager.load_existing_configuration(config_file)
        
        # Run discovery for validation context
        discovered_data = manager.run_discovery_phase()
        
        # Validate configuration
        validation_result = manager.validator.validate_configuration(
            configuration, discovered_data
        )
        
        # Display results
        ui = ConsoleUI()
        
        if validation_result.is_valid:
            ui.show_success("Configuration validation passed!")
        else:
            ui.show_error("Configuration validation failed!")
        
        if validation_result.errors:
            ui.show_section_header("Errors")
            for error in validation_result.errors:
                ui.show_error(error)
        
        if validation_result.warnings:
            ui.show_section_header("Warnings")
            for warning in validation_result.warnings:
                ui.show_warning(warning)
        
        if validation_result.recommendations:
            ui.show_section_header("Recommendations")
            for recommendation in validation_result.recommendations:
                ui.show_info(recommendation)
        
        sys.exit(0 if validation_result.is_valid else 1)
        
    except Exception as e:
        console.print(f"\n[red]Validation failed: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.pass_context
def discover(ctx):
    """Run discovery phase only to scan the environment."""
    verbose = ctx.obj['verbose']
    project_root = ctx.obj['project_root']
    
    try:
        manager = ConfigurationManager(
            project_root=project_root,
            verbose=verbose
        )
        
        # Run discovery
        discovered_data = manager.run_discovery_phase()
        
        # Display results
        ui = ConsoleUI()
        ui.show_title("Discovery Results")
        
        # Environment data
        env_data = discovered_data.get('environment', {})
        if env_data:
            ui.show_section_header("Environment Variables")
            ui.show_info(f"Found {env_data.get('relevant_count', 0)} relevant environment variables")
            if env_data.get('sensitive_count', 0) > 0:
                ui.show_warning(f"{env_data['sensitive_count']} sensitive variables detected")
        
        # System data
        system_data = discovered_data.get('system', {})
        if system_data:
            ui.show_section_header("System Information")
            platform_info = system_data.get('platform', {})
            ui.show_info(f"Platform: {platform_info.get('system', 'Unknown')} {platform_info.get('release', '')}")
            ui.show_info(f"Hostname: {platform_info.get('hostname', 'Unknown')}")
            
            hardware_info = system_data.get('hardware', {})
            if 'memory' in hardware_info:
                memory_gb = hardware_info['memory'].get('total_gb', 0)
                ui.show_info(f"Memory: {memory_gb:.1f} GB")
        
        # Docker data
        docker_data = discovered_data.get('docker', {})
        if docker_data:
            ui.show_section_header("Docker Environment")
            if docker_data.get('docker_available'):
                ui.show_success("Docker is available")
                containers = docker_data.get('containers', [])
                ui.show_info(f"Found {len(containers)} containers")
                
                openproject_containers = docker_data.get('openproject_containers', [])
                if openproject_containers:
                    ui.show_warning(f"Found {len(openproject_containers)} existing OpenProject containers")
                
                db_containers = docker_data.get('database_containers', [])
                if db_containers:
                    ui.show_info(f"Found {len(db_containers)} database containers")
            else:
                ui.show_error("Docker is not available")
        
        console.print("\n[bold green]✓ Discovery complete![/bold green]")
        
    except Exception as e:
        console.print(f"\n[red]Discovery failed: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['cfg', 'env']), default='cfg',
              help='Export format (cfg or env)')
@click.option('--output', '-o', type=click.Path(),
              help='Output file path')
@click.pass_context
def export(ctx, config_file, format, output):
    """Export configuration to different formats."""
    verbose = ctx.obj['verbose']
    project_root = ctx.obj['project_root']
    
    try:
        manager = ConfigurationManager(
            project_root=project_root,
            config_file=config_file,
            verbose=verbose
        )
        
        # Load configuration
        configuration = manager.load_existing_configuration(config_file)
        
        # Determine output path
        if not output:
            base_name = Path(config_file).stem
            if format == 'cfg':
                output = f"{base_name}.cfg"
            elif format == 'env':
                output = f"{base_name}.env"
        
        # Export based on format
        if format == 'cfg':
            exported_path = manager.exporter.write_configuration(configuration, output)
        elif format == 'env':
            exported_path = manager.exporter.write_docker_compose_env(configuration, output)
        
        console.print(f"\n[bold green]✓ Export complete![/bold green]")
        console.print(f"Configuration exported to: [cyan]{exported_path}[/cyan]")
        
    except Exception as e:
        console.print(f"\n[red]Export failed: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    from . import __version__
    console.print(f"OpenProject Configuration Manager v{__version__}")


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()