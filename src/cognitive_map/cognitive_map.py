"""
cognitive_map.py — The Mixed-Reality Cognitive Map (shared Blackboard).

This is the unified world model for the Smart Office Agent.
It stores the current state of all physical, IoT, web, and desktop entities
in a single queryable interface.

Three roles in the system interact with it:
  - Perception layer  → writes sensor readings and WoT device state (update)
  - LLM Supervisor    → reads a full snapshot to reason over (snapshot)
  - Execution layer   → reads specific nodes to dispatch actions (get / query)
"""

from __future__ import annotations

import dataclasses
from src.cognitive_map.nodes import Node, NodeType


class CognitiveMap:
    """
    A key-value store for Mixed-Reality world state.

    Keys are string identifiers (e.g. "room", "thermostat", "calendar").
    Values are typed node dataclasses (PhysicalNode, IoTNode, WebNode, DesktopNode).
    """

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}

    def update(self, node_id: str, node: Node) -> None:
        """
        Insert or overwrite a node in the map.

        Called by the perception layer whenever a sensor reading changes
        or a WoT property is refreshed.
        """
        self._nodes[node_id] = node

    def get(self, node_id: str) -> Node | None:
        """
        Return the node stored under `node_id`, or None if not found.

        Used by the execution layer to look up a specific device before
        invoking a WoT action.
        """
        return self._nodes.get(node_id)

    def query(self, node_type: NodeType) -> list[Node]:
        """
        Return all nodes of the given NodeType.

        Example: query(NodeType.IOT) returns all WoT devices currently
        in the map, which the LLM Supervisor can enumerate as affordances.
        """
        return [node for node in self._nodes.values() if node.node_type == node_type]

    def snapshot(self) -> dict:
        """
        Export the entire map as a plain nested dict.

        The result is JSON-serialisable and is passed directly to the
        LLM Supervisor as the 'current world state' section of the prompt.
        """
        return {
            node_id: dataclasses.asdict(node)
            for node_id, node in self._nodes.items()
        }
