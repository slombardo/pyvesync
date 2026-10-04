# Research: VeSync Dehumidifier Support

> **Post-implementation revision**: The original proposal to nest dehumidifiers inside the humidifier device family was superseded. Based on maintainer feedback that a dehumidifier should not be grouped under `manager.devices.humidifiers`, the implementation was refactored into an independent `Dehumidifier` product family with its own `ProductTypes.DEHUMIDIFIER`, `DehumidifierMap`, base/device/model modules, and `manager.devices.dehumidifiers` container property.
>
> This document also records the API behavior verified against a real dehumidifier using the decompiled VeSync Android application and live Bypass V2 requests. The live observations below are the source of truth for the device protocol and must be reflected in fixtures, models, command methods, and error handling.

## Decision

Implement VeSync dehumidifiers as an independent device family using the existing Bypass V2 transport and response-processing infrastructure. Do not treat the device as a humidifier with renamed fields, and do not expose it only through `manager.devices.humidifiers`.

The public device should be available through the dehumidifier container and should provide typed state and explicit command methods. Unsupported controls must be gated by the device feature map.

## Rationale

The repository already provides the infrastructure needed for a separate product family:

- `src/pyvesync/base_devices/dehumidifier_base.py` provides the dehumidifier state/device contract.
- `src/pyvesync/devices/vesyncdehumidifier.py` provides the concrete implementation.
- `src/pyvesync/device_map.py` provides `DehumidifierMap` and `dehumidifier_modules`.
- `src/pyvesync/utils/device_mixins.py` provides `BypassV2Mixin` and the common request builder.
- Existing helper functions process both outer and nested Bypass V2 response envelopes.

A separate family is necessary because the dehumidifier status schema and command names differ materially from the humidifier schemas, even though both use the Bypass V2 endpoint.

## Verified API transport

### Endpoint

All observed calls use:

```text
POST /cloud/v2/deviceManaged/bypassV2
```

The existing Bypass V2 request builder should be reused. The request payload has the following relevant structure:

```json
{
  "method": "bypassV2",
  "payload": {
    "method": "<device method>",
    "source": "APP",
    "data": { }
  }
}
```

The existing request builder supplies the account, device, token, trace, and other required fields. No new transport layer is required.

### Confirmed status request

The decompiled application defines the status method as:

```text
getDeHumidifierStatus
```

The request uses an empty data object. The live status response was successful with both outer and nested codes equal to zero.

The implementation MUST call `getDeHumidifierStatus`, not `getHumidifierStatus`.

### Confirmed command method names

The decompiled application exposes these dehumidifier Bypass V2 methods:

- `setSwitch`
- `setTargetHumidity`
- `setWorkMode`
- `setChildLock`
- `setMuteSwitch`
- `setPowerSavingSwitch`
- `setAutoStart`
- `setPumpSwitch`
- `setDisplay`
- `setDrainage`
- `getDeHumidifierStatus`
- timer-related methods exposed by the device implementation where supported

The following method-to-payload mappings were verified by successful live calls:

| API method | Verified payload field | Example |
|---|---|---|
| `setSwitch` | `powerSwitch` | `{ "powerSwitch": 1 }` |
| `setTargetHumidity` | `targetHumidity` | `{ "targetHumidity": 50 }` |
| `setWorkMode` | `workMode` | `{ "workMode": "turbo" }` |
| `setChildLock` | `childLockSwitch` | `{ "childLockSwitch": 0 }` |
| `setMuteSwitch` | `muteSwitch` | `{ "muteSwitch": 0 }` |
| `setPowerSavingSwitch` | `powerSavingSwitch` | `{ "powerSavingSwitch": 0 }` |
| `setAutoStart` | `autoStartSwitch` | `{ "autoStartSwitch": 1 }` |
| `setPumpSwitch` | `pumpEnable` | `{ "pumpEnable": 1 }` |
| `setDisplay` | `screenSwitch` | `{ "screenSwitch": 1 }` |
| `setDrainage` | `drainageTypeConfig` | `{ "drainageTypeConfig": "pump" }` |

