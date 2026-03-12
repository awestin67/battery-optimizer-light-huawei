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

"""Test the Huawei Battery Optimizer config flow."""
import pytest

from homeassistant import data_entry_flow
from homeassistant.core import HomeAssistant

from custom_components.battery_optimizer_light_huawei.config_flow import HuaweiConfigFlow


@pytest.mark.asyncio
async def test_successful_config_flow(hass: HomeAssistant) -> None:
    """Test a successful config flow."""
    # 1. Starta flödet manuellt (eftersom vi mockar HA core)
    flow = HuaweiConfigFlow()
    flow.hass = hass

    result = await flow.async_step_user()

    # Kontrollera att vi fick ett formulär
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    # 2. Simulera användarinmatning
    user_input = {
        "battery_device_id": "test_device_id",
        "working_mode_entity": "select.test_working_mode",
    }

    # 3. Skicka in data till flödet
    result = await flow.async_step_user(user_input)

    # 3. Verifiera att entry skapades korrekt
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Battery Optimizer Light Huawei"
    assert result["data"] == user_input
