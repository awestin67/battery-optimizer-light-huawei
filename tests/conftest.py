# Battery Optimizer Light
# Copyright (C) 2026 @awestin67
"""Konfiguration för pytest."""
import os
import sys
from unittest.mock import MagicMock, AsyncMock
import pytest

# Lägg till rotkatalogen i sys.path så att vi kan importera custom_components
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- MOCK HOME ASSISTANT ---
# Skapa en bas-mock som agerar paket (package)
mock_hass = MagicMock()
mock_hass.__path__ = []
mock_hass.callback = lambda func: func

# Peka om alla relevanta moduler till denna mock
sys.modules["homeassistant"] = mock_hass
sys.modules["homeassistant.core"] = mock_hass
sys.modules["homeassistant.config_entries"] = mock_hass
sys.modules["homeassistant.data_entry_flow"] = mock_hass
sys.modules["homeassistant.helpers"] = mock_hass
sys.modules["homeassistant.helpers.entity"] = mock_hass
sys.modules["homeassistant.helpers.entity_platform"] = mock_hass
sys.modules["homeassistant.helpers.update_coordinator"] = mock_hass
sys.modules["homeassistant.helpers.aiohttp_client"] = mock_hass
sys.modules["homeassistant.helpers.event"] = mock_hass
sys.modules["homeassistant.helpers.device_registry"] = mock_hass
sys.modules["homeassistant.helpers.selector"] = mock_hass
sys.modules["homeassistant.components"] = mock_hass
sys.modules["homeassistant.components.sensor"] = mock_hass
sys.modules["homeassistant.components.switch"] = mock_hass
sys.modules["homeassistant.components.binary_sensor"] = mock_hass
sys.modules["homeassistant.const"] = mock_hass
sys.modules["homeassistant.util"] = mock_hass
sys.modules["homeassistant.exceptions"] = mock_hass
sys.modules["voluptuous"] = mock_hass

# Mocka Event-klassen för att undvika InvalidSpecError i tester
class MockEvent:
    def __init__(self, data=None):
        self.data = data or {}
mock_hass.Event = MockEvent


class MockEntity:
    """En mer komplett mock för HA-entiteter som löser alla fel."""
    _attr_name = None
    _attr_is_on = None
    _attr_native_value = None
    hass = None

    def __init__(self, *args, **kwargs):
        pass

    def async_write_ha_state(self):
        pass

    def async_on_remove(self, func):
        """Mock för async_on_remove som saknades."""
        pass

    @property
    def name(self):
        return self._attr_name

    @property
    def is_on(self):
        return self._attr_is_on

    @is_on.setter
    def is_on(self, value):
        self._attr_is_on = value

    @property
    def native_value(self):
        return self._attr_native_value

    @native_value.setter
    def native_value(self, value):
        self._attr_native_value = value

# VIKTIGT: Placera klasserna direkt på mock_hass eftersom sys.modules pekar dit.
# Detta gör att 'from homeassistant.components.sensor import SensorEntity' hittar rätt klass.
mock_hass.Entity = MockEntity
mock_hass.SensorEntity = MockEntity
mock_hass.BinarySensorEntity = MockEntity

# Sätt även på under-attribut för säkerhets skull
mock_hass.helpers.entity.Entity = MockEntity
mock_hass.components.sensor.SensorEntity = MockEntity
mock_hass.components.binary_sensor.BinarySensorEntity = MockEntity


class MockFlow:
    """Gemensam mock för ConfigFlow och OptionsFlow."""
    def __init_subclass__(cls, **kwargs):
        """Tillåt argument som 'domain' vid klassdefinition."""
        pass

    def __init__(self):
        self.hass = None

    async def async_step_init(self, user_input=None):
        """LÖSNING: Returnerar ett formulär för att lösa TypeError i test_options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(step_id="init")

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(step_id="user")

    def async_show_form(self, step_id, data_schema=None, errors=None, **kwargs):
        return {"type": "form", "step_id": step_id, "data_schema": data_schema, "errors": errors or {}}

    def async_create_entry(self, title="", data=None, **kwargs):
        return {"type": "create_entry", "title": title, "data": data}

    def add_suggested_values_to_schema(self, schema, suggested_values):
        return schema

# Sätt Flow-klasserna på mock_hass
mock_hass.ConfigFlow = MockFlow
mock_hass.OptionsFlow = MockFlow
mock_hass.config_entries.ConfigFlow = MockFlow
mock_hass.config_entries.OptionsFlow = MockFlow


class MockFlowResultType:
    FORM = "form"
    CREATE_ENTRY = "create_entry"
    ABORT = "abort"
mock_hass.data_entry_flow.FlowResultType = MockFlowResultType
mock_hass.FlowResultType = MockFlowResultType


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations():
    """Dummy fixture för att ersätta den från pytest-homeassistant-custom-component."""
    yield

@pytest.fixture
def hass():
    """Fixture för en mockad HA-instans."""
    hass = MagicMock()
    hass.config.components = set()

    # Konfigurera asynkrona mockar för att undvika TypeError vid await
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.services.async_call = AsyncMock(return_value=True)

    return hass
