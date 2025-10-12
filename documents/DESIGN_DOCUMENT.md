# Configuration Manager - Detailed Design Document

## Context & Purpose

This document captures the comprehensive design for the **Configuration Manager** component of the OpenProject Python rebuild project. This is part of a larger multi-repository architecture transformation.

### Project Background

- **Repository**: `openproject-config-manager` (standalone, reusable)
- **Parent Project**: OpenProject Docker Compose Python rebuild
- **Architecture**: Multi-repo design with 4 repositories total
- **Status**: Currently in migration from main repo to standalone submodule

### Related Repositories

1. **openproject-docker-compose** (main) - Integration + Maintenance Manager
2. **openproject-config-manager** (this repo) - Configuration discovery & collection
3. **openproject-deploy-manager** - Deployment orchestration
4. **docker-prober-utility** - HTTP/HTTPS validation utility

## Design Philosophy

### Core Principles

1. **Discovery First**: Automatically probe environment before asking user questions
2. **Smart Defaults**: Use discovered information to provide intelligent defaults
3. **Interactive Excellence**: Rich terminal UI with progressive disclosure
4. **Validation Loop**: Allow users to iterate between configuration and validation
5. **Standalone Reusability**: Works for any Docker Compose project, not just OpenProject

### Target User Experience

```bash
# Single command starts entire flow
config-manager configure

# System automatically:
# 1. Probes environment (30 seconds)
# 2. Presents interactive prompts with smart defaults
# 3. Validates configuration with live testing
# 4. Loops back for fixes if needed
# 5. Exports final .cfg/.env for deployment
```

## Control Flow Architecture

### Phase 1: Environment Discovery & Probing

**Purpose**: Generate `.cfg.defaults` file with intelligent defaults based on system detection

**Implementation Module**: `discovery.py`

**Discovery Tasks**:

1. **Operating System Detection**
   ```python
   os_info = {
       'family': 'linux',           # linux, darwin, windows
       'distribution': 'ubuntu',    # ubuntu, centos, debian, etc.
       'version': '22.04',          # OS version
       'architecture': 'x86_64'     # x86_64, arm64, etc.
   }
   ```

2. **Network Configuration**
   ```python
   network_info = {
       'hostname': 'myserver.local',
       'interfaces': ['eth0', 'wlan0'],
       'primary_ip': '192.168.1.100',
       'external_ip': '203.0.113.42',  # via external API
       'dns_servers': ['8.8.8.8', '1.1.1.1']
   }
   ```

3. **Docker Environment**
   ```python
   docker_info = {
       'installed': True,
       'version': '24.0.5',
       'daemon_running': True,
       'user_access': True,         # can run without sudo
       'compose_version': '2.20.2'
   }
   ```

4. **Port Availability Scanning**
   ```python
   port_scan = {
       'available_ports': [80, 443, 8080, 8443],
       'conflicting_services': {
           '80': 'apache2',
           '443': 'nginx'
       },
       'suggested_ports': [8080, 8443]
   }
   ```

5. **SSL Certificate Detection**
   ```python
   ssl_info = {
       'letsencrypt_available': True,
       'existing_certs': ['/etc/ssl/certs/mysite.pem'],
       'certbot_installed': True,
       'domains_configured': ['example.com']
   }
   ```

6. **System Resources**
   ```python
   resources = {
       'memory_gb': 16,
       'disk_space_gb': 500,
       'cpu_cores': 8,
       'docker_limits': {'memory': '2g', 'cpus': '2.0'}
   }
   ```

**Output**: `.cfg.defaults` file with intelligent defaults for interactive session

### Phase 2: Interactive Configuration Collection

**Purpose**: Guide user through Rich-based terminal UI to collect final configuration

**Implementation Module**: `collector.py`

**UI Framework**: Rich library with panels, tables, progress bars, and color coding

**Configuration Sections** (Progressive Disclosure):

1. **Environment Type Selection**
   ```
   ┌─ Environment Type ─────────────────────────────┐
   │ What type of deployment is this?                │
   │                                                │
   │ › Production (public-facing, high security)    │
   │   Development (local testing)                  │
   │   Staging (pre-production testing)             │
   └───────────────────────────────────────────────┘
   ```

2. **Repository & Version**
   ```
   ┌─ Application Configuration ────────────────────┐
   │ OpenProject Version: [16-slim     ] (latest)   │
   │ Custom Tag:         [             ] (optional) │
   │ Repository:         [openproject/... ] (auto)  │
   └───────────────────────────────────────────────┘
   ```

3. **Network Configuration**
   ```
   ┌─ Network Configuration ────────────────────────┐
   │ Domain Name:    [myproject.example.com      ]  │
   │ Primary Port:   [8080] (detected available)    │
   │ HTTPS Port:     [8443] (detected available)    │
   │ Enable HTTPS:   [Yes] No                       │
   └───────────────────────────────────────────────┘
   ```

4. **URL Configuration**
   ```
   ┌─ URL Configuration ────────────────────────────┐
   │ URL Prefix:     [/openproject] (optional)      │
   │ Namespace:      [            ] (optional)      │
   │ Full URL:       https://myproject.example.com  │
   └───────────────────────────────────────────────┘
   ```

5. **Proxy Configuration**
   ```
   ┌─ Proxy Configuration ──────────────────────────┐
   │ Reverse Proxy:  [Caddy] Nginx None             │
   │ SSL Termination:[Auto ] Manual Custom          │
   │ HTTP Redirect:  [Yes] No                       │
   │ Rate Limiting:  Yes [No]                       │
   └───────────────────────────────────────────────┘
   ```

6. **Database Configuration**
   ```
   ┌─ Database Configuration ───────────────────────┐
   │ Database Type:  [PostgreSQL] MySQL             │
   │ Version:        [13] 14 15 16                  │
   │ Memory Limit:   [2GB] (based on system RAM)    │
   │ Storage Path:   [/var/lib/postgresql/data   ]  │
   └───────────────────────────────────────────────┘
   ```

7. **Application Storage**
   ```
   ┌─ Storage Configuration ────────────────────────┐
   │ Data Directory: [/var/openproject/data      ]  │
   │ Asset Storage:  [local] s3 gcs azure          │
   │ Backup Storage: [local] s3 gcs azure          │
   │ Log Retention:  [30] days                     │
   └───────────────────────────────────────────────┘
   ```

**Navigation Features**:
- **Back**: Return to previous section
- **Skip**: Skip optional sections
- **Resume**: Resume interrupted sessions
- **Preview**: Show current configuration
- **Help**: Context-sensitive help

**Real-time Validation**: Validate inputs as user types (port conflicts, domain format, etc.)

**Output**: `.cfg` file with complete user configuration

### Phase 3: Pre-Deploy Validation

**Purpose**: Comprehensive validation with live testing using Prober utility

**Implementation Module**: `validation.py`

**Validation Categories**:

1. **Configuration Completeness**
   ```python
   completeness_check = {
       'required_fields': ['domain', 'ports', 'database'],
       'missing_fields': [],
       'conflicting_values': [],
       'warnings': ['http_redirect_without_ssl']
   }
   ```

2. **Live Network Testing** (via Prober)
   ```python
   prober_tests = {
       'dns_resolution': True,      # Domain resolves to correct IP
       'port_accessibility': True,  # Ports 80/443 reachable
       'ssl_validation': False,     # SSL cert issues
       'url_rewriting': True,       # Proxy rules work
       'health_checks': True        # App endpoints respond
   }
   ```

3. **Resource Validation**
   ```python
   resource_check = {
       'disk_space': 'sufficient',     # >10GB available
       'memory': 'adequate',           # >4GB available
       'docker_permissions': True,     # User can run Docker
       'port_conflicts': []            # No conflicting services
   }
   ```

**Validation Results Display**:
```
┌─ Validation Results ────────────────────────────────────┐
│ ✓ Configuration completeness                            │
│ ✓ DNS resolution (myproject.example.com → 203.0.113.42)│
│ ✓ Port accessibility (8080, 8443)                      │
│ ✗ SSL certificate invalid                               │
│ ✓ URL rewriting rules                                   │
│ ⚠ Low disk space (8GB available, 10GB recommended)     │
│                                                         │
│ [Fix Issues] [Deploy Anyway] [Reconfigure]             │
└─────────────────────────────────────────────────────────┘
```

**Loop Back Option**: If validation fails, user can:
- **Fix Issues**: Return to Phase 2 to modify configuration
- **Deploy Anyway**: Proceed despite warnings
- **Abort**: Exit configuration process

### Phase 4: Final Configuration Export

**Purpose**: Generate deployment-ready configuration files

**Implementation Module**: `finalizer.py`

**Export Formats**:

1. **Docker Compose .env File**
   ```bash
   # Generated by openproject-config-manager
   OPENPROJECT_HOST__NAME=myproject.example.com
   OPENPROJECT_HTTPS=true
   OPENPROJECT_TAG=16-slim
   PORT=8080
   SSL_PORT=8443
   DATABASE_URL=postgres://postgres:password@db/openproject
   ```

2. **Configuration .cfg File** (for scripts)
   ```bash
   # Configuration metadata
   DOMAIN_NAME="myproject.example.com"
   HTTPS_ENABLED="true"
   PRIMARY_PORT="8080"
   SSL_PORT="8443"
   PROXY_TYPE="caddy"
   ```

3. **Jinja2 Template Variables** (for Deploy Manager)
   ```python
   template_vars = {
       'domain': 'myproject.example.com',
       'https_enabled': True,
       'ports': {'http': 8080, 'https': 8443},
       'proxy_config': {...},
       'database_config': {...}
   }
   ```

**Additional Outputs**:
- **Summary Report**: Human-readable configuration summary
- **Next Steps**: Instructions for deployment
- **Rollback Info**: How to restore previous configuration

