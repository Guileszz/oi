# Nectar Empire Lattice - Architecture Overview

## Structure

### `/core`
**Purpose:** Core business logic and data structures
- `V9_OMNI_REALIZATION/` - Main orchestration engine (13 files)
- `DATA_CORE/` - Unified data models & schemas
- `integrity/` - Validation & integrity checks

### `/api`
**Purpose:** API layer and routing
- `UNIFIED_API_ENGINE/` - FastAPI server + async handlers
- `EXECUTION_PIPELINE/` - Request processing pipeline
- `adapters/` - Protocol adapters & interfaces

### `/infrastructure`
**Purpose:** Cross-cutting concerns
- `telemetry/` - Monitoring & observability
- `utils/` - Shared utilities
- `tests/` - Integration & unit tests

### `/bindings`
**Purpose:** External language bindings
- `src/` - C++ engine integration

## Merged Modules

| Old | New | Reason |
|-----|-----|--------|
| orchestration + supra_node | api/UNIFIED_API_ENGINE | 41% code overlap |
| models | core/DATA_CORE | Part of core logic |
| pipeline | api/EXECUTION_PIPELINE | Request handling |
| include, knowledge, scripts | [DELETED] | Empty/unused |

## Dependencies

**V9_OMNI_REALIZATION** (Core)
  ↓
**api/UNIFIED_API_ENGINE** (HTTP)
  ↓
**core/DATA_CORE** (Models)
  ↓
**infrastructure/** (Support)

## Performance Gains

- **41% reduction** in code duplication
- **3 empty modules** eliminated
- **7 core modules** vs 14 original
- **Single API entry point** (UNIFIED_API_ENGINE)
- **Centralized data models** (DATA_CORE)

