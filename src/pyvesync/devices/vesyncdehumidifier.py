"""VeSync Dehumidifier Devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import orjson

from pyvesync.base_devices.dehumidifier_base import VeSyncDehumidifierBase
from pyvesync.const import ConnectionStatus, DehumidifierModes, DeviceStatus
from pyvesync.models import dehumidifier_models as models
from pyvesync.utils.device_mixins import (
    BypassV2Mixin,
    process_bypassv2_response,
    process_bypassv2_result,
)
from pyvesync.utils.helpers import Timer, Validators

if TYPE_CHECKING:
    from pyvesync import VeSync
    from pyvesync.device_map import DehumidifierMap
    from pyvesync.models.vesync_models import ResponseDeviceDetailsModel


logger = logging.getLogger(__name__)


class VeSyncDehumidifier(BypassV2Mixin, VeSyncDehumidifierBase):
    """VeSync Dehumidifier Class.

    Uses the Bypass V2 command family to read and write humidity, fan speed,
    mode, power, display, child lock, and supported advanced status/control paths.

    Args:
        details (ResponseDeviceDetailsModel): The device details.
        manager (VeSync): The manager object for API calls.
        feature_map (DehumidifierMap): The feature map for the device.

    Attributes:
        state (DehumidifierState): The state of the dehumidifier.
        last_response (ResponseInfo): Last response from API call.
        manager (VeSync): Manager object for API calls.
        device_name (str): Name of device.
        device_image (str): URL for device image.
        cid (str): Device ID.
        connection_type (str): Connection type of device.
        device_type (str): Type of device.
        type (str): Type of device.
        uuid (str): UUID of device, not always present.
        config_module (str): Configuration module of device.
        mac_id (str): MAC ID of device.
        current_firm_version (str): Current firmware version of device.
        device_region (str): Region of device. (US, EU, etc.)
        pid (str): Product ID of device, pulled by some devices on update.
        sub_device_no (int): Sub-device number of device.
        product_type (str): Product type of device.
        features (list[str]): Features of device.
        fan_levels (list[int]): List of fan speed levels.
        modes (dict[str, str]): Dictionary of operating modes.
        target_minmax (tuple[int, int]): Tuple of target min and max humidity values.
    """

    __slots__ = ()

    def __init__(
        self,
        details: ResponseDeviceDetailsModel,
        manager: VeSync,
        feature_map: DehumidifierMap,
    ) -> None:
        """Initialize Dehumidifier class."""
        super().__init__(details, manager, feature_map)

    def _set_state(self, resp_model: models.DehumidifierResult) -> None:
        """Set state from Dehumidifier API result model."""
        self.state.device_status = DeviceStatus.from_int(resp_model.powerSwitch)
        self.state.connection_status = ConnectionStatus.ONLINE
        self.state.mode = self._reverse_modes.get(resp_model.workMode)
        if self.state.mode is None:
            logger.warning('Unknown mode received: %s', resp_model.workMode)

        self.state.target_humidity = resp_model.targetHumidity
        self.state.humidity = resp_model.humidity
        self.state.work_state = resp_model.workState
        self.state.fan_speed = resp_model.fanSpeedLevel
        self.state.manual_fan_speed = resp_model.manualSpeedLevel
        self.state.fan_virtual_speed = resp_model.manualSpeedLevel
        self.state.tank_level = resp_model.tankLevel
        self.state.tank_in_place = (
            bool(resp_model.tankInPlace) if resp_model.tankInPlace is not None else None
        )
        self.state.water_tank_full = bool(resp_model.waterTankFull)
        self.state.display_set_status = DeviceStatus.from_int(resp_model.screenSwitch)
        self.state.display_status = DeviceStatus.from_int(resp_model.screenState)
        self.state.schedule_count = resp_model.scheduleCount
        self.state.auto_start = (
            bool(resp_model.autoStartSwitch)
            if resp_model.autoStartSwitch is not None
            else None
        )
        self.state.error_codes = list(resp_model.errorCodes)
        self.state.filter_life_percent = resp_model.filterLifePercent
        self.state.filter_remaining_days = resp_model.filterRemainingDays
        self.state.reset_filter_date = resp_model.resetFilterDate
        self.state.child_lock = (
            bool(resp_model.childLockSwitch)
            if resp_model.childLockSwitch is not None
            else None
        )
        self.state.mute_status = DeviceStatus.from_int(resp_model.muteSwitch)
        self.state.power_saving_status = DeviceStatus.from_int(
            resp_model.powerSavingSwitch
        )
        self.state.power_saving_active = (
            bool(resp_model.powerSavingState)
            if resp_model.powerSavingState is not None
            else None
        )
        self.state.power_saving_time_sec = resp_model.powerSavingTimeSec
        self.state.pump_installed = (
            bool(resp_model.pumpInPlace) if resp_model.pumpInPlace is not None else None
        )
        self.state.pump_enabled = (
            bool(resp_model.pumpEnable) if resp_model.pumpEnable is not None else None
        )
        self.state.pump_working = (
            bool(resp_model.pumpWorking) if resp_model.pumpWorking is not None else None
        )
        self.state.water_sensor_in_place = (
            bool(resp_model.waterSensorInPlace)
            if resp_model.waterSensorInPlace is not None
            else None
        )
        self.state.water_sensor_detects_water = (
            bool(resp_model.waterSensorDetectsWater)
            if resp_model.waterSensorDetectsWater is not None
            else None
        )
        self.state.mold_removal_reminder = (
            bool(resp_model.moldRemovalRemind)
            if resp_model.moldRemovalRemind is not None
            else None
        )
        self.state.reach_target = (
            bool(resp_model.reachTargetState)
            if resp_model.reachTargetState is not None
            else None
        )
        self.state.drainage_mode = resp_model.drainageTypeConfig
        self.state.compressor_state = DeviceStatus.from_int(resp_model.compressorState)
        self.state.coil_temperature = resp_model.coilTemp
        self.state.exhaust_pipe_temperature = resp_model.exhaustPipeTemp
        self.state.actual_run_level = resp_model.actualRunLevel
        self.state.temperature = (
            resp_model.tempInF
            if resp_model.tempInF is not None
            else resp_model.temperature
        )
        if resp_model.timerRemain > 0:
            self.state.timer = Timer(
                resp_model.timerRemain,
                DeviceStatus.from_bool(self.state.device_status != DeviceStatus.ON),
            )
        else:
            self.state.timer = None

    async def get_details(self) -> None:
        r_dict = await self.call_bypassv2_api('getDeHumidifierStatus')
        r_model = process_bypassv2_result(
            self, logger, 'get_details', r_dict, models.DehumidifierResult
        )
        if r_model is None:
            return

        self._set_state(r_model)

    async def toggle_switch(self, toggle: bool | None = None) -> bool:
        """Toggle the dehumidifier power on/off."""
        if toggle is None:
            toggle = self.state.device_status != DeviceStatus.ON

        payload_data = {'powerSwitch': int(toggle), 'switchIdx': 0}
        r_dict = await self.call_bypassv2_api('setSwitch', payload_data)
        r = process_bypassv2_response(self, logger, 'toggle_switch', r_dict)
        if r is None:
            return False

        self.state.device_status = DeviceStatus.from_bool(toggle)
        self.state.connection_status = ConnectionStatus.ONLINE
        return True

    async def toggle_display(self, toggle: bool | None = None) -> bool:
        """Toggle the display on/off."""
        if not self.supports_display:
            logger.warning(
                '%s is a %s does not have a display or it is not supported.',
                self.device_name,
                self.device_type,
            )
            return False

        if toggle is None:
            toggle = self.state.display_set_status != DeviceStatus.ON

        payload_data = {'screenSwitch': int(toggle)}
        r_dict = await self.call_bypassv2_api('setDisplay', payload_data)
        r = process_bypassv2_response(self, logger, 'set_display', r_dict)
        if r is None:
            return False

        self.state.display_set_status = DeviceStatus.from_bool(toggle)
        self.state.connection_status = ConnectionStatus.ONLINE
        return True

    async def set_humidity(self, humidity: int) -> bool:
        """Set target humidity level to stop dehumidifying at."""
        if not Validators.validate_range(humidity, *self.target_minmax):
            logger.warning(
                'Humidity value must be set between %s and %s',
                self.target_minmax[0],
                self.target_minmax[1],
            )
            return False

        payload_data = {'targetHumidity': humidity}
        r_dict = await self.call_bypassv2_api('setTargetHumidity', payload_data)
        r = process_bypassv2_response(self, logger, 'set_humidity', r_dict)
        if r is None:
            return False

        self.state.target_humidity = humidity
        self.state.connection_status = ConnectionStatus.ONLINE
        return True

    async def set_mode(self, mode: str) -> bool:
        if mode not in self.modes:
            logger.warning('Invalid dehumidifier mode used - %s', mode)
            logger.info(
                'Proper modes for this device are - %s',
                orjson.dumps(
                    self.modes, option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS
                ),
            )
            return False

        payload_data = {'workMode': self.modes[mode]}
        r_dict = await self.call_bypassv2_api('setWorkMode', payload_data)

        r = process_bypassv2_response(self, logger, 'set_work_mode', r_dict)
        if r is None:
            return False

        self.state.mode = mode
        self.state.device_status = DeviceStatus.ON
        self.state.connection_status = ConnectionStatus.ONLINE
        return True

    async def set_fan_speed(self, level: int) -> bool:
        """Set the dehumidifier fan speed level."""
        if level not in self.fan_levels:
            logger.warning(
                'Dehumidifier fan speed level must be one of %s', self.fan_levels
            )
            return False

        if self.state.mode != DehumidifierModes.MANUAL:
            logger.warning(
                'Dehumidifier fan speed can only be changed while in manual mode.'
            )
            return False

        payload_data = {'manualSpeedLevel': level}
        r_dict = await self.call_bypassv2_api('setLevel', payload_data)
        r = process_bypassv2_response(self, logger, 'set_fan_speed', r_dict)
        if r is None:
            return False

        self.state.mode = DehumidifierModes.MANUAL
        self.state.fan_speed = level
        self.state.manual_fan_speed = level
        self.state.fan_virtual_speed = level
        self.state.connection_status = ConnectionStatus.ONLINE
        return True

    async def set_mist_level(self, level: int) -> bool:
        """Set the dehumidifier fan speed level.

        Alias for `set_fan_speed` to match the humidifier device contract.
        """
        return await self.set_fan_speed(level)

    async def toggle_child_lock(self, toggle: bool | None = None) -> bool:
        if not self.supports_child_lock:
            logger.warning(
                '%s is a %s does not have a child lock or it is not supported.',
                self.device_name,
                self.device_type,
            )
            return False

        if toggle is None:
            toggle = self.state.child_lock is not True

        payload_data = {'childLockSwitch': int(toggle)}
        r_dict = await self.call_bypassv2_api('setChildLock', payload_data)
        r = process_bypassv2_response(self, logger, 'toggle_child_lock', r_dict)
        if r is None:
            return False

        self.state.child_lock = toggle
        self.state.connection_status = ConnectionStatus.ONLINE
        return True

    async def toggle_mute(self, toggle: bool | None = None) -> bool:
        """Toggle mute on/off."""
        if not self.supports_mute:
            logger.warning(
                '%s is a %s does not have mute or it is not supported.',
                self.device_name,
                self.device_type,
            )
            return False
        if toggle is None:
            toggle = self.state.mute_status != DeviceStatus.ON
        payload_data = {'muteSwitch': int(toggle)}
        r_dict = await self.call_bypassv2_api('setMuteSwitch', payload_data)
        r = process_bypassv2_response(self, logger, 'toggle_mute', r_dict)
        if r is None:
            return False
        self.state.mute_status = DeviceStatus.from_bool(toggle)
        self.state.connection_status = ConnectionStatus.ONLINE
        return True

    async def toggle_power_saving(self, toggle: bool | None = None) -> bool:
        """Toggle power-saving on/off."""
        if not self.supports_power_saving:
            logger.warning(
                '%s is a %s does not have power-saving or it is not supported.',
                self.device_name,
                self.device_type,
            )
            return False
        if toggle is None:
            toggle = self.state.power_saving_status != DeviceStatus.ON
        payload_data = {'powerSavingSwitch': int(toggle)}
        r_dict = await self.call_bypassv2_api('setPowerSavingSwitch', payload_data)
        r = process_bypassv2_response(self, logger, 'toggle_power_saving', r_dict)
        if r is None:
            return False
        self.state.power_saving_status = DeviceStatus.from_bool(toggle)
        self.state.connection_status = ConnectionStatus.ONLINE
        return True

    async def toggle_auto_start(self, toggle: bool | None = None) -> bool:
        """Toggle auto-start on/off."""
        if not self.supports_auto_start:
            logger.warning(
                '%s is a %s does not have auto-start or it is not supported.',
                self.device_name,
                self.device_type,
            )
            return False
        if toggle is None:
            toggle = self.state.auto_start is not True
        payload_data = {'autoStartSwitch': int(toggle)}
        r_dict = await self.call_bypassv2_api('setAutoStart', payload_data)
        r = process_bypassv2_response(self, logger, 'toggle_auto_start', r_dict)
        if r is None:
            return False
        self.state.auto_start = toggle
        self.state.connection_status = ConnectionStatus.ONLINE
        return True

    async def toggle_pump(self, toggle: bool | None = None) -> bool:
        """Toggle pump on/off."""
        if not self.supports_pump:
            logger.warning(
                '%s is a %s does not have pump control or it is not supported.',
                self.device_name,
                self.device_type,
            )
            return False
        if toggle is None:
            toggle = self.state.pump_enabled is not True
        payload_data = {'pumpEnable': int(toggle)}
        r_dict = await self.call_bypassv2_api('setPumpSwitch', payload_data)
        r = process_bypassv2_response(self, logger, 'toggle_pump', r_dict)
        if r is None:
            return False
        self.state.pump_enabled = toggle
        self.state.connection_status = ConnectionStatus.ONLINE
        return True

    async def set_drainage(self, mode: str) -> bool:
        """Set drainage mode."""
        if not self.supports_drainage:
            logger.warning(
                '%s is a %s does not have drainage control or it is not supported.',
                self.device_name,
                self.device_type,
            )
            return False
        payload_data = {'drainageTypeConfig': mode}
        r_dict = await self.call_bypassv2_api('setDrainage', payload_data)
        r = process_bypassv2_response(self, logger, 'set_drainage', r_dict)
        if r is None:
            return False
        self.state.drainage_mode = mode
        self.state.connection_status = ConnectionStatus.ONLINE
        return True

    async def get_timer(self) -> Timer | None:
        """Get the timer state reported by the dehumidifier status payload."""
        await self.get_details()
        return self.state.timer
