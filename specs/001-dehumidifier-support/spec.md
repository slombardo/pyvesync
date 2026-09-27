# Feature Specification: VeSync Dehumidifier Support

**Feature Branch**: `001-dehumidifier-support`

**Created**: 2026-09-27

**Status**: Draft

**Input**: User description: "We need to add support for the vesync dehumidifiers. We need to allow for all the dehumidifier commands for vesync"

> **Post-implementation revision**: Based on maintainer feedback that a dehumidifier
> should not be grouped under `manager.devices.humidifiers`, the implementation was
> refactored into an independent `Dehumidifier` product family with its own
> `ProductTypes.DEHUMIDIFIER`, `DehumidifierMap`, `manager.devices.dehumidifiers`
> container property, and dedicated device/base/model modules, rather than the
> humidifier-family model described in the "Assumptions" section below. See
> `tasks.md` for details of the affected files.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Discover and manage a supported dehumidifier (Priority: P1)

A user with a VeSync dehumidifier wants the library to recognize the device, list it correctly, and expose the same core management workflow used for other VeSync device families.

**Why this priority**: Device recognition and standard device actions are the minimum viable capability required for the feature to be useful and safe for users.

**Independent Test**: A user can authenticate, list devices, identify a dehumidifier, and retrieve its state without custom handling outside the standard library flow.

**Acceptance Scenarios**:

1. **Given** a valid VeSync account with at least one dehumidifier, **When** the user logs in and requests the device list, **Then** the dehumidifier is discovered as a supported device type and exposed through the library's standard device container.
2. **Given** a discovered dehumidifier, **When** the user refreshes its state, **Then** the library returns the device's current operating values, status mode, and relevant environmental metrics.

---

### User Story 2 - Control the dehumidifier's core operating functions (Priority: P1)

A user wants to turn the dehumidifier on and off and adjust the operating modes that are normally available from the VeSync app, without needing custom API calls.

**Why this priority**: Core control operations are the main value of the feature and are critical to support real-world use.

**Independent Test**: A user can issue standard commands for power, mode selection, and target humidity changes and observe the resulting device state updates.

**Acceptance Scenarios**:

1. **Given** a connected dehumidifier, **When** the user sends a power command, **Then** the device transitions to the requested on or off state and the state is reflected in library data.
2. **Given** a connected dehumidifier, **When** the user sets a mode or target humidity, **Then** the library sends the request through the standard library API and updates the device state consistently.

---

### User Story 3 - Access advanced dehumidifier controls and monitoring (Priority: P2)

A user wants to manage advanced settings such as fan speeds, timers, humidity targets, child lock behavior, or continuous-operation modes in a consistent way across supported devices.

**Why this priority**: These features increase usability and parity with the official app, but the minimum viable release can still provide value without every advanced mode.

**Independent Test**: A user can inspect multiple available dehumidifier capabilities and change supported modes or settings through the library without unsupported ad hoc methods.

**Acceptance Scenarios**:

1. **Given** a dehumidifier exposing advanced settings, **When** the user requests available controls or state properties, **Then** the library exposes the supported options through the standard device contract.
2. **Given** a dehumidifier with a valid advanced control request, **When** the user changes a supported setting, **Then** the new state is reflected in the device object and persists through the next refresh.

---

### Edge Cases

- What happens when a dehumidifier is offline or the API returns an error during a state refresh?
- How does the system handle a dehumidifier that does not support a given setting or mode?
- What happens when device metadata or state reports values outside the expected operational range?
- How does the system behave when a user requests a setting not supported by the model or firmware?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST detect VeSync dehumidifiers as a supported device type during login and device enumeration.
- **FR-002**: The system MUST expose dehumidifier devices through the library's standard device container and type model in the same way as other supported VeSync device families.
- **FR-003**: The system MUST support retrieving the dehumidifier's operational state, environmental readings, and availability status.
- **FR-004**: The system MUST support the standard power commands needed to turn a dehumidifier on and off.
- **FR-005**: The system MUST support the primary mode and humidity control commands exposed by VeSync dehumidifiers.
- **FR-006**: The system MUST surface any supported dehumidifier-specific settings that are exposed by the VeSync API through the device model contract.
- **FR-007**: The system MUST expose device errors, unsupported operations, and API failures in a way consistent with the library's existing error handling patterns.
- **FR-008**: The system MUST preserve the project's existing naming and behavior conventions for device state, actions, and helper methods across device families.
- **FR-009**: The system MUST include or update tests to validate dehumidifier discovery, command handling, and state parsing against recorded API responses.
- **FR-010**: The system MUST keep the new functionality documented in the project documentation and examples when user-facing behavior changes.

### Key Entities *(include if feature involves data)*

- **VeSync Dehumidifier**: A supported home appliance represented by the library as a distinct device type with operational state, environment readings, and configuration controls.
- **Device State**: The current runtime status of the dehumidifier, including power state, mode, target settings, and environmental metrics.
- **Device Command**: A user-initiated action such as power toggle, mode change, humidity target adjustment, or supported advanced setting update.
- **Recorded API Fixture**: A representative API payload used to validate parsing, command flows, and regression safety for the device family.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can discover a supported VeSync dehumidifier through the standard device enumeration flow without custom per-device workarounds.
- **SC-002**: Users can complete the primary power and mode-control workflows for a dehumidifier without unsupported or ad hoc API calls.
- **SC-003**: The dehumidifier support passes the project’s required linting, typing, and test checks before merge.
- **SC-004**: At least one end-to-end regression path verifies the dehumidifier state parsing and command flow using the project’s existing fixture-based testing model.
- **SC-005**: Documentation and examples are updated for any user-visible dehumidifier behavior or API exposure added by the feature.

## Assumptions

- The feature targets the library's existing async device model and standard API conventions rather than a parallel dehumidifier-specific interface.
- Users expect parity with other supported device families in naming, state access, and action patterns.
- Dehumidifier commands will be implemented only for supported device capabilities reported by the VeSync API and will not fabricate unsupported operations.
- This feature assumes the repository's existing device test framework and YAML-based API fixtures remain the primary validation mechanism.
- Device capability coverage may vary by model or firmware version; the library will expose only the capabilities actually returned by the API.
