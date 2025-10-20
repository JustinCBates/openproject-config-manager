# Configuration Manager

Interactive configuration management for Docker Compose projects with intelligent discovery and live validation.

## Features

- **Auto-Discovery**: Automatically detects OS, network configuration, Docker installation, available ports, and existing certificates
- **Interactive UI**: Beautiful Rich-based terminal interface with smart defaults
- **Live Validation**: Integrates with docker-prober-utility for real-time configuration testing
- **Configuration Persistence**: Generates `.env` and `.cfg` files for deployment
- **Resumable Sessions**: Can resume interrupted configuration sessions
- **Template Support**: Supports predefined configuration templates for common scenarios

## Purpose

This is a generic, reusable configuration tool designed to work with any Docker Compose project. It eliminates the need for manual configuration file editing by providing an intelligent, interactive setup experience.

## Installation

```bash
pip install openproject-config-manager
```

Or install from source:

```bash
git clone https://github.com/JustinCBates/openproject-config-manager.git
cd openproject-config-manager
pip install -e .
```

## Usage

### Basic Usage

```python
from openproject_config_manager import ConfigurationManager

# Run interactive configuration
config_manager = ConfigurationManager()
result = config_manager.run_interactive(
    template="docker-compose",
    prober_enabled=True
)

# Result includes paths to generated files
print(f"Configuration saved to {result.env_path}")
```

### Command Line Interface

```bash
# Run interactive configuration
config-manager configure --interactive

# Resume interrupted session
config-manager configure --resume

# Use predefined template
config-manager configure --template=production

# Show current configuration
config-manager show

# Validate existing configuration
config-manager validate
```

## Architecture

### Control Flow

```
User Input
    ↓
Discovery Engine (auto-detect environment)
    ↓
Interactive Collector (Rich UI for user input with smart defaults)
    ↓
Validation Engine (validate completeness + live testing with prober)
    ↓
Configuration Finalizer (generate .env and .cfg files)
    ↓
Configuration Output (.env, .cfg)
```

### Components

#### 1. Discovery Engine (`discovery.py`)
**Purpose**: Automatically detect environment characteristics to provide intelligent defaults

**Discovers**:
- Operating system (family, version, distribution)
- Network configuration (hostname, IP addresses, DNS settings)
- Docker installation (version, daemon status, available images)
- Port availability (detect conflicts, suggest alternatives)
- Existing certificates (for HTTPS/TLS configuration)

**Output**: `DiscoveryResults` object with all detected information

#### 2. Interactive Collector (`collector.py`)
**Purpose**: Guide users through configuration with beautiful terminal UI

**Features**:
- Rich-based UI with colors, tables, and panels
- Progressive disclosure (7 configuration sections)
- Real-time input validation
- Smart defaults from discovery results
- Navigation (back, skip, resume)

**Configuration Sections**:
1. Environment Type (production, development, staging)
2. Repository & Version
3. Network Configuration (domain, ports)
4. URL Configuration (prefixes, namespaces)
5. Proxy Configuration (TLS, redirects)
6. Database Configuration
7. Application Storage

#### 3. Validation Engine (`validation.py`)
**Purpose**: Validate configuration completeness and consistency

**Validates**:
- Required fields present
- No conflicting values
- Port availability
- Network reachability
- **Live endpoint testing** (via prober integration)

**Live Validation**:
- Launches minimal test environment
- Tests HTTP/HTTPS endpoints
- Validates TLS configuration
- Tests URL rewriting
- Returns actionable recommendations

#### 4. Prober Client (`prober_client.py`)
**Purpose**: Interface to external docker-prober-utility for live validation

**Modes**:
- **Quick Mode**: Lightweight validation during configuration (fast iteration)
- **Thorough Mode**: Comprehensive validation before finalization

**Integration**: Uses `docker-prober-utility` as external dependency

#### 5. Configuration Finalizer (`finalizer.py`)
**Purpose**: Generate final configuration files

