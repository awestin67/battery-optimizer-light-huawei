# Battery Optimizer Light
# Copyright (C) 2026 @awestin67

"""Test the Huawei Battery Optimizer options flow."""
from unittest.mock import MagicMock, patch
import pytest

from homeassistant.data_entry_flow import FlowResultType
from homeassistant.core import HomeAssistant

from custom_components.battery_optimizer_light_huawei.const import DOMAIN, CONF_AUTO_CONTROL
from custom_components.battery_optimizer_light_huawei.config_flow import HuaweiOptionsFlowHandler

@pytest.mark.asyncio
async def test_options_flow(hass: HomeAssistant) -> None:
    """Test options flow to toggle auto control."""

    # 1. Skapa en mockad Config Entry
    config_entry = MagicMock()
    config_entry.entry_id = "test_entry_id"
    config_entry.domain = DOMAIN
    config_entry.options = {CONF_AUTO_CONTROL: True} # Default värde

    # 2. Initiera Options Flow
    flow = HuaweiOptionsFlowHandler(config_entry)
    flow.hass = hass

    # 3. Starta flödet (init step)
    result = await flow.async_step_init()

    # Verifiera att vi får ett formulär
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # 4. Simulera att användaren ändrar inställningen till False
    user_input = {CONF_AUTO_CONTROL: False}

    # Vi måste mocka config_entries.async_update_entry eftersom vi inte kör hela HA
    with patch.object(hass.config_entries, "async_update_entry") as mock_update:
        result = await flow.async_step_init(user_input)

        # Verifiera att flödet avslutades och skapade entry
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"] == user_input

        # Verifiera att entry uppdaterades i HA
        assert mock_update.called
        args = mock_update.call_args
        assert args[0][0] == config_entry
        assert args[1]["options"] == user_input
