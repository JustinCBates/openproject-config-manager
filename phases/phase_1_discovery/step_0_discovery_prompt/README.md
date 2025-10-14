# Discovery Configuration Prompt

**Status**: PLANNED  
**Type**: interactive  
**Sequence**: 0

## Description

Ask user whether to use automatic system discovery or manual configuration

This step interacts with the user to collect input.

## Implementation

- **Main file**: `discovery_prompt.py`
- **Function**: `execute_discovery_prompt(context, phase_dir)`

### TUI Form

This step uses the TUI Form Engine for interactive input.

- **Layout file**: `discovery_prompt.layout.yml`
- **Mock responses**: `mock_responses.json` (for testing)


## Testing

Run standalone:
```bash
python discovery_prompt.py
```

## TODO

- [ ] Implement core logic
- [ ] Add error handling
- [ ] Add logging
- [ ] Write unit tests
- [ ] Update documentation
