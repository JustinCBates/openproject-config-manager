# Integration & Enhancement Backlog

**Last Updated**: October 16, 2025  
**Repository**: openproject-config-manager  
**Status**: Planning

---

## Overview

This document tracks planned integrations and enhancements for the Config Manager beyond current field collection capabilities.

---

## 1. Prober Integration (Live Validation)

**Priority**: Low (Future Enhancement)  
**Status**: Not Implemented  
**Estimated Effort**: 6-8 hours  
**Owner**: Unassigned

### Problem Statement

Currently, config-manager validates configurations statically (syntax, schema, required fields). It cannot validate against live system state:
- Are ports actually available?
- Is Docker daemon responsive?
- Are network endpoints reachable?
- Does the host have sufficient resources?

### Proposed Solution

Integrate with `docker-prober-utility` to enable live validation during configuration generation.

### User Story

> As a DevOps engineer configuring a deployment, I want config-manager to validate my settings against the actual target system, so I can catch issues before deployment.

### Acceptance Criteria

- [ ] Config-manager can call prober HTTP endpoints
- [ ] Prober validates Docker daemon connectivity
- [ ] Prober checks port availability for configured services
- [ ] Prober validates network connectivity to required endpoints
- [ ] Results displayed in interactive TUI with actionable errors
- [ ] Validation failures show specific remediation steps
- [ ] Can disable prober validation via flag (`--no-prober`)
- [ ] Gracefully handles prober service unavailable

### Technical Design

**Architecture**:
```
config-manager (TUI)
    ↓
prober_client.py (HTTP client)
    ↓
docker-prober-utility (Flask service)
    ↓
System Validation (ports, docker, resources)
```

**Implementation Tasks**:

1. **Create prober_client.py module** (2 hours)
   - HTTP client with retry logic
   - Timeout handling (5s default)
   - Fallback when prober unavailable
   - Error parsing and formatting
   
   ```python
   # Example API
   from config_manager.prober_client import ProberClient
   
   prober = ProberClient(url="http://localhost:8080", timeout=5)
   result = prober.validate_ports([80, 443, 5432])
   
   if not result.all_available:
       print(f"Ports in use: {result.unavailable_ports}")
   ```

2. **Integrate with validation pipeline** (2 hours)
   - Add validation step after schema validation
   - Call prober for live checks
   - Display results in TUI
   - Add to validation report

3. **Update ConfigManager class** (1 hour)
   - Add `prober_enabled` parameter (already exists as stub)
   - Add `prober_url` configuration
   - Wire up prober_client calls
   
   ```python
   manager = ConfigManager(
       prober_enabled=True,
       prober_url="http://localhost:8080"
   )
   ```

4. **Error Handling** (1 hour)
   - Prober service not reachable → warning, not failure
   - Timeout → graceful degradation
   - Invalid response → log and continue
   - Provide helpful error messages

5. **Testing** (2 hours)
   - Unit tests for prober_client
   - Mock prober responses
   - Test timeout scenarios
   - Test unavailable service
   - Integration test with real prober

6. **Documentation** (1 hour)
   - Update README with prober integration
   - Add configuration examples
   - Document troubleshooting
   - Update DUAL_MODE_ORCHESTRATION.md

### Dependencies

**External**:
- docker-prober-utility service must be running
- Network connectivity to prober service
- Prober API must be stable (see prober/BACKLOG.md)

**Internal**:
- None (prober_enabled stub already exists)

### Configuration

**Environment Variables**:
```bash
PROBER_ENABLED=true              # Enable/disable prober validation
PROBER_URL=http://localhost:8080 # Prober service URL
PROBER_TIMEOUT=5                 # Timeout in seconds
```

**pyproject.toml**:
```toml
[tool.config-manager.prober]
enabled = true
url = "http://localhost:8080"
timeout = 5
fail_on_unavailable = false  # Don't fail if prober unreachable
```

### API Contract (Prober)

What we need from prober:

```
POST /v1/validate/ports
Body: {"ports": [80, 443, 5432]}
Response: {"available": [80, 443], "in_use": [5432]}

GET /v1/validate/docker
Response: {"status": "healthy", "version": "24.0.5", "containers": 12}

POST /v1/validate/endpoints
Body: {"urls": ["http://api.example.com", "https://db.example.com:5432"]}
Response: {"reachable": [...], "unreachable": [...]}

GET /v1/validate/resources
Response: {"disk_free_gb": 50, "memory_free_gb": 8, "cpu_usage": 25}
```

