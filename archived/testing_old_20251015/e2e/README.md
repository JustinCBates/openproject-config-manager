# End-to-End Tests

Complete workflow tests that exercise the entire system.

## Running E2E Tests
```bash
pytest testing/e2e/ -v
```

## Structure
- Test complete user workflows
- Use real components (minimal mocking)
- Slower execution time expected