"""Data models for VeSync Dehumidifiers.

These models inherit from `BypassV2InnerResult` in the `bypass_models` module.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pyvesync.models.bypass_models import BypassV2InnerResult


@dataclass
class DehumidifierResult(BypassV2InnerResult):
    """Dehumidifier Result Model."""

    powerSwitch: int
    humidity: int
    targetHumidity: int
    workMode: str
    tempInF: int | None = None
    workState: str | None = None
    fanSpeedLevel: int | None = None
    manualSpeedLevel: int | None = None
    tankLevel: int | None = None
    tankInPlace: int | None = None
    screenSwitch: int | None = None
    screenState: int | None = None
    scheduleCount: int | None = None
    timerRemain: int = 0
    autoStartSwitch: int | None = None
    errorCodes: list[int] = field(default_factory=list)
    filterLifePercent: int | None = None
    filterRemainingDays: int | None = None
    resetFilterDate: int | None = None
    childLockSwitch: int | None = None
    muteSwitch: int | None = None
    powerSavingSwitch: int | None = None
    powerSavingState: int | None = None
    powerSavingTimeSec: int | None = None
    pumpInPlace: int | None = None
    pumpEnable: int | None = None
    pumpWorking: int | None = None
    waterSensorInPlace: int | None = None
    waterSensorDetectsWater: int | None = None
    moldRemovalRemind: int | None = None
    reachTargetState: int | None = None
    drainageTypeConfig: str | None = None
    compressorState: int | None = None
    coilTemp: int | None = None
    exhaustPipeTemp: int | None = None
    actualRunLevel: int | None = None
    autoStopSwitch: int | None = None
    autoStopState: int | None = None
    waterTankFull: int | None = None
    temperature: int | None = None
    virtualLevel: int | None = None
    mistLevel: int | None = None
    errorCode: int | None = None
