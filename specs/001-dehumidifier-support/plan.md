Existing findings file exists; let me read it and search the source.

Good: `FlatteningRequestVesyncConverter`. Read it, plus the response-unwrapping converter (bypass/a-c) and `source` value.

Now the flattening converter and the response handling.

Key mapping methods: `a2`, `b2`, `n3`, `o3`, `U1`, `X1`, `S2`, `T2`, `e2`, `X2`.

This file is the status→UI-state mapper. Read it fully.

# Investigation report: VeSync dehumidifier API contracts, from the decompiled APK

**Scope.** Read-only. Source root is `C:\temp\vesync-src\sources`, and every path below is relative to it. I did not modify any repository.

**Prior notes.** `C:\temp\dehumidifier-apk-findings.md` already existed. I re-verified its claims against the code and corrected several of them (see 7.4).

**Capture.** `vesync-capture.mitm` is only 471 bytes, so there is no real traffic. All JSON below is reconstructed from code.

## 0. Headline findings

1. **`LDH-H251S-WUS` is not in this APK.** Searches for `H251` and `LDH-` return only one dehumidifier module, `VS_WFON_DHM_LDH-H321S-WUS_US` (the H321S). Every contract below is verified for the H321S-era dehumidifier code path. For the H251S it is **Inferred** only, because the same `getDeHumidifierStatus` / `set*` family is shared.
2. **There is no model or firmware branching in the dehumidifier client code.** `r81/a.java:a(configModel)` returns `new u81.a()` on both branches. Control visibility is derived from status fields, not from model or firmware.
3. **This APK's status model has no compressor, coil, exhaust or temperature fields.** I found no `compressorState`, `coilTemp`, `exhaustPipeTemp`, `tempInF`, `fanSpeedLevel`, `actualRunLevel` or temperature-unit setter anywhere in the dehumidifier code. They are **Unresolved**. The error codes for coil and exhaust NTC sensors exist (section 5), so those sensors exist on the hardware.
4. **The status serializer descriptor (`w81/w$a`) was not emitted by jadx.** Status wire names are taken from `w81/w.java:toString()` (line ~535) and property names, so they are **Inferred**. They are consistent with the request descriptors, which are Verified. The next diagnostic step is a runtime capture of `getDeHumidifierStatus`.

## 1. Device identification and capability gating

**Identifiers (Verified).** `com/vesync/databus/deviceconfig/DeHumidifierH321Us.java`, lines 49–52:
- `@DeviceConfigModule("VS_WFON_DHM_LDH-H321S-WUS_US")`
- `DEHUMIDIFIER_H321_US_BLE_MODEL = 165`
- `getDeviceMainPageConfig()` returns `DeviceMainPageConfig(AIR_DEVICE, AirDeviceType.DEHUMIDIFIER)`.

Product-ID matching is not used.

**Classes (Verified).**
- UI: `com.dehumidifier.*`.
- KMP logic: `com.vesync.kmp.air.dehumidifier.*`.
- Models: `w81.*`.
- Repository: `com/vesync/kmp/air/dehumidifier/repository/a.java`.
- Retrofit-style client: `.../http/bypass/a.java` (interface), `.../http/bypass/h0.java` (generated implementation).
- Legacy Retrofit class for the filter screen only: `com/dehumidifier/http/*`.
- Wire models: `w81/w.java` (status) and `w81/{o0,p0,q0,r0,s0,t0,u0,v0,x0,y0,z0,z,a,x,m0,n0}.java` (requests).

**How support is decided.**
- **Model or config module:** only to get here. The `configModule` is passed through as an opaque string on every call (`b0.f120528z`, set in `S2()` at `b0.java:6073`).
- **Status response:** this drives which controls appear and whether they are enabled (`w81/c.java`, section 2.3).
- **Server config (Verified):** `AirDehumidifierRepository.getDeviceConfig(configModel, category, configKey, version)` returns `configMap` with entries `{configKey, configValue, version}` (`w81/h0.java`, `b0.java`, `c0.java`). The app reads `popup / errorText` for error text (`b0.java:5955`). `DeviceFilterRemainDaySwitch` (per configModel) gates the filter-days display (`EnergyManagementActivity.java`), and `DeviceLifeThreshold(configModel, lowLifeThreshold, riskLifeThreshold)` provides filter thresholds (`ua1/b.java`, `wa1/g.java`). Fallback thresholds are 20 and 5 (`b0.java:6438`) and 30 and 10 in the legacy filter screen.
- **Firmware version:** I found no dehumidifier-specific firmware gating.
- **Capability flags:** none for sensors or compressor. The only per-device "installed" flags are `tankInPlace`, `pumpInPlace` and `waterSensorInPlace`.

## 2. Read API contract

### 2.1 Outer envelope (all calls, reads and writes)

Verified from `http/bypass/h0.java`, `kmp/vesync/config/convert/bypass/d.java`, `kmp/vesync/config/config/p.java`, `pa1/{r,l,q,a0}.java` and `kmp/vesync/config/config/y.java`.

- **Method and URL:** `POST {cloud base URL}/cloud/v2/deviceManaged/bypassV2`. The same path is used by every method. The legacy filter client also uses `@POST("/cloud/v2/deviceManaged/bypassV2")` (`RetrofitServiceModelDeHumidifierByPassApi.java`). The server-tag is `cloud` (`j0.java`).
- **Command name:** the annotation `@ba1.u("<name>")` becomes the nested `payload.method`. It is not a URL.
- **Body:** a `PassRequestV2Vesync{context, data}` is flattened into one JSON object (`p.java:a`). The context fields come first, then the data fields.
  - **Top-level (context):** `traceId`, `method:"bypassV2"`, `token`, `accountID`, `timeZone`, `userCountryCode`, `acceptLanguage`, `debugMode`, `osInfo`, `clientType`, `clientVersion`, `terminalId`, `clientInfo`, `appVersion`, `phoneOS`, `phoneBrand`, plus optional `cid`, `configModule`, `subDeviceType`, `subDeviceNo`, `uuid`, `sourceAppID`, `appID` (`a0.java:131-153`).
  - **Top-level (data):** `payload`, `cid`, `groupId`, `configModule`, `isAsync` (`pa1/l.java:58-62`).
  - **`payload`:** `{method, data, source, subDeviceType?, subDeviceNo?}` (`pa1/q.java:60-64`).
- **Where `deviceId` and `configModule` go:** the converter (`d.java:c`) moves them from the request object to the top-level `cid` and `configModule`, then nulls them. The inner `payload.data` therefore normally carries only the command fields.
- **`source` value:** **Unresolved.** The runtime implementation is injected. The default stub returns `"APP_Vesync"` (`y.java`, class `e`).
- **Response (Verified):** `{traceId, code, msg, result:{code, msg, result:<payload>}}` (`pa1/v.java:55-58`, `pa1/s.java:52-54`). `convert/bypass/h.java` returns the inner `result.result` only when outer `code == 0` and inner `code == 0`. Otherwise it throws `oa1.f(code…)`.
- **Success semantics for Unit-returning writes:** **Inferred**. I did not trace which of the converters `f`, `g`, `h` handles Unit.

### 2.2 `getDeHumidifierStatus`

- **Command:** `getDeHumidifierStatus`.
- **Request:** `data = {}`. The request class `w81.z` has only `deviceId` and `configModule`, and both are moved to the top level (`z.java:41-43`).
- **Response:** `w81.w` (`AirDehumidifierStatus`). One call returns every field, so there are no separate reads.
- **Updates:**
  - **Polling:** `com.vesync.kmp.air.common.util.o(10000L, deviceId, fetcher=a3→repo.g(), …)` is constructed at `b0.java:5976`. Polling every 10 s is **Inferred** from the `10000L` argument.
  - **Poll suppression:** poll results are ignored if less than 2 s after a local write (`b0.java` `y2.a.emit`).
  - **Writes:** the app updates its local copy first, then sends the request. It does not re-read the status after most writes.
  - **Push messages (Verified list):** `l.java` and `MyFirebaseMessagingService` define push types such as `dehumidifier:device:waterFull`, `…:moldRemoval`, `…:WaterTankMaintenance` and `dehumidifier:filter:lowQuality`. They are carried into the screen as an intent (`S2`) and shown as dialogs. They do not carry state.
  - **Websocket or other realtime channel:** **Unresolved**.

### 2.3 Status fields (`w81/w.java`)

Field order and defaults come from the constructor and `B0()` (lines 131–340). Names are **Inferred** (see headline 4). Types and defaults are Verified.

| Wire name | Type | Default if absent | App interpretation (Verified unless noted) |
|---|---|---|---|
| `powerSwitch` | bool/int | false | `Z()`. |
| `workMode` | string | `"auto"` | Unknown strings fall back to `AUTO` (`t.java` serializer). |
| `manualSpeedLevel` | int 1..3 | 1 | Used as the fan level when `workMode == "ventilation"`. |
| `targetHumidity` | int % | 55 | Slider 35–70, step 1 (`DhTargetHumidityView`). |
| `humidity` | int % | 40 | Displayed as `min(h,100)%`, or `--` if `<= 0` (`c.java:B`). |
| `childLockSwitch` | bool | false | |
| `screenSwitch` | bool | false | Configured display state. Used by the display control (`c.n`). |
| `muteSwitch` | bool | false | |
| `screenState` | bool | false | Parsed. **No consumer found.** It is probably the actual display state (Inferred). |
| `autoStartSwitch` | bool | false | |
| `drainageType` | string? | null | Overrides `drainageTypeConfig` when non-null (`c.z`: `strM = M() ?: N()`). |
| `drainageTypeConfig` | string | `"innerTank"` | Configured drainage. |
| `pumpEnable` | bool | false | Configured pump-on state. |
| `pumpWorking` | bool | false | Parsed. **No consumer found.** |
| `pumpInPlace` | bool | false | |
| `errorCodes` | `List<Int>` | `[]` | |
| `workState` | string | `"dehumidification"` | `b1` enum (`b1.java`). |
| `tankInPlace` | bool | **true** | |
| `tankLevel` | int | 1 | **Status code.** Only `10` has meaning (`a1.TANK_FULL(10)`). Other values are not defined. It is not a percentage or physical level in this code. |
| `waterSensorInPlace` | bool | false | The expansion-tank sensor. |
| `filterLifePercent` | int % | 100 | |
| `filterRemainingDays` | int | 15 | |
| `reachTargetState` | bool | false | |
| `waterSensorDetectsWater` | bool | false | |
| `moldRemovalRemind` | int | 0 | See 2.5. |
| `scheduleCount` | int | 0 | Parsed. **No consumer found** in the main screen. |
| `timerRemain` | int **seconds** | 0 | |
| `powerSavingState` | bool | false | Whether power-saving is currently active. |
| `powerSavingTimeSec` | int sec | 0 | |
| `sceneStateList` | `List<p81.t>?` | null | Scene-dry state. Out of scope. |
| `resetFilterDate` | Int? | null | **Unix epoch seconds** (Verified: `h0.g(j)` does `new Date(j*1000)`, `aircomment/utils/h0.java:168`). |

**Getter-to-field mapping used in the app.**
- `Z`: power.
- `z0`: workMode.
- `s0`: tankLevel.
- `q0`: tankInPlace.
- `x0`: waterSensorInPlace.
- `v0`: waterSensorDetectsWater.
- `d0`: pumpInPlace.
- `b0`: pumpEnable.
- `A0`: workState.
- `O`: errorCodes.
- `T`: moldRemovalRemind.
- `Y`: powerSavingTimeSec.
- `u0`: timerRemain.
- `j0`: resetFilterDate.

### 2.4 Derived values (app-computed, not on the wire)

All are in `w81/c.java`.

- **Run status (`u` enum), `D()`.** Offline → `offLine`. Power off → `off`. `workState` `onStandby` → `standby`. `dehumidification`, `compressorProtection` or `defrost` → `dehumidification`. `ventilation` → `ventilation`. Anything else, including `moldRemoval`, → `dehumidification`. This is the older "work-state-like" enum from the prior notes. It is the UI run status, not wire data.
- **Tank full (`I()`).** `(tankLevel == 10 && tankInPlace) || (waterSensorInPlace && waterSensorDetectsWater)`.
- **Inner-tank state (`G`).** Full if `tankInPlace && tankLevel == 10`, else normal if `tankInPlace`, else not installed.
- **Expansion tank (`F`).** Full if `sensor && water`. Normal if `sensor && !water`. Otherwise sensor not installed.
- **Pump state (`J`).** `pumpInPlace` → `PUMP_NORMAL`, else `PUMP_ERROR`.
- **Effective drainage (`z`).** `drainageType ?: drainageTypeConfig`, then the expansion, pump or inner-tank state above.
- **Not-in-place list (`b0.U1`).** `!tankInPlace` → `TANK_NOT_IN_PLACE`. `!pumpInPlace` → `PUMP_NOT_IN_PLACE`. `!waterSensorInPlace` → `SENSOR_NOT_IN_PLACE`.
- **Target reached (`c.i`).** Shown only if `reachTargetState && mode ∈ {auto, turbo, quiet} && power`.
- **Filter tip (`c.i`).** Shown when `filterLifePercent ∈ {0, 5, 30}`.
- **Filter severity (`c.h`).** `life <= riskThreshold` → exhausted. `life <= lowThreshold` → dangerous. Otherwise normal.
- **Power-saving minutes (`c.e`).** `(powerSavingTimeSec + 59) / 60`.
- **Timer display (`r.i`).** Seconds rounded up to minutes, shown as `HH:mm`. `timerRemain <= 0` shows an empty value.

