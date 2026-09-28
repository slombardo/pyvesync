# Dehumidifier APK Findings

Analysis performed against `C:\temp\vesync-src\sources` (jadx-decompiled, obfuscated Java from a jadx run recorded in `C:\temp\decompile.ps1`; original APK at `C:\tmp\vesync.apk`, not touched/modified in this session). Read-only source inspection only; no network calls made.

## Where the logic lives

- **Java/Kotlin sources (jadx `sources/`)** — Present and is where essentially all dehumidifier logic lives. Two parallel implementations exist:
  - Legacy/UI package `com.dehumidifier.*` (Activities/Fragments/Views/Dialogs) — UI glue, error dialogs, esave/scenario-dry screens.
  - Kotlin-Multiplatform (KMP) shared business logic under `com.vesync.kmp.air.dehumidifier.*` and its serialization models in package `w81` (obfuscated short package name; confirmed via `SourceDebugExtension` comments referencing `AirDehumidifierModel.kt` / `AirDeviceModel.kt`). **This `w81` package is the authoritative source for wire-format field names**, because kotlinx.serialization descriptors (`l2Var.r("fieldName", ...)`) and `toString()` implementations preserve the real JSON field names even though class/field identifiers were obfuscated.
- **React Native / Hermes bundle**: NOT FOUND. No `index.android.bundle` or similar was searched/located as part of this analysis; the dehumidifier feature is 100% native Kotlin/Java, not RN.
- **Flutter (`libapp.so`)**: NOT FOUND / not applicable — no evidence this app uses Flutter for this feature.
- **Runtime-downloaded panels**: NOT FOUND. No code was found that downloads a dehumidifier-specific UI "panel" package by `configModule`/model ID at runtime; the dehumidifier UI (Activities/Fragments/Compose screens) ships inside the APK itself.
- **`res/values/strings.xml`**: Present and used — confirmed dehumidifier-specific UI strings (see Q1, Q2).
- **Model identifiers**: `LDH-` prefix strings were **NOT FOUND** anywhere in the decompiled tree (searched via background sub-agent). The app instead keys everything off a generic `configModule` string field (present on every bypass request/response DTO, e.g. `w81.p0`, `w81.y0`, etc.) and a `deviceId`; no hard-coded model-code branching (e.g. `"LDH-H251S"`) was found in the dehumidifier package. This suggests device-specific behavior differences (if any) are server/config-driven, not client hard-coded, **or** this app build simply doesn't special-case model variants for the fields covered by these questions.

---

## Q1. Quiet mode

**Answer:** Quiet is a **distinct `workMode` value** (`"quiet"`), not manual mode + low fan speed.

**Confidence:** High

**Evidence:**
`C:\temp\vesync-src\sources\w81\t.java` (enum `t` = `AirDHWorkMode`, lines 12-17):
```java
public enum t {
    AUTO("auto"),
    TURBO("turbo"),
    QUIET("quiet"),
    MANUAL("manual"),
    VENTILATION(ln1.i.f207600n);   // ln1.i.f207600n == "ventilation"
```
`C:\temp\vesync-src\sources\com\dehumidifier\model\ScenarioMode.java` (lines 40-46) — the "expand/scenario" quick-select row maps UI labels to `(mode, manualSpeedLevel)` pairs:
```java
QUIET = new ScenarioMode("QUIET", 0, i13 /*R.string...expend_02*/, t.QUIET, i.LOW);
AUTO  = new ScenarioMode("AUTO",  1, R.string...19_04,               t.AUTO, i.LOW);
TURBO = new ScenarioMode("TURBO", 2, R.string...expend_01,           t.TURBO, i.LOW);
HIGH  = new ScenarioMode("HIGH",  3, R.string...01c_01, t.MANUAL, i.HIGH);
MED   = new ScenarioMode("MED",   4, R.string...01c_08, t.MANUAL, i.MEDIUM);
LOW   = new ScenarioMode("LOW",   5, R.string...01c_02, t.MANUAL, i.LOW);
```
Labels resolved in `C:\temp\vesync-src\resources\res\values\strings.xml:7490-7491`:
```xml
<string name="levoit_dehumidifier_main_expend_01">Turbo</string>
<string name="levoit_dehumidifier_main_expend_02">Quiet</string>
```
The `AirSetWorkModeReq` payload class only carries the `workMode` string — no speed field is sent alongside it (`C:\temp\vesync-src\sources\w81\z0.java:44-47`):
```java
l2Var.r("workMode", false);
l2Var.r("configModule", false);
l2Var.r("deviceId", false);
```

**`workMode` values the app can send/recognize (full list):**

