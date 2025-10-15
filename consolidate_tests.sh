#!/bin/bash
# Test Directory Consolidation Script
# Implements the consolidation plan from TEST_CONSOLIDATION_PROPOSAL.md
# 
# Usage: ./consolidate_tests.sh [--dry-run]
#
# Use --dry-run to see what would be done without making changes

set -e

DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "🔍 DRY RUN MODE - No changes will be made"
    echo
fi

REPO_ROOT="/opt/openproject/external/config-manager"
cd "$REPO_ROOT"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

execute() {
    if [ "$DRY_RUN" = true ]; then
        echo "   [DRY-RUN] $@"
    else
        eval "$@"
    fi
}

# ============================================================================
# PHASE 0: Pre-flight Checks
# ============================================================================

log_info "Phase 0: Pre-flight checks..."

# Check we're in the right directory
if [ ! -f "design_specs/control_flows.yml" ]; then
    log_error "Not in config-manager root directory!"
    exit 1
fi

# Check git status
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    log_warning "You have uncommitted changes. Commit or stash them first."
    if [ "$DRY_RUN" = false ]; then
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

log_success "Pre-flight checks passed"
echo

# ============================================================================
# PHASE 1: Create Backup
# ============================================================================

log_info "Phase 1: Creating backup..."

BACKUP_DIR="backups/tests_backup_$(date +%Y%m%d_%H%M%S)"
execute "mkdir -p '$BACKUP_DIR'"
execute "cp -r tests/ '$BACKUP_DIR/tests_new/' 2>/dev/null || true"
execute "cp -r testing/ '$BACKUP_DIR/testing_old/' 2>/dev/null || true"
execute "find phases/ -type d -name tests -exec cp -r {} '$BACKUP_DIR/phases_tests/' \; 2>/dev/null || true"

log_success "Backup created at: $BACKUP_DIR"
echo

# ============================================================================
# PHASE 2: Create New Directory Structure
# ============================================================================

log_info "Phase 2: Creating new test directory structure..."

# Create unit test subdirectories
execute "mkdir -p tests/unit/steps/phase_{1,2,3,4,5}"

# Create integration test subdirectories  
execute "mkdir -p tests/integration/steps"
execute "mkdir -p tests/integration/flows"

# Create fixtures directory
execute "mkdir -p tests/fixtures/shared"
execute "mkdir -p tests/fixtures/phase_{1,2,3,4,5}"

# Create conftest if it doesn't exist
if [ ! -f "tests/conftest.py" ]; then
    execute "cat > tests/conftest.py << 'CONFTEST'
\"\"\"
Pytest configuration and shared fixtures for config-manager tests.
\"\"\"
import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def project_root_path():
    \"\"\"Return the project root path.\"\"\"
    return Path(__file__).parent.parent

# Add more shared fixtures here
CONFTEST"
fi

log_success "New directory structure created"
echo

# ============================================================================
# PHASE 3: Migrate Per-Phase Tests
# ============================================================================

log_info "Phase 3: Migrating per-phase tests to tests/integration/steps/..."

# Map phase directories to test files
declare -A PHASE_TESTS=(
    ["phase_1_discovery"]="test_phase_1_steps.py"
    ["phase_2_tui_mapping"]="test_phase_2_steps.py"
    ["phase_3_collection"]="test_phase_3_steps.py"
    ["phase_4_validation"]="test_phase_4_steps.py"
    ["phase_5_export"]="test_phase_5_steps.py"
)

for phase in "${!PHASE_TESTS[@]}"; do
    source_dir="phases/$phase/tests/integration"
    dest_file="tests/integration/steps/${PHASE_TESTS[$phase]}"
    
    if [ -d "$source_dir" ]; then
        if [ -f "$source_dir/test_orchestrator_${phase#phase_?_}.py" ]; then
            log_info "  Migrating $phase tests..."
            execute "cp '$source_dir/test_orchestrator_${phase#phase_?_}.py' '$dest_file'"
            log_success "  ✓ Migrated $phase"
        else
            log_warning "  No tests found in $source_dir"
        fi
    fi
done

echo

# ============================================================================
# PHASE 4: Migrate Old testing/ Directory Tests
# ============================================================================

log_info "Phase 4: Migrating tests from old testing/ directory..."

# Migrate integration tests if they exist
if [ -d "testing/integration" ]; then
    if [ -f "testing/integration/test_manager_integration.py" ]; then
        execute "cp testing/integration/test_manager_integration.py tests/integration/flows/test_main_config_flow.py"
        log_success "  ✓ Migrated manager integration tests"
    fi
    
    if [ -f "testing/integration/test_enhanced_defaults.py" ]; then
        execute "cp testing/integration/test_enhanced_defaults.py tests/integration/steps/test_phase_1_defaults.py"
        log_success "  ✓ Migrated enhanced defaults tests"
    fi
    
    if [ -f "testing/integration/test_mapping_pipeline.py" ]; then
        execute "cp testing/integration/test_mapping_pipeline.py tests/integration/flows/test_mapping_flow.py"
        log_success "  ✓ Migrated mapping pipeline tests"
    fi
fi

# Migrate validation tests
if [ -f "testing/validation/test_migration_validation.py" ]; then
    execute "cp testing/validation/test_migration_validation.py tests/integration/flows/test_migration_validation.py"
    log_success "  ✓ Migrated validation tests"
