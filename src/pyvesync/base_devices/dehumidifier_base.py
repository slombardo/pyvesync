"""Base Device and State Class for VeSync Dehumidifiers."""

from __future__ import annotations

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from pyvesync.base_devices.vesyncbasedevice import DeviceState, VeSyncBaseToggleDevice
from pyvesync.const import DehumidifierFeatures, DehumidifierModes, DeviceStatus

if TYPE_CHECKING:
    from pyvesync import VeSync
    from pyvesync.device_map import DehumidifierMap
    from pyvesync.models.vesync_models import ResponseDeviceDetailsModel


logger = logging.getLogger(__name__)


class DehumidifierState(DeviceState):
    """State Class for VeSync Dehumidifiers.

    Attributes:
        actual_run_level (int): Actual run level.
        auto_start (bool): Auto-start status.
        child_lock (bool): Child lock status.
        compressor_state (str): Compressor state.
        coil_temperature (int): Coil temperature.
        drainage_mode (str): Drainage mode.
        display_set_status (str): Display set status.
        display_status (str): Display status.
        error_codes (list[int]): Active device error codes.
        exhaust_pipe_temperature (int): Exhaust-pipe temperature.
        fan_speed (int): Fan speed level.
        fan_virtual_speed (int): Fan virtual speed level.
        filter_life_percent (int): Remaining filter life percentage.
        filter_remaining_days (int): Remaining filter life days.
        humidity (int): Current humidity level.
        manual_fan_speed (int): Manual fan speed setting.
        mold_removal_reminder (bool): Mold-removal reminder state.
        mute_status (str): Mute status.
        mode (str): Current mode.
        power_saving_active (bool): Power-saving active state.
        power_saving_status (str): Power-saving configured status.
        power_saving_time_sec (int): Power-saving timer value.
        pump_enabled (bool): Pump enabled state.
        pump_installed (bool): Pump installed state.
        pump_working (bool): Pump running state.
        reach_target (bool): Reach-target state.
        reset_filter_date (int): Filter reset timestamp/value.
        schedule_count (int): Schedule count.
        tank_in_place (bool): Tank-installed state.
        tank_level (int): Tank level/status indicator.
        target_humidity (int): Target humidity level.
        temperature (float): Current temperature.
        water_tank_full (bool): Water tank full status.
        water_sensor_detects_water (bool): Water-sensor detected-water state.
        water_sensor_in_place (bool): Water-sensor installed state.
        work_state (str): Current work state.
    """

    __slots__ = (
        'actual_run_level',
        'auto_start',
        'child_lock',
        'coil_temperature',
        'compressor_state',
        'display_set_status',
        'display_status',
        'drainage_mode',
        'error_codes',
        'exhaust_pipe_temperature',
        'fan_speed',
        'fan_virtual_speed',
        'filter_life_percent',
        'filter_remaining_days',
        'humidity',
        'manual_fan_speed',
        'mode',
        'mold_removal_reminder',
        'mute_status',
        'power_saving_active',
        'power_saving_status',
        'power_saving_time_sec',
        'pump_enabled',
        'pump_installed',
        'pump_working',
        'reach_target',
        'reset_filter_date',
        'schedule_count',
        'tank_in_place',
        'tank_level',
        'target_humidity',
        'temperature',
        'water_sensor_detects_water',
        'water_sensor_in_place',
        'water_tank_full',
        'work_state',
    )

    def __init__(
        self,
        device: VeSyncDehumidifierBase,
        details: ResponseDeviceDetailsModel,
        feature_map: DehumidifierMap,
    ) -> None:
        """Initialize VeSync Dehumidifier State.

        Args:
            device (VeSyncDehumidifierBase): The device object.
            details (ResponseDeviceDetailsModel): The device details.
            feature_map (DehumidifierMap): The feature map for the device.
        """
        super().__init__(device, details, feature_map)
        self.actual_run_level: int | None = None
        self.auto_start: bool | None = None
        self.child_lock: bool | None = None
        self.compressor_state: str = DeviceStatus.UNKNOWN
        self.coil_temperature: int | None = None
        self.drainage_mode: str | None = None
        self.display_set_status: str = DeviceStatus.UNKNOWN
        self.display_status: str = DeviceStatus.UNKNOWN
        self.error_codes: list[int] = []
        self.exhaust_pipe_temperature: int | None = None
        self.fan_speed: int | None = None
        self.fan_virtual_speed: int | None = None
        self.filter_life_percent: int | None = None
        self.filter_remaining_days: int | None = None
        self.humidity: int | None = None
        self.manual_fan_speed: int | None = None
        self.mold_removal_reminder: bool | None = None
        self.mute_status: str = DeviceStatus.UNKNOWN
        self.mode: str | None = None
        self.power_saving_active: bool | None = None
        self.power_saving_status: str = DeviceStatus.UNKNOWN
        self.power_saving_time_sec: int | None = None
        self.pump_enabled: bool | None = None
        self.pump_installed: bool | None = None
        self.pump_working: bool | None = None
        self.reach_target: bool | None = None
        self.reset_filter_date: int | None = None
        self.schedule_count: int | None = None
        self.tank_in_place: bool | None = None
        self.tank_level: int | None = None
        self.target_humidity: int | None = None
        self.temperature: float | int | None = None
        self.water_tank_full: bool = False
        self.water_sensor_detects_water: bool | None = None
        self.water_sensor_in_place: bool | None = None
        self.work_state: str | None = None

