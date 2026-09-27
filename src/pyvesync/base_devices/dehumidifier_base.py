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
        auto_stop_target_reached (bool): Automatic stop target reached.
        automatic_stop_config (bool): Automatic stop configuration.
        child_lock (bool): Child lock status.
        display_set_status (str): Display set status.
        display_status (str): Display status.
        fan_speed (int): Fan speed level.
        fan_virtual_speed (int): Fan virtual speed level.
        humidity (int): Current humidity level.
        mode (str): Current mode.
        target_humidity (int): Target humidity level.
        temperature (float): Current temperature.
        water_tank_full (bool): Water tank full status.
    """

    __slots__ = (
        'auto_stop_target_reached',
        'automatic_stop_config',
        'child_lock',
        'display_set_status',
        'display_status',
        'fan_speed',
        'fan_virtual_speed',
        'humidity',
        'mode',
        'target_humidity',
        'temperature',
        'water_tank_full',
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
        self.auto_stop_target_reached: bool = False
        self.automatic_stop_config: bool = False
        self.child_lock: bool | None = None
        self.display_set_status: str = DeviceStatus.UNKNOWN
        self.display_status: str = DeviceStatus.UNKNOWN
        self.fan_speed: int | None = None
        self.fan_virtual_speed: int | None = None
        self.humidity: int | None = None
        self.mode: str | None = None
        self.target_humidity: int | None = None
        self.temperature: float | None = None  # Fahrenheit
        self.water_tank_full: bool = False

    @property
    def automatic_stop(self) -> bool:
        """Return the automatic stop status.

        Returns:
            bool: True if automatic stop is enabled, False otherwise.
        """
        return self.automatic_stop_config


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
    def supports_automatic_stop(self) -> bool:
        """Return True if the device supports automatic stop."""
        return DehumidifierFeatures.AUTO_STOP in self.features

    @property
    def supports_display(self) -> bool:
        """Return True if the device supports the display toggle."""
        return DehumidifierFeatures.DISPLAY in self.features

    @property
    def supports_child_lock(self) -> bool:
        """Return True if the device supports the child lock toggle."""
        return DehumidifierFeatures.CHILD_LOCK in self.features

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
    async def toggle_automatic_stop(self, toggle: bool | None = None) -> bool:
        """Toggle automatic stop when the water tank is full.

        Args:
            toggle (bool | None): True to enable automatic stop, False to disable.

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

    async def turn_on_automatic_stop(self) -> bool:
        """Turn on automatic stop.

        Returns:
            bool: Success of request.
        """
        return await self.toggle_automatic_stop(True)

    async def turn_off_automatic_stop(self) -> bool:
        """Turn off automatic stop.

        Returns:
            bool: Success of request.
        """
        return await self.toggle_automatic_stop(False)

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
