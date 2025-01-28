"""Support for Micronova Agua IOT heating devices."""

from datetime import timedelta
import logging

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_UUID, DOMAIN, PLATFORMS, UPDATE_INTERVAL
from .totalcontrol import TotalControlConnectError, totalcontrol, totalcontrolError

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the totalcontrol integration."""
    if DOMAIN in config:
        for entry_config in config[DOMAIN]:
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN, context={"source": SOURCE_IMPORT}, data=entry_config
                )
            )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up totalcontrol entry."""
    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]
    gen_uuid = entry.data[CONF_UUID]

    agua = totalcontrol(
        email=email,
        password=password,
        unique_id=gen_uuid,
    )

    try:
        await agua.connect()
    except TotalControlConnectError as e:
        _LOGGER.error("Connection error to Agua IOT: %s", e)
        return False
    except totalcontrolError as e:
        _LOGGER.error("Unknown Agua IOT error: %s", e)
        return False

    async def async_update_data():
        """Get the latest data."""
        try:
            await agua.update()
        except TotalControlConnectError as e:
            _LOGGER.error("Connection error to Agua IOT: %s", e)
            return False
        except totalcontrolError as e:
            _LOGGER.error("Unknown Agua IOT error: %s", e)
            return False

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="totalcontrol",
        update_method=async_update_data,
        update_interval=timedelta(seconds=UPDATE_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "agua": agua,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Services
    async def async_close_connection(event: Event) -> None:
        """Close totalcontrol connection on HA Stop."""
        # await agua.close()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, async_close_connection)
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
