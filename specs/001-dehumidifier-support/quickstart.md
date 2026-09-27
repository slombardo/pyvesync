# Quickstart: VeSync Dehumidifier Support Validation

> **Post-implementation revision**: Dehumidifiers are implemented as an independent
> product family rather than part of the humidifier architecture described below.
> Based on maintainer feedback that a dehumidifier should not be grouped under
> `manager.devices.humidifiers`, use `src/tests/test_dehumidifiers.py` and the
> `src/tests/api/vesyncdehumidifier/` fixtures in place of the humidifier paths
> referenced in this document. See `tasks.md` for the list of affected files.

## Prerequisites

- Python 3.11+
- repository dependencies installed via `pip install -e .[dev]`
- optional: pre-commit installed and configured locally

## Validation scenarios

### 1. Device discovery

Run the dehumidifier test set to confirm the library still recognizes existing dehumidifier models and can instantiate new dehumidifier mappings correctly.

```bash
pytest src/tests/test_dehumidifiers.py
```

Expected outcome:

- tests pass for devices using the dehumidifier architecture
- no regression in model discovery or state parsing

### 2. Fixture authoring for new dehumidifier models

When adding a new dehumidifier model:

```bash
pytest src/tests/test_dehumidifiers.py --write_api
```

Expected outcome:

- a fixture is created or updated under `src/tests/api/vesyncdehumidifier/`
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
