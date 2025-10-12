# Dependency Management System

This directory contains all dependency tracking and management files for the config-manager component.

## Files

### Documentation
- **`DEPENDENCIES.md`** - Dependency specification for this component
- **`DEPENDENCY_SYSTEM_SUMMARY.md`** - Overview of the complete dependency system

### Tools
- **`install_deps.py`** - Smart Python dependency installer with mode selection
- **`update_docs.py`** - Documentation updater that syncs README files

## Usage

### Install Dependencies
```bash
# Minimal production setup
cd dependencies
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
# Update all repo documentation from dependency files
cd dependencies
python update_docs.py

# Update specific repo
python update_docs.py --repo config-manager
```

## Dependency Classification

The system uses a **4-permutation classification**:

### Production Dependencies
- **Absolute**: Required for all installations
- **Ad-Hoc**: Context-dependent (based on environment)

### Developer Dependencies  
- **Absolute**: Required for development
- **Ad-Hoc**: Optional development tools

## System Architecture

```
Dependencies System:
├── DEPENDENCIES.md (per repo)     # Simple markdown tracking
├── Installation helpers           # Smart installers
├── Documentation automation       # Auto-sync README files
└── Cross-repo support            # Works across all 6 components
```

## Cross-Repository Support

This dependency system works across all OpenProject repositories:
- **Main repo**: System dependencies (Docker, Git, etc.)
- **Config-manager**: Python packages and development tools
- **Deploy-manager**: Deployment tools and utilities
- **Prober**: Flask service and monitoring dependencies
- **Control**: PostgreSQL tools and backup utilities
- **Proxy**: Caddy server and networking tools

## Design Philosophy

- **Simple**: Markdown files that grow organically
- **Practical**: Installation helpers for different scenarios
- **Cross-platform**: Works on various operating systems
- **Automatic**: Documentation stays in sync
- **Organic Growth**: Add dependencies as you discover them

## System Benefits

1. **🎯 Simple Tracking**: Easy markdown format
2. **🔧 Smart Installation**: Context-aware installers
3. **📚 Auto Documentation**: README files stay current
4. **🌍 Cross-Platform**: Works on Linux, macOS, Windows
5. **📊 Complete Coverage**: All 6 components tracked
6. **🔄 Organic Growth**: Evolves with your project