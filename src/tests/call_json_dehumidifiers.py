"""
Dehumidifier Device API Responses

DEHUMIDIFIERS variable is a list of setup_entry's from the device_map

DETAILS_RESPONSES variable is a dictionary of responses from the API
for get_details() methods.  The keys are the device types and the
values are the responses.  The responses are tuples of (response, status)

METHOD_RESPONSES variable is a Default Dictionary of responses from the API. This is
the FunctionResponse variable from the utils module in the tests dir.
The default response is a tuple with the value ({"code": 0, "msg": "success"}, 200).

The values of METHOD_RESPONSES can be a function that takes a single argument or
a static value. The value is checked if callable at runtime and if so, it is called
with the provided argument. If not callable, the value is returned as is.
"""
from copy import deepcopy

from pyvesync.device_map import dehumidifier_modules
from pyvesync.const import DehumidifierModes, DeviceStatus, ConnectionStatus
from defaults import build_bypass_v2_response, FunctionResponsesV2

DEHUMIDIFIERS = [m.setup_entry for m in dehumidifier_modules]
DEHUMIDIFIERS_NUM = len(DEHUMIDIFIERS)


class DehumidifierDefaults:
    device_status = DeviceStatus.ON
    connection_status = ConnectionStatus.ONLINE
    mode = DehumidifierModes.MANUAL
    child_lock_switch = DeviceStatus.OFF
    temperature = 70 * 10
    humidity = 50
    target_humidity = 60
    fan_speed = 2
    virtual_fan_speed = 2
    water_tank_full = False
    auto_stop = False
    auto_stop_reached = False
    display_config = DeviceStatus.ON
    display = DeviceStatus.ON


DEHUMIDIFIER_DETAILS = {
    "LV-HD350": {  # Dehumidifier 30 Pint
        "powerSwitch": int(DehumidifierDefaults.device_status),
        "humidity": DehumidifierDefaults.humidity,
        "targetHumidity": DehumidifierDefaults.target_humidity,
        "virtualLevel": DehumidifierDefaults.virtual_fan_speed,
        "mistLevel": DehumidifierDefaults.fan_speed,
        "workMode": DehumidifierDefaults.mode.value,
        "waterTankFull": int(DehumidifierDefaults.water_tank_full),
        "autoStopSwitch": int(DehumidifierDefaults.auto_stop),
        "autoStopState": int(DehumidifierDefaults.auto_stop_reached),
        "screenSwitch": int(DehumidifierDefaults.display_config),
        "screenState": int(DehumidifierDefaults.display),
        "childLockSwitch": int(DehumidifierDefaults.child_lock_switch),
        "timerRemain": 0,
        "errorCode": 0,
        "temperature": DehumidifierDefaults.temperature,
    },
}
"""This dictionary contains the details response for each dehumidifier.

It stores the innermost result that is passed to the DETAILS_RESPONSE variable where
the full API response is built."""


DETAILS_RESPONSES = {
    "LV-HD350": build_bypass_v2_response(inner_result=DEHUMIDIFIER_DETAILS["LV-HD350"]),
}


METHOD_RESPONSES = {
    "LV-HD350": deepcopy(FunctionResponsesV2),
}
