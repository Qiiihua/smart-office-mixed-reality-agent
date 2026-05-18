"""
Tests for the Mixed-Reality Cognitive Map.

The CognitiveMap must:
- Store any node type under a string key
- Return None for missing keys
- Filter nodes by NodeType via query()
- Export all nodes as a plain dict via snapshot()
- Overwrite an existing node when update() is called again with the same key
"""

import pytest
from src.cognitive_map.cognitive_map import CognitiveMap
from src.cognitive_map.nodes import NodeType, PhysicalNode, IoTNode, WebNode, DesktopNode


class TestUpdateAndGet:
    def test_stored_node_can_be_retrieved(self):
        cm = CognitiveMap()
        node = PhysicalNode(id="room", presence=True, co2_ppm=420.0)
        cm.update("room", node)
        assert cm.get("room") is node

    def test_missing_key_returns_none(self):
        cm = CognitiveMap()
        assert cm.get("nonexistent") is None

    def test_update_overwrites_existing_node(self):
        cm = CognitiveMap()
        node_a = PhysicalNode(id="room", presence=False, co2_ppm=400.0)
        node_b = PhysicalNode(id="room", presence=True,  co2_ppm=850.0)
        cm.update("room", node_a)
        cm.update("room", node_b)
        assert cm.get("room").presence is True

    def test_multiple_nodes_stored_independently(self):
        cm = CognitiveMap()
        cm.update("room", PhysicalNode(id="room", presence=True, co2_ppm=420.0))
        cm.update("therm", IoTNode(id="therm", properties={}, actions={}, events={}))
        assert cm.get("room") is not None
        assert cm.get("therm") is not None


class TestQuery:
    def test_query_returns_only_matching_type(self):
        cm = CognitiveMap()
        cm.update("room",  PhysicalNode(id="room",  presence=True, co2_ppm=420.0))
        cm.update("therm", IoTNode(id="therm", properties={}, actions={}, events={}))
        cm.update("cal",   WebNode(id="cal", data={}))

        physical = cm.query(NodeType.PHYSICAL)
        assert len(physical) == 1
        assert physical[0].id == "room"

    def test_query_returns_all_nodes_of_type(self):
        cm = CognitiveMap()
        cm.update("therm", IoTNode(id="therm", properties={}, actions={}, events={}))
        cm.update("lights", IoTNode(id="lights", properties={}, actions={}, events={}))
        cm.update("room",  PhysicalNode(id="room", presence=True, co2_ppm=420.0))

        iot_nodes = cm.query(NodeType.IOT)
        assert len(iot_nodes) == 2

    def test_query_empty_result_returns_empty_list(self):
        cm = CognitiveMap()
        cm.update("room", PhysicalNode(id="room", presence=False, co2_ppm=400.0))
        assert cm.query(NodeType.DESKTOP) == []


class TestSnapshot:
    def test_snapshot_returns_dict(self):
        cm = CognitiveMap()
        cm.update("room", PhysicalNode(id="room", presence=False, co2_ppm=400.0))
        snap = cm.snapshot()
        assert isinstance(snap, dict)

    def test_snapshot_contains_all_keys(self):
        cm = CognitiveMap()
        cm.update("room", PhysicalNode(id="room", presence=True, co2_ppm=420.0))
        cm.update("cal",  WebNode(id="cal", data={"events": []}))
        snap = cm.snapshot()
        assert "room" in snap
        assert "cal" in snap

    def test_snapshot_values_are_plain_dicts(self):
        """snapshot() must return serialisable dicts, not dataclass instances."""
        cm = CognitiveMap()
        cm.update("room", PhysicalNode(id="room", presence=True, co2_ppm=420.0))
        snap = cm.snapshot()
        # The value must be a plain dict, not a PhysicalNode instance
        assert isinstance(snap["room"], dict)
        assert snap["room"]["presence"] is True

    def test_snapshot_of_empty_map_returns_empty_dict(self):
        cm = CognitiveMap()
        assert cm.snapshot() == {}
