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

import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval

from .const import DOMAIN, CONF_BATTERY_DEVICE_ID, CONF_WORKING_MODE_ENTITY, CONF_AUTO_CONTROL

_LOGGER = logging.getLogger(__name__)

# Ladda sensor-plattformarna för att skapa status-entiteter.
PLATFORMS = ["binary_sensor", "sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Huawei Optimizer from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "auto_control_listener": None,  # Placeholder for the listener
    }

    # This will call async_setup_auto_control when options change
    entry.add_update_listener(async_update_options)

    # Initial setup of auto control
    await async_setup_auto_control(hass, entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # --- Registrera tjänster ---
    SERVICE_SCHEMA = vol.Schema({vol.Required("power"): vol.All(vol.Coerce(int), vol.Range(min=0))})

    async def handle_force_charge(call):
        """Handle the force_charge service call."""
        device_id = entry.data.get(CONF_BATTERY_DEVICE_ID)
        power = call.data.get("power", 0)
        await hass.services.async_call(
            "huawei_solar", "forcible_charge",
            {"device_id": device_id, "power": power, "duration": 60}
        )

    async def handle_force_discharge(call):
        """Handle the force_discharge service call."""
        device_id = entry.data.get(CONF_BATTERY_DEVICE_ID)
        power = call.data.get("power", 0)
        await hass.services.async_call(
            "huawei_solar", "forcible_discharge",
            {"device_id": device_id, "power": power, "duration": 60}
        )

    async def handle_hold(call):
        """Handle the hold service call (Manual mode, 0W)."""
        device_id = entry.data.get(CONF_BATTERY_DEVICE_ID)
        working_mode = entry.data.get(CONF_WORKING_MODE_ENTITY)
        await hass.services.async_call(
            "huawei_solar", "stop_forcible_charge", {"device_id": device_id}
        )
        await hass.services.async_call(
            "select", "select_option", {"entity_id": working_mode, "option": "fixed_charge_discharge"}
        )

    async def handle_auto(call):
        """Handle the auto service call (Self-consumption)."""
        device_id = entry.data.get(CONF_BATTERY_DEVICE_ID)
        working_mode = entry.data.get(CONF_WORKING_MODE_ENTITY)
        await hass.services.async_call(
            "huawei_solar", "stop_forcible_charge", {"device_id": device_id}
        )
        await hass.services.async_call(
            "select", "select_option", {"entity_id": working_mode, "option": "maximise_self_consumption"}
        )

    hass.services.async_register(DOMAIN, "force_charge", handle_force_charge, schema=SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, "force_discharge", handle_force_discharge, schema=SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, "hold", handle_hold)
    hass.services.async_register(DOMAIN, "auto", handle_auto)

    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await async_setup_auto_control(hass, entry)

async def async_setup_auto_control(hass: HomeAssistant, entry: ConfigEntry):
    """Set up or tear down the automatic control listener."""
    domain_data = hass.data[DOMAIN][entry.entry_id]

    device_id = entry.data.get(CONF_BATTERY_DEVICE_ID)
    working_mode_entity = entry.data.get(CONF_WORKING_MODE_ENTITY)

    # Cancel any existing listeners
    if domain_data.get("auto_control_listener"):
        _LOGGER.debug("Cancelling existing auto control listener.")
        domain_data["auto_control_listener"]()
        domain_data["auto_control_listener"] = None

    # If auto control is enabled, set up a new listener
    if entry.options.get(CONF_AUTO_CONTROL, True):
        _LOGGER.info("Automatic control enabled (Event & Time interval).")

        async def update_battery_control(event=None):
            """Evaluate logic and control battery based on current sensor state."""
            # Hämta aktuell status (oavsett om vi triggades av event eller tid)
            action_state = hass.states.get("sensor.optimizer_light_action")
            if not action_state or action_state.state in ("unknown", "unavailable"):
                return
            current_action = action_state.state
            _LOGGER.debug(f"Optimizer action changed to: {current_action}")

            # Hämta nuvarande driftläge för att undvika onödiga anrop (Filter)
            current_mode_state = hass.states.get(working_mode_entity)
            current_mode = current_mode_state.state if current_mode_state else None

            # Hämta effektvärde om det behövs (för Charge/Discharge)
            target_power = 0
            if current_action in ["CHARGE", "DISCHARGE"]:
                power_state = hass.states.get("sensor.optimizer_light_power")
                if power_state:
                    try:
                        # Konvertera kW till W och säkerställ int
                        target_power = int(float(power_state.state) * 1000)
                    except (ValueError, TypeError):
                        _LOGGER.warning(f"Invalid power value: {power_state.state}")
                        return

            if current_action == "CHARGE":
                await hass.services.async_call(
                    "huawei_solar",
                    "forcible_charge",
                    {
                        "device_id": device_id,
                        "power": target_power,
                        "duration": 60 # Enligt automationen
                    }
                )

            elif current_action == "DISCHARGE":
                await hass.services.async_call(
                    "huawei_solar",
                    "forcible_discharge",
                    {
                        "device_id": device_id,
                        "power": target_power,
                        "duration": 60
                    }
                )

            elif current_action == "HOLD":
                # Filter: Om vi redan är i fixed_charge_discharge (Hold), gör inget.
                if current_mode == "fixed_charge_discharge":
                    _LOGGER.debug("Battery already in fixed_charge_discharge (HOLD). Skipping.")
                    return

                # Stoppa ev. pågående tvingad laddning/urladdning
                await hass.services.async_call(
                    "huawei_solar", "stop_forcible_charge", {"device_id": device_id}
                )
                # Sätt läge till fixed_charge_discharge (Stoppar batteriet från att agera på huslast)
                await hass.services.async_call(
                    "select", "select_option",
                    {"entity_id": working_mode_entity, "option": "fixed_charge_discharge"}
                )

            elif current_action == "IDLE":
                # Filter: Om vi redan är i adaptive (Auto), gör inget.
                if current_mode == "maximise_self_consumption":
                    _LOGGER.debug("Battery already in maximise_self_consumption mode (IDLE). Skipping.")
                    return

                # IDLE = Auto/Self Consumption
                await hass.services.async_call(
                    "huawei_solar", "stop_forcible_charge", {"device_id": device_id}
                )
                # Byt tillbaka till adaptive (Maximise Self Consumption)
                await hass.services.async_call(
                    "select", "select_option",
                    {"entity_id": working_mode_entity, "option": "maximise_self_consumption"}
                )
            else:
                # Default action (från automationens 'default' block)
                # Körs om action är något annat än ovanstående (men inte unknown/unavailable)
                await hass.services.async_call(
                    "huawei_solar",
                    "forcible_charge",
                    {
                        "device_id": device_id,
                        "power": 10,
                        "duration": 60
                    }
                )

        # Lyssnare 1: Vid statusförändring
        unsub_state = async_track_state_change_event(
            hass, ["sensor.optimizer_light_action"], update_battery_control
        )
        # Lyssnare 2: Var 5:e minut (Time Pattern)
        unsub_time = async_track_time_interval(
            hass, update_battery_control, timedelta(minutes=5)
        )

        # Spara en funktion som avregistrerar båda
        domain_data["auto_control_listener"] = lambda: (unsub_state(), unsub_time())


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    domain_data = hass.data[DOMAIN].get(entry.entry_id)
    if domain_data and domain_data.get("auto_control_listener"):
        domain_data["auto_control_listener"]()

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
