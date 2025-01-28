"""Support for total control sensor entity."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, SENSORS


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> None:
    """Representation of setup entry."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    agua = hass.data[DOMAIN][entry.entry_id]["agua"]

    sensors = [
        totalcontrolHeatingSensor(coordinator, device, sensor)
        for device in agua.devices
        for sensor in SENSORS
    ]

    async_add_entities(sensors, True)


class totalcontrolHeatingSensor(CoordinatorEntity, SensorEntity):
    """Representation of an total control sensor entity."""

    def __init__(self, coordinator, device, description) -> None:
        """Initialize the thermostat."""
        CoordinatorEntity.__init__(self, coordinator)
        self._device = device
        self.entity_description = description

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._device.id}_{self.entity_description.key}"

    @property
    def name(self):
        """Return the name of the device, if any."""
        return f"{self._device.name} {self.entity_description.name}"

    @property
    def device_info(self):
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device.id)},
            name=self._device.name,
            manufacturer=self._device.manufacturer,
            model=self._device.codArt,
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.entity_description.raw_value:
            return self._device.get_register_value(self.entity_description.key)

        return self._device.get_register_value_description(self.entity_description.key)