The live test confirmed that all of the above requests returned success envelopes with the tested payloads. Successful execution confirms the method and basic payload shape, but does not by itself establish every permitted value for every field.

### Work-mode caution

The live device reported:

```text
workMode: "turbo"
```

A deliberately invalid request:

```json
{ "workMode": "bogusmode" }
```

returned an outer device-timeout response rather than a clean validation error. Therefore:

- The public API MUST validate modes against the model's known mode map before sending.
- Unknown mode strings MUST be rejected locally.
- A device timeout MUST NOT be interpreted as proof that a valid command was accepted.
- The model's mode map must include the actual values supported by the target device. The currently observed `turbo` value must not be discarded merely because an earlier map only listed `auto` and `manual`.

The exact complete mode set still needs to be confirmed from the device's model metadata or additional valid app traffic before hard-coding a universal list.

### Target-humidity validation

The live device accepted a target of `50` and reported it in status. Deliberately invalid values produced the following nested error:

```json
{ "targetHumidity": 999 }
```

and:

```json
{ "targetHumidity": 0 }
```

Both returned nested code `11003000`.

The implementation MUST validate target humidity locally using the model's configured `target_minmax` and MUST return `False` without sending values outside that range. The live experiment proves that `0` and `999` are invalid; it does not independently prove the complete inclusive range. The current model configuration of `(30, 80)` must be verified against additional device/app evidence before being treated as universal for all dehumidifier models.

## Verified status response schema

The successful live response was:

```json
{
  "traceId": "1790545847",
  "code": 0,
  "msg": "request success",
  "module": null,
  "stacktrace": null,
  "result": {
    "traceId": "1790545847",
    "code": 0,
    "result": {
      "powerSwitch": 1,
      "humidity": 79,
      "tempInF": 18,
      "targetHumidity": 50,
      "workState": "dehumidification",
      "workMode": "turbo",
      "fanSpeedLevel": 3,
      "manualSpeedLevel": 1,
      "tankLevel": 1,
      "tankInPlace": 1,
      "screenSwitch": 1,
      "screenState": 1,
      "scheduleCount": 0,
      "timerRemain": 0,
      "autoStartSwitch": 1,
      "errorCodes": [],
      "filterLifePercent": 95,
      "filterRemainingDays": 44,
      "resetFilterDate": 0,
      "childLockSwitch": 0,
      "muteSwitch": 0,
      "powerSavingSwitch": 0,
      "powerSavingState": 0,
      "powerSavingTimeSec": 0,
      "pumpInPlace": 1,
      "pumpEnable": 1,
      "pumpWorking": 0,
      "waterSensorInPlace": 0,
      "waterSensorDetectsWater": 0,
      "moldRemovalRemind": 0,
      "reachTargetState": 0,
      "drainageTypeConfig": "innerTank",
      "compressorState": 1,
      "coilTemp": 5,
      "exhaustPipeTemp": 55,
      "actualRunLevel": 3
    }
  }
}
```

The typed dehumidifier result model should represent these fields, allowing optional fields where firmware/model variation is expected:

| Field | Meaning / expected representation |
|---|---|
| `powerSwitch` | Device power state, integer switch value |
| `humidity` | Current relative humidity |
| `tempInF` | Reported temperature value from the API; preserve the API unit/scale until confirmed |
| `targetHumidity` | Configured target humidity |
| `workState` | Current operating state, e.g. `dehumidification` |
| `workMode` | Current operating mode, e.g. `turbo` |
| `fanSpeedLevel` | Current fan speed |
| `manualSpeedLevel` | Manual fan speed setting |
| `tankLevel` | Tank level/status indicator |
| `tankInPlace` | Whether the tank is installed |
| `screenSwitch` | Configured display switch |
| `screenState` | Actual display state |
| `scheduleCount` | Number of schedules |
| `timerRemain` | Remaining timer value |
| `autoStartSwitch` | Auto-start configuration |
| `errorCodes` | List of device fault codes; empty list observed for healthy device |
| `filterLifePercent` | Remaining filter life percentage |
| `filterRemainingDays` | Estimated filter days remaining |
| `resetFilterDate` | Filter reset timestamp/value |
| `childLockSwitch` | Child-lock configuration |
| `muteSwitch` | Mute configuration |
| `powerSavingSwitch` | Power-saving configuration |
| `powerSavingState` | Current power-saving state |
| `powerSavingTimeSec` | Power-saving duration/value in seconds |
| `pumpInPlace` | Whether a pump is installed |
| `pumpEnable` | Whether pump drainage is enabled |
| `pumpWorking` | Whether the pump is currently running |
| `waterSensorInPlace` | Whether the water sensor is installed |
| `waterSensorDetectsWater` | Water sensor detection state |
| `moldRemovalRemind` | Mold-removal reminder state |
| `reachTargetState` | Whether the target state has been reached |
| `drainageTypeConfig` | Drainage mode, observed as `innerTank` |
| `compressorState` | Compressor state |
| `coilTemp` | Coil temperature value |
| `exhaustPipeTemp` | Exhaust pipe temperature value |
| `actualRunLevel` | Actual current run level |

The implementation must preserve unknown fields or tolerate additional firmware fields where the project's model configuration permits it. It must not silently map dehumidifier fields to unrelated humidifier fields such as `water_lacks` or `mist_level` unless the mapping is explicitly documented and semantically correct.

## Verified response and error handling

The API has two relevant response-code layers.

### Successful getter response

For `getDeHumidifierStatus`:

- outer `response["code"] == 0`
- outer `response["msg"] == "request success"`
- nested `response["result"]["code"] == 0`
- status payload is in `response["result"]["result"]`

### Successful setter response

For setters such as `setTargetHumidity` and `setSwitch`:

- outer `response["code"] == 0`
- outer `response["msg"] == "request success"`
- nested `response["result"]["code"] == 0`
- there may be no nested `response["result"]["result"]` payload

### Invalid target-humidity response

For invalid target humidity values:

```json
{
  "traceId": "1790545691",
  "code": 0,
  "msg": "request success",
  "module": null,
  "stacktrace": null,
  "result": {
    "traceId": "1790545691",
    "code": 11003000
  }
}
```

This means the cloud request succeeded, but the device/API rejected the command. The implementation must surface the nested nonzero code and return failure.

### Device-timeout response

For the invalid work mode `bogusmode`:

```json
{
  "traceId": "1790545691",
  "code": -11302030,
  "msg": "device timeout",
  "module": null,
  "stacktrace": null,
  "result": null
}
```

This means:

- outer code is nonzero;
- the message is `device timeout`;
- nested result is `null`;
- there is no nested code to inspect.

The response processor MUST check the outer code before dereferencing the nested result and MUST safely handle `result: null`. It must not classify this response as success and must not raise a secondary `NoneType`/missing-result exception.

### Error-code policy

The implementation should apply this order:

1. If the response is missing or `None`, report an unexpected API failure.
2. If the outer code is present and nonzero, report the outer code/message.
3. If the outer code is zero, inspect the nested result.
4. If the nested result is missing or `None`, report a malformed/incomplete response.
5. If the nested code is present and nonzero, report the nested code/message.
6. Only treat the command as successful when both available code layers are zero.

Do not automatically retry validation failures such as `11003000`. A device timeout such as `-11302030` may be retried only for a known-valid payload and only under the library's existing retry policy; malformed or unvalidated commands must not be retried blindly.

### Persistent device faults

The status field `errorCodes` is independent of the request envelope. A request can return success while the device has persistent hardware/status faults. The implementation should expose `errorCodes` as part of device state and should not infer it from the request's outer or nested response code.

The observed healthy device returned:

```json
"errorCodes": []
```

## Device configuration observations

The live device reported:

```text
pumpInPlace: 1
pumpEnable: 1
pumpWorking: 0
drainageTypeConfig: innerTank
```

