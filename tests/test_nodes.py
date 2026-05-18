"""
Tests for cognitive map node types.

Each node type must:
- Be creatable with required fields only
- Automatically carry the correct NodeType enum value
- Store all provided field values without mutation
"""

import pytest
from src.cognitive_map.nodes import (
    NodeType,
    PhysicalNode,
    IoTNode,
    WebNode,
    DesktopNode,
)


class TestPhysicalNode:
    def test_node_type_is_physical(self):
        node = PhysicalNode(id="room", presence=False, co2_ppm=400.0)
        assert node.node_type == NodeType.PHYSICAL

    def test_stores_presence_and_co2(self):
        node = PhysicalNode(id="room", presence=True, co2_ppm=850.5)
        assert node.presence is True
        assert node.co2_ppm == 850.5

    def test_timestamp_defaults_to_zero(self):
        node = PhysicalNode(id="room", presence=False, co2_ppm=400.0)
        assert node.timestamp == 0.0

    def test_id_is_stored(self):
        node = PhysicalNode(id="office-a", presence=True, co2_ppm=420.0)
        assert node.id == "office-a"


class TestIoTNode:
    def test_node_type_is_iot(self):
        node = IoTNode(id="thermostat", properties={}, actions={}, events={})
        assert node.node_type == NodeType.IOT

    def test_stores_affordance_dicts(self):
        props = {"temperature": {"type": "number"}}
        actions = {"setTemperature": {"input": {"type": "number"}}}
        events = {"temperatureReached": {"data": {"type": "number"}}}
        node = IoTNode(id="thermostat", properties=props, actions=actions, events=events)
        assert "temperature" in node.properties
        assert "setTemperature" in node.actions
        assert "temperatureReached" in node.events

    def test_td_url_defaults_to_empty_string(self):
        node = IoTNode(id="lights", properties={}, actions={}, events={})
        assert node.td_url == ""

    def test_td_url_can_be_set(self):
        node = IoTNode(
            id="lights", properties={}, actions={}, events={},
            td_url="http://localhost:3002/lights",
        )
        assert node.td_url == "http://localhost:3002/lights"


class TestWebNode:
    def test_node_type_is_web(self):
        node = WebNode(id="calendar", data={})
        assert node.node_type == NodeType.WEB

    def test_stores_data_dict(self):
        data = {"events": [{"title": "video call", "time": "10:00"}]}
        node = WebNode(id="calendar", data=data)
        assert node.data["events"][0]["title"] == "video call"


class TestDesktopNode:
    def test_node_type_is_desktop(self):
        node = DesktopNode(id="desktop", locked=True, active_apps=[], session_urls=[])
        assert node.node_type == NodeType.DESKTOP

    def test_stores_lock_state(self):
        node = DesktopNode(id="desktop", locked=False, active_apps=[], session_urls=[])
        assert node.locked is False

    def test_stores_active_apps(self):
        node = DesktopNode(
            id="desktop", locked=False,
            active_apps=["Chrome", "Slack"], session_urls=[],
        )
        assert "Chrome" in node.active_apps

    def test_stores_session_urls(self):
        urls = ["https://calendar.google.com", "https://github.com"]
        node = DesktopNode(id="desktop", locked=False, active_apps=[], session_urls=urls)
        assert len(node.session_urls) == 2
