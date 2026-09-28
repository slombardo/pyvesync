# Data Model: VeSync Dehumidifier Support

> **Post-implementation revision**: This document describes entities in terms of the
> original `HumidifierMap`/`VeSyncHumidifier` design. Based on maintainer feedback
> that a dehumidifier should not be grouped under `manager.devices.humidifiers`, the
> implementation was refactored into an independent `Dehumidifier` product family:
> `HumidifierMap` below corresponds to `DehumidifierMap`, and `VeSyncHumidifier`
> corresponds to `VeSyncDehumidifierBase`/`VeSyncDehumidifier`. See `tasks.md` for
> the list of affected files.

## Core Entities

### HumidifierMap

Represents a mapping for a specific device model, including the device class name, supported features, control modes, and valid value ranges.

Fields:

- `dev_types`: list of model identifiers returned by the VeSync API
- `class_name`: implementation class used for the device
- `features`: supported feature flags such as `NIGHTLIGHT`, `AUTO_STOP`, `WARM_MIST`, or any dehumidifier-specific options
- `mist_modes`: mapping of mode names to API values
- `mist_levels`: valid mist-level values supported by the model
- `target_minmax`: valid target humidity range
- `warm_mist_levels`: warm-mist level range when applicable
- `setup_entry`: canonical model identifier used for fixtures and tests

Validation rules:

- Each dehumidifier model MUST have a stable `setup_entry`.
- Product mapping MUST resolve to a valid `HumidifierMap` entry before the device is instantiated.
- Unsupported controls MUST be gated by the feature map instead of being unconditionally exposed.

### VeSyncHumidifier

Base device class for all humidifier-family devices, including dehumidifiers if they share the same protocol family.

Key responsibilities:

- device discovery and identification
- standard command calls for power and state updates
- shared logic for humidity target controls and mode changes
- access to device state and feature capabilities

Important fields:

- `state`: current runtime details
- `features`: set of supported device features
- `mist_levels`: valid mist level values
- `mist_modes`: valid mode mappings
- `target_minmax`: valid target humidity range

### HumidifierState

Runtime state representation for the dehumidifier.

Core fields:

- `device_status`: on/off or running state
- `mode`: active operating mode
- `humidity`: current room humidity
- `target_humidity`: configured humidity target
- `mist_level`: current output level
- `display_status`: display or indicator state
- `child_lock`: lock state when supported
- `temperature`: runtime temperature when reported
- `water_lacks`: low-water condition
- `water_tank_lifted`: tank state

Validation rules:

- State values should be normalized to project `StrEnum` or typed strongly typed values when possible.
- Missing or unsupported values should stay unset and not break the main device contract.
- API parsing should keep errors and unknown values explicit instead of silently coercing them.

## Relationships

- One `HumidifierMap` entry resolves to one concrete device class.
- One device instance owns one `HumidifierState` object.
- Feature flags determine which actions are valid for that model.
- Fixture data and API payloads are the source of truth for accepted state fields and command payloads.

## State transitions

- `OFF` -> `ON` via standard power command
- `MANUAL` / `AUTO` / `HUMIDITY` mode selections via `set_*_mode` commands
- humidity target changes update `auto_target_humidity` and reflect the next refresh
- unsupported mode or setting changes should fail with the existing error flow, not with silent no-ops