### Migration Path

**Phase 1**: Optional validation (default: disabled)
- Add prober_client module
- Implement basic port checking
- Document in README

**Phase 2**: Enable by default with fallback
- Enable prober_enabled=True by default
- Gracefully handle unavailable service
- Show validation results in TUI

**Phase 3**: Advanced validation
- Resource checks (disk, memory)
- Docker daemon validation
- Endpoint reachability
- Historical data comparison

### Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Prober service down | Validation unavailable | Fail gracefully, show warning |
| Network latency | Slow validation | Add timeout, make async |
| API changes | Integration breaks | Version API, graceful degradation |
| False positives | User confusion | Clear error messages, override flag |

### Success Metrics

- **Adoption**: % of users with prober_enabled=True
- **Value**: # of issues caught by prober validation
- **Reliability**: % of validations that complete successfully
- **Performance**: Average validation time < 2s

### Related Work

- Prober backlog: `external/prober/BACKLOG.md`
- Deploy-manager integration: `external/deploy-manager/...` (prober_runner.py)
- Current README references: Lines 237-244 (mentioned but not implemented)

### References

- **Documentation**: Lines in README mentioning prober (aspirational)
- **Stub Parameters**: `prober_enabled=True` in codebase
- **Similar Tools**: 
  - Docker healthchecks
  - Kubernetes readiness probes
  - Ansible preflight checks

---

## 2. GitHub Secrets Integration

**Priority**: Medium  
**Status**: Idea  
**Estimated Effort**: 4-6 hours

### Problem

Users must manually enter secrets during configuration. No integration with GitHub Secrets for automated deployments.

### Proposed Solution

Read secrets from GitHub Secrets API during CI/CD, populate config automatically.

### Tasks

- [ ] Research GitHub Secrets API
- [ ] Add authentication mechanism
- [ ] Create secrets fetcher
- [ ] Update config generation
- [ ] Test in GitHub Actions

---

## 3. Configuration Templates Library

**Priority**: Medium  
**Status**: Idea  
**Estimated Effort**: 3-5 hours

### Problem

Users start from scratch each time. Common patterns repeated.

### Proposed Solution

Pre-built configuration templates for common scenarios:
- Basic web app (nginx + app + postgres)
- Microservices (multiple services)
- Development environment
- Production environment

### Tasks

- [ ] Create template structure
- [ ] Build 5-10 common templates
- [ ] Add template selector to TUI
- [ ] Document template format
- [ ] Allow user-defined templates

---

## 4. Configuration Diff Viewer

**Priority**: Low  
**Status**: Idea  
**Estimated Effort**: 2-3 hours

### Problem

Hard to see what changed between config versions.

### Proposed Solution

Side-by-side diff viewer in TUI showing changes between configs.

### Tasks

- [ ] Add diff library (difflib or similar)
- [ ] Create comparison view
- [ ] Highlight changes
- [ ] Add to TUI navigation

---

## 5. Import from Existing docker-compose.yml

**Priority**: High  
**Status**: Idea  
**Estimated Effort**: 6-8 hours

### Problem

Users with existing docker-compose.yml must recreate config manually.

### Proposed Solution

Parse existing docker-compose.yml and import into config-manager format.

### Tasks

- [ ] YAML parser for docker-compose
- [ ] Map docker-compose fields to config schema
- [ ] Handle unsupported fields
- [ ] Validation after import
- [ ] Add import command to CLI

---

## Decision Log

### 2025-10-16: Prober Integration Status

**Decision**: Mark as "NOT IMPLEMENTED - FUTURE FEATURE"

**Rationale**:
- Extensive documentation exists but no code
- Stub parameters present but unused
- No user demand yet
- Other priorities more important

**Action**:
- Add to backlog for future consideration
- Keep stub parameters (harmless)
- Mark clearly in documentation
- Revisit when integration need identified

---

## Contributing

To propose new backlog items:
1. Create GitHub issue with "enhancement" label
2. Include problem statement and proposed solution
3. Estimate effort and priority
4. Tag with relevant components

---

## Review Schedule

**Quarterly Review**: Reassess priorities based on:
- User feedback
- Issues reported
- Strategic direction
- Available resources

**Next Review**: Q1 2026
