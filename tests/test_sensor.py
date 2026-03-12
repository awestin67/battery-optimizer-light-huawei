# Battery Optimizer Light
# Copyright (C) 2026 @awestin67

"""Test the Huawei Battery Optimizer sensors."""
from unittest.mock import MagicMock
import pytest
from homeassistant.core import HomeAssistant

from custom_components.battery_optimizer_light_huawei.const import (
    CONF_BATTERY_DEVICE_ID,
    CONF_WORKING_MODE_ENTITY,
    CONF_DEVICE_STATUS_ENTITY
)
from custom_components.battery_optimizer_light_huawei.sensor import async_setup_entry

@pytest.mark.asyncio
async def test_sensors_setup_and_update(hass: HomeAssistant) -> None:
    """Test that sensors are created and update correctly."""

    # 1. Mock Config Entry
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_BATTERY_DEVICE_ID: "device_123",
        CONF_WORKING_MODE_ENTITY: "select.huawei_mode",
        CONF_DEVICE_STATUS_ENTITY: "sensor.huawei_status",
    }

    # Mocka async_add_entities callback
    async_add_entities = MagicMock()

    # 2. Setup sensors
    await async_setup_entry(hass, entry, async_add_entities)

    # Verifiera att två sensorer lades till
    assert async_add_entities.called
    sensors = async_add_entities.call_args[0][0]
    assert len(sensors) == 2

    working_mode_sensor = sensors[0]
    device_status_sensor = sensors[1]

    # Sätt hass på sensorerna (sker normalt av HA)
    working_mode_sensor.hass = hass
    device_status_sensor.hass = hass

    # --- Test: Working Mode Sensor ---
    assert working_mode_sensor.name == "Huawei Working Mode"

    # Simulera att sensorerna läggs till i HA (aktiverar lyssnare)
    await working_mode_sensor.async_added_to_hass()
    await device_status_sensor.async_added_to_hass()

    # Verifiera att mock_track_state_change_event anropades
    # Vi måste fiska upp callback-funktionen som registrerades
    # working_mode_sensor lyssnar på select.huawei_mode

    # Simulera state update: "adaptive"
    mock_state = MagicMock()
    mock_state.state = "adaptive"
    hass.states.get.return_value = mock_state

    # Trigga uppdatering manuellt (privat metod, men nödvändigt för enhetstest)
    working_mode_sensor._update_state()
    assert working_mode_sensor.native_value == "adaptive"

    # Simulera "unavailable"
    mock_state.state = "unavailable"
    hass.states.get.return_value = mock_state
    working_mode_sensor._update_state()
    assert working_mode_sensor.native_value == "Unknown"

    # --- Test: Device Status Sensor ---
    assert device_status_sensor.name == "Huawei Device Status"

    # Simulera state update: "On-grid"
    mock_state.state = "On-grid"
    hass.states.get.return_value = mock_state

    device_status_sensor._update_state()
    assert device_status_sensor.native_value == "On-grid"

    # Simulera "unknown"
    mock_state.state = "unknown"
    hass.states.get.return_value = mock_state
    device_status_sensor._update_state()
    assert device_status_sensor.native_value == "Unknown"
