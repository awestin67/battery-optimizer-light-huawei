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

"""Binary Sensor for Battery Optimizer Light Huawei."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, CONF_WORKING_MODE_ENTITY, CONF_BATTERY_DEVICE_ID

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor."""
    target_entity = entry.data.get(CONF_WORKING_MODE_ENTITY)
    device_id = entry.data.get(CONF_BATTERY_DEVICE_ID)

    async_add_entities([HuaweiConnectivitySensor(hass, target_entity, device_id, entry.entry_id)])

class HuaweiConnectivitySensor(BinarySensorEntity):
    """Representation of the connection status to Huawei Solar."""

    _attr_has_entity_name = True
    _attr_name = "Huawei Solar Connection"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hass, target_entity, device_id, entry_id):
        """Initialize the binary sensor."""
        self._target_entity = target_entity
        self._attr_unique_id = f"{entry_id}_connectivity"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Battery Optimizer Light Huawei",
            "manufacturer": "Community",
        }
        # Om vi har ett device_id från Huawei, länka till den enheten istället
        # men för tydlighetens skull skapar vi oftast en egen tjänste-enhet.
        # Här behåller vi den under integrationens egna enhet.

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
        # Connected if state exists and is not unavailable/unknown
        self._attr_is_on = state is not None and state.state not in ("unavailable", "unknown")
        self.async_write_ha_state()