### 2.5 Interpretation caveats

- **`moldRemovalRemind`.** It is only shown while `power == off && workState == "moldRemoval" && value > 0`. The app counts it down locally (`AirTimerService`) and draws progress as `(99 - v) / 99`. So it is a remaining-seconds-style countdown of the mold-removal run, not a "reminder due" flag. This is **Inferred**. The units are not proven, and the name is misleading.
- **`screenState` and `pumpWorking`.** Both are parsed but never consumed. The comments "actual display" and "pump running" are **Inferred** from the names only.
- **`scheduleCount`.** It is not consumed by the main screen.

## 3. Write API contract

All writes are `POST …/bypassV2` with `payload.method = <command>` and the nested `payload.data` shown below. `deviceId` and `configModule` go to the top-level `cid` and `configModule` (see 2.1). Success and failure are as in 2.1 (**Inferred** for Unit-returning calls). None of the writes require other settings in the same request. Each request class carries only its own field plus `configModule` and `deviceId` (`w81/*.java` descriptors).

| Command | `payload.data` | Values | Trace | Preconditions in the app |
|---|---|---|---|---|
| `setSwitch` | `{"powerSwitch":0\|1,"switchIdx":0}` | int via `q.b(bool)` | `b0.r1` (`b0.java:3906`) → `repo.s` → `x0` | The UI always sends `switchIdx = 0`. The field is nullable. |
| `setWorkMode` | `{"workMode":"<str>"}` | `auto`, `turbo`, `quiet`, `ventilation` | `v2` (`b0.java:4927`) → `repo.w` → `z0` | The main UI sends `ventilation` for fan-only mode (`ComDeHumNvgFragment.java:1663`). `manual` is used by scene editing. |
| `setLevel` | `{"manualSpeedLevel":1\|2\|3}` | `i`: LOW 1, MEDIUM 2, HIGH 3 | `i2` (`b0.java:2082`) → `repo.p` → `s0` | The control is enabled only when `workMode == "ventilation"` and power is on with no errors (`c.l`, `z17`). |
| `setTargetHumidity` | `{"targetHumidity":int}` | Slider 35–70 | `b0.java:2710` → `repo.v` → `y0` | The control is disabled when offline, off, in error, tank full, tank not in place, or the expansion sensor reports water (`c.l`, `!z18`). The range is a client constant (`DhTargetHumidityView`, `o.java`). |
| `setChildLock` | `{"childLockSwitch":0\|1}` | | `b0.java:817` → `repo.m` → `p0` | Enabled only when online, on and error-free (`c.p`). |
| `setDisplay` | `{"screenSwitch":0\|1}` | | `b0.java:1492` → `repo.n` → `q0` | Disabled when offline, off, or in error. There is also a Quiet-mode restriction (see 3.1). |
| `setMuteSwitch` | `{"muteSwitch":0\|1}` | | `b0.java:3952` → `repo.q` → `t0` | Same as display. |
| `setAutoStart` | `{"autoStartSwitch":0\|1}` | | `b0.java:5695` → `repo.l` → `o0` | Enabled when online and error-free (`c.a`). It does not require power on. The help text says it turns the unit on automatically when power is connected (`strings.xml:7494`). |
| `setPumpSwitch` | **`{"pumpSwitch":0\|1}`** | | `b0.java:4653/4676` → `repo.u` → `v0` | See 3.2. |
| `setDrainage` | `{"drainageType":"innerTank"\|"expansionTank"\|"pipe"\|"pump"}` | The field name is the constant `InstallingInstructionActivity.f54889d`, which resolves to `drainageType` (**Verified** in the prior notes). | `b0.java:3507` and `installinginstruction/g.java:225` → `repo.o` → `r0` | See 3.2. |
| `setPowerSavingSwitch` | **`{"enabled":0\|1}`** (decompiled) | | `repo.r` → `u0` (`u0.java:36-42`) | Your live capture shows a different key (`powerSavingSwitch`). **Unresolved**, see 3.3. |
| `getPowerSavingConfig` | `{}` | Response `m0`: `{enabled:int, slots:[{id,startMin,endMin}]}` | `repo.k` | Minute-of-day slots. |
| `addPowerSavingSlot` | `{"startMin":int,"endMin":int}` | Response `w81.b` (carries the new id) | `repo.d` → `a` | |
| `updatePowerSavingSlot` | `{"id":int,"startMin":int,"endMin":int}` | | `repo.x` | |
| `deletePowerSavingSlot` | `{"id":int}` | | `repo.e` → `x` | |

