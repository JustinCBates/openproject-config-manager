# Configuration Examples

This directory contains practical configuration examples for various scenarios and use cases.

## 📁 Example Categories

### Basic Examples
- **`minimal_config.cfg`** - Minimal working configuration
- **`development_config.cfg`** - Typical development environment setup
- **`production_config.cfg`** - Production-ready configuration with security

### Deployment Scenarios
- **`docker_compose/`** - Docker Compose deployment examples
- **`kubernetes/`** - Kubernetes deployment configurations
- **`bare_metal/`** - Direct server installation examples
- **`cloud_providers/`** - Cloud-specific configurations (AWS, GCP, Azure)

### Database Configurations
- **`postgresql/`** - PostgreSQL database configurations
- **`mysql/`** - MySQL database configurations
- **`sqlite/`** - SQLite configurations for development

### Proxy and SSL
- **`caddy/`** - Caddy reverse proxy configurations
- **`nginx/`** - Nginx reverse proxy configurations
- **`ssl_certificates/`** - SSL certificate management examples
- **`lets_encrypt/`** - Let's Encrypt automation examples

### Special Configurations
- **`high_availability/`** - High availability setups
- **`backup_strategies/`** - Backup and disaster recovery
- **`monitoring/`** - Monitoring and logging configurations
- **`security_hardening/`** - Security-focused configurations

## 📖 Using Examples

### File Naming Convention
- **`.cfg`** - Configuration manager native format
- **`.env`** - Environment variable format
- **`.yaml`** - YAML format for Docker Compose
- **`.json`** - JSON format for APIs

### Example Structure
Each example directory contains:
- **`README.md`** - Description and usage instructions
- **Configuration files** - Ready-to-use configurations
- **`docker-compose.yml`** - Docker Compose setup (if applicable)
- **`setup.sh`** - Automated setup script (if needed)

### Testing Examples
All examples are tested to ensure they work correctly:
```bash
# Test an example configuration
cd examples/production_config/
./test_config.sh
```

## 🚀 Quick Start Examples

### Development Setup
```bash
# Copy and customize development example
cp examples/development_config.cfg my_config.cfg
# Edit my_config.cfg for your environment
```

### Production Deployment
```bash
# Use production template
cp examples/production_config.cfg openproject.cfg
# Review and customize security settings
```

## 📝 Contributing Examples

When adding new examples:
1. Create a dedicated directory for the scenario
2. Include a comprehensive README
3. Test the configuration thoroughly
4. Document any prerequisites
5. Add to the appropriate category above

### Example Template
```
examples/
├── new_scenario/
│   ├── README.md           # Description and instructions
│   ├── config.cfg          # Main configuration
│   ├── docker-compose.yml  # Docker setup (if applicable)
│   └── test_config.sh      # Validation script
```

## 🔗 Related Documentation

- **Configuration Reference** - See `../api/` for configuration options
- **User Guides** - See `../guides/` for step-by-step tutorials
- **Troubleshooting** - See `../guides/troubleshooting.md` for common issues

For contribution guidelines, see `../project/CONTRIBUTING.md`.