## Technical Implementation

### Module Structure

```
src/openproject_config_manager/
├── __init__.py
├── main.py                 # Main orchestrator
├── discovery.py            # Phase 1: Environment probing
├── collector.py            # Phase 2: Interactive UI
├── validation.py           # Phase 3: Validation & prober integration
├── finalizer.py            # Phase 4: Export generation
├── prober_client.py        # Prober utility interface
├── config_formats.py       # .cfg/.env file handling
└── ui/
    ├── __init__.py
    ├── sections.py          # Rich UI sections
    ├── navigation.py        # UI navigation logic
    └── themes.py            # Rich themes and styling
```

### Key Dependencies

```toml
dependencies = [
    "rich>=13.0.0",           # Terminal UI
    "click>=8.1.0",           # CLI framework
    "python-dotenv>=1.0.0",   # .env file handling
    "pyyaml>=6.0",            # .cfg file handling
    "docker>=7.0.0",          # Docker SDK for discovery
    "requests>=2.31.0",       # HTTP requests for external IP
    "psutil>=5.9.0",          # System resource detection
    "netifaces>=0.11.0",      # Network interface detection
]
```

### External Integration

**Prober Utility Integration**:
```python
from docker_prober_utility import ProberClient

prober = ProberClient()
results = prober.validate_configuration({
    'domain': 'myproject.example.com',
    'ports': [8080, 8443],
    'ssl_enabled': True,
    'proxy_config': {...}
})
```

## Session Management

### Resumable Sessions

**Session File**: `.config-session.json`
```json
{
    "session_id": "uuid-string",
    "started_at": "2025-10-11T14:30:00Z",
    "current_phase": 2,
    "current_section": "network_configuration",
    "discovery_results": {...},
    "user_inputs": {...},
    "validation_results": {...}
}
```

**Resume Logic**:
- Detect interrupted sessions on startup
- Offer to resume or start fresh
- Restore user inputs and continue from last section
- Preserve discovery results (expensive to regenerate)

### Backup & Rollback

**Configuration Backup**:
- Backup existing `.env`/`.cfg` files before modification
- Create timestamped backup directory
- Provide rollback command to restore previous configuration

## Error Handling

### Graceful Degradation

1. **Discovery Failures**: Use fallback defaults if discovery fails
2. **Prober Unavailable**: Skip live validation, show warning
3. **Network Issues**: Cache results, work offline where possible
4. **Permission Issues**: Provide clear instructions for resolution

### User-Friendly Error Messages

```
❌ Discovery Error: Docker daemon not accessible

💡 Solution:
   1. Start Docker daemon: sudo systemctl start docker
   2. Add user to docker group: sudo usermod -aG docker $USER
   3. Log out and back in, then retry

[Retry] [Skip Docker Detection] [Exit]
```

## Testing Strategy

### Unit Tests
- **discovery.py**: Mock system calls, test detection logic
- **collector.py**: Test UI logic, input validation
- **validation.py**: Mock prober responses, test validation rules
- **finalizer.py**: Test file generation, template rendering

### Integration Tests
- **Full Flow**: End-to-end configuration flow
- **Prober Integration**: Real prober utility testing
- **File I/O**: Real file system operations
- **Docker Integration**: Real Docker daemon interaction

### Test Data
- **Sample Environments**: Various OS/Docker configurations
- **Mock Responses**: Prober utility responses
- **Configuration Templates**: Known-good configurations

## Future Enhancements

### Template Library
- **Predefined Templates**: Production, development, staging configurations
- **Project Types**: OpenProject, WordPress, Django, etc.
- **Cloud Providers**: AWS, GCP, Azure optimized configurations

### Advanced Features
- **Configuration Diff**: Compare configurations visually
- **Import/Export**: Share configurations between environments
- **Team Collaboration**: Multi-user configuration workflows
- **Monitoring Integration**: Connect to monitoring systems

### Internationalization
- **Multi-language Support**: Translate UI to multiple languages
- **Regional Defaults**: Country-specific default configurations
- **Currency/Date Formats**: Localized formatting

## Documentation Requirements

### User Documentation
- **Quick Start Guide**: Get running in 5 minutes
- **Configuration Reference**: All available options
- **Troubleshooting Guide**: Common issues and solutions
- **Best Practices**: Recommended configurations

### Developer Documentation
- **API Reference**: Complete module documentation
- **Plugin Development**: Extend for new project types
- **Testing Guide**: How to run and write tests
- **Contributing Guide**: Code style, PR process

---

## Version History

- **v0.1.0**: Core configuration file handling (current main repo implementation)
- **v0.2.0**: Environment discovery engine (planned)
- **v0.3.0**: Interactive Rich UI (planned)
- **v0.4.0**: Prober integration and validation (planned)
- **v1.0.0**: Complete feature set with documentation (target)

---

*Last Updated: October 11, 2025*  
*Author: OpenProject Python Rebuild Team*