| workMode wire value | Enum constant | UI label | Notes |
|---|---|---|---|
| `auto` | `t.AUTO` | (Auto) | Default/fallback if server sends unrecognized value (`t.a()`/`t.b()` fall back to `AUTO`) |
| `turbo` | `t.TURBO` | "Turbo" (`levoit_dehumidifier_main_expend_01`) | |
| `quiet` | `t.QUIET` | "Quiet" (`levoit_dehumidifier_main_expend_02`) | |
| `manual` | `t.MANUAL` | High/Med/Low (uses `manualSpeedLevel`) | UI further distinguishes High/Med/Low display labels, all wire-encoded as `workMode=manual` |
| `ventilation` | `t.VENTILATION` | (Ventilation / fan-only) | Also appears as `workState` value `"ventilation"` (see Q11) |

Note: `t.Companion.a(source)` (used in one code path, `t.java:87-97`) only recognizes `AUTO, TURBO, QUIET` and defaults everything else (including `manual`/`ventilation`) to `AUTO` — this looks like a narrower "scenario mode" selector context, while the general deserializer `t.Companion.b(source)` (`t.java:99-108`) recognizes all 5 values.

**Payload for selecting Quiet:**
```json
{ "workMode": "quiet" }
```
(sent to method `setWorkMode`, wrapped with the standard bypass envelope including `configModule`/`deviceId` — confirmed route name at `C:\temp\vesync-src\sources\com\vesync\kmp\air\dehumidifier\http\bypass\a.java:61` `@ba1.u("setWorkMode")`).

---

## Q2. Auto Off vs. auto-stop

**Answer:** The app's confirmed method is **`setAutoStart`**, and the UI label for it is **"Auto-Start"**, not "Auto Off". Its behavior, per the in-app help text, is: *turn the dehumidifier back on automatically after a power interruption* — i.e., resume-on-power-restore, **not** an auto-shutoff/auto-stop feature.

**Confidence:** High for what `setAutoStart`/`autoStartSwitch` does; the APK gives **no evidence of any distinct "Auto Off" feature or a `setAutoStopSwitch` method for this device.**

**Evidence:**
UI label string `C:\temp\vesync-src\resources\res\values\strings.xml:7492,7494`:
```xml
<string name="levoit_dehumidifier_main_expend_04">Auto-Start</string>
<string name="levoit_dehumidifier_main_expend_06">This mode will automatically turn the dehumidifier on when power is connected.</string>
```
UI wiring, `C:\temp\vesync-src\sources\com\dehumidifier\ui\config\nvg\ComDeHumNvgFragment.java:1086-1088`:
```java
ControlItemView autoStartItemView = comDeHumNvgFragment.O1().autoStartItemView;
Intrinsics.o(autoStartItemView, "autoStartItemView");
comDeHumNvgFragment.d4(autoStartItemView, R.string.levoit_dehumidifier_main_expend_06);
```
API route + request payload, `C:\temp\vesync-src\sources\com\vesync\kmp\air\dehumidifier\http\bypass\a.java:216-217` (`@ba1.u("setAutoStart")`), and `C:\temp\vesync-src\sources\w81\o0.java` (`AirSetAutoStartReq`, field `autoStartSwitch` — int 0/1, plus `configModule`/`deviceId`).

**Is there a separate `setAutoStopSwitch`/`autoStopSwitch` for this device?**
**NOT FOUND.** Searched the whole decompiled tree for `autoStopSwitch`/`AutoStop` (case-insensitive) — every match is in the **humidifier** code (`com.humidifierV2.model.SetAutoStopSwitchParam`, `com.humidifierV2.model.ModelHumidifierStatus`, `com.vesync.kmp.air.humidifier.*`), never in `com.dehumidifier` or `com.vesync.kmp.air.dehumidifier`. **pyvesync's current assumption of `setAutoStopSwitch`/`autoStopSwitch` for the dehumidifier does not match anything in this APK** — that call likely simply doesn't exist for this device family. The status model `w81.w` (`AirDehumidifierStatus`) has no `autoStopSwitch` field; it does have `autoStartSwitch` (see full field table below).

**Relation to `reachTargetState` / `autoStartSwitch` / `tankLevel`:**
No code path was found that ties `autoStartSwitch` to `reachTargetState` or `tankLevel` — they are three independent boolean/int fields on `AirDehumidifierStatus` (`w81.w`) with no cross-referencing logic visible in the reviewed fragments/viewmodels. `reachTargetState` appears to be a pure status flag (device reached the configured `targetHumidity`) with no client-side "turn off" logic attached to it in the code reviewed — turning off when the target is reached, if it happens, is device-firmware behavior reported via this status flag, not something the app triggers by calling an "auto-stop" API.

**Conclusion:** "Auto Off" as pyvesync/HA might label a control does not exist as such in this app. The real, confirmed feature is "Auto-Start" (resume power-on state after outage), controlled by `setAutoStart`/`autoStartSwitch`, and reflected back by the `autoStartSwitch` status field.

---

## Q3. Target humidity range

**Answer:** **35–70%, hard-coded client-side**, default target 55%, step 1 (whole percent). A separate, narrower **recommended band of 40–60%** is shown as a visual hint inside the same slider (not a hard limit).

**Confidence:** High for the 35–70 selectable range and the 40–60 recommended band (both found hard-coded in two independent places); Medium on "step = 1" (inferred from the seek-bar being an integer-percent control with no explicit step parameter found).

**Evidence:**
1. UI slider bounds, `C:\temp\vesync-src\sources\com\dehumidifier\view\DhTargetHumidityView.java:65-67`:
```java
this.f54966b = new IntRange(35, 70);
...
this.f54965a.recommendSeekBar.setProgressStart(this.f54966b.d());  // 35
this.f54965a.recommendSeekBar.setProgressEnd(70);
```
Recommended-band text at line ~140: `l1.c(com.vesync.resource.R.string.levoit_dehumidifier_main_expend_05, "40-60")` → renders as *"40-60% is recommended"* (string `levoit_dehumidifier_main_expend_05` = `"%s%% is recommended"`, `strings.xml:7493`).

2. ViewModel default state, `C:\temp\vesync-src\sources\com\vesync\kmp\air\dehumidifier\vm\dehumidifiermain\o.java:236`:
```java
(i14 & 512)  != 0 ? new IntRange(40, 60) : intRange,   // recommendHumidifier
(i14 & 1024) != 0 ? new IntRange(35, 70) : intRange2,  // humidityOptionalRange
(i14 & 128)  != 0 ? 50 : i13,                          // default targetHumidity when unset = 50
```
No call site in `AirDeHumidifierMainViewModel` (`b0.java`, the file that builds this state from live device status) overrides `humidityOptionalRange`/`recommendHumidifier` with device-supplied values — grep for `IntRange(` in `b0.java` returns no matches — so the 35–70 bound is not read from a per-device/server config in the code paths reviewed; it is a constant for all dehumidifier devices in this app build.

3. Status model default target humidity is 55, `C:\temp\vesync-src\sources\w81\w.java` (constructor comments / `toString`), consistent with `targetHumidity` default seen in the two view/viewmodel defaults above.

**Special values below the minimum ("continuous"/CO mode):** NOT FOUND. No evidence of a special "continuous" sentinel value or below-minimum mode for target humidity in the dehumidifier code.

**Per-model variation:** NOT FOUND — no branching on model/`configModule` for the humidity range was located.

---

## Q4. Timer and e-save (power saving)

### Timer

**Answer:** There is **no dehumidifier-specific `addTimer`/`getTimer`/`delTimer` bypass method**. The complete list of dehumidifier bypass-V2 methods found (interface `com.vesync.kmp.air.dehumidifier.http.bypass.a`, full contents read) is:

```
getDeHumidifierStatus, setDrainage, setMuteSwitch, setDisplay, setChildLock,
setAutoStart, setPumpSwitch, setTargetHumidity, setSwitch, setWorkMode,
setLevel, setPowerSavingSwitch, getPowerSavingConfig,
addPowerSavingSlot, updatePowerSavingSlot, deletePowerSavingSlot
```
(Evidence: `C:\temp\vesync-src\sources\com\vesync\kmp\air\dehumidifier\http\bypass\a.java`, full file — method-name constants at lines 26-73 and `@ba1.u(...)`-annotated interface methods at lines 156-220.)

None of these is `addTimer`/`getTimer`/`delTimer`. A **generic, device-agnostic** legacy timer API does exist elsewhere in the app (`com.vesync.schedule.http.ScheduleApi` / `MethodKt`: `ADD_TIMER="addTimer"`, `GET_TIMER="getTimer"`, `DELETE_TIMER="delTimer"`, plus V2/V3 variants), with payload model `com.vesync.schedule.model.AddTimer`:
```java
public final class AddTimer {
    private final String action;   // e.g. "on" (legacy V1 timer convention elsewhere in app)
    private final int total;       // total duration
}
```
**However, no call site inside `com.dehumidifier.*` or `com.vesync.kmp.air.dehumidifier.*` invoking this generic Schedule/Timer API was found** — searched for `Timer`/`addTimer`/`getTimer`/`delTimer` across both packages; the only hits are:
- `com.vesync.kmp.air.dehumidifier.util.e` (`AirTimerService`) — a **purely local, in-memory coroutine countdown** (`kotlinx.coroutines.flow`), not a network call. It just ticks a `Flow<Integer>` down once per second from a starting value.
- `AirDeHumidifierMainViewModel` (`b0.java`) has `handleClickTimerIntent`/`startTimer` methods, but their bodies (as decompiled) call into `AirTimerService`/local UI state, not a bypass or schedule API.
- View-model state class `n.java` (`AirDHTimerState`) only carries a `reminderTime` field plus `showFunc`/`enableFunc` flags — consistent with a local reminder countdown, not a server-side schedule.

**Conclusion (Medium-High confidence):** For this device, the "timer" UI most likely just displays/counts down the `timerRemain` value that the device itself reports in `getDeHumidifierStatus`, decremented locally between polls for a smooth UI (classic "client interpolates between polls" pattern), rather than the app creating a server-side timer via `addTimer`. **I could not find code that lets the app itself create/query/delete a timer for the dehumidifier** — this is an open item; it's possible that capability doesn't exist for this device, or is driven by the shared cross-device `com.vesync.schedule` module through a code path not reached by my searches (its generic nature makes it hard to prove a negative). Payload shape/allowed durations/allowed `action` values for a hypothetical dehumidifier `addTimer` call: **NOT FOUND**.

**`timerRemain` meaning/units:** Not explicitly documented in code, but by construction (paired with the local per-second countdown in `AirTimerService`) it behaves as **seconds remaining**. No explicit unit conversion/label was found to contradict this.

**Turn on after timer (device off):** NOT FOUND — no evidence either way given no confirmed timer-creation call was located.

### E-save / power saving

**Answer:** `setPowerSavingSwitch` is a simple **on/off toggle** for a power-saving feature that runs on **time-of-day schedule slots**, configured separately via `getPowerSavingConfig` / `addPowerSavingSlot` / `updatePowerSavingSlot` / `deletePowerSavingSlot`.

**Confidence:** High

**Evidence — the toggle itself**, `C:\temp\vesync-src\sources\w81\u0.java:36-42` (`AirSetPowerSavingSwitchReq`):
```java
l2Var = new l2("com.vesync.kmp.air.dehumidifier.model.AirSetPowerSavingSwitchReq", aVar, 3);
l2Var.r("enabled", false);
l2Var.r("configModule", false);
l2Var.r("deviceId", false);
```
⚠️ **Discrepancy flag:** the decompiled request body field is literally **`enabled`** (int 0/1), *not* `powerSavingSwitch`. This conflicts with what you confirmed live against your real device (`{"powerSavingSwitch": 0|1}`). Both can't be verified as simultaneously true from this evidence alone — possibilities: (a) this APK build/version encodes a different wire field than your device's current firmware/backend expects, (b) the backend accepts both keys, or (c) there's a second/updated request class for this call that jadx didn't surface under this exact path. **Since your own live capture is ground truth for your device, trust `powerSavingSwitch` for that field name — but flag this class (`w81.u0`) as the likely origin of the `enabled` naming if you see it in older API traces or other client versions.**

**Evidence — schedule config**, `C:\temp\vesync-src\sources\w81\m0.java` (`AirPowerSavingConfigResponse`, fields `enabled` (int) + `slots: List<AirPowerSavingSlot>`) and `C:\temp\vesync-src\sources\w81\n0.java` (`AirPowerSavingSlot`, fields `id`, `startMin`, `endMin` — all ints, i.e. minute-of-day start/end):
```java
l2Var.r("id", false); l2Var.r("startMin", false); l2Var.r("endMin", false);
```
Add/update slot request, `C:\temp\vesync-src\sources\w81\a.java:37-42` (`AirAddOrUpdatePowerSavingSlotReq`):
```java
l2Var.r("id", true);        // optional (present for update, absent for add)
l2Var.r("startMin", false);
l2Var.r("endMin", false);
l2Var.r("configModule", false);
l2Var.r("deviceId", false);
```
Route names, `C:\temp\vesync-src\sources\com\vesync\kmp\air\dehumidifier\http\bypass\a.java:180-220`: `getPowerSavingConfig`, `addPowerSavingSlot` (returns a `w81.b` response with an id), `updatePowerSavingSlot`, `deletePowerSavingSlot` (request `w81.x`, not fully inspected but presumed to carry the slot `id`).

**`powerSavingState` / `powerSavingTimeSec` meaning:** These are **status/read-only fields** (on `AirDehumidifierStatus`, confirmed by `toString()` at `w.java:535`: `...powerSavingState=" + this.B + ", powerSavingTimeSec=" + this.C...`). No code was found computing/consuming `powerSavingTimeSec` beyond storing/displaying it, so its precise semantics (e.g., "seconds until next slot" vs "seconds power-saving has been active") could not be confirmed — **NOT FOUND** beyond field existence and default value 0.

**What triggers power-saving to become active:** Time-of-day, via the configured slots (`startMin`/`endMin`), while `enabled`/`powerSavingSwitch` is on — this is a schedule evaluated device-side (or possibly cloud-side); no app-side trigger logic beyond CRUD of slots was found.

**Does enabling it disable/change other controls?** NOT FOUND — no UI code was reviewed showing other controls being disabled when power-saving activates (only `ESaveActivity`/`CreateOrEditESaveDialog` UI for managing the schedule slots themselves was inspected).

---

## Additional questions

### Q5. Fan speed

**Answer:** A **dedicated `setLevel` method exists** (this is new information beyond your confirmed method list) with payload field **`manualSpeedLevel`** (int 1/2/3 = LOW/MEDIUM/HIGH).

**Confidence:** High

**Evidence:** Route, `C:\temp\vesync-src\sources\com\vesync\kmp\air\dehumidifier\http\bypass\a.java:203-205`:
```java
@ba1.u("setLevel")
Object h(@rq2.l s0 s0Var, @rq2.l Continuation<? super Unit> continuation);
```
Payload, `C:\temp\vesync-src\sources\w81\s0.java:44` (field name resolved via constant `h70.i1.f174771w`):
```java
l2Var.r(i1.f174771w, false);   // i1.f174771w == "manualSpeedLevel"  (h70/i1.java:99)
l2Var.r("configModule", false);
l2Var.r("deviceId", false);
```
Level enum, `C:\temp\vesync-src\sources\w81\i.java:13-15` (`AirDHFanSpeedLevel`):
```java
LOW(1), MEDIUM(2), HIGH(3);
```
So the exact payload is: `{ "manualSpeedLevel": 1|2|3 }` via method `setLevel` — **not** `setVirtualLevel`/`levelIdx` as used by some other VeSync device families.

**Valid range:** 1–3 only (LOW/MEDIUM/HIGH) — no finer granularity found for this model.

**Is fan speed only settable in manual mode?** Strong circumstantial evidence yes: `ScenarioMode` only assigns distinct `manualSpeedLevel` values (`HIGH/MEDIUM/LOW`) when `mode == t.MANUAL`; for `AUTO`/`TURBO`/`QUIET` the associated `manualSpeedLevel` is always `i.LOW` (a throwaway/default), implying the UI doesn't let the user pick a level in those modes (`ScenarioMode.java:40-42`). No explicit server-side rejection logic was found (that would live server-side, not in this APK).

**`fanSpeedLevel` vs `manualSpeedLevel` vs `actualRunLevel`:** The decompiled `AirDehumidifierStatus` (`w81.w`) model **only contains `manualSpeedLevel`** (the last commanded/manual level) — it has **no `fanSpeedLevel` or `actualRunLevel` field** (see full field table below). ViewModel state classes (`o.java`, `l.java` — `AirDHWorkModeState`/`AirDHRunStatusState`) do have a client-side `fanSpeedLevel: w81.i` property, but it's a **derived/display value computed by the app**, not a field parsed directly off the wire in the status model reviewed. This strongly suggests `fanSpeedLevel` and `actualRunLevel` are newer wire fields (added to the live API after this APK's model classes were generated) that this app version doesn't explicitly parse — it's likely tolerant/ignores unknown JSON keys. **This is an open item**: I could not find where `fanSpeedLevel`/`actualRunLevel` are consumed from the wire in this codebase.

### Q6. State rules

Partial evidence only. `ScenarioMode` (Q1/Q5) shows fan-level selection is meaningful only for `MANUAL`. `DhTargetHumidityView.setEnable(boolean)` (`DhTargetHumidityView.java` line ~104) dims/enables the humidity slider as a whole (alpha 0.65 when disabled), called presumably when power is off or in a mode where target humidity doesn't apply — but the exact call sites (which modes/power states pass `false`) were **NOT FOUND** in the files reviewed (would require reading the full `ComDeHumNvgFragment.java`/`AirDeHumidifierMainViewModel` state-reduction logic, which is very large — see Open Items). Tank-full disabling of controls: **NOT FOUND** in the reviewed subset.

### Q7. `errorCodes`

**Answer:** Error code → message/level/steps mapping is **NOT embedded in the APK as a static table** — it's modeled as a **server-driven content object**.

**Confidence:** High that it's server-driven; the code confirms the *shape* of that content, not the concrete code→message table.

**Evidence:** `C:\temp\vesync-src\sources\w81\g.java` (`AirDHErrorInfo`) fields: `errorCode` (int), `level` (enum `h`: `LEVEL_1`/`LEVEL_2`/`LEVEL_3`), `priority` (int), `title` (String), `content` (String), `errorImg` (nullable String — an **image URL**, a strong signal of CMS/server-driven content), `resolveSteps` (`List<AirDHStep>` — each step has `step`/`info` text, `w81.r.java`), `tip` (nullable String), `buttonText` (nullable String). No JSON asset or hard-coded map from `errorCode` (int) → `AirDHErrorInfo` was found anywhere in `sources/` or searched under `resources/` (searched for `AirDHErrorInfo`/`errorInfoList`/`DHError` in json files — no matches). The two dialog classes `ErrorLevel1Dialog`/`ErrorLevel2Dialog` (`com.dehumidifier.view.dialog.*`, both fully read) simply render whatever `AirDHErrorInfo` object they're given — they contain no code→text table themselves; Level 1 shows a full-screen dialog with numbered resolution steps, Level 2 shows a bottom-sheet with either a single description or a numbered step list, both driven purely by the passed-in `g` (`AirDHErrorInfo`) object.

**Conclusion:** The actual error-code table (which codes exist, what tank-full/sensor-fault/compressor-fault/defrost messages look like) is very likely fetched from a VeSync backend content/config endpoint at runtime and **is not recoverable from static APK analysis**. This is an important limitation to report back: **if you need the concrete error-code table, this APK cannot provide it.**

### Q8. `tankLevel` / `tankInPlace`

`tankInPlace` (`w81.w` field `f268936r`, boolean, **default `true`**) and `tankLevel` (`f268937s`, int, **default `1`**) are both plain status booleans/ints on `AirDehumidifierStatus`. No enum or named constants for `tankLevel`'s possible integer values were found (unlike `drainageTypeConfig`, `workState`, `workMode`, which are all proper serialized enums) — **NOT FOUND**: whether `tankLevel` is a 0/1 full-flag, or a finer scale, could not be determined from the code (it's typed as a bare `int`, with no consuming logic located in the files reviewed).

### Q9. `drainageTypeConfig`

**Answer — all 4 allowed values found:**

`C:\temp\vesync-src\sources\w81\g0.java:11-14` (`AirDrainageType`):
```java
INNER_TANK("innerTank"),
EXPANSION_TANK("expansionTank"),
PIPE("pipe"),
PUMP("pump");
```
Default is `INNER_TANK` (both as enum fallback and as the `AirDehumidifierStatus.drainageTypeConfig` default). The `setDrainage` request payload field is literally **`drainageType`** (not `drainageTypeConfig`) per `C:\temp\vesync-src\sources\w81\r0.java` descriptor (`l2Var.r(InstallingInstructionActivity.f54889d, false)`, where that constant resolves to `"drainageType"`), while the **status** field that reports the current value back is `drainageTypeConfig`. So: you *read* `drainageTypeConfig`, but you *write* `{"drainageType": "innerTank"|"expansionTank"|"pipe"|"pump"}` via `setDrainage`. (Your confirmed live test used `"innerTank"`/`"pump"` — both match two of these four enum values; `expansionTank` and `pipe` are additional values this app's model supports that you haven't tried.)

**Relation to `pumpEnable`/`pumpInPlace`:** No explicit cross-validation code (e.g., "can't select PUMP if `pumpInPlace` is false") was found in the reviewed files — these three fields (`drainageTypeConfig`, `pumpEnable`, `pumpInPlace`) all live independently on `AirDehumidifierStatus`; `SelectDrainageTypeActivity`/`SelectSetUpDrainageActivity` (present under `com.dehumidifier.ui.setting`) were not read in full and may contain this logic — **Open item**.

### Q10. Temperatures

**Answer:** For the one temperature-scaling rule directly located in dehumidifier-adjacent shared code, the wire value is a raw integer that must be **divided by 10** to get actual °F. **`coilTemp`/`exhaustPipeTemp` scaling: NOT FOUND** (no dehumidifier-specific code referencing these two field names exists in this decompiled build at all — see Where-the-logic-lives note and Q5 open item on newer fields).

**Confidence:** Medium (the /10 rule is confirmed for a same-named `tempInF` field in a **sibling** humidity-history model, not proven for the live top-level status field you observed).

**Evidence:** `C:\temp\vesync-src\sources\w81\k0.java` (`AirHumidityInfo`, used for humidity/temp history charting) constructor:
```java
this.f268824d = f13 != null ? Double.valueOf(((double) f13.floatValue()) / ((double) 10)) : null;
// field f13 = wire "tempInF" (Float); field f268824d = derived "tempF" (Double) = tempInF / 10
```
Serialization descriptor confirms field names, `k0.java:44-47`:
```java
l2Var.r("timestamp", false);
l2Var.r("humidity", false);
l2Var.r("tempInF", true);
l2Var.r("tempF", true);
```
Additionally, a generic unit-preference converter exists at `C:\temp\vesync-src\sources\com\vesync\kmp\air\dehumidifier\util\d.java` (°F↔°C, standard formula `F = C*1.8+32`), used to re-display an already-computed temperature in the user's preferred unit — this is a **second, independent** conversion layered on top of the /10 raw-value scaling, and applies generically (not dehumidifier-specific math).