The power-saving slot write operations are request-verified, but they sit outside the main fields requested, so I did not trace their UI.

### 3.1 Mode-dependent control availability (`w81/c.java:l`)

- The target-humidity control is shown for modes `auto`, `turbo` and `quiet`, or while a scene is running.
- The fan-level control is shown only for `ventilation` with no scene running.
- Display and mute are disabled when `workMode == "quiet"` and no manual-mode scene is active (`c.n`, `c.r`). This is only **Inferred**, because jadx duplicated the control-flow block there.
- **Correction to the prior notes:** the High/Med/Low "scenario" labels in `ScenarioMode.java` belong to the scenario-dry editor. On the main screen the fan level is tied to `ventilation`, not `manual`.

### 3.2 Pump and drainage rules

Verified from `installinginstruction/g.java` (`g1()` and `c`), `b0.java:X1` (6263) and `selectdrainage/g.java`.

- After `setDrainage` to `pump` or `expansionTank`, the app re-reads `getDeHumidifierStatus` and validates it:
  - **Pump:** requires `drainageTypeConfig == "pump"` and `pumpInPlace`. It then also requires `pumpEnable`.
  - **Expansion tank:** requires `drainageTypeConfig == "expansionTank"` and `waterSensorInPlace`.
  - **`innerTank` and `pipe`:** no validation was found.
- If those checks fail, the app shows install or "not detected" prompts. For some failures it writes `setDrainage(innerTank)` to revert (`b0.java:3507`).
- Pump control is applied locally first (`pumpEnable` is updated in the local state), then `setPumpSwitch` is sent (`b0.java:4626-4680`).
- **Meaning of `pipe` versus the other values:** not defined beyond the string. The app has no pipe-specific installed flag.
- **Model differences:** none found. These rules apply to every device on this code path.

### 3.3 Power-saving field-name conflict

The decompiled request is `{"enabled":int}` (`u0.java`). Your live capture shows `powerSavingSwitch`. A newer app version, a different request class for the H251S, or server tolerance of both keys are all plausible. This is **Unresolved**. Test both keys against the real device.

### 3.4 Not supported or not found (do not invent setters)

- **Filter reset:** no setter. It appears to be a device-side action. The push `dehumidifier:filter:reset:success` (`w81/l.java: RESET_FILTER`) only reports success.
- **Mold-removal acknowledgement or reset:** no setter. The "cancel mold removal" dialog handler (`handleCancelMoldRemovalDialogIntent`) does not call a dedicated API method that I could find.
- **Timer or schedule:** no dehumidifier-specific command. Only a local countdown (`AirTimerService`).
- **Temperature unit:** no setter. `kmp/air/dehumidifier/util/d.java` converts an already-known temperature for display only.
- **Error acknowledgement:** nothing found beyond a UI `cancelError`.

## 4. Field mapping table

