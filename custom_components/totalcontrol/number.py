"""Support for total control number entity."""

import logging

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, NUMBERS
from .totalcontrol import totalcontrolError

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Representation of setup entry."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    agua = hass.data[DOMAIN][entry.entry_id]["agua"]

    numbers = [
        totalcontrolHeatingNumber(coordinator, device, number)
        for number in NUMBERS
        for device in agua.devices
        if number.key in device.registers and (number.force_enabled)
    ]

    async_add_entities(numbers, True)


class totalcontrolHeatingNumber(CoordinatorEntity, NumberEntity):
    """Representation of an total control number entity."""

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
        return self._device.get_register_value(self.entity_description.key)

    @property
    def native_min_value(self):
        """Return the min value of the sensor."""
        return self._device.get_register_value_min(self.entity_description.key)

    @property
    def native_max_value(self):
        """Return the max value of the sensor."""
        return self._device.get_register_value_max(self.entity_description.key)

    async def async_set_native_value(self, value):
        """Set value of the sensor."""
        try:
            await self._device.set_register_value(self.entity_description.key, value)
            await self.coordinator.async_request_refresh()
        except (ValueError, totalcontrolError) as err:
            _LOGGER.error("Failed to set value, error: %s", err)