This shows that pump hardware can be present and enabled while the configured drainage mode is still `innerTank`. The library must expose these as separate state fields and must not infer drainage configuration solely from pump presence or enablement.

The live device also reported `workState: dehumidification`, `compressorState: 1`, and `reachTargetState: 0`, demonstrating that operating state, compressor state, and target-reached state are distinct concepts.

## Existing implementation findings

- `BypassV2Mixin.call_bypassv2_api()` is suitable for these calls and should remain the common transport entry point.
- `src/pyvesync/devices/vesyncdehumidifier.py` must use `getDeHumidifierStatus` for refresh.
- The dehumidifier implementation must use `setWorkMode` rather than the humidifier-oriented `setHumidityMode`.
- The dehumidifier implementation must parse `fanSpeedLevel` and related dehumidifier fields rather than assuming the humidifier `mistLevel`/`virtualLevel` schema.
- Error processing must support successful setter envelopes without a result payload and failed envelopes with `result: null`.
- The dehumidifier-specific result model should live in the dehumidifier model module and should not reuse a humidifier result model merely because the transport endpoint is shared.
- Feature flags should gate display, child lock, automatic stop, water-tank status, pump, drainage, mute, and power-saving controls according to model capability.

## Open questions and follow-up validation

The following items remain model-specific and must be confirmed before presenting them as universal across all dehumidifiers:

- The exact `deviceType` returned by the user's account for the tested unit.
- The complete valid mode set; `turbo` was observed live, while the current map must be checked for all supported values.
- The exact target-humidity range for each model.
- The exact payload shape and accepted values for fan-level control, timer operations, drainage types, and advanced switches across firmware versions.
- The unit and scaling of `tempInF`, `coilTemp`, and `exhaustPipeTemp`.
- The semantic mapping of `tankLevel` and the complete set of possible `errorCodes` values.
- Whether `setAutoStart`, `setPumpSwitch`, `setDrainage`, `setMuteSwitch`, and `setPowerSavingSwitch` should be public methods immediately or remain internal until fixture coverage is added.

## Alternatives considered

### 1. Nest dehumidifiers under the humidifier family

Rejected. The verified API schema and command names are sufficiently different that doing so would encourage incorrect method reuse and incorrect state mappings.

### 2. New top-level product type without shared transport helpers

Rejected. A separate product family is correct, but it should reuse the established Bypass V2 request/response infrastructure rather than duplicate HTTP and authentication code.

### 3. Ad hoc calls through `call_bypassv2_api()` as the public API

Rejected as the long-term interface. The generic method is useful for discovery and investigation, but supported controls should be represented by explicit, validated device methods with feature gating and typed state updates.

## Validation approach

Add fixture-backed tests for:

- discovery and dehumidifier container placement;
- status parsing using the complete observed response schema;
- successful power, target humidity, work-mode, child-lock, display, and fan-speed calls;
- successful setter envelopes with no result payload;
- nested validation failure `11003000`;
- outer timeout `-11302030` with `result: null`;
- status `errorCodes` preservation;
- pump presence versus drainage configuration as separate state values;
- local rejection of invalid target humidity and unknown mode values.

Run the repository's normal test, lint, type-check, and documentation validation commands before merging the feature.

## Open questions resolved by live testing

- Device status method: `getDeHumidifierStatus`
- Status endpoint: `/cloud/v2/deviceManaged/bypassV2`
- Setter success envelope: outer code `0`, nested code `0`, often without nested result data
- Invalid target humidity code: nested `11003000`
- Invalid/malformed work-mode behavior observed: outer `-11302030`, message `device timeout`, nested result `null`
- Device health field: `errorCodes`, observed as an empty list on a healthy device
- Pump/drainage fields: independently reported as `pumpInPlace`, `pumpEnable`, `pumpWorking`, and `drainageTypeConfig`
- Current live status: power on, humidity 79, target 50, work mode turbo, fan speed 3, no device error codes
