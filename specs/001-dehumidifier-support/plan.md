# Implementation Plan: VeSync Dehumidifier Support

**Branch**: `001-dehumidifier-support` | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-dehumidifier-support/spec.md`

> **Post-implementation revision**: This plan describes the original design of
> mapping dehumidifiers into the existing `HumidifierMap`/`VeSyncHumidifier` flow.
> Based on maintainer feedback that a dehumidifier should not be grouped under
> `manager.devices.humidifiers`, the implementation was refactored into an
> independent `Dehumidifier` product family (own `ProductTypes.DEHUMIDIFIER`,
> `DehumidifierMap`, base/device/model modules, and `manager.devices.dehumidifiers`
> container property) instead. See `tasks.md` for the list of affected files.

## Summary

Add VeSync dehumidifier support as an independent device family that reuses the existing Bypass V2 transport and response-processing infrastructure. The implementation will map dehumidifier identifiers to `DehumidifierMap`/`VeSyncDehumidifier`, expose the supported device commands and verified state attributes surfaced by the VeSync API, and validate the behavior with the repo's fixture-driven pytest workflow.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: aiohttp, mashumaro[orjson], pytest, tox, ruff, pylint, mypy

**Storage**: N/A; the library stores device state in memory and validates behavior via YAML fixtures under `src/tests/api/`

**Testing**: pytest with recorded API fixtures plus tox, ruff, pylint, and mypy

**Target Platform**: Python library for VeSync device integration

**Project Type**: library

**Performance Goals**: Preserve the current async API behavior and existing device-family performance characteristics without introducing new blocking patterns or broader regressions

**Constraints**: Must keep the public device contract stable, use the existing async `VeSync` patterns, and gate unsupported controls by the device feature map

**Scale/Scope**: Add support for VeSync dehumidifier models under an independent dehumidifier architecture while preserving compatibility with the existing WiFi device model and test harness

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

This feature passes the constitution because it:

- maintains the existing public device contract for an independent dehumidifier device family
- stays within the async request pattern already enforced by the project
- requires fixture-backed regression coverage for API parsing and command behavior
- requires linting, type checks, and documentation updates for any user-visible change

## Project Structure

### Documentation (this feature)

```text
specs/001-dehumidifier-support/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (not created here)
```

### Source Code (repository root)

```text
src/pyvesync/
├── base_devices/
│   ├── dehumidifier_base.py
│   ├── vesyncbasedevice.py
│   └── ...
├── const.py
├── device_map.py
├── devices/
│   └── vesyncdehumidifier.py
├── models/
│   └── dehumidifier_models.py
├── utils/
└── ...

tests/
├── api/vesyncdehumidifier/
├── call_json_dehumidifiers.py
├── test_dehumidifiers.py
└── ...
```

**Structure Decision**: Implement the feature as its own dehumidifier architecture. The modification points are `src/pyvesync/device_map.py`, `src/pyvesync/const.py`, `src/pyvesync/base_devices/dehumidifier_base.py`, `src/pyvesync/devices/vesyncdehumidifier.py`, and `src/pyvesync/models/dehumidifier_models.py`, with recorded API fixtures under `src/tests/api/vesyncdehumidifier/`.

## Complexity Tracking

No constitution violations require additional justification for this feature.
