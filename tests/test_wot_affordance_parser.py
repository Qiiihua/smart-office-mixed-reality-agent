from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch
from src.perception.wot_affordance_parser import WoTAffordanceParser
from src.cognitive_map.nodes import IoTNode

MOCK_TD = {
    "title": "Thermostat",
    "id": "urn:smart-office:thermostat",
    "properties": {
        "temperature": {"type": "number", "readOnly": True}
    },
    "actions": {
        "setTemperature": {"input": {"type": "number"}}
    },
    "events": {
        "temperatureReached": {"data": {"type": "number"}}
    },
    "forms": [],
    "base": "http://localhost:3001",
}


@pytest.mark.asyncio
async def test_parse_returns_iot_node():
    parser = WoTAffordanceParser()
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value=MOCK_TD)
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=False)
        mock_get.return_value = mock_resp

        node = await parser.parse("http://localhost:3001/thermostat")

    assert isinstance(node, IoTNode)
    assert node.id == "thermostat"
    assert "temperature" in node.properties
    assert "setTemperature" in node.actions
    assert "temperatureReached" in node.events


@pytest.mark.asyncio
async def test_read_property_returns_value():
    parser = WoTAffordanceParser()
    node = IoTNode(
        id="thermostat",
        properties={"temperature": {"type": "number"}},
        actions={},
        events={},
        td_url="http://localhost:3001/thermostat",
    )
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value=28.0)
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=False)
        mock_get.return_value = mock_resp

        value = await parser.read_property(node, "temperature")

    assert value == 28.0


@pytest.mark.asyncio
async def test_invoke_action_returns_ok():
    parser = WoTAffordanceParser()
    node = IoTNode(
        id="thermostat",
        properties={},
        actions={"setTemperature": {"input": {"type": "number"}}},
        events={},
        td_url="http://localhost:3001/thermostat",
    )
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=False)
        mock_post.return_value = mock_resp

        result = await parser.invoke_action(node, "setTemperature", 20.0)

    assert result["status"] == "ok"
