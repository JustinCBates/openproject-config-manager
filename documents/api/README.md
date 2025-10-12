# API Documentation

This directory contains API documentation for the OpenProject Configuration Manager.

## 📁 Contents

### Core APIs
- **Configuration Management API** - Main configuration handling interfaces
- **Discovery API** - Environment detection and auto-discovery
- **Validation API** - Configuration validation and testing
- **Export API** - Configuration export and format conversion

### UI APIs
- **Console UI API** - Rich terminal interface components
- **Interactive Collector API** - Interactive configuration collection

### Plugin APIs
- **Validation Plugins** - Custom validation plugin interface
- **Export Plugins** - Custom export format plugins

## 📖 Documentation Format

Each API is documented with:
- **Overview** - Purpose and scope
- **Classes/Functions** - Detailed interface documentation
- **Examples** - Usage examples and code snippets
- **Error Handling** - Exception types and error scenarios

## 🔧 API Reference Generation

API documentation is generated from docstrings in the source code. To regenerate:

```bash
# Generate API docs (when implemented)
python scripts/generate_api_docs.py
```

## 📚 Related Documentation

- See `../guides/` for user-facing tutorials
- See `../architecture/` for technical architecture
- See `../../testing/documentation/` for testing APIs