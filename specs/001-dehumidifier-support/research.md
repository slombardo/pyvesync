# Research: VeSync Dehumidifier Support

## Decision

Treat VeSync dehumidifiers as part of the existing humidifier device family and add model-specific mapping, state parsing, and command support to the established `VeSyncHumidifier` architecture.

## Rationale

The repository already contains a complete humidifier framework that matches the design needed for dehumidifiers:

- `src/pyvesync/base_devices/humidifier_base.py` defines a humidifier state model and public device API surface.
- `src/pyvesync/device_map.py` maps model IDs to a device class and a feature set via `HumidifierMap`.
- `src/pyvesync/devices/vesynchumidifier.py` holds the concrete device implementations and command methods.
- `src/tests/test_humidifiers.py` validates the fixture-driven behavior for humidifier commands.

This gives a clear pattern for adding a new product variant without creating a second parallel class hierarchy.

## Alternatives considered

### 1. New `Dehumidifier` base class
Rejected because the repository patterns and user-facing operations are already organized under the humidifier family. A new class would duplicate the same state, command, and mapping responsibilities and would not align with current project conventions.

### 2. New top-level `ProductTypes.DEHUMIDIFIER`
Rejected because the existing `ProductTypes` enum and device registry are already built around `humidifier`, and no evidence suggests a separate device family is required in the current architecture.

### 3. Ad hoc methods outside the standard device model
Rejected because it would violate the library's established contract pattern and make feature discovery and testing inconsistent.

## Implementation findings

- The feature should be added in the existing humidifier path, not as a new product family.
- Dehumidifier support needs a model-specific entry in `humidifier_modules` with class mapping, feature flags, and API fixture coverage.
- The public surface should remain consistent with other devices: `turn_on()`, `turn_off()`, `set_humidity()`, `set_auto_mode()`, `set_manual_mode()`, and any model-specific dehumidifier commands.
- Unsupported controls should be hidden behind feature checks rather than added as unconditional methods.

## Open questions resolved

- Device family grouping: humidifier family
- Primary implementation surface: `device_map.py`, `const.py`, `humidifier_base.py`, `vesynchumidifier.py`
- Validation approach: existing YAML-backed pytest tests and fixture updates
- Public API contract: keep consistent with current humidifier/device patterns and project feature gating
