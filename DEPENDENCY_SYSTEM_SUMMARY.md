# Simple Dependency Tracking System

## Overview

Created a simple, practical dependency tracking system with 4 permutations:
- **Absolute/Ad-Hoc**: Required vs Optional
- **Production/Developer**: End users vs Contributors

## What We Built

### 1. Dependency Files (`DEPENDENCIES.md`)
Each repo now has a simple markdown file tracking discovered dependencies:

#### `/opt/openproject/DEPENDENCIES.md` (Main Repo)
- Docker, Docker Compose (absolute production)
- Git, curl, openssl (ad-hoc production)
- Development tools (git, make, etc.)

#### `/opt/openproject/external/config-manager/DEPENDENCIES.md`
- Python packages organized by type
- Clear production vs development separation
- Installation commands for different scenarios

#### `/opt/openproject/external/deploy-manager/DEPENDENCIES.md`
- System tools focus (docker, docker-compose)
- Python dependencies as code is added
- Development tools for shell scripts

#### `/opt/openproject/external/prober/DEPENDENCIES.md`
- Flask-based dependencies
- Optional features (requests, psutil, docker)
- Testing dependencies

### 2. Installation Helpers

#### `/opt/openproject/check_deps.sh`
- Simple bash script to check system dependencies
- Auto-install option for missing packages
- Cross-platform support (Linux/macOS)

#### `/opt/openproject/external/config-manager/install_deps.py`
- Smart Python dependency installer
- Supports different modes (minimal, production, development)
- Optional feature installation (--features docker,ssl)
- Optional dev tools (--dev-tools coverage,security)

### 3. Documentation Updater

#### `/opt/openproject/external/config-manager/update_docs.py`
- Reads DEPENDENCIES.md files
- Updates README.md files automatically
- Maintains consistent documentation

## Usage Examples

### Check System Dependencies
```bash
# Check what's installed
./check_deps.sh

# Auto-install missing dependencies
./check_deps.sh --install
```

### Install Python Dependencies
```bash
# Minimal production setup
python install_deps.py --mode minimal

# Full development environment
python install_deps.py --mode development

# Production with optional features
python install_deps.py --mode production --features docker,ssl,system

# Development with extra tools
python install_deps.py --mode development --dev-tools coverage,security
```

### Update Documentation
```bash
# Update all repo documentation
python update_docs.py

# Update specific repo
python update_docs.py --repo config-manager
```

## Benefits

1. **Simple**: Just markdown files tracking what we find
2. **Practical**: Installation helpers for common scenarios
3. **Flexible**: Ad-hoc dependencies installed only when needed
4. **Maintainable**: Easy to update as we develop
5. **Cross-repo**: Each repo tracks its own dependencies

## Maintenance

1. **Add new dependencies**: Update the relevant DEPENDENCIES.md file
2. **Test installation**: Use the helper scripts to verify setup
3. **Update docs**: Run update_docs.py to sync README files
4. **Keep it simple**: Don't over-engineer, just track what we discover

## File Structure
```
/opt/openproject/
├── DEPENDENCIES.md           # Main repo dependencies
├── check_deps.sh            # System dependency checker
├── control/
│   └── DEPENDENCIES.md      # Control component dependencies
├── proxy/
│   └── DEPENDENCIES.md      # Proxy component dependencies
└── external/
    ├── config-manager/
    │   ├── DEPENDENCIES.md   # Python package dependencies
    │   ├── install_deps.py   # Python dependency installer
    │   └── update_docs.py    # Documentation updater
    ├── deploy-manager/
    │   └── DEPENDENCIES.md   # Deploy tool dependencies
    └── prober/
        └── DEPENDENCIES.md   # Prober service dependencies
```

This system grows organically as we develop and discover new dependencies, without over-engineering upfront.