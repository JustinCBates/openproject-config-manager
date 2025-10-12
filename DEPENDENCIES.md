# Dependencies for OpenProject Config Manager

## Production Dependencies (Required for all users)

### Absolute (Always needed)
- click>=8.1.0                 # CLI framework
- rich>=13.0.0                 # Terminal UI/formatting  
- pydantic>=2.0.0              # Data validation
- python-dotenv>=1.0.0         # Environment variables
- pyyaml>=6.0.0                # YAML parsing

### Ad Hoc (Needed for optional features)
- docker>=7.0.0                # Docker integration (if using docker features)
- requests>=2.31.0             # HTTP requests (if using external services)
- psutil>=5.9.0                # System monitoring (if using system discovery)
- cryptography>=41.0.0         # SSL/crypto (if generating certificates)
- netifaces>=0.11.0            # Network interfaces (if doing network discovery)

## Developer Dependencies (Only needed for development)

### Absolute (Core development tools)
- pytest>=7.0.0                # Testing framework
- pytest-json-report           # Test reporting
- black>=23.0.0                # Code formatting
- flake8>=6.0.0                # Code linting
- mypy>=1.0.0                  # Type checking

### Ad Hoc (Optional development tools)
- pytest-cov>=4.0.0            # Test coverage (if doing coverage analysis)
- pytest-mock>=3.11.0          # Test mocking (if doing advanced testing)
- bandit>=1.7.0                # Security linting (if doing security analysis)
- safety>=2.3.0                # Security scanning (if scanning dependencies)
- sphinx>=5.0.0                # Documentation (if generating docs)

## System Dependencies
- git                          # Version control
- python>=3.8                  # Python runtime

## Installation Commands

### Production Only (Minimal)
```bash
pip install click rich pydantic python-dotenv pyyaml
```

### Development Environment
```bash
pip install -e ".[dev]"
```

### With Optional Features
```bash
# Docker integration
pip install docker

# System monitoring
pip install psutil netifaces

# Security features
pip install cryptography

# External service integration  
pip install requests
```

## Notes
- Production dependencies are defined in pyproject.toml
- This file tracks what we've discovered during development
- Update this file when adding new dependencies
- Use this file to update documentation