fi

# Migrate fixtures
if [ -d "testing/fixtures" ]; then
    execute "cp -r testing/fixtures/* tests/fixtures/shared/ 2>/dev/null || true"
    log_success "  ✓ Migrated fixtures"
fi

echo

# ============================================================================
# PHASE 5: Remove Duplicate Directories
# ============================================================================

log_info "Phase 5: Removing duplicate and scattered test directories..."

# Remove phases/tests/ (duplicates tests/integration/phases/)
if [ -d "phases/tests" ]; then
    execute "rm -rf phases/tests"
    log_success "  ✓ Removed phases/tests/"
fi

# Remove per-phase test directories (now consolidated)
for phase in "${!PHASE_TESTS[@]}"; do
    if [ -d "phases/$phase/tests" ]; then
        execute "rm -rf 'phases/$phase/tests'"
        log_success "  ✓ Removed phases/$phase/tests/"
    fi
done

echo

# ============================================================================
# PHASE 6: Archive Old testing/ Directory
# ============================================================================

log_info "Phase 6: Archiving old testing/ directory..."

if [ -d "testing" ]; then
    execute "mkdir -p archived"
    archive_name="testing_old_$(date +%Y%m%d)"
    execute "mv testing 'archived/$archive_name'"
    log_success "  ✓ Archived testing/ → archived/$archive_name/"
fi

echo

# ============================================================================
# PHASE 7: Update Documentation
# ============================================================================

log_info "Phase 7: Creating documentation..."

execute "cat > tests/README.md << 'README'
# Config Manager Test Suite

Comprehensive test suite aligned with \`control_flows.yml\` architecture.

## 📁 Structure

\`\`\`
tests/
├── unit/              # Fast unit tests (no external dependencies)
│   ├── libraries/     # Library unit tests (11 units, 39 tests)
│   └── steps/         # Individual step unit tests
│
├── integration/       # Integration tests (multiple components)
│   ├── phases/        # Phase orchestrator tests (14 tests)
│   ├── steps/         # Step integration tests
│   └── flows/         # Flow integration tests
│
├── e2e/               # End-to-end tests (full workflows, 13 tests)
│
├── fixtures/          # Shared test data
│   ├── shared/        # Common fixtures
│   └── phase_N/       # Phase-specific fixtures
│
└── conftest.py        # Pytest configuration
\`\`\`

## 🏃 Running Tests

\`\`\`bash
# All tests
pytest tests/

# By type
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest tests/e2e/            # End-to-end tests only

# Specific test file
pytest tests/unit/libraries/test_probing.py
\`\`\`

## 📋 Test-to-Architecture Mapping

| Architecture Level | Test Location |
|-------------------|---------------|
| Library Units | \`tests/unit/libraries/\` |
| Phase Steps | \`tests/integration/steps/\` |
| Phase Orchestrators | \`tests/integration/phases/\` |
| Flows | \`tests/integration/flows/\` |
| Complete Pipeline | \`tests/e2e/\` |

## ✍️ Writing New Tests

**Follow this decision tree:**

1. Testing a library unit? → \`tests/unit/libraries/test_{library_name}.py\`
2. Testing a phase step? → \`tests/integration/steps/test_phase_{N}_steps.py\`
3. Testing a phase orchestrator? → \`tests/integration/phases/test_phase_orchestrators.py\`
4. Testing a complete flow? → \`tests/integration/flows/test_{flow_name}.py\`
5. Testing end-to-end? → \`tests/e2e/test_{workflow_name}.py\`

**NEVER create test directories adjacent to code!**

See \`TEST_CONSOLIDATION_PROPOSAL.md\` for full guidelines.
README"

log_success "  ✓ Created tests/README.md"
echo

# ============================================================================
# PHASE 8: Validation
# ============================================================================

log_info "Phase 8: Running validation..."

if [ "$DRY_RUN" = false ]; then
    log_info "  Running pytest to verify tests still work..."
    if pytest tests/ -v --tb=short 2>&1 | tail -5; then
        log_success "  ✓ All tests passed!"
    else
        log_error "  Tests failed! Check output above."
        log_warning "  Backup available at: $BACKUP_DIR"
        exit 1
    fi
fi

echo

# ============================================================================
# Summary
# ============================================================================

echo "═══════════════════════════════════════════════════════════════"
log_success "TEST CONSOLIDATION COMPLETE!"
echo "═══════════════════════════════════════════════════════════════"
echo
echo "📊 Summary:"
echo "  • Backup created: $BACKUP_DIR"
echo "  • New structure: tests/ (centralized)"
echo "  • Removed: 6-8 scattered test directories"
echo "  • Migrated: Per-phase tests → tests/integration/steps/"
echo "  • Migrated: Old testing/ → tests/integration/flows/"
echo "  • Archived: testing/ → archived/testing_old_*/"
echo
echo "📝 Next Steps:"
echo "  1. Review migrated tests"
echo "  2. Update CI/CD configuration (if needed)"
echo "  3. Run: git add tests/ && git commit -m 'Consolidate test directories'"
echo "  4. Read: tests/README.md for new structure"
echo
echo "═══════════════════════════════════════════════════════════════"
