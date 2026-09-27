# Quickstart: VeSync Dehumidifier Support Validation

## Prerequisites

- Python 3.11+
- repository dependencies installed via `pip install -e .[dev]`
- optional: pre-commit installed and configured locally

## Validation scenarios

### 1. Device discovery

Run the humidifier test set to confirm the library still recognizes existing humidifier models and can instantiate new dehumidifier mappings correctly.

```bash
pytest src/tests/test_humidifiers.py
```

Expected outcome:

- tests pass for devices using the humidifier architecture
- no regression in model discovery or state parsing

### 2. Fixture authoring for new dehumidifier models

When adding a new dehumidifier model:

```bash
pytest src/tests/test_humidifiers.py --write_api
```

Expected outcome:

- a fixture is created or updated under `src/tests/api/vesynchumidifier/`
- the recorded API payload matches the device's actual VeSync responses

### 3. Lint and type checks

```bash
ruff check src/pyvesync
mypy src/pyvesync
pylint src/pyvesync
```

Expected outcome:

- no lint or type regressions from the new functionality
- public contract remains consistent with the project's standards

## Success criteria

The feature is considered ready when:

- dehumidifier model mappings are recognized and tested
- humidity/mode/power command flows pass fixture validation
- lint, type, and unit tests remain green
- documentation is updated when the user-visible API changes