**Actions**:
- Backup existing configurations
- Merge discovery results + user input + validation fixes
- Generate `.env` file (environment variables)
- Generate `.cfg` file (configuration metadata)
- Provide next-step instructions

#### 6. Core Configuration (`core.py`)
**Purpose**: Low-level configuration file operations

**Features**:
- Load from multiple sources (.env, .cfg, environment variables)
- Override chain (env vars > .env > .cfg > defaults)
- Validate configuration schema
- Mask sensitive values in output
- Save to disk with proper formatting

## Implementation Strategy

### Phase 1: Core Configuration (Foundation)
- Implement `core.py` for basic config operations
- Support .env and .cfg file formats
- Implement override chain
- Add validation framework

### Phase 2: Discovery Engine
- Implement OS detection (platform module)
- Implement network discovery (socket, netifaces)
- Implement Docker detection (docker-py)
- Implement port scanning
- Implement certificate detection

### Phase 3: Interactive Collector
- Implement Rich-based UI
- Implement section-based flow
- Add smart defaults from discovery
- Add navigation (back, skip, resume)
- Add session persistence

### Phase 4: Validation Engine
- Implement completeness validation
- Implement consistency checks
- Add prober integration for live testing
- Generate actionable recommendations

### Phase 5: Integration & Polish
- Implement Configuration Finalizer
- Add CLI wrapper
- Add comprehensive tests
- Add documentation
- Add examples

## Dependencies

### Required Dependencies

```toml
dependencies = [
    "python-dotenv>=1.0.0",    # .env file handling
    "pyyaml>=6.0",              # .cfg file handling
    "rich>=13.0.0",             # Terminal UI
    "docker>=7.0.0",            # Docker SDK
    "click>=8.1.0",             # CLI framework
]
```

### External Dependencies

- **docker-prober-utility**: Live validation of HTTP/HTTPS endpoints
  ```toml
  docker-prober-utility @ git+https://github.com/JustinCBates/docker_prober_utility.git@main
  ```

### Development Dependencies

```toml
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/JustinCBates/openproject-config-manager.git
cd openproject-config-manager

# Install in development mode
pip install -e ".[dev]"
```

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=openproject_config_manager --cov-report=term-missing

# Run specific test
pytest tests/test_discovery.py
```

### Code Quality

```bash
# Format code
black src tests

# Lint code
flake8 src tests

# Type checking
mypy src
```

### CI/CD

GitHub Actions workflows are configured for:
- Linting (black, flake8)
- Testing (Python 3.8-3.12)
- Coverage reporting
- Automated releases

## Project Structure

```
openproject-config-manager/
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── .gitignore
│
├── src/
│   └── openproject_config_manager/
│       ├── __init__.py
│       ├── core.py              # Core configuration operations
│       ├── discovery.py         # Environment discovery
│       ├── collector.py         # Interactive UI
│       ├── validation.py        # Validation engine
│       ├── prober_client.py     # Prober integration
│       ├── finalizer.py         # Configuration finalization
│       ├── cli.py               # CLI interface
│       └── utils/
│           ├── __init__.py
│           ├── logging.py
│           └── errors.py
│
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   ├── test_discovery.py
│   ├── test_collector.py
│   ├── test_validation.py
│   ├── test_finalizer.py
│   └── fixtures/
│       └── sample_configs/
│
└── .github/
    └── workflows/
        └── ci.yml
```

## License

MIT

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass and code is formatted
5. Submit a pull request

## Support

- **Issues**: https://github.com/JustinCBates/openproject-config-manager/issues
- **Discussions**: https://github.com/JustinCBates/openproject-config-manager/discussions

## Roadmap

- [ ] Phase 1: Core Configuration (v0.1.0)
- [ ] Phase 2: Discovery Engine (v0.2.0)
- [ ] Phase 3: Interactive Collector (v0.3.0)
- [ ] Phase 4: Validation Engine (v0.4.0)
- [ ] Phase 5: Integration & Polish (v1.0.0)
- [ ] Future: Template library for common projects
- [ ] Future: Configuration import/export
- [ ] Future: Multi-language support