| Feature | Wire field | Meaning / type | Units / scaling | Read | Write | Allowed write values | Model support | Evidence |
|---|---|---|---|---|---|---|---|---|
| Power | `powerSwitch` | bool/int | — | `getDeHumidifierStatus` | `setSwitch` | 0/1 (+ `switchIdx:0`) | H321S verified, H251S Inferred | `c.java:D`, `b0:r1` |
| Current humidity | `humidity` | int | % | status | none | read-only | same | `c.java:B` |
| Target humidity | `targetHumidity` | int | % | status | `setTargetHumidity` | 35–70 (UI) | same | `DhTargetHumidityView`, `y0` |
| Mode | `workMode` | string | — | status | `setWorkMode` | `auto`/`turbo`/`quiet`/`ventilation` (+`manual` in scenes) | same | `t.java` |
| Manual speed | `manualSpeedLevel` | int | 1–3 | status | `setLevel` | 1,2,3 | same | `s0`, `i.java` |
| Virtual level, actual run level, `fanSpeedLevel` | — | not in APK | — | — | — | — | Unresolved | none found |
| Temperature, unit | — | not in APK | — | — | — | — | Unresolved | none found |
| Tank installed | `tankInPlace` | bool (default true) | — | status | none | read-only | same | `w.java` |
| Tank full | `tankLevel` | status code; `10` = full | — | status | none | read-only | same | `a1.java`, `c.I` |
| Water sensor installed | `waterSensorInPlace` | bool | — | status | none | read-only | same | `w.x0` |
| Water detected | `waterSensorDetectsWater` | bool | — | status | none | read-only | same | `w.v0` |
| Target reached | `reachTargetState` | bool | — | status | none | read-only | same | `c.i` |
| Pump installed | `pumpInPlace` | bool | — | status | none | read-only | same | `b0.U1` |
| Pump enabled (configured) | `pumpEnable` | bool | — | status | `setPumpSwitch` (`pumpSwitch`) | 0/1 | same | `v0.java` |
| Pump running (actual) | `pumpWorking` | bool | — | status (no consumer) | none | read-only | Inferred | `w.java` |
| Drainage (configured) | `drainageTypeConfig` | string | — | status | `setDrainage` (`drainageType`) | 4 values | same | `g0.java` |
| Drainage (override) | `drainageType` | string? | — | status | none | read-only | Inferred | `c.z` |
| Display (configured) | `screenSwitch` | bool | — | status | `setDisplay` | 0/1 | same | `q0.java` |
| Display (actual) | `screenState` | bool | — | status (no consumer) | none | read-only | Inferred | `w.java` |
| Child lock | `childLockSwitch` | bool | — | status | `setChildLock` | 0/1 | same | `p0.java` |
| Mute | `muteSwitch` | bool | — | status | `setMuteSwitch` | 0/1 | same | `t0.java` |
| Auto-start | `autoStartSwitch` | bool | — | status | `setAutoStart` | 0/1 | same | `o0.java` |
| Power-saving (configured) | `getPowerSavingConfig.enabled` | int | — | `getPowerSavingConfig` | `setPowerSavingSwitch` | 0/1 | conflict in field name | `m0.java`, `u0.java` |
| Power-saving (active) | `powerSavingState` | bool | — | status | none | read-only | same | `w.java` |
| Power-saving remaining | `powerSavingTimeSec` | int | seconds | status | none | read-only | same | `c.e` |
| Compressor, coil, exhaust temp | — | not in APK | — | — | — | — | Unresolved | none |
| Work state | `workState` | string | — | status | none | read-only | same | `b1.java` |
| Filter life | `filterLifePercent` | int | % | status | none | read-only | same | `c.h` |
| Filter remaining days | `filterRemainingDays` | int | days | status | none | read-only | same | `c.h`, `FilterModel.java` |
| Filter reset time | `resetFilterDate` | Int? | epoch **seconds** | status | none | read-only | same | `h0.g`, `EnergyManagementActivity` |
| Mold removal | `moldRemovalRemind` | int | likely seconds (Inferred) | status | none | read-only | Inferred | `c.j` |
| Errors | `errorCodes` | `List<Int>` | — | status | none | read-only | same | `qa1/d.java` |
| Schedule count | `scheduleCount` | int | — | status (no consumer) | none | unknown | Inferred | `w.java` |
| Timer remain | `timerRemain` | int | seconds | status | none | read-only | same | `c.x`, `r.i` |

## 5. Enum and error-code tables

**`workMode`** (`w81/t.java`).

| Wire value | Meaning |
|---|---|
| `auto` | Auto. Also the fallback for any unknown string. |
| `turbo` | Turbo. |
| `quiet` | Quiet. A distinct mode, not manual plus low fan. |
| `manual` | Used by scenes. |
| `ventilation` | Fan-only. Uses `manualSpeedLevel`. |

