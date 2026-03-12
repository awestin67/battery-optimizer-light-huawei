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

"""Diagnostics support for Battery Optimizer Light Huawei."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import CONF_BATTERY_DEVICE_ID, CONF_WORKING_MODE_ENTITY, CONF_DEVICE_STATUS_ENTITY

TO_REDACT = {CONF_BATTERY_DEVICE_ID}

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    diag_data = {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "entities": {},
        "device_info": {},
    }

    # 1. Kontrollera konfigurerade Huawei-entiteter (Working Mode)
    # Detta avslöjar om Huawei-integrationen är 'unavailable'
    working_mode_entity = entry.data.get(CONF_WORKING_MODE_ENTITY)
    if working_mode_entity:
        state = hass.states.get(working_mode_entity)
        diag_data["entities"][working_mode_entity] = {
            "state": state.state if state else None,
            "attributes": state.attributes if state else None,
        }

    # 2. Kontrollera Device Status-entitet
    device_status_entity = entry.data.get(CONF_DEVICE_STATUS_ENTITY)
    if device_status_entity:
        state = hass.states.get(device_status_entity)
        diag_data["entities"][device_status_entity] = {
            "state": state.state if state else None,
            "attributes": state.attributes if state else None,
        }

    # 3. Kontrollera Optimizer Light-sensorer
    # Detta visar vad optimeraren försöker göra just nu
    for entity_id in ["sensor.optimizer_light_action", "sensor.optimizer_light_power"]:
        state = hass.states.get(entity_id)
        diag_data["entities"][entity_id] = {
            "state": state.state if state else None,
            "attributes": state.attributes if state else None,
        }

    # 4. Kontrollera Huawei-enheten i registret
    # Hämtar info om växelriktare/batteri för att se FW-version och modell
    device_id = entry.data.get(CONF_BATTERY_DEVICE_ID)
    if device_id:
        device_registry = dr.async_get(hass)
        device = device_registry.async_get(device_id)
        if device:
            diag_data["device_info"] = {
                "name": device.name,
                "model": device.model,
                "manufacturer": device.manufacturer,
                "sw_version": device.sw_version,
                "disabled": device.disabled_by,
                "identifiers": list(device.identifiers),
            }

    return diag_data
