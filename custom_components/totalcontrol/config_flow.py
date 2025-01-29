"""Config flow for Agua IOT."""

import logging
import uuid

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from .const import CONF_UUID, DOMAIN
from .totalcontrol import totalcontrol, totalcontrolError

_LOGGER = logging.getLogger(__name__)


def conf_entries(hass: HomeAssistant):
    """Return the email tuples for the domain."""
    return {
        (entry.data[CONF_EMAIL]) for entry in hass.config_entries.async_entries(DOMAIN)
    }


class totalcontrolConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Agua IOT Config Flow handler."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def _entry_in_configuration_exists(self, user_input) -> bool:
        """Return True if config already exists in configuration."""
        email = user_input[CONF_EMAIL]
        if (email) in conf_entries(self.hass):
            return True
        return False

    async def async_step_user(self, user_input=None):
        """User initiated integration."""
        errors = {}
        if user_input is not None:
            # Validate user input
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]

            if self._entry_in_configuration_exists(user_input):
                return self.async_abort(reason="device_already_configured")

            try:
                gen_uuid = str(uuid.uuid1())
                agua = totalcontrol(
                    email=email,
                    password=password,
                    unique_id=gen_uuid,
                )
                await agua.connect()

            except totalcontrolError as e:
                _LOGGER.error("Login error: %s", e)
                errors["base"] = "login_error"

            if "base" not in errors:
                return self.async_create_entry(
                    title="Extraflame",
                    data={
                        CONF_EMAIL: email,
                        CONF_PASSWORD: password,
                        CONF_UUID: gen_uuid,
                    },
                )
        else:
            user_input = {}

        data_schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL, default=user_input.get(CONF_EMAIL)): str,
                vol.Required(CONF_PASSWORD, default=user_input.get(CONF_PASSWORD)): str,
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