**Fan level** (`w81/i.java`): LOW 1, MEDIUM 2, HIGH 3. The fallback for out-of-range values was not read.

**Drainage type** (`g0.java`).

| Wire value | Notes |
|---|---|
| `innerTank` | Default and fallback. |
| `expansionTank` | Requires the expansion sensor. |
| `pipe` | No installed flag. |
| `pump` | Requires the pump. |

**`workState`** (`b1.java`). The default and fallback is `onStandby`.

| Wire value |
|---|
| `defrost` |
| `moldRemoval` |
| `dehumidification` |
| `ventilation` |
| `compressorProtection` |
| `onStandby` |

**Compressor state.** No enum exists in this APK. **Unresolved.** Only `compressorProtection` appears in `workState`.

**`tankLevel`.** `10` = tank full (`a1.TANK_FULL`). Default is 1. No other values are defined.

**UI run status (app-derived)** (`u.java`): `standby`, `dehumidification`, `ventilation`, `defrost`, `off`, `offLine`.

**Scene state** (`p81/u`): END 0, IN_PROGRESS 1, INTERRUPT 2.

**UI banner codes** (`w81/m.java`, app-internal): TANK_NOT_INSTALL 0, WATER_FULL 1, FILTER_TIP 2, REACH_TARGET 3, DEFROST 4, MOLD_REMOVAL 5, COMPRESSOR_PROTECT 6.

**Device error codes in `errorCodes`** (`qa1/d.java:276-283`, positive ints).

| Code | Name |
|---|---|
| 11609000 | FAN_MOTOR |
| 11701000 | COMPRESSOR_ERROR |
| 11702000 | COIL_NTC_ERROR |
| 11703000 | EXHAUST_PIPE_NTC_ERROR |
| 11704000 | LACK_FLUORIDE (the name suggests refrigerant) |
| 11705000 | WATER_PUMP_ERROR |
| 11809000 | TEMPERATURE_SENSOR_ERROR |

Message text, level (1–3), steps and priority come from server config (`popup/errorText` → `d0`: `type, level, errorCode, priority, title, warning, resolveSteps, optionList, imageUrl, content`). They are not embedded in the APK. Codes not in this list are ignored by the app if the server returns no entry (`c.g`).

**Push types** (`w81/l.java`, `MyFirebaseMessagingService.java`): `dehumidifier:device:waterFull`, `…:moldRemoval`, `…:WaterTankMaintenance`, `…:WaterPumpMaintenance`, `…:drainModePumpStart`, `…:drainModePumpStop`, `…:drainModeExtendedDetectorConnected`, `…:drainModeExtendedDetectorRemoved`, `dehumidifier:waterPump:errorOccurred`, `dehumidifier:filter:lowQuality`, `…:lossQuality`, `…:noneQuality`, `dehumidifier:filter:reset:success`.

## 6. Reconstructed examples (not real traffic)

**Write, `setWorkMode`:**
```json
{
  "traceId": "<ts>", "method": "bypassV2", "token": "<TOKEN>", "accountID": "<ACCOUNT_ID>",
  "timeZone": "<tz>", "userCountryCode": "<cc>", "acceptLanguage": "en",
  "clientType": "<…>", "clientVersion": "<…>", "terminalId": "<…>", "appVersion": "<…>",
  "cid": "<DEVICE_ID>", "configModule": "<CONFIG_MODULE>",
  "payload": { "method": "setWorkMode", "source": "<APP_SOURCE>", "data": { "workMode": "quiet" } }
}
```

**Read, `getDeHumidifierStatus`:** same envelope with `"payload":{"method":"getDeHumidifierStatus","source":"<APP_SOURCE>","data":{}}`.

**Reconstructed response** (names Inferred, values are placeholders):
```json
{ "traceId": "<id>", "code": 0, "msg": "request success",
  "result": { "code": 0, "msg": "", "result": {
    "powerSwitch": 1, "workMode": "auto", "manualSpeedLevel": 1, "targetHumidity": 55, "humidity": 48,
    "childLockSwitch": 0, "screenSwitch": 1, "muteSwitch": 0, "screenState": 1, "autoStartSwitch": 0,
    "drainageTypeConfig": "innerTank", "pumpEnable": 0, "pumpWorking": 0, "pumpInPlace": 0,
    "errorCodes": [], "workState": "dehumidification", "tankInPlace": 1, "tankLevel": 1,
    "waterSensorInPlace": 0, "waterSensorDetectsWater": 0, "filterLifePercent": 90,
    "filterRemainingDays": 120, "reachTargetState": 0, "moldRemovalRemind": 0, "scheduleCount": 0,
    "timerRemain": 0, "powerSavingState": 0, "powerSavingTimeSec": 0, "resetFilterDate": 1700000000 } } }
```
Booleans may be sent as 0/1 or true/false. The app uses a custom bool serializer (`za1.b`). Check the real form at runtime.

