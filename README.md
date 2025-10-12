# Configuration Manager

Interactive configuration management for Docker Compose projects with intelligent discover### Phase 4: Final Configuration Export
```
Export for Deployment
├── Generate primary .cfg file (interactive_config.cfg)
├── Convert .cfg to .env format (for Docker Compose)
├── Create template variables (for Jinja2 rendering)
└── Hand off to Deploy Manager
```ve validation.

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

The Configuration Manager follows a **4-phase control flow** designed for maximum automation and validation:

#### **Phase 1: Environment Discovery & Probing**
```
OS Probe → Generate .cfg.defaults
├── Detect OS (Linux distro, version, architecture)  
├── Scan network interfaces & available IPs
├── Check Docker installation & version
├── Scan available ports (80, 443, 8080, etc.)
├── Detect existing SSL certificates
├── Check system resources (RAM, disk space)
└── Write .cfg.defaults with intelligent defaults
```

#### **Phase 2: Interactive Configuration Collection**
```
Rich Interactive UI → Generate .cfg
├── Load .cfg.defaults as starting point
├── Present Rich-based prompts with smart defaults
├── Collect user preferences:
│   ├── Domain name & SSL preferences
│   ├── Port configurations  
│   ├── Database settings
│   ├── Email/IMAP configuration
│   └── Advanced options (if requested)
├── Real-time validation during input
└── Save final .cfg file
```

#### **Phase 3: Pre-Deploy Validation**  
```
Validation Pass → Prober Integration
├── Load .cfg file
├── Validate configuration completeness
├── Use Prober utility for live testing:
│   ├── DNS resolution checks
│   ├── Port availability testing
│   ├── SSL certificate validation
│   └── Network connectivity tests
├── Present validation results
└── Option to loop back to Phase 2 if issues found
```

#### **Phase 4: Final Configuration Export**
```
Export for Deployment
├── Convert .cfg to .env format
├── Generate Docker Compose overrides
├── Prepare Jinja2 template variables
└── Hand off to Deploy Manager
```

**Key Design Principle**: The user can loop between Phases 2 and 3 until all validation passes, ensuring a bulletproof configuration before deployment.

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

**Primary Output**: `interactive_config.cfg` file
- **Format**: Bash-style key="value" pairs
- **Content**: Complete deployment configuration
- **Usage**: Consumed by Deployment Manager for build process

**Secondary Outputs**:
- `.env` file (Docker Compose environment variables)
- Template variables (for Jinja2 rendering)
- Configuration backup and metadata

**Configuration File Structure**:
```bash
# interactive_config.cfg
# Core OpenProject Configuration
DOMAIN_NAME="myproject.example.com"
OPENPROJECT_HTTPS="true"
PORT="8080"

# Database Configuration  
DATABASE_URL="postgres://..."
POSTGRES_PASSWORD="secure_password"

# Deployment Settings
PROXY_TYPE="caddy"
PROBER_ENABLED="true"
# ... (see interactive_config.cfg.example for complete format)
```
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

### Production (End Users)

**Required:**
- `click>=8.1.0` - CLI framework
- `rich>=13.0.0` - Terminal UI/formatting
- `pydantic>=2.0.0` - Data validation
- `python-dotenv>=1.0.0` - Environment variables
- `pyyaml>=6.0.0` - YAML parsing

**Optional Features:**
- `docker>=7.0.0` - Docker integration (if using docker features)
- `requests>=2.31.0` - HTTP requests (if using external services)
- `psutil>=5.9.0` - System monitoring (if using system discovery)
- `cryptography>=41.0.0` - SSL/crypto (if generating certificates)
- `netifaces>=0.11.0` - Network interfaces (if doing network discovery)

### Development (Contributors)

**Required:**
- `pytest>=7.0.0` - Testing framework
- `pytest-json-report` - Test reporting
- `black>=23.0.0` - Code formatting
- `flake8>=6.0.0` - Code linting
- `mypy>=1.0.0` - Type checking

**Optional Tools:**
- `pytest-cov>=4.0.0` - Test coverage (if doing coverage analysis)
- `pytest-mock>=3.11.0` - Test mocking (if doing advanced testing)
- `bandit>=1.7.0` - Security linting (if doing security analysis)
- `safety>=2.3.0` - Security scanning (if scanning dependencies)
- `sphinx>=5.0.0` - Documentation (if generating docs)
- `git` - Version control
- `python>=3.8` - Python runtime


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
