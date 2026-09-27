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

from defaults import build_base_response, build_bypass_v2_response, FunctionResponsesV2
from pyvesync.const import ConnectionStatus, DehumidifierModes, DeviceStatus
from pyvesync.device_map import dehumidifier_modules

DEHUMIDIFIERS = [m.setup_entry for m in dehumidifier_modules]
DEHUMIDIFIERS_NUM = len(DEHUMIDIFIERS)


def build_setter_success_without_result(_payload: dict | None = None) -> dict:
    """Build a successful Bypass V2 setter response without result payload."""
    response = build_base_response(code=0, msg="request success")
    response["result"] = {
        "traceId": response["traceId"],
        "code": 0,
    }
    return response


def build_invalid_target_humidity_response() -> dict:
    """Build a nested validation-error response for target humidity."""
    return build_bypass_v2_response(code=0, msg="request success", inner_code=11003000)


def build_device_timeout_response() -> dict:
    """Build a device-timeout response with null result."""
    return build_base_response(
        code=-11302030,
        msg="device timeout",
        merge_dict={"result": None},
    )


class DehumidifierDefaults:
    device_status = DeviceStatus.ON
    connection_status = ConnectionStatus.ONLINE
    mode = DehumidifierModes.TURBO
    work_state = "dehumidification"
    child_lock_switch = DeviceStatus.OFF
    temperature = 18
    humidity = 79
    target_humidity = 50
    fan_speed = 3
    manual_fan_speed = 1
    tank_level = 1
    tank_in_place = True
    display_config = DeviceStatus.ON
    display = DeviceStatus.ON
    auto_start = True
    error_codes: list[int] = []
    filter_life_percent = 95
    filter_remaining_days = 44
    reset_filter_date = 0
    mute_status = DeviceStatus.OFF
    power_saving = DeviceStatus.OFF
    power_saving_state = False
    power_saving_time_sec = 0
    pump_in_place = True
    pump_enable = True
    pump_working = False
    water_sensor_in_place = False
    water_sensor_detects_water = False
    mold_removal_remind = False
    reach_target = False
    drainage_type = "innerTank"
    compressor_state = DeviceStatus.ON
    coil_temp = 5
    exhaust_pipe_temp = 55
    actual_run_level = 3


DEHUMIDIFIER_DETAILS = {
    "LDH-H251S": {
        "powerSwitch": int(DehumidifierDefaults.device_status),
        "humidity": DehumidifierDefaults.humidity,
        "tempInF": DehumidifierDefaults.temperature,
        "targetHumidity": DehumidifierDefaults.target_humidity,
        "workState": DehumidifierDefaults.work_state,
        "workMode": DehumidifierDefaults.mode.value,
        "fanSpeedLevel": DehumidifierDefaults.fan_speed,
        "manualSpeedLevel": DehumidifierDefaults.manual_fan_speed,
        "tankLevel": DehumidifierDefaults.tank_level,
        "tankInPlace": int(DehumidifierDefaults.tank_in_place),
        "screenSwitch": int(DehumidifierDefaults.display_config),
        "screenState": int(DehumidifierDefaults.display),
        "scheduleCount": 0,
        "timerRemain": 0,
        "autoStartSwitch": int(DehumidifierDefaults.auto_start),
        "errorCodes": DehumidifierDefaults.error_codes,
        "filterLifePercent": DehumidifierDefaults.filter_life_percent,
        "filterRemainingDays": DehumidifierDefaults.filter_remaining_days,
        "resetFilterDate": DehumidifierDefaults.reset_filter_date,
        "childLockSwitch": int(DehumidifierDefaults.child_lock_switch),
        "muteSwitch": int(DehumidifierDefaults.mute_status),
        "powerSavingSwitch": int(DehumidifierDefaults.power_saving),
        "powerSavingState": int(DehumidifierDefaults.power_saving_state),
        "powerSavingTimeSec": DehumidifierDefaults.power_saving_time_sec,
        "pumpInPlace": int(DehumidifierDefaults.pump_in_place),
        "pumpEnable": int(DehumidifierDefaults.pump_enable),
        "pumpWorking": int(DehumidifierDefaults.pump_working),
        "waterSensorInPlace": int(DehumidifierDefaults.water_sensor_in_place),
        "waterSensorDetectsWater": int(
            DehumidifierDefaults.water_sensor_detects_water
        ),
        "moldRemovalRemind": int(DehumidifierDefaults.mold_removal_remind),
        "reachTargetState": int(DehumidifierDefaults.reach_target),
        "drainageTypeConfig": DehumidifierDefaults.drainage_type,
        "compressorState": int(DehumidifierDefaults.compressor_state),
        "coilTemp": DehumidifierDefaults.coil_temp,
        "exhaustPipeTemp": DehumidifierDefaults.exhaust_pipe_temp,
        "actualRunLevel": DehumidifierDefaults.actual_run_level,
    },
}
"""This dictionary contains the details response for each dehumidifier.

It stores the innermost result that is passed to the DETAILS_RESPONSE variable where
the full API response is built."""


DETAILS_RESPONSES = {
    "LDH-H251S": build_bypass_v2_response(
        code=0,
        msg="request success",
        inner_result=DEHUMIDIFIER_DETAILS["LDH-H251S"],
    ),
}


METHOD_RESPONSES = {
    "LDH-H251S": deepcopy(FunctionResponsesV2),
}

for key in METHOD_RESPONSES:
    METHOD_RESPONSES[key]["turn_on_mute"] = build_setter_success_without_result
    METHOD_RESPONSES[key]["turn_off_mute"] = build_setter_success_without_result
    METHOD_RESPONSES[key]["turn_on_power_saving"] = build_setter_success_without_result
    METHOD_RESPONSES[key]["turn_off_power_saving"] = build_setter_success_without_result
    METHOD_RESPONSES[key]["turn_on_auto_start"] = build_setter_success_without_result
    METHOD_RESPONSES[key]["turn_off_auto_start"] = build_setter_success_without_result
    METHOD_RESPONSES[key]["turn_on_pump"] = build_setter_success_without_result
    METHOD_RESPONSES[key]["turn_off_pump"] = build_setter_success_without_result
    METHOD_RESPONSES[key]["set_drainage"] = build_setter_success_without_result
    METHOD_RESPONSES[key]["get_timer"] = build_bypass_v2_response(
        code=0,
        msg="request success",
        inner_result={
            "timers": [{"id": 1, "remain": 120, "action": "off", "total": 300}]
        },
    )
    METHOD_RESPONSES[key]["set_timer"] = build_bypass_v2_response(
        code=0,
        msg="request success",
        inner_result={"id": 1},
    )
