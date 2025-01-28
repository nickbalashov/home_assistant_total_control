"""Support for Extraflame heating devices."""

import logging

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_HALVES, UnitOfTemperature
from homeassistant.helpers.entity import DeviceInfo, HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, JsonDataField
from .totalcontrol import totalcontrolError

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Representation of setup entry."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    agua = hass.data[DOMAIN][entry.entry_id]["agua"]
    entities = [totalcontrolWaterDevice(coordinator, device) for device in agua.devices]
    async_add_entities(entities, True)


class totalcontrolWaterDevice(CoordinatorEntity, ClimateEntity):
    """Representation of an Extraflame heating device."""

    def __init__(self, coordinator, device) -> None:
        """Initialize the thermostat."""
        CoordinatorEntity.__init__(self, coordinator)
        self._enable_turn_on_off_backwards_compatibility = False
        self._device = device

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
    def temperature_unit(self):
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_HALVES

    @property
    def unique_id(self):
        """Return the unique ID of the climate."""
        return self._device.id

    @property
    def name(self):
        """Return the name of the climate."""
        return self._device.name

    @property
    def icon(self):
        """Return the icon of the climate."""
        return "mdi:water"

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return (
            ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TARGET_TEMPERATURE
        )

    @property
    def hvac_action(self):
        """Return HVAC action."""
        return self._device.get_register_value_description(JsonDataField.MACHINE_STATE)

    @property
    def hvac_modes(self):
        """Return HVAC modes."""
        return [HVACMode.HEAT, HVACMode.OFF]

    @property
    def hvac_mode(self):
        """Return HVAC mode."""
        if self._device.get_register_value(JsonDataField.MACHINE_STATE) == 0:
            return HVACMode.OFF

        return HVACMode.HEAT

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
        elif hvac_mode == HVACMode.HEAT:
            await self.async_turn_on()

    async def async_turn_off(self):
        """Turn device off."""
        try:
            await self._device.set_register_value(JsonDataField.MACHINE_STATE, 0)
            await self.coordinator.async_request_refresh()
        except (ValueError, totalcontrolError) as err:
            _LOGGER.error("Failed to stop, error: %s", err)

    async def async_turn_on(self):
        """Turn device on."""
        try:
            await self._device.set_register_value(JsonDataField.MACHINE_STATE, 1)
            await self.coordinator.async_request_refresh()
        except (ValueError, totalcontrolError) as err:
            _LOGGER.error("Failed to start, error: %s", err)

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._device.get_register_value(JsonDataField.ROOM_TEMPERATURE)

    @property
    def min_temp(self):
        """Return the minimum temperature to set."""
        return self._device.get_register_value_min(
            JsonDataField.TARGET_WATER_TEMPERATURE
        )

    @property
    def max_temp(self):
        """Return the maximum temperature to set."""
        return self._device.get_register_value_max(
            JsonDataField.TARGET_WATER_TEMPERATURE
        )

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._device.get_register_value(JsonDataField.TARGET_WATER_TEMPERATURE)

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        try:
            await self._device.set_register_value(
                JsonDataField.TARGET_WATER_TEMPERATURE, temperature
            )
            await self.coordinator.async_request_refresh()
        except (ValueError, totalcontrolError) as err:
            _LOGGER.error("Failed to set temperature, error: %s", err)

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return self._device.get_register(JsonDataField.TARGET_WATER_TEMPERATURE).get(
            "step", 1
        )
