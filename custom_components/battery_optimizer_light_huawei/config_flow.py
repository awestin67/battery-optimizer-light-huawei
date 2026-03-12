# Battery Optimizer Light
# Copyright (C) 2026 @awestin67
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Config flow för Sonnen Batteri."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_BATTERY_DEVICE_ID, CONF_WORKING_MODE_ENTITY, CONF_AUTO_CONTROL

_LOGGER = logging.getLogger(__name__)

class HuaweiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Huawei Battery Optimizer."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return HuaweiOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step where user selects devices."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="Battery Optimizer Light Huawei",
                data=user_input
            )

        data_schema = vol.Schema({
            vol.Required(CONF_BATTERY_DEVICE_ID): selector.DeviceSelector(
                selector.DeviceSelectorConfig(integration="huawei_solar")
            ),
            vol.Required(CONF_WORKING_MODE_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="select")
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "api_token_url": "https://community.home-assistant.io/t/sonnen-battery-and-home-assistant/16124/165"
            },
        )

class HuaweiOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Huawei."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options (Auto Control)."""
        if user_input is not None:

            self.hass.config_entries.async_update_entry(
                self._config_entry,
                options=user_input, # Options are stored in entry.options
            )

            return self.async_create_entry(title="", data=user_input)

        # Hämta nuvarande värden (data + options)
        current_options = self._config_entry.options

        schema = vol.Schema({
            vol.Optional(CONF_AUTO_CONTROL): bool,
        })

        # Fyll i värden med suggested_values (Modern metod som fungerar bättre)
        suggested_values = {
            CONF_AUTO_CONTROL: current_options.get(CONF_AUTO_CONTROL, True),
        }
        schema = self.add_suggested_values_to_schema(schema, suggested_values)
