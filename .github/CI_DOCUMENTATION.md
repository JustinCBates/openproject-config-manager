# CI/CD Pipeline Documentation

This document describes the comprehensive CI/CD pipeline setup for the openproject-config-manager repository.

## Pipeline Overview

The CI/CD pipeline consists of multiple workflows that ensure code quality, security, and reliable releases:

### 🔄 Main CI Pipeline (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` 
- Release publications

**Jobs:**

1. **Code Quality (`lint`)**
   - Black code formatting check
   - Flake8 linting
   - MyPy type checking
   - Import sorting (isort)

2. **Security Scanning (`security`)**
   - Bandit security linting
   - Safety dependency vulnerability check
   - Uploads security reports as artifacts

3. **Test Matrix (`test`)**
   - **OS Coverage**: Ubuntu, Windows, macOS
   - **Python Versions**: 3.8, 3.9, 3.10, 3.11, 3.12
   - **Optimized Matrix**: Reduced combinations for faster CI
   - Coverage reporting to Codecov

4. **Integration Tests (`integration`)**
   - Docker-based integration testing
   - Prober utility integration
   - Real Docker daemon testing

5. **Documentation (`docs`)**
   - Sphinx documentation build
   - HTML output generation

6. **Performance Tests (`performance`)**
   - Benchmark testing (main branch only)
   - Performance regression detection

7. **Build & Package (`build`)**
   - Python package building
   - Package validation with twine

8. **Release (`release`)**
   - Automated PyPI publishing
   - Triggered only on GitHub releases
   - Uses trusted publishing (OIDC)

### 🔒 Security Workflows

**CodeQL Analysis (`codeql.yml`)**
- Weekly scheduled security scans
- GitHub security advisory integration
- Advanced security query sets

**Dependency Review (`dependency-review`)**
- PR-based dependency analysis
- Vulnerability detection in new dependencies

### 🤖 Automation Workflows

**Dependabot (`dependabot.yml`)**
- Weekly dependency updates
- Auto-approval for patch updates
- Auto-merge for safe updates

## Configuration Files

### Code Quality Tools

**`.flake8`**
```ini
max-line-length = 88
extend-ignore = E203, E501, W503
max-complexity = 10
```

**`pyproject.toml`** (tool configurations)
- Black formatting (line-length: 88)
- isort import sorting
- MyPy type checking
- pytest configuration
- Coverage settings

### GitHub Templates

**Issue Templates:**
- Bug reports (`.github/ISSUE_TEMPLATE/bug_report.yml`)
- Feature requests (`.github/ISSUE_TEMPLATE/feature_request.yml`)

**Pull Request Template:**
- Standardized PR format
- Checklist for contributors
- Type classification

## Environment Setup

### Required Secrets

For automated releases, configure these repository secrets:

1. **`PYPI_API_TOKEN`**
   - PyPI API token for package publishing
   - Scope: Entire account or specific project

2. **`CODECOV_TOKEN`** (optional)
   - For private repositories
   - Enhances coverage reporting

### Branch Protection

Recommended branch protection rules for `main`:

```yaml
protection_rules:
  required_status_checks:
    - "Code Quality"
    - "Test Suite (ubuntu-latest, 3.11)"
    - "Integration Tests" 
    - "Build Package"
  require_branches_to_be_up_to_date: true
  required_reviews: 1
  dismiss_stale_reviews: true
  require_code_owner_reviews: true
  required_linear_history: true
```

## Local Development

### Pre-commit Setup

Install development dependencies:
```bash
pip install -e ".[dev]"
```

Run quality checks locally:
```bash
# Code formatting
black src tests

# Linting
flake8 src tests

# Type checking
mypy src

# Import sorting
isort src tests

# Tests with coverage
pytest --cov=openproject_config_manager
```

### Git Hooks (Recommended)

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

## Performance Monitoring

### Benchmark Tests

Performance tests run automatically on `main` branch:

```bash
pytest tests/performance/ --benchmark-json=results.json
```

### Coverage Targets

- **Minimum Coverage**: 80%
- **Target Coverage**: 90%
- **Critical Paths**: 95%+ (discovery, validation)

## Deployment Process

### Automated Release Flow

1. **Version Bump**
   ```bash
   # Update version in pyproject.toml
   git tag v0.2.0
   git push origin v0.2.0
   ```

2. **GitHub Release**
   - Create release from tag
   - Add release notes
   - CI automatically publishes to PyPI

### Manual Release (Emergency)

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

## Monitoring & Alerts

### CI Failure Notifications

The pipeline includes a notification job that triggers on main branch failures. Configure notifications by updating the `notify` job in `ci.yml`.

**Available Integrations:**
- Slack webhooks
- Email notifications
- Discord webhooks
- Microsoft Teams

### Dependency Monitoring

Dependabot provides:
- Weekly dependency updates
- Security vulnerability alerts
- Automated PR creation
- Auto-merge for safe updates

## Troubleshooting

### Common CI Issues

**1. Test Failures on Specific OS/Python**
```bash
# Run specific matrix combination locally
python3.9 -m pytest tests/
```

**2. Coverage Drops**
```bash
# Generate detailed coverage report
pytest --cov=openproject_config_manager --cov-report=html
open htmlcov/index.html
```

**3. Security Scan Failures**
```bash
# Run security checks locally
bandit -r src/
safety check
```

**4. Integration Test Failures**
```bash
# Check Docker availability
docker info
docker run hello-world
```

### Performance Issues

**Slow CI Pipeline:**
- Review matrix size in `ci.yml`
- Consider caching improvements
- Optimize test selection

**Large Artifacts:**
- Review artifact retention policies
- Compress large reports
- Clean up old artifacts

## Contributing

### Code Quality Standards

All contributions must pass:
- ✅ Code formatting (Black)
- ✅ Linting (Flake8)
- ✅ Type checking (MyPy)
- ✅ Security scanning (Bandit)
- ✅ Test coverage (>80%)
- ✅ Integration tests

### Review Process

1. Fork repository
2. Create feature branch
3. Make changes with tests
4. Run local quality checks
5. Submit pull request
6. Address review feedback
7. Merge after approval

---

**Last Updated**: October 11, 2025  
**Maintainer**: OpenProject Config Manager Team