**Conclusion / open item:** `coilTemp` and `exhaustPipeTemp` are not present anywhere in this decompiled dehumidifier code, and the top-level status model (`AirDehumidifierStatus`/`w81.w`) has no `tempInF` field either (see Q5's open item) — meaning your confirmed live API response includes fields this APK build's client code doesn't know about. Best-effort guidance: **if the live `tempInF` value follows the same convention as `AirHumidityInfo.tempInF`, divide by 10 to get °F** — but this is an inference across a related-but-not-identical model, not directly proven for the live status payload.

### Q11. `workState`

**Answer — full enum found**, `C:\temp\vesync-src\sources\w81\b1.java:12-17` (`AirWorkState`):
```java
DE_FROST("defrost"),
MOLD_REMOVAL("moldRemoval"),
DEHUMIDIFIER("dehumidification"),
VENTILATION("ventilation"),
COMPRESSOR_PROTECTION("compressorProtection"),
ON_STANDBY("onStandby");
```
Default/fallback is `ON_STANDBY` (`"onStandby"`) — used both as the enum-deserialization fallback and as `AirDehumidifierStatus.workState`'s default value.

A **second, seemingly older/alternate** work-state-like enum was found at `C:\temp\vesync-src\sources\w81\u.java:8-13`, with different wire strings: `standby`, `dehumidification`, `ventilation`, `defrost`, `off`, `offLine` — this one is used somewhere else in the codebase (not confirmed to be for the same status field; flagged as a possible legacy/alternate representation, not double-checked against actual usage sites due to time constraints — **Open item**).

### Q12. Response codes `-11302030` / `11003000`

**NOT FOUND.** Searched the full decompiled tree for both exact strings (`-11302030`, `11003000`) — zero matches. A **different, unrelated** code `-11003000` (extra dash and one fewer trailing zero than what you asked about) does appear in a few generic error-handling files (`cm/c.java`, `com/vesync/base/y0.java`, `qa1/d.java`), but nothing conclusively tied to the dehumidifier, and it doesn't match either of your two codes exactly. Treat this as **not resolvable from this APK** — these look like backend/cloud response codes that may simply not appear in client-side string/constant form (i.e., handled generically by a numeric-range check rather than a named constant).

---

## Complete method table

| UI control | API method | Payload JSON | Status field(s) | Notes |
|---|---|---|---|---|
| Get status | `getDeHumidifierStatus` | `{}` | (all) | Confirmed by you; response type `w81.w` |
| Power on/off | `setSwitch` | `{"powerSwitch":0\|1,"switchIdx"?:int}` | `powerSwitch` | `switchIdx` optional/nullable field also exists in payload (`w81.x0`) |
| Target humidity | `setTargetHumidity` | `{"targetHumidity":35-70}` | `targetHumidity` | Range hard-coded client-side, see Q3 |
| Work mode | `setWorkMode` | `{"workMode":"auto"\|"turbo"\|"quiet"\|"manual"\|"ventilation"}` | `workMode` | See Q1 |
| Fan/manual speed | `setLevel` **(new — not in your original list)** | `{"manualSpeedLevel":1\|2\|3}` | `manualSpeedLevel` | LOW=1,MEDIUM=2,HIGH=3 |
| Child lock | `setChildLock` | `{"childLockSwitch":0\|1}` | `childLockSwitch` | |
| Mute | `setMuteSwitch` | `{"muteSwitch":0\|1}` | `muteSwitch` | |
| Power saving toggle | `setPowerSavingSwitch` | decompiled field is `{"enabled":0\|1}`; **your live capture showed `{"powerSavingSwitch":0\|1}`** | `powerSavingState`, `powerSavingTimeSec` | ⚠️ Field-name discrepancy, see Q4 |
| Power-saving schedule | `getPowerSavingConfig` / `addPowerSavingSlot` / `updatePowerSavingSlot` / `deletePowerSavingSlot` **(new)** | `{"startMin":int,"endMin":int[,"id":int]}` | (n/a — separate schedule object) | Minute-of-day slots, see Q4 |
| Auto-Start (resume after power loss) | `setAutoStart` | `{"autoStartSwitch":0\|1}` | `autoStartSwitch` | NOT "auto off"; see Q2 |
| Water pump | `setPumpSwitch` | `{"pumpEnable":0\|1}` | `pumpEnable`, `pumpWorking`, `pumpInPlace` | |
| Display/screen | `setDisplay` | `{"screenSwitch":0\|1}` | `screenSwitch`, `screenState` | |
| Drainage type | `setDrainage` | `{"drainageType":"innerTank"\|"expansionTank"\|"pipe"\|"pump"}` | `drainageTypeConfig` | Write field name differs from read field name, see Q9 |
| Timer | NOT FOUND (dehumidifier-specific) | — | `timerRemain`, `scheduleCount` | See Q4 |

---

## Complete workMode table

| workMode value | UI label | Notes |
|---|---|---|
| `auto` | (Auto) | Default/fallback value |
| `turbo` | "Turbo" | |
| `quiet` | "Quiet" | Distinct mode, not manual+low |
| `manual` | High / Med / Low (via `manualSpeedLevel` 3/2/1) | Only mode where `setLevel` selection is meaningful |
| `ventilation` | (Ventilation / fan-only) | Also a `workState` value |

---

## Full `AirDehumidifierStatus` (`w81.w`, i.e. `getDeHumidifierStatus` response) field list, in wire order

Recovered from the class's `toString()` implementation (`w81\w.java:535`), which is the most reliable source since jadx failed to reconstruct the kotlinx.serialization descriptor class for this particular model (confirmed: no `l2Var.r(...)` calls found in `w.java` itself, unlike every other model in this package):

```
powerSwitch, workMode, manualSpeedLevel, targetHumidity, humidity, childLockSwitch,
screenSwitch, muteSwitch, screenState, autoStartSwitch, drainageType, drainageTypeConfig,
pumpEnable, pumpWorking, pumpInPlace, errorCodes, workState, tankInPlace, tankLevel,
waterSensorInPlace, filterLifePercent, filterRemainingDays, reachTargetState,
waterSensorDetectsWater, moldRemovalRemind, scheduleCount, timerRemain, powerSavingState,
powerSavingTimeSec, sceneStateList, resetFilterDate
```

Fields present in your live capture but **NOT present** in this decompiled model: `tempInF`, `fanSpeedLevel`, `powerSavingSwitch` (as a status field name — the model instead uses `powerSavingState`), `compressorState`, `coilTemp`, `exhaustPipeTemp`, `actualRunLevel`. This strongly suggests this APK build is older than the firmware/backend schema your device currently returns, and that these newer fields are simply ignored/unparsed by this app version rather than being absent from the protocol.

Fields present in this model but not in your listed live fields: `drainageType` (separate from `drainageTypeConfig`), `sceneStateList` (list of scenario-dry states, out of scope here).

---

## Open items / couldn't determine

1. **`fanSpeedLevel` / `actualRunLevel` / `compressorState` / `coilTemp` / `exhaustPipeTemp` / top-level `tempInF`** — not present in the decompiled `AirDehumidifierStatus` model at all. Searched exhaustively (`grep` across entire `sources/` tree) — these look like newer API fields added after this APK build. Cannot determine scaling/meaning from this APK; recommend trusting your own live captures for these.
2. **Concrete `errorCodes` → message/level table** — confirmed to be server/CMS-driven (image URLs, nullable tip/button text in the model), not embedded in the APK. Cannot be recovered by static analysis.
3. **Timer add/get/delete for the dehumidifier specifically** — no dehumidifier bypass method found; a generic, unrelated `com.vesync.schedule` Timer API exists in the app but no call site tying it to the dehumidifier was located. `timerRemain`/`scheduleCount` semantics beyond "some seconds-remaining counter, decremented locally by `AirTimerService` between polls" could not be fully confirmed.
4. **`setPowerSavingSwitch` payload field name discrepancy** (`enabled` in decompiled code vs. `powerSavingSwitch` in your live capture) — flagged above; recommend trusting your live capture, but worth being aware the same endpoint name may accept different historical field names.
5. **State-disabling rules (Q6)** — only partial evidence (fan level only meaningful in `manual`; a generic `setEnable(boolean)` on the humidity slider). Full state-machine (which controls disable when off/tank full/in which `workMode`) would require reading the very large `AirDeHumidifierMainViewModel` (`b0.java`, thousands of lines) end-to-end, which was only partially reviewed due to size.
6. **`tankLevel` integer scale** and **`drainageTypeConfig` ↔ `pumpEnable`/`pumpInPlace` validation rules** — fields exist but no consuming/validating logic was located in the files reviewed (`SelectDrainageTypeActivity`/`SelectSetUpDrainageActivity` were not read in full).
7. **Model identifiers (`LDH-...`, `configModule` values)** — no hard-coded model-code strings found anywhere in the dehumidifier package; the app appears to treat `configModule` as an opaque per-device string, not a client-side branch key, for all the behaviors covered here.
8. **Response codes `-11302030` / `11003000`** — not found anywhere in the APK.
