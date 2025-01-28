"""Agua IOT constants."""

from dataclasses import dataclass
from enum import StrEnum

from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import Platform, UnitOfTemperature


@dataclass
class totalcontrolSensorEntityDescription(SensorEntityDescription):
    """Sensor Entity Description."""

    force_enabled: bool = False
    raw_value: bool = False


@dataclass
class totalcontrolNumberEntityDescription(NumberEntityDescription):
    """Number Entity Description."""

    force_enabled: bool = False


DOMAIN = "totalcontrol"
CONF_UUID = "uuid"
MANUFACTURER = "Extraflame"

PLATFORMS = [
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SENSOR,
]


class PayloadField(StrEnum):
    """Available payload datafields."""

    ACTION = "_action"
    EMAIL = "email"
    PASSWORD = "password"
    UNIQUE_ID = "uuid"
    TOKEN = "token"
    MAC = "mac"
    PARAMETER_ID = "parameterId"
    PARAMETER_VALUE = "parameterValue"


class JsonDataField(StrEnum):
    """Available Json datafields."""

    ALARM = "alarmMemoryCode"
    CODE_ART = "codArt"
    CREATION_DATE = "creationDate"
    DATA = "data"
    FRIENDLY_NAME = "friendlyName"
    ID = "id"
    MAC = "mac"
    MACHINE_STATE = "machineState"
    POWER = "power"
    REGISTRATION_CODE = "registrationCode"
    RESULT_CODE = "resultCode"
    ROOM_TEMPERATURE = "roomTemp"
    SERIAL = "serial"
    SMOKE_TEMPERATURE = "smokeTemp"
    STOVE_STATE = "stoveState"
    TARGET_ROOM_TEMPERATURE = "targetRoomTemp"
    TARGET_WATER_TEMPERATURE = "targetWaterTemp"
    TARGET_POWER = "targetPower"
    TOKEN = "token"
    WATER_TEMPERATURE = "waterTemp"


REGISTERS = {
    JsonDataField.ALARM: {
        "enc_val": {
            0: "None",
            1: "Unknown 1",
            2: "Unknown 2",
            3: "Unknown 3",
            4: "Unknown 4",
            5: "Unknown 5",
            6: "Unknown 6",
        }
    },
    JsonDataField.CREATION_DATE: {},
    JsonDataField.MACHINE_STATE: {
        "parameterId": 0,
        "set_min": 0,
        "set_max": 1,
        "enc_val": {
            0: "Off",
            1: "On",
            2: "Ignition",
            3: "Start",
            4: "Working",
            5: "Cleaning",
            6: "Final cleaning",
            7: "Waiting restart",
            8: "Alarm",
            9: "Alarm Memory",
        },
    },
    JsonDataField.POWER: {},
    JsonDataField.ROOM_TEMPERATURE: {},
    JsonDataField.WATER_TEMPERATURE: {},
    JsonDataField.SMOKE_TEMPERATURE: {},
    JsonDataField.TARGET_ROOM_TEMPERATURE: {
        "set_min": 65,
        "set_max": 80,
        "parameterId": 4,
    },
    JsonDataField.TARGET_POWER: {"set_min": 1, "set_max": 5, "parameterId": 5},
    JsonDataField.TARGET_WATER_TEMPERATURE: {
        "set_min": 65,
        "set_max": 80,
        "parameterId": 6,
    },
}

UPDATE_INTERVAL = 60

SENSORS = (
    totalcontrolSensorEntityDescription(
        key=JsonDataField.MACHINE_STATE,
        name="Status",
        icon="mdi:fire",
        native_unit_of_measurement=None,
        state_class=None,
        device_class=SensorDeviceClass.ENUM,
    ),
    totalcontrolSensorEntityDescription(
        key=JsonDataField.ALARM,
        name="Alarm",
        icon="mdi:alert-outline",
        native_unit_of_measurement=None,
        state_class=None,
        device_class=SensorDeviceClass.ENUM,
        force_enabled=True,
    ),
    totalcontrolSensorEntityDescription(
        key=JsonDataField.ROOM_TEMPERATURE,
        name="Room Temperature",
        icon="mdi:gauge",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    totalcontrolSensorEntityDescription(
        key=JsonDataField.SMOKE_TEMPERATURE,
        name="Smoke Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    totalcontrolSensorEntityDescription(
        key=JsonDataField.WATER_TEMPERATURE,
        name="Water Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
)

NUMBERS = (
    totalcontrolNumberEntityDescription(
        key=JsonDataField.TARGET_POWER,
        name="Pellet Power",
        icon="mdi:fire",
        native_step=1,
        force_enabled=True,
    ),
    totalcontrolNumberEntityDescription(
        key=JsonDataField.TARGET_ROOM_TEMPERATURE,
        name="Room temperature",
        icon="mdi:gauge",
        native_step=1,
        force_enabled=True,
    ),
    totalcontrolNumberEntityDescription(
        key=JsonDataField.TARGET_WATER_TEMPERATURE,
        name="Water temperature",
        icon="mdi:gauge",
        native_step=1,
        force_enabled=True,
    ),
)
