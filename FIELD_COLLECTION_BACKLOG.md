# Config-Manager Field Collection Backlog

**Created**: October 15, 2025  
**Purpose**: Track which fields from the legacy interactive_config.cfg are being collected in the new config-manager system

---

## Legacy Configuration Fields (from interactive_config.cfg)

This document tracks the 19 configuration fields collected by the old interactive configuration system and maps them to the new config-manager collection system.

---

## Status Legend

- ✅ **COLLECTED** - Field is being collected in current config-manager
- 🔄 **MAPPED** - Similar/equivalent field collected with different name
- ❌ **MISSING** - Field is NOT currently collected
- 📋 **BACKLOG** - Needs investigation/implementation
- 🎯 **ENHANCED** - New system handles this better with multiple fields

---

## Field Mapping Analysis

### 1. Proxy & TLS Configuration

| Legacy Field | Status | Current Field(s) | Location | Notes |
|--------------|--------|-----------------|----------|-------|
| `PROXY_TLS_MODE` | 📋 **BACKLOG** | None | N/A | Need to collect: internal/letsencrypt/letsencrypt_staging |
| `PROXY_HTTPS_REDIRECT` | 📋 **BACKLOG** | None | N/A | HTTP→HTTPS redirect setting |
| `PROXY_BIND_ADDRESS` | 📋 **BACKLOG** | None | N/A | Network binding (0.0.0.0 vs localhost) |
| `PROXY_HTTP_PORT` | 🔄 **MAPPED** | `port` | network.layout.yml | May need separate HTTP/HTTPS ports |
| `PROXY_HTTPS_PORT` | 📋 **BACKLOG** | None | N/A | HTTPS port (443) - currently only one `port` field |

### 2. Project & Identity

| Legacy Field | Status | Current Field(s) | Location | Notes |
|--------------|--------|-----------------|----------|-------|
| `GIT_USERNAME` | 📋 **BACKLOG** | None | N/A | For commits/automation |
| `GIT_EMAIL` | 🔄 **MAPPED** | `admin_email` | project_basics.layout.yml | Reusing admin_email, but may need separate |
| `ENVIRONMENT_TYPE` | 🔄 **MAPPED** | `environment` | environment.layout.yml | dev/staging/production |

### 3. OpenProject Configuration

| Legacy Field | Status | Current Field(s) | Location | Notes |
|--------------|--------|-----------------|----------|-------|
| `OPENPROJECT_TAG` | 📋 **BACKLOG** | None | N/A | Docker image tag (stable/16) |
| `OPENPROJECT_HOST_NAME` | 🎯 **ENHANCED** | `domain` | network.layout.yml | New system uses domain |
| `OPENPROJECT_HTTPS` | 📋 **BACKLOG** | None | N/A | Boolean: enable HTTPS (true/false) |

### 4. Domain & Networking

| Legacy Field | Status | Current Field(s) | Location | Notes |
|--------------|--------|-----------------|----------|-------|
| `DOMAIN_NAME` | ✅ **COLLECTED** | `domain` | network.layout.yml | ✅ Mapped directly |
| `URI_NAMESPACE_ENABLED` | 📋 **BACKLOG** | None | N/A | Boolean: enable URI namespacing |
| `URI_NAMESPACE` | 📋 **BACKLOG** | None | N/A | Path prefix (e.g., "StatesmenProjects") |

### 5. Operating System

| Legacy Field | Status | Current Field(s) | Location | Notes |
|--------------|--------|-----------------|----------|-------|
| `OS_FAMILY` | 📋 **BACKLOG** | None | N/A | debian/rhel/arch - Should be auto-detected |

### 6. Database Configuration

| Legacy Field | Status | Current Field(s) | Location | Notes |
|--------------|--------|-----------------|----------|-------|
| `DEFAULT_DBADMIN_PASSWORD` | 🔄 **MAPPED** | `postgres_password` | database.layout.yml | Different name, same purpose |
| `DATABASE_STORAGE_TYPE` | 📋 **BACKLOG** | None | N/A | docker-volumes vs bind-mounts |

### 7. Currently Collected (New Fields)

These fields are collected in the new system but weren't in the legacy config:

| New Field | Location | Purpose |
|-----------|----------|---------|
| `project_name` | project_basics.layout.yml | Project identifier |
| `admin_email` | project_basics.layout.yml | Administrator email |
| `admin_password` | project_basics.layout.yml | Admin user password |
| `postgres_db` | database.layout.yml | Database name |
| `postgres_user` | database.layout.yml | Database username |
| `memory_limit` | resources.layout.yml | Container memory limit |
| `backup_retention` | resources.layout.yml | Backup retention days |

---

## Summary Statistics

**Total Legacy Fields**: 19

**Status Breakdown**:
- ✅ Collected: 1 (5%)
- 🔄 Mapped: 4 (21%)
- 📋 Backlog: 13 (68%)
- 🎯 Enhanced: 1 (5%)

**Missing from New System**: 13 fields (68%)

---

## Priority Action Items

### 🔴 High Priority (Core Functionality)

1. **PROXY_TLS_MODE** - Critical for TLS configuration
   - Values: `internal`, `letsencrypt`, `letsencrypt_staging`
   - Add to: network.layout.yml or new tls.layout.yml
   - Field type: select/radio

2. **OPENPROJECT_TAG** - Docker image version
   - Values: `stable/16`, `stable/15`, `dev`, etc.
   - Add to: project_basics.layout.yml or new docker.layout.yml
   - Field type: text with validation

3. **OPENPROJECT_HTTPS** - Enable/disable HTTPS
   - Values: `true`, `false`
   - Add to: network.layout.yml
   - Field type: confirm (boolean)

4. **URI_NAMESPACE_ENABLED** - Enable path-based routing
   - Values: `true`, `false`
   - Add to: network.layout.yml
   - Field type: confirm (boolean)

5. **URI_NAMESPACE** - URL path prefix
   - Values: string (e.g., "StatesmenProjects")
   - Add to: network.layout.yml
   - Field type: text (conditional on URI_NAMESPACE_ENABLED)

### 🟡 Medium Priority (Important but can use defaults)

6. **PROXY_HTTP_PORT** / **PROXY_HTTPS_PORT** - Split port field
   - Current: Single `port` field
   - Proposed: Add `http_port` and `https_port` to network.layout.yml

7. **PROXY_HTTPS_REDIRECT** - Auto-redirect HTTP→HTTPS
   - Values: `true`, `false`
   - Add to: network.layout.yml
   - Field type: confirm (boolean)

8. **DATABASE_STORAGE_TYPE** - Storage backend choice
   - Values: `docker-volumes`, `bind-mounts`
   - Add to: database.layout.yml or resources.layout.yml
   - Field type: select

9. **GIT_USERNAME** - For automation/commits
   - Add to: project_basics.layout.yml
   - Field type: text

### 🟢 Low Priority (Auto-detect or use defaults)

10. **OS_FAMILY** - Operating system detection
    - Should be auto-detected in Phase 1 (Discovery)
    - Add to: enhanced_defaults.yml output
    - May not need user input

11. **PROXY_BIND_ADDRESS** - Network binding
    - Default: `0.0.0.0` (all interfaces)
    - Edge case: `127.0.0.1` (localhost only)
    - Add to: network.layout.yml (advanced section)

12. **GIT_EMAIL** - Separate from admin_email
    - Currently reusing `admin_email`
    - Consider: Keep as is or add separate field

---

## Implementation Plan

### Phase 1: Core Missing Fields (High Priority)
**Target**: Add 5 critical fields
**Estimated Effort**: 2-3 hours

1. Create new sublayout: `tls.layout.yml`
   - PROXY_TLS_MODE (select)
   - OPENPROJECT_HTTPS (confirm)
   - PROXY_HTTPS_REDIRECT (confirm)

2. Enhance `network.layout.yml`
   - URI_NAMESPACE_ENABLED (confirm)
   - URI_NAMESPACE (text, conditional)

3. Enhance `project_basics.layout.yml`
   - OPENPROJECT_TAG (text with validation)

### Phase 2: Enhanced Port Handling (Medium Priority)
**Target**: Split port configuration
**Estimated Effort**: 1-2 hours

1. Update `network.layout.yml`
   - Replace single `port` with `http_port` and `https_port`
   - Add conditional logic (only show HTTPS port if HTTPS enabled)

### Phase 3: Storage & Git Configuration (Medium Priority)
**Target**: Add 3 configuration fields
**Estimated Effort**: 1-2 hours

1. Update `database.layout.yml`
   - DATABASE_STORAGE_TYPE (select)

2. Update `project_basics.layout.yml`
   - GIT_USERNAME (text)
   - Consider separate GIT_EMAIL field

### Phase 4: Auto-Detection Enhancement (Low Priority)
**Target**: Reduce manual input via auto-detection
**Estimated Effort**: 2-3 hours

1. Enhance Phase 1 (Discovery)
   - Auto-detect OS_FAMILY
   - Auto-detect PROXY_BIND_ADDRESS based on environment
   - Add to enhanced_defaults.yml

---

## Notes

### Field Naming Conventions

**Legacy vs New**:
- Legacy used SCREAMING_SNAKE_CASE
- New system uses lowercase_snake_case
- This is intentional for better consistency

### URL/Domain Handling Improvement

The new system handles domain/URL configuration better:
- **Legacy**: Separate OPENPROJECT_HOST_NAME and DOMAIN_NAME (confusing)
- **New**: Single `domain` field with better validation
- **Enhancement**: Can add protocol, ports, namespace as separate fields

### Conditional Fields

Several new fields should be conditional:
- `URI_NAMESPACE` only shown if `URI_NAMESPACE_ENABLED=true`
- `https_port` only shown if `OPENPROJECT_HTTPS=true`
- This improves UX by reducing clutter

### Discovery Phase Integration

Some fields should come from Phase 1 Discovery:
- `OS_FAMILY` - Auto-detected
- `PROXY_BIND_ADDRESS` - Inferred from environment type
- These reduce manual user input and errors

---

## Questions for Resolution

1. **Port Configuration**: Should we keep single `port` field or split into `http_port`/`https_port`?
2. **Git Identity**: Should GIT_EMAIL be separate from admin_email or reuse it?
3. **TLS Layout**: Should TLS config be in network.layout.yml or separate tls.layout.yml?
4. **Advanced Fields**: Should PROXY_BIND_ADDRESS be in main flow or "advanced" section?
5. **Version Selection**: Should OPENPROJECT_TAG be freeform text or dropdown with known versions?

---

## Related Files

- Current layouts: `/opt/openproject/external/config-manager/phases/phase_3_collection/step_1_collect_user_configuration/layouts/`
- Legacy config: `/opt/openproject/scripts/installation_scripts/interactive_config.cfg`
- Discovery output: `/opt/openproject/external/config-manager/phases/phase_1_discovery/outputs/discovery/enhanced_defaults.yml`

---

**Next Steps**: Review this backlog and prioritize which fields to implement first based on deploy-manager requirements.
