# Battery Optimizer Light
# Copyright (C) 2026 @awestin67

"""Konfiguration för pytest."""
import os
import sys
from unittest.mock import MagicMock
import pytest

# Lägg till rotkatalogen i sys.path så att vi kan importera custom_components
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- MOCK HOME ASSISTANT ---
# Vi måste mocka HA-moduler INNAN vi importerar komponenter
# för att slippa installera 'homeassistant' och dess tunga beroenden.

mock_hass = MagicMock()
sys.modules["homeassistant"] = mock_hass
sys.modules["homeassistant.core"] = mock_hass

# Se till att callback bara returnerar funktionen (identity decorator)
mock_hass.callback = lambda func: func

sys.modules["homeassistant.config_entries"] = mock_hass
sys.modules["homeassistant.data_entry_flow"] = mock_hass
sys.modules["homeassistant.helpers"] = mock_hass
sys.modules["homeassistant.helpers.entity"] = mock_hass
sys.modules["homeassistant.helpers.update_coordinator"] = mock_hass
sys.modules["homeassistant.helpers.aiohttp_client"] = mock_hass
sys.modules["homeassistant.helpers.event"] = mock_hass
sys.modules["homeassistant.helpers.selector"] = mock_hass
sys.modules["homeassistant.components"] = mock_hass
sys.modules["homeassistant.components.sensor"] = mock_hass
sys.modules["homeassistant.components.switch"] = mock_hass
sys.modules["homeassistant.components.binary_sensor"] = mock_hass
sys.modules["homeassistant.const"] = mock_hass
sys.modules["homeassistant.util"] = mock_hass
sys.modules["homeassistant.exceptions"] = mock_hass

# Mocka voluptuous för att undvika problem med installation/version
sys.modules["voluptuous"] = mock_hass

# Konfigurera nödvändiga klasser och attribut på mocken
mock_hass.config_entries = mock_hass
mock_hass.data_entry_flow = mock_hass
mock_hass.SOURCE_USER = "user"

class MockConfigFlow:
    """Mock för ConfigFlow."""
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()

    def __init__(self):
        self.hass = None
    async def async_step_user(self, user_input=None):
        pass

    def async_show_form(
        self,
        step_id=None,
        data_schema=None,
        errors=None,
        description_placeholders=None,
        last_step=None,
    ):
        """Mock method for showing a form."""
        return {
            "type": "form",
            "step_id": step_id,
            "data_schema": data_schema,
            "errors": errors or {},
            "description_placeholders": description_placeholders,
        }

    def async_create_entry(self, title=None, data=None, description=None, description_placeholders=None):
        """Mock method for creating an entry."""
        return {
            "type": "create_entry",
            "title": title,
            "data": data,
            "description": description,
            "description_placeholders": description_placeholders,
        }

    async def async_set_unique_id(self, *args, **kwargs):
        """Mock method for setting unique ID."""

    def _abort_if_unique_id_configured(self, *args, **kwargs):
        """Mock method for aborting."""

    def async_update_reload_and_abort(self, *args, **kwargs):
        """Mock method for update reload and abort."""
mock_hass.ConfigFlow = MockConfigFlow

class MockOptionsFlow:
    """Mock för OptionsFlow."""
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
    def __init__(self):
        self.hass = None
    async def async_step_init(self, user_input=None):
        pass

    def async_show_form(self, *args, **kwargs):
        """Mock method for showing a form."""

    def async_create_entry(self, *args, **kwargs):
        """Mock method for creating an entry."""

    def add_suggested_values_to_schema(self, schema, suggested_values):
        """Mock method for adding suggested values."""
        return schema

mock_hass.OptionsFlow = MockOptionsFlow

class FlowResultType:
    FORM = "form"
    CREATE_ENTRY = "create_entry"
    ABORT = "abort"
mock_hass.FlowResultType = FlowResultType

class UpdateFailed(Exception):
    pass
mock_hass.UpdateFailed = UpdateFailed

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations():
    """Dummy fixture för att ersätta den från pytest-homeassistant-custom-component."""
    yield

@pytest.fixture
def hass():
    """Fixture för en mockad HA-instans."""
    hass = MagicMock()
    hass.config.components = set()
    return hass
