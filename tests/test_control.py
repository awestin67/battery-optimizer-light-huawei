# Battery Optimizer Light
# Copyright (C) 2026 @awestin67

"""Test the Huawei Battery Optimizer control logic."""
from unittest.mock import MagicMock, call
import pytest
from homeassistant.core import Event

# Eftersom conftest.py mockar modulerna, importerar vi från dem för att få mock-objekten
from homeassistant.helpers.event import async_track_state_change_event as mock_track_state_change

from custom_components.battery_optimizer_light_huawei import async_setup_entry
from custom_components.battery_optimizer_light_huawei.const import (
    DOMAIN,
    CONF_BATTERY_DEVICE_ID,
    CONF_WORKING_MODE_ENTITY,
    CONF_AUTO_CONTROL,
)

@pytest.mark.asyncio
async def test_control_services(hass):
    """Test that services are registered and call the correct underlying Huawei services."""

    # 1. Skapa en mockad Config Entry
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_BATTERY_DEVICE_ID: "huawei_device_123",
        CONF_WORKING_MODE_ENTITY: "select.working_mode",
    }
    entry.options = {CONF_AUTO_CONTROL: False} # Stäng av auto för detta test

    # 2. Setup av integrationen
    assert await async_setup_entry(hass, entry)

    # Verifiera att 4 tjänster registrerades
    assert hass.services.async_register.call_count == 4

    # Fånga upp callback-funktionerna för tjänsterna
    services = {}
    for call_args in hass.services.async_register.call_args_list:
        args = call_args.args
        if args[0] == DOMAIN:
            services[args[1]] = args[2] # args[2] är handler-funktionen

    assert "force_charge" in services
    assert "force_discharge" in services
    assert "hold" in services
    assert "auto" in services

    # --- Test: force_charge ---
    service_call = MagicMock()
    service_call.data = {"power": 5000}

    await services["force_charge"](service_call)

    hass.services.async_call.assert_called_with(
        "huawei_solar", "forcible_charge",
        {"device_id": "huawei_device_123", "power": 5000, "duration": 60}
    )
    hass.services.async_call.reset_mock()

    # --- Test: force_discharge ---
    service_call.data = {"power": 3000}
    await services["force_discharge"](service_call)

    hass.services.async_call.assert_called_with(
        "huawei_solar", "forcible_discharge",
        {"device_id": "huawei_device_123", "power": 3000, "duration": 60}
    )
    hass.services.async_call.reset_mock()

    # --- Test: hold ---
    await services["hold"](None)

    # Hold ska stoppa laddning OCH sätta driftläge
    expected_calls = [
        call("huawei_solar", "stop_forcible_charge", {"device_id": "huawei_device_123"}),
        call("select", "select_option", {"entity_id": "select.working_mode", "option": "fixed_charge_discharge"})
    ]
    hass.services.async_call.assert_has_calls(expected_calls)
    hass.services.async_call.reset_mock()

    # --- Test: auto ---
    await services["auto"](None)

    # Auto ska stoppa laddning OCH sätta driftläge till adaptive
    expected_calls = [
        call("huawei_solar", "stop_forcible_charge", {"device_id": "huawei_device_123"}),
        call("select", "select_option", {"entity_id": "select.working_mode", "option": "maximise_self_consumption"})
    ]
    hass.services.async_call.assert_has_calls(expected_calls)


@pytest.mark.asyncio
async def test_auto_control_logic(hass):
    """Test the automatic control logic driven by sensor state changes."""

    # Mock Config Entry med Auto Control PÅSLAGET
    entry = MagicMock()
    entry.entry_id = "test_entry_auto"
    entry.data = {
        CONF_BATTERY_DEVICE_ID: "huawei_device_123",
        CONF_WORKING_MODE_ENTITY: "select.working_mode",
    }
    entry.options = {CONF_AUTO_CONTROL: True}

    # Förbered hass.data
    hass.data = {DOMAIN: {}}

    # Setup
    await async_setup_entry(hass, entry)

    # Hitta lyssnaren som registrerades (via mockad homeassistant.helpers.event)
    assert mock_track_state_change.called
    args = mock_track_state_change.call_args[0]
    assert args[1] == ["sensor.optimizer_light_action"] # Verifiera att vi lyssnar på rätt sensor
    listener_callback = args[2]

    # Hjälpfunktion för att simulera händelser och sensorvärden
    async def simulate_event(new_state_str, power_kw="0", current_mode="maximise_self_consumption"):
        event = MagicMock(spec=Event)
        new_state = MagicMock()
        new_state.state = new_state_str
        event.data = {"new_state": new_state}

        # Mocka hass.states.get för att returnera våra simulerade värden
        def get_state(entity_id):
            m_state = MagicMock()
            if entity_id == "sensor.optimizer_light_action":
                m_state.state = new_state_str
                return m_state
            if entity_id == "sensor.optimizer_light_power":
                m_state.state = power_kw
                return m_state
            if entity_id == "select.working_mode":
                m_state.state = current_mode
                return m_state
            return None

        hass.states.get.side_effect = get_state

        # Kör lyssnaren
        await listener_callback(event)

    # --- Test: CHARGE ---
    # Effekt 2.5 kW -> 2500 W
    await simulate_event("CHARGE", power_kw="2.5")
    hass.services.async_call.assert_called_with(
        "huawei_solar", "forcible_charge",
        {"device_id": "huawei_device_123", "power": 2500, "duration": 60}
    )
    hass.services.async_call.reset_mock()

    # --- Test: DISCHARGE ---
    # Effekt 1.0 kW -> 1000 W
    await simulate_event("DISCHARGE", power_kw="1.0")
    hass.services.async_call.assert_called_with(
        "huawei_solar", "forcible_discharge",
        {"device_id": "huawei_device_123", "power": 1000, "duration": 60}
    )
    hass.services.async_call.reset_mock()

    # --- Test: HOLD (Normalfall) ---
    await simulate_event("HOLD", current_mode="maximise_self_consumption")
    hass.services.async_call.assert_any_call(
        "select", "select_option",
        {"entity_id": "select.working_mode", "option": "fixed_charge_discharge"}
    )
    hass.services.async_call.reset_mock()

    # --- Test: HOLD (Filter) ---
    # Om vi redan är i fixed_charge_discharge ska INGET anrop göras
    await simulate_event("HOLD", current_mode="fixed_charge_discharge")
    hass.services.async_call.assert_not_called()

    # --- Test: IDLE (Normalfall) ---
    await simulate_event("IDLE", current_mode="fixed_charge_discharge")
    hass.services.async_call.assert_any_call(
        "select", "select_option",
        {"entity_id": "select.working_mode", "option": "maximise_self_consumption"}
    )
    hass.services.async_call.reset_mock()

    # --- Test: IDLE (Filter) ---
    # Om vi redan är i adaptive ska INGET anrop göras
    await simulate_event("IDLE", current_mode="maximise_self_consumption")
    hass.services.async_call.assert_not_called()

    # --- Test: Default (Okänd Action) ---
    # Om action är något annat (t.ex. "UNKNOWN_COMMAND") ska den köra default (Ladda 10W)
    await simulate_event("UNKNOWN_COMMAND")
    hass.services.async_call.assert_called_with(
        "huawei_solar", "forcible_charge",
        {"device_id": "huawei_device_123", "power": 10, "duration": 60}
    )
    hass.services.async_call.reset_mock()
