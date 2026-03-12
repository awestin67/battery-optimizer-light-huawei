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

"""Sensor for Battery Optimizer Light Huawei."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, CONF_WORKING_MODE_ENTITY, CONF_DEVICE_STATUS_ENTITY

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the status sensor."""
    entities = []

    target_entity = entry.data.get(CONF_WORKING_MODE_ENTITY)
    if target_entity:
        entities.append(HuaweiWorkingModeSensor(hass, target_entity, entry.entry_id))

    device_status_entity = entry.data.get(CONF_DEVICE_STATUS_ENTITY)
    if device_status_entity:
        entities.append(HuaweiDeviceStatusSensor(hass, device_status_entity, entry.entry_id))

    async_add_entities(entities)

class HuaweiWorkingModeSensor(SensorEntity):
    """Representation of the Huawei System Status (Working Mode)."""

    _attr_has_entity_name = True
    _attr_name = "Huawei Working Mode"
    _attr_icon = "mdi:solar-power"

    def __init__(self, hass, target_entity, entry_id):
        """Initialize the sensor."""
        self._target_entity = target_entity
        self._attr_unique_id = f"{entry_id}_system_status"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Battery Optimizer Light Huawei",
            "manufacturer": "Community",
        }

    async def async_added_to_hass(self) -> None:
        """Subscribe to updates."""
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._target_entity], self._update_state
            )
        )
        self._update_state()

    @callback
    def _update_state(self, event=None):
        """Update the state based on the target entity."""
        state = self.hass.states.get(self._target_entity)
        if state and state.state not in ("unavailable", "unknown"):
            self._attr_native_value = state.state
        else:
            self._attr_native_value = "Unknown"

        self.async_write_ha_state()

class HuaweiDeviceStatusSensor(SensorEntity):
    """Representation of the Huawei Device Status (e.g. On-grid)."""

    _attr_has_entity_name = True
    _attr_name = "Huawei Device Status"
    _attr_icon = "mdi:information-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hass, target_entity, entry_id):
        """Initialize the sensor."""
        self._target_entity = target_entity
        self._attr_unique_id = f"{entry_id}_device_status"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Battery Optimizer Light Huawei",
            "manufacturer": "Community",
        }

    async def async_added_to_hass(self) -> None:
        """Subscribe to updates."""
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._target_entity], self._update_state
            )
        )
        self._update_state()

    @callback
    def _update_state(self, event=None):
        """Update the state based on the target entity."""
        state = self.hass.states.get(self._target_entity)
        if state and state.state not in ("unavailable", "unknown"):
            self._attr_native_value = state.state
        else:
            self._attr_native_value = "Unknown"

        self.async_write_ha_state()
