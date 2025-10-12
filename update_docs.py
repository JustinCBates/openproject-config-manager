#!/usr/bin/env python3
"""
Simple documentation updater that reads dependency files and updates documentation.

Usage:
    python update_docs.py                    # Update all documentation
    python update_docs.py --repo config-manager  # Update specific repo docs
"""

import argparse
from pathlib import Path
import re


def parse_dependencies_file(file_path):
    """Parse a DEPENDENCIES.md file and extract dependency information."""
    if not file_path.exists():
        return None
    
    content = file_path.read_text()
    
    # Extract dependencies by category
    deps = {
        "production_absolute": [],
        "production_adhoc": [],
        "developer_absolute": [],
        "developer_adhoc": [],
        "system": []
    }
    
    current_section = None
    
    for line in content.split('\n'):
        line = line.strip()
        
        # Track sections
        if "Production Dependencies" in line:
            current_category = "production"
        elif "Developer Dependencies" in line:
            current_category = "developer"
        elif "System Dependencies" in line or "System Requirements" in line:
            current_category = "system"
        elif "### Absolute" in line:
            current_section = f"{current_category}_absolute"
        elif "### Ad Hoc" in line:
            current_section = f"{current_category}_adhoc"
        
        # Extract dependency lines (start with -)
        if line.startswith('- ') and current_section:
            # Extract package name and description
            match = re.match(r'- ([^#\s]+).*?# (.+)', line)
            if match:
                package, description = match.groups()
                deps[current_section].append({
                    "package": package,
                    "description": description.strip()
                })
            elif current_section == "system":
                # System deps might not have # comments
                package = line[2:].split()[0]
                deps[current_section].append({
                    "package": package,
                    "description": "System dependency"
                })
    
    return deps


def update_readme_dependencies(readme_path, deps, repo_name):
    """Update README.md with dependency information."""
    if not readme_path.exists():
        print(f"⚠️  README not found: {readme_path}")
        return False
    
    content = readme_path.read_text()
    
    # Generate dependency section
    dep_section = f"\n## Dependencies\n\n"
    
    # Production dependencies
    if deps["production_absolute"] or deps["production_adhoc"]:
        dep_section += "### Production (End Users)\n\n"
        
        if deps["production_absolute"]:
            dep_section += "**Required:**\n"
            for dep in deps["production_absolute"]:
                dep_section += f"- `{dep['package']}` - {dep['description']}\n"
            dep_section += "\n"
        
        if deps["production_adhoc"]:
            dep_section += "**Optional Features:**\n"
            for dep in deps["production_adhoc"]:
                dep_section += f"- `{dep['package']}` - {dep['description']}\n"
            dep_section += "\n"
    
    # Developer dependencies
    if deps["developer_absolute"] or deps["developer_adhoc"]:
        dep_section += "### Development (Contributors)\n\n"
        
        if deps["developer_absolute"]:
            dep_section += "**Required:**\n"
            for dep in deps["developer_absolute"]:
                dep_section += f"- `{dep['package']}` - {dep['description']}\n"
            dep_section += "\n"
        
        if deps["developer_adhoc"]:
            dep_section += "**Optional Tools:**\n"
            for dep in deps["developer_adhoc"]:
                dep_section += f"- `{dep['package']}` - {dep['description']}\n"
            dep_section += "\n"
    
    # System dependencies
    if deps["system"]:
        dep_section += "### System Requirements\n\n"
        for dep in deps["system"]:
            dep_section += f"- `{dep['package']}` - {dep['description']}\n"
        dep_section += "\n"
    
    # Find existing dependencies section or add new one
    dep_pattern = r'\n## Dependencies.*?(?=\n## |\n# |\Z)'
    
    if re.search(dep_pattern, content, re.DOTALL):
        # Replace existing section
        content = re.sub(dep_pattern, dep_section, content, flags=re.DOTALL)
        print(f"✅ Updated existing dependencies section in {readme_path}")
    else:
        # Add new section before installation if it exists, otherwise at the end
        install_pattern = r'\n## Installation'
        if re.search(install_pattern, content):
            content = re.sub(install_pattern, dep_section + "\n## Installation", content)
        else:
            content += dep_section
        print(f"✅ Added new dependencies section to {readme_path}")
    
    readme_path.write_text(content)
    return True


def main():
    parser = argparse.ArgumentParser(description="Update documentation from dependency files")
    parser.add_argument("--repo", help="Specific repo to update (main, config-manager, deploy-manager, prober, control, proxy)")
    
    args = parser.parse_args()
    
    print("📚 Documentation Updater")
    print("=" * 30)
    
    # Define repos and their paths
    repos = {
        "main": {
            "deps_file": Path("/opt/openproject/DEPENDENCIES.md"),
            "readme_file": Path("/opt/openproject/README.md")
        },
        "config-manager": {
            "deps_file": Path("/opt/openproject/external/config-manager/DEPENDENCIES.md"),
            "readme_file": Path("/opt/openproject/external/config-manager/README.md")
        },
        "deploy-manager": {
            "deps_file": Path("/opt/openproject/external/deploy-manager/DEPENDENCIES.md"),
            "readme_file": Path("/opt/openproject/external/deploy-manager/README.md")
        },
        "prober": {
            "deps_file": Path("/opt/openproject/external/prober/DEPENDENCIES.md"),
            "readme_file": Path("/opt/openproject/external/prober/README.md")
        },
        "control": {
            "deps_file": Path("/opt/openproject/control/DEPENDENCIES.md"),
            "readme_file": Path("/opt/openproject/control/README.md")
        },
        "proxy": {
            "deps_file": Path("/opt/openproject/proxy/DEPENDENCIES.md"),
            "readme_file": Path("/opt/openproject/proxy/README.md")
        }
    }
    
    # Filter to specific repo if requested
    if args.repo:
        if args.repo in repos:
            repos = {args.repo: repos[args.repo]}
        else:
            print(f"❌ Unknown repo: {args.repo}")
            print(f"Available repos: {', '.join(repos.keys())}")
            return 1
    
    success_count = 0
    total_count = 0
    
    for repo_name, paths in repos.items():
        total_count += 1
        print(f"\n📦 Processing {repo_name}...")
        
        # Parse dependencies
        deps = parse_dependencies_file(paths["deps_file"])
        if not deps:
            print(f"⚠️  No dependencies file found: {paths['deps_file']}")
            continue
        
        # Update README
        if update_readme_dependencies(paths["readme_file"], deps, repo_name):
            success_count += 1
    
    print(f"\n🎉 Updated {success_count}/{total_count} repositories")
    
    if success_count == total_count:
        print("✅ All documentation updated successfully!")
        return 0
    else:
        print("⚠️  Some updates failed - check the output above")
        return 1


if __name__ == "__main__":
    exit(main())