class VeSyncDehumidifierBase(VeSyncBaseToggleDevice):
    """Base Class for VeSync Dehumidifiers.

    Args:
        details (ResponseDeviceDetailsModel): The device details.
        manager (VeSync): The VeSync manager.
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

    __slots__ = ('_reverse_modes', 'fan_levels', 'modes', 'target_minmax')

    def __init__(
        self,
        details: ResponseDeviceDetailsModel,
        manager: VeSync,
        feature_map: DehumidifierMap,
    ) -> None:
        """Initialize VeSync Dehumidifier Base Class."""
        super().__init__(details, manager, feature_map)
        self.state: DehumidifierState = DehumidifierState(self, details, feature_map)
        self.modes: dict[str, str] = feature_map.modes
        self._reverse_modes: dict[str, str] = {v: k for k, v in self.modes.items()}
        self.fan_levels: list[int] = feature_map.fan_levels
        self.target_minmax: tuple[int, int] = feature_map.target_minmax

    @property
    def supports_water_tank_full(self) -> bool:
        """Return True if the device reports a water tank full status."""
        return DehumidifierFeatures.WATER_TANK_FULL in self.features

    @property
    def supports_display(self) -> bool:
        """Return True if the device supports the display toggle."""
        return DehumidifierFeatures.DISPLAY in self.features

    @property
    def supports_child_lock(self) -> bool:
        """Return True if the device supports the child lock toggle."""
        return DehumidifierFeatures.CHILD_LOCK in self.features

    @property
    def supports_mute(self) -> bool:
        """Return True if the device supports mute."""
        return DehumidifierFeatures.MUTE in self.features

    @property
    def supports_power_saving(self) -> bool:
        """Return True if the device supports power-saving."""
        return DehumidifierFeatures.POWER_SAVING in self.features

    @property
    def supports_auto_start(self) -> bool:
        """Return True if the device supports auto-start."""
        return DehumidifierFeatures.AUTO_START in self.features

    @property
    def supports_pump(self) -> bool:
        """Return True if the device supports pump controls."""
        return DehumidifierFeatures.PUMP in self.features

    @property
    def supports_drainage(self) -> bool:
        """Return True if the device supports drainage controls."""
        return DehumidifierFeatures.DRAINAGE in self.features

    @abstractmethod
    async def set_mode(self, mode: str) -> bool:
        """Set Dehumidifier Mode.

        Args:
            mode (str): Dehumidifier mode.

        Returns:
            bool: Success of request.

        Note:
            Modes for device are defined in `self.modes`.
        """

    @abstractmethod
    async def set_fan_speed(self, level: int) -> bool:
        """Set Fan Speed for Dehumidifier.

        Args:
            level (int): Fan speed level.

        Returns:
            bool: Success of request.

        Note:
            Fan speed levels are defined in `self.fan_levels`.
        """

    @abstractmethod
    async def set_humidity(self, humidity: int) -> bool:
        """Set Dehumidifier Target Humidity.

        Args:
            humidity (int): Target humidity level.

        Returns:
            bool: Success of request.
        """

    @abstractmethod
    async def toggle_display(self, toggle: bool | None = None) -> bool:
        """Toggle the display on/off.

        Args:
            toggle (bool | None): True to turn on the display, False to turn off.

        Returns:
            bool: Success of request.
        """

    @abstractmethod
    async def toggle_child_lock(self, toggle: bool | None = None) -> bool:
        """Toggle the child lock on/off.

        Args:
            toggle (bool | None): True to enable child lock, False to disable.

        Returns:
            bool: Success of request.
        """

    @abstractmethod
    async def toggle_mute(self, toggle: bool | None = None) -> bool:
        """Toggle mute on/off."""

    @abstractmethod
    async def toggle_power_saving(self, toggle: bool | None = None) -> bool:
        """Toggle power-saving on/off."""

    @abstractmethod
    async def toggle_auto_start(self, toggle: bool | None = None) -> bool:
        """Toggle auto-start on/off."""

    @abstractmethod
    async def toggle_pump(self, toggle: bool | None = None) -> bool:
        """Toggle pump on/off."""

    @abstractmethod
    async def set_drainage(self, mode: str) -> bool:
        """Set drainage mode."""

    async def turn_on_display(self) -> bool:
        """Turn on the display.

        Returns:
            bool: Success of request.
        """
        return await self.toggle_display(True)

    async def turn_off_display(self) -> bool:
        """Turn off the display.

        Returns:
            bool: Success of request.
        """
        return await self.toggle_display(False)

    async def turn_on_child_lock(self) -> bool:
        """Turn on the child lock.

        Returns:
            bool: Success of request.
        """
        return await self.toggle_child_lock(True)

    async def turn_off_child_lock(self) -> bool:
        """Turn off the child lock.

        Returns:
            bool: Success of request.
        """
        return await self.toggle_child_lock(False)

    async def turn_on_mute(self) -> bool:
        """Turn mute on."""
        return await self.toggle_mute(True)

    async def turn_off_mute(self) -> bool:
        """Turn mute off."""
        return await self.toggle_mute(False)

    async def turn_on_power_saving(self) -> bool:
        """Turn power-saving on."""
        return await self.toggle_power_saving(True)

    async def turn_off_power_saving(self) -> bool:
        """Turn power-saving off."""
        return await self.toggle_power_saving(False)

    async def turn_on_auto_start(self) -> bool:
        """Turn auto-start on."""
        return await self.toggle_auto_start(True)

    async def turn_off_auto_start(self) -> bool:
        """Turn auto-start off."""
        return await self.toggle_auto_start(False)

    async def turn_on_pump(self) -> bool:
        """Turn pump on."""
        return await self.toggle_pump(True)

    async def turn_off_pump(self) -> bool:
        """Turn pump off."""
        return await self.toggle_pump(False)

    async def set_auto_mode(self) -> bool:
        """Set Dehumidifier to Auto Mode.

        Returns:
            bool: Success of request.
        """
        if 'auto' in self.modes:
            return await self.set_mode(DehumidifierModes.AUTO)
        logger.error('Auto mode not supported for this device.')
        return False

    async def set_manual_mode(self) -> bool:
        """Set Dehumidifier to Manual Mode.

        Returns:
            bool: Success of request.
        """
        if 'manual' in self.modes:
            return await self.set_mode(DehumidifierModes.MANUAL)
        logger.error('Manual mode not supported for this device.')
        return False

    async def set_turbo_mode(self) -> bool:
        """Set Dehumidifier to Turbo Mode."""
        if 'turbo' in self.modes:
            return await self.set_mode(DehumidifierModes.TURBO)
        logger.error('Turbo mode not supported for this device.')
        return False

    async def set_quiet_mode(self) -> bool:
        """Set Dehumidifier to Quiet Mode."""
        if 'quiet' in self.modes:
            return await self.set_mode(DehumidifierModes.QUIET)
        logger.error('Quiet mode not supported for this device.')
        return False
