"""Data models for VeSync Dehumidifiers.

These models inherit from `BypassV2InnerResult` in the `bypass_models` module.
"""

from __future__ import annotations

from dataclasses import dataclass

from pyvesync.models.bypass_models import BypassV2InnerResult


@dataclass
class DehumidifierResult(BypassV2InnerResult):
    """Dehumidifier Result Model."""

    powerSwitch: int
    humidity: int
    targetHumidity: int
    virtualLevel: int
    mistLevel: int
    workMode: str
    waterTankFull: int
    autoStopSwitch: int
    autoStopState: int
    screenSwitch: int
    screenState: int
    childLockSwitch: int
    timerRemain: int
    errorCode: int
    temperature: int
