# Battery Optimizer Light
# Copyright (C) 2026 @awestin67

"""Test the Huawei Battery Optimizer binary sensor."""
from unittest.mock import MagicMock
import pytest
from homeassistant.core import HomeAssistant

from custom_components.battery_optimizer_light_huawei.const import (
    CONF_BATTERY_DEVICE_ID,
    CONF_WORKING_MODE_ENTITY,
)
from custom_components.battery_optimizer_light_huawei.binary_sensor import async_setup_entry

@pytest.mark.asyncio
async def test_binary_sensor_setup_and_update(hass: HomeAssistant) -> None:
    """Test that the connectivity sensor works."""

    # 1. Mock Config Entry
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_BATTERY_DEVICE_ID: "device_123",
        CONF_WORKING_MODE_ENTITY: "select.huawei_mode",
    }

    # Mocka callback
    async_add_entities = MagicMock()

    # 2. Setup
    await async_setup_entry(hass, entry, async_add_entities)

    assert async_add_entities.called
    sensor = async_add_entities.call_args[0][0][0]
    sensor.hass = hass

    assert sensor.name == "Huawei Solar Connection"

    # Simulera start
    await sensor.async_added_to_hass()

    # --- Test 1: Entity Available (Connected) ---
    mock_state = MagicMock()
    mock_state.state = "adaptive"
    hass.states.get.return_value = mock_state

    sensor._update_state()
    assert sensor.is_on is True

    # --- Test 2: Entity Unavailable (Disconnected) ---
    mock_state.state = "unavailable"
    hass.states.get.return_value = mock_state

    sensor._update_state()
    assert sensor.is_on is False

    # --- Test 3: Entity Missing (Disconnected) ---
    hass.states.get.return_value = None

    sensor._update_state()
    assert sensor.is_on is False
