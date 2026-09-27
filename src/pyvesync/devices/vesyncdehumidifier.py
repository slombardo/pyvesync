"""VeSync Dehumidifier Devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import orjson

from pyvesync.base_devices.dehumidifier_base import VeSyncDehumidifierBase
from pyvesync.const import ConnectionStatus, DeviceStatus
from pyvesync.models import dehumidifier_models as models
from pyvesync.models.bypass_models import ResultV2GetTimer, ResultV2SetTimer
from pyvesync.utils.device_mixins import BypassV2Mixin, process_bypassv2_result
from pyvesync.utils.helpers import Helpers, Timer, Validators

if TYPE_CHECKING:
    from pyvesync import VeSync
    from pyvesync.device_map import DehumidifierMap
    from pyvesync.models.vesync_models import ResponseDeviceDetailsModel


logger = logging.getLogger(__name__)


class VeSyncDehumidifier(BypassV2Mixin, VeSyncDehumidifierBase):
    """VeSync Dehumidifier Class.

    Uses the Bypass V2 command family to read and write humidity, fan speed,
    mode, power, display, child lock, automatic stop and water tank status.

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
        self.state.fan_speed = resp_model.mistLevel
        self.state.fan_virtual_speed = resp_model.virtualLevel
        self.state.water_tank_full = bool(resp_model.waterTankFull)
        self.state.automatic_stop_config = bool(resp_model.autoStopSwitch)
        self.state.auto_stop_target_reached = bool(resp_model.autoStopState)
        self.state.display_set_status = DeviceStatus.from_int(resp_model.screenSwitch)
        self.state.display_status = DeviceStatus.from_int(resp_model.screenState)
        self.state.child_lock = bool(resp_model.childLockSwitch)
        self.state.temperature = (
            resp_model.temperature / 10
        )  # Fahrenheit but without decimals
        if resp_model.timerRemain > 0:
            self.state.timer = Timer(
                resp_model.timerRemain,
                DeviceStatus.from_bool(self.state.device_status != DeviceStatus.ON),
            )

    async def get_details(self) -> None:
        r_dict = await self.call_bypassv2_api('getHumidifierStatus')
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
        r = Helpers.process_dev_response(logger, 'toggle_switch', self, r_dict)
        if r is None:
            return False

        self.state.device_status = DeviceStatus.from_bool(toggle)
        self.state.connection_status = ConnectionStatus.ONLINE
        return True

    async def toggle_automatic_stop(self, toggle: bool | None = None) -> bool:
        """Toggle automatic stop when the water tank is full."""
        if not self.supports_automatic_stop:
            logger.warning(
                '%s is a %s does not have automatic stop or it is not supported.',
                self.device_name,
                self.device_type,
            )
            return False

        if toggle is None:
            toggle = self.state.automatic_stop_config is not True

        payload_data = {'autoStopSwitch': int(toggle)}
        r_dict = await self.call_bypassv2_api('setAutoStopSwitch', payload_data)
        r = Helpers.process_dev_response(logger, 'toggle_automatic_stop', self, r_dict)
        if r is None:
            return False

        self.state.automatic_stop_config = toggle
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
        r = Helpers.process_dev_response(logger, 'set_display', self, r_dict)
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
        r = Helpers.process_dev_response(logger, 'set_humidity', self, r_dict)
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
        r_dict = await self.call_bypassv2_api('setHumidityMode', payload_data)

        r = Helpers.process_dev_response(logger, 'set_humidity_mode', self, r_dict)
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

        payload_data = {'levelIdx': 0, 'virtualLevel': level, 'levelType': 'mist'}
        r_dict = await self.call_bypassv2_api('setVirtualLevel', payload_data)
        r = Helpers.process_dev_response(logger, 'set_fan_speed', self, r_dict)
        if r is None:
            return False

        self.state.fan_speed = level
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
        r = Helpers.process_dev_response(logger, 'toggle_child_lock', self, r_dict)
        if r is None:
            return False

        self.state.child_lock = toggle
        self.state.connection_status = ConnectionStatus.ONLINE
        return True

    async def get_timer(self) -> Timer | None:
        """Get active dehumidifier timer, if any."""
        r_dict = await self.call_bypassv2_api('getTimer')
        result_model = process_bypassv2_result(
            self, logger, 'get_timer', r_dict, ResultV2GetTimer
        )
        if result_model is None:
            return None
        if not result_model.timers:
            logger.debug('No timers found')
            return None
        timer = result_model.timers[0]
        self.state.timer = Timer(
            timer_duration=timer.total,
            action=timer.action,
            id=timer.id,
        )
        return self.state.timer

    async def clear_timer(self) -> bool:
        """Clear the active dehumidifier timer."""
        if self.state.timer is None:
            logger.debug('No timer to clear, run get_timer() first.')
            return False
        payload = {
            'id': self.state.timer.id,
        }
        r_dict = await self.call_bypassv2_api('delTimer', payload)
        r = Helpers.process_dev_response(logger, 'clear_timer', self, r_dict)
        if r is None:
            return False
        self.state.timer = None
        return True

    async def set_timer(self, duration: int, action: str | None = None) -> bool:
        """Set a dehumidifier timer for the given duration in seconds."""
        if action is None:
            action = (
                DeviceStatus.OFF
                if self.state.device_status == DeviceStatus.ON
                else DeviceStatus.ON
            )
        payload_data = {
            'action': str(action),
            'total': duration,
        }
        r_dict = await self.call_bypassv2_api('addTimer', payload_data)
        r = process_bypassv2_result(self, logger, 'set_timer', r_dict, ResultV2SetTimer)
        if r is None:
            return False

        self.state.timer = Timer(
            timer_duration=duration, action=action, id=r.id, remaining=0
        )
        return True
