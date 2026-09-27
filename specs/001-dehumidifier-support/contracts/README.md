# Public Interface Contract Notes

This feature is implemented within the existing library contract rather than as a separate external service API.

The relevant public interfaces are the standard device classes already used across the library:

- `VeSync` manager for account/session setup and device enumeration
- `DeviceContainer` for grouping device families
- `VeSyncHumidifier` as the base device class for humidifier-family devices
- `HumidifierState` as the state model
- `HumidifierMap` as the model-to-feature mapping contract

The contract rule for this feature is that any dehumidifier support must obey the same public behavior and feature-gating patterns as the existing humidifier family. Unsupported actions must not be exposed as unconditional methods, and public state properties must stay consistent with the project's established naming conventions.
