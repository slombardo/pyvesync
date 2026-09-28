"""
This tests requests for Dehumidifiers.

All tests inherit from the TestBase class which contains the fixtures
and methods needed to run the tests.

The tests are automatically parametrized by `pytest_generate_tests` in
conftest.py. The two methods that are parametrized are `test_details`
and `test_methods`. The class variables are used to build the list of
devices, test methods and arguments.

The `helpers.call_api` method is patched to return a mock response.
The method, endpoint, headers and json arguments are recorded
in YAML files in the api directory, categorized in folders by
module and files by the class name.

The default is to record requests that do not exist and compare requests
that already exist. If the API changes, set the overwrite argument to True
in order to overwrite the existing YAML file with the new request.

See Also
--------
`utils.TestBase` - Base class for all tests, containing mock objects
`confest.pytest_generate_tests` - Parametrizes tests based on
    method names & class attributes
`call_json_dehumidifiers` - Contains API responses
"""

import logging
import call_json_dehumidifiers
import pyvesync.const as const
from base_test_cases import TestBase
from pyvesync.base_devices.dehumidifier_base import VeSyncDehumidifierBase
from utils import assert_test, parse_args


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TestDehumidifiers(TestBase):
    """Dehumidifier testing class.

    This class tests Dehumidifier product details and methods. The methods are
    parametrized from the class variables using `pytest_generate_tests`.
    The call_json_dehumidifiers module contains the responses for the API
    requests. The device is instantiated from the details provided by
    `call_json.DeviceList.device_list_item()`. Inherits from `utils.TestBase`.

    Instance Attributes
    -------------------
    self.manager : VeSync
        Instantiated VeSync object
    self.mock_api : Mock
        Mock with patched `helpers.call_api` method
    self.caplog : LogCaptureFixture
        Pytest fixture for capturing logs

    Class Variables
    ---------------
    device : str
        Name of product class - dehumidifiers
    dehumidifiers : list
        List of setup_entry's for dehumidifiers, this variable is named
        after the device variable value
    base_methods : List[List[str, Dict[str, Any]]]
        List of common methods for all devices
    device_methods : Dict[List[List[str, Dict[str, Any]]]]
        Dictionary of methods specific to device types

    Methods
    --------
    test_details()
        Test the device details API request and response
    test_methods()
        Test device methods API request and response
    """

    device = "dehumidifiers"
    dehumidifiers = call_json_dehumidifiers.DEHUMIDIFIERS
    base_methods = [
        ["turn_on"],
        ["turn_off"],
        ["turn_on_display"],
        ["turn_off_display"],
        ["set_humidity", {"humidity": 50}],
        ["set_auto_mode"],
        ["set_quiet_mode"],
        ["set_manual_mode"],
        ["set_turbo_mode"],
        ["set_fan_speed", {"level": 2}],
        ["turn_on_child_lock"],
        ["turn_off_child_lock"],
        ["turn_on_mute"],
        ["turn_off_mute"],
        ["turn_on_power_saving"],
        ["turn_off_power_saving"],
        ["turn_on_auto_start"],
        ["turn_off_auto_start"],
        ["turn_on_pump"],
        ["turn_off_pump"],
        ["set_drainage", {"mode": "pump"}],
        ["get_timer"],
    ]
    device_methods: dict = {}

    def test_details(self, setup_entry, method):
        """Test the device details API request and response.

        This method is automatically parametrized by `pytest_generate_tests`
        based on class variables `device` (name of product class -
        dehumidifiers), device name (dehumidifiers) list of setup_entry's.

        See Also
        --------
        `utils.TestBase` class docstring
        `call_json_dehumidifiers` module docstring

        Notes
        ------
        The device is instantiated using the `call_json.DeviceList.device_list_item()`
        method. The device details contain the default values set in
        `call_json_dehumidifiers.DehumidifierDefaults`
        """
        return_dict = call_json_dehumidifiers.DETAILS_RESPONSES[setup_entry]
        return_val = (return_dict, 200)
        self.mock_api.return_value = return_val

        dehumid_obj = self.get_device("dehumidifiers", setup_entry)
        assert isinstance(dehumid_obj, VeSyncDehumidifierBase)

        method_call = getattr(dehumid_obj, method)
        self.run_in_loop(method_call)

        assert dehumid_obj.state.device_status == const.DeviceStatus.ON
        assert dehumid_obj.state.connection_status == const.ConnectionStatus.ONLINE
        assert dehumid_obj.state.mode == call_json_dehumidifiers.DehumidifierDefaults.mode
        assert dehumid_obj.state.humidity == call_json_dehumidifiers.DehumidifierDefaults.humidity
        assert (
            dehumid_obj.state.target_humidity
            == call_json_dehumidifiers.DehumidifierDefaults.target_humidity
        )
        assert dehumid_obj.state.fan_speed == call_json_dehumidifiers.DehumidifierDefaults.fan_speed
        assert (
            dehumid_obj.state.manual_fan_speed
            == call_json_dehumidifiers.DehumidifierDefaults.manual_fan_speed
        )
        assert dehumid_obj.state.display_status == call_json_dehumidifiers.DehumidifierDefaults.display
        assert dehumid_obj.state.child_lock == bool(
            call_json_dehumidifiers.DehumidifierDefaults.child_lock_switch
        )
        assert dehumid_obj.state.work_state == call_json_dehumidifiers.DehumidifierDefaults.work_state
        assert dehumid_obj.state.error_codes == call_json_dehumidifiers.DehumidifierDefaults.error_codes
        assert dehumid_obj.state.drainage_mode == call_json_dehumidifiers.DehumidifierDefaults.drainage_type
        assert dehumid_obj.state.pump_enabled == call_json_dehumidifiers.DehumidifierDefaults.pump_enable
        assert dehumid_obj.state.temperature == call_json_dehumidifiers.DehumidifierDefaults.temperature
        assert dehumid_obj.state.timer is not None
        assert (
            dehumid_obj.state.timer.time_remaining
            <= call_json_dehumidifiers.DehumidifierDefaults.timer_remain
        )

        # Parse mock_api args tuple from arg, kwargs to kwargs
        all_kwargs = parse_args(self.mock_api)

        # Assert request matches recorded request or write new records
        assert assert_test(
            method_call, all_kwargs, setup_entry, self.write_api, self.overwrite
        )

    def test_methods(self, setup_entry, method):
        """Test device methods API request and response.

        This method is automatically parametrized by `pytest_generate_tests`
        based on class variables `device` (name of product class -
        dehumidifiers), device name (dehumidifiers) list of setup_entry's,
        `base_methods` - list of methods for all devices, and
        `device_methods` - list of methods for each device type.

        See Also
        --------
        `TestBase` class method
        `call_json_dehumidifiers` module
        """
        method_name = method[0]
        if len(method) == 2 and isinstance(method[1], dict):
            method_kwargs = method[1]
        else:
            method_kwargs = {}

        method_response = call_json_dehumidifiers.METHOD_RESPONSES[setup_entry][method_name]

        dehumid_obj = self.get_device("dehumidifiers", setup_entry)
        assert isinstance(dehumid_obj, VeSyncDehumidifierBase)

        if callable(method_response):
            if method_kwargs:
                self.mock_api.return_value = method_response(method_kwargs), 200
            else:
                self.mock_api.return_value = method_response(), 200
        else:
            self.mock_api.return_value = method_response, 200

        method_call = getattr(dehumid_obj, method[0])

        # Ensure method runs based on device configuration
        if method[0] == "turn_on":
            dehumid_obj.state.device_status = const.DeviceStatus.OFF
        elif method[0] == "turn_off":
            dehumid_obj.state.device_status = const.DeviceStatus.ON
        elif method[0] == "set_auto_mode":
            dehumid_obj.state.mode = const.DehumidifierModes.MANUAL
        elif method[0] == "set_quiet_mode":
            dehumid_obj.state.mode = const.DehumidifierModes.AUTO
        elif method[0] == "set_manual_mode":
            dehumid_obj.state.mode = const.DehumidifierModes.AUTO
        elif method[0] == "set_turbo_mode":
            dehumid_obj.state.mode = const.DehumidifierModes.AUTO
        elif method[0] == "set_fan_speed":
            dehumid_obj.state.mode = const.DehumidifierModes.MANUAL
        elif method[0] == "turn_on_mute":
            dehumid_obj.state.mute_status = const.DeviceStatus.OFF
        elif method[0] == "turn_off_mute":
            dehumid_obj.state.mute_status = const.DeviceStatus.ON
        elif method[0] == "turn_on_power_saving":
            dehumid_obj.state.power_saving_status = const.DeviceStatus.OFF
        elif method[0] == "turn_off_power_saving":
            dehumid_obj.state.power_saving_status = const.DeviceStatus.ON
        elif method[0] == "turn_on_auto_start":
            dehumid_obj.state.auto_start = False
        elif method[0] == "turn_off_auto_start":
            dehumid_obj.state.auto_start = True
        elif method[0] == "turn_on_pump":
            dehumid_obj.state.pump_enabled = False
        elif method[0] == "turn_off_pump":
            dehumid_obj.state.pump_enabled = True

        if method_kwargs:
            self.run_in_loop(method_call, **method_kwargs)
        else:
            self.run_in_loop(method_call)

        if method[0] == "set_auto_mode":
            assert dehumid_obj.state.mode == const.DehumidifierModes.AUTO
        elif method[0] == "set_quiet_mode":
            assert dehumid_obj.state.mode == const.DehumidifierModes.QUIET
        elif method[0] == "set_manual_mode":
            assert dehumid_obj.state.mode == const.DehumidifierModes.MANUAL
        elif method[0] == "set_turbo_mode":
            assert dehumid_obj.state.mode == const.DehumidifierModes.TURBO
        elif method[0] == "set_humidity":
            assert dehumid_obj.state.target_humidity == method_kwargs["humidity"]
        elif method[0] == "set_fan_speed":
            assert dehumid_obj.state.fan_speed == method_kwargs["level"]
        elif method[0] == "turn_on_child_lock":
            assert dehumid_obj.state.child_lock is True
        elif method[0] == "turn_off_child_lock":
            assert dehumid_obj.state.child_lock is False
        elif method[0] == "turn_on_mute":
            assert dehumid_obj.state.mute_status == const.DeviceStatus.ON
        elif method[0] == "turn_off_mute":
            assert dehumid_obj.state.mute_status == const.DeviceStatus.OFF
        elif method[0] == "turn_on_power_saving":
            assert dehumid_obj.state.power_saving_status == const.DeviceStatus.ON
        elif method[0] == "turn_off_power_saving":
            assert dehumid_obj.state.power_saving_status == const.DeviceStatus.OFF
        elif method[0] == "turn_on_auto_start":
            assert dehumid_obj.state.auto_start is True
        elif method[0] == "turn_off_auto_start":
            assert dehumid_obj.state.auto_start is False
        elif method[0] == "turn_on_pump":
            assert dehumid_obj.state.pump_enabled is True
        elif method[0] == "turn_off_pump":
            assert dehumid_obj.state.pump_enabled is False
        elif method[0] == "set_drainage":
            assert dehumid_obj.state.drainage_mode == method_kwargs["mode"]
        elif method[0] == "get_timer":
            assert dehumid_obj.state.timer is not None
            assert (
                dehumid_obj.state.timer.time_remaining
                <= call_json_dehumidifiers.DehumidifierDefaults.timer_remain
            )

        all_kwargs = parse_args(self.mock_api)

        assert assert_test(
            method_call, all_kwargs, setup_entry, self.write_api, self.overwrite
        )

    def test_invalid_target_humidity_response(self):
        """Test nested validation failures are surfaced as request failures."""
        self.mock_api.return_value = (
            call_json_dehumidifiers.build_invalid_target_humidity_response(),
            200,
        )
        dehumid_obj = self.get_device("dehumidifiers", "LDH-H251S")
        assert isinstance(dehumid_obj, VeSyncDehumidifierBase)

        result = self.run_in_loop(dehumid_obj.set_humidity, humidity=50)

        assert result is False
        assert dehumid_obj.last_response.code == 11003000

    def test_device_timeout_mode_response(self):
        """Test outer device-timeout responses are surfaced cleanly."""
        self.mock_api.return_value = (
            call_json_dehumidifiers.build_device_timeout_response(),
            200,
        )
        dehumid_obj = self.get_device("dehumidifiers", "LDH-H251S")
        assert isinstance(dehumid_obj, VeSyncDehumidifierBase)

        result = self.run_in_loop(
            dehumid_obj.set_mode, mode=const.DehumidifierModes.TURBO
        )

        assert result is False
        assert dehumid_obj.last_response.code == -11302030

    def test_humidity_range_validation(self):
        """Test target humidity is constrained to the verified 35-70% range."""
        dehumid_obj = self.get_device("dehumidifiers", "LDH-H251S")
        assert isinstance(dehumid_obj, VeSyncDehumidifierBase)

        assert self.run_in_loop(dehumid_obj.set_humidity, humidity=34) is False
        assert self.run_in_loop(dehumid_obj.set_humidity, humidity=71) is False
        self.mock_api.assert_not_called()

    def test_fan_speed_requires_manual_mode(self):
        """Test manual fan speed changes are rejected outside manual mode."""
        dehumid_obj = self.get_device("dehumidifiers", "LDH-H251S")
        assert isinstance(dehumid_obj, VeSyncDehumidifierBase)
        dehumid_obj.state.mode = const.DehumidifierModes.TURBO

        result = self.run_in_loop(dehumid_obj.set_fan_speed, level=2)

        assert result is False
        self.mock_api.assert_not_called()

    def test_timer_set_not_supported(self):
        """Test dehumidifier timer creation is not advertised without verified API."""
        dehumid_obj = self.get_device("dehumidifiers", "LDH-H251S")
        assert isinstance(dehumid_obj, VeSyncDehumidifierBase)

        result = self.run_in_loop(dehumid_obj.set_timer, duration=300)

        assert result is False
        self.mock_api.assert_not_called()

    def test_timer_clear_not_supported(self):
        """Test dehumidifier timer clearing is not advertised without verified API."""
        dehumid_obj = self.get_device("dehumidifiers", "LDH-H251S")
        assert isinstance(dehumid_obj, VeSyncDehumidifierBase)

        result = self.run_in_loop(dehumid_obj.clear_timer)

        assert result is False
        self.mock_api.assert_not_called()