## 7. Implementation guidance

### 7.1 Ready in pyvesync (Verified for the H321S path, Inferred for the H251S)

All of these are read from the status call:
- **Basic state:** power, humidity, target humidity, mode, manual speed.
- **Switches:** child lock, display (`screenSwitch`), mute, auto-start.
- **Tank, pump and water:** tank installed, tank full (`tankLevel == 10`), water sensor installed, water detected, pump installed, pump enabled, drainage config.
- **Diagnostics:** error codes, power-saving state and seconds, filter life, filter days, filter reset date (epoch seconds), `workState`.

**Verified setters:** `setSwitch`, `setWorkMode`, `setLevel`, `setTargetHumidity`, `setChildLock`, `setDisplay`, `setMuteSwitch`, `setAutoStart`, `setPumpSwitch`, `setDrainage`.

### 7.2 Capability and precondition checks to implement

- Do not send `setLevel` unless `workMode == "ventilation"`.
- `setTargetHumidity` is only meaningful in `auto`, `turbo` and `quiet`, with the tank installed and not full.
- `setPumpSwitch` and `setDrainage(pump)` need `pumpInPlace`.
- `setDrainage(expansionTank)` needs `waterSensorInPlace`.
- After `setDrainage` to pump or expansion tank, re-read the status and validate as in 3.2.

### 7.3 Read-only fields

Humidity, `tankLevel`, `workState`, `errorCodes`, filter life, days and reset date, `powerSavingState`, `powerSavingTimeSec`, `timerRemain`, `moldRemovalRemind`, `scheduleCount`, `pumpWorking`, `screenState`.

### 7.4 Interpretations that may be wrong (pyvesync or the prior notes)

- **Pump write key:** it is `pumpSwitch`, not `pumpEnable`. The prior notes' method table said `pumpEnable`, which is the status field. The setter descriptor is `v0.java:44`.
- **Power-saving write key:** the APK says `enabled`. See 3.3.
- **Fan control and `manual`:** the main UI applies fan level to `ventilation`, not `manual`. `manual` mode is a scene concept.
- **`tankLevel`:** it is a status code (`10` = full), not a percentage.
- **`workState` values:** see section 5. The older `standby`/`off`/`offLine` enum is the app-derived UI status, not a wire enum.
- **`resetFilterDate`:** treat as epoch seconds. This is Verified by the formatter code.
- **`moldRemovalRemind`:** a countdown while mold removal runs, not a boolean "reminder due".
- **`autoStopSwitch`:** it does not exist for dehumidifiers in this APK. The real feature is `setAutoStart`.

### 7.5 Unresolved (needs runtime capture or device testing)

- Whether the H251S uses the same command names and fields as the H321S (this APK cannot confirm it).
- `source` value in the payload.
- Current temperature, temperature scaling and unit, coil temp, exhaust-pipe temp, compressor state, `fanSpeedLevel`, `actualRunLevel`, virtual level. None of these are in this APK. Capture the live `getDeHumidifierStatus` for the H251S, then inspect the newest app version.
- Units and semantics of `moldRemovalRemind`, `scheduleCount`, `screenState`, `pumpWorking`.
- Timer or schedule control and any real-time push or websocket channel.
- Success and error semantics of Unit-returning writes, and device-specific response codes.
- Whether the Quiet-mode display and mute lock is real (3.1).
- The `enabled` versus `powerSavingSwitch` key.
- Which `tankLevel` values other than 10 exist.

## 8. Limits of this investigation

- Obfuscation: `w$a` (status serializer descriptor) is missing from the jadx output. Some control-flow blocks are duplicated or mangled (`c.n`, `c.r`).
- This APK predates or excludes the H251S module, so any H251S-specific behavior must come from runtime traffic or a newer APK.
