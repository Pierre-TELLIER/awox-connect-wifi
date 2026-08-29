import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_PASSWORD, CONF_USERNAME, DOMAIN


class AwoxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an AwoX config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_USERNAME],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )
