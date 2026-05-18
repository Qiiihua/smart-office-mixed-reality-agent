"""
nodes.py — Data classes for the four node types in the Mixed-Reality Cognitive Map.

Each node represents one layer of the unified world model:
  - PhysicalNode : state perceived from the physical environment (camera, sensors)
  - IoTNode      : a WoT-enabled device with its affordances (properties/actions/events)
  - WebNode      : data fetched from a web source (calendar, weather API)
  - DesktopNode  : current state of the user's desktop session

All node types carry a `node_type` field that is set automatically
via a post-init default — callers never pass it explicitly.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any


class NodeType(str, Enum):
    """Identifies which reality layer a Cognitive Map node belongs to."""

    PHYSICAL = "physical"
    IOT = "iot"
    WEB = "web"
    DESKTOP = "desktop"


@dataclasses.dataclass
class PhysicalNode:
    """
    Represents the physical state of the office room.

    Written by the Physical Scene Parser and CO₂ sensor poller.
    Read by the Reflex Loop (presence rules) and LLM Supervisor.
    """

    id: str
    presence: bool          # True if a person is detected in the room
    co2_ppm: float          # Current CO₂ concentration in parts per million
    timestamp: float = 0.0  # Unix timestamp of the last update
    node_type: NodeType = dataclasses.field(
        default=NodeType.PHYSICAL, init=False
    )


@dataclasses.dataclass
class IoTNode:
    """
    Represents a WoT-enabled IoT device.

    Populated by the WoT Affordance Parser from a Thing Description (TD).
    `properties`, `actions`, and `events` mirror the TD structure so the
    LLM Supervisor can reason about available affordances directly.
    """

    id: str
    properties: dict[str, Any]  # TD properties catalog  e.g. {"temperature": {...}}
    actions: dict[str, Any]     # TD actions catalog      e.g. {"setTemperature": {...}}
    events: dict[str, Any]      # TD events catalog       e.g. {"temperatureReached": {...}}
    td_url: str = ""            # URL where the Thing Description was fetched from
    node_type: NodeType = dataclasses.field(
        default=NodeType.IOT, init=False
    )


@dataclasses.dataclass
class WebNode:
    """
    Represents data fetched from a web source (calendar, weather API, etc.).

    Written by AppAgent (Chrome) after reading the relevant page.
    The `data` dict is free-form JSON — structure depends on the source.
    """

    id: str
    data: dict[str, Any]  # Parsed content from the web source
    node_type: NodeType = dataclasses.field(
        default=NodeType.WEB, init=False
    )


@dataclasses.dataclass
class DesktopNode:
    """
    Represents the current state of the user's desktop session.

    Written by the Hybrid Desktop Detector (UIA + OmniParser).
    Used by the LLM Supervisor to decide whether to lock/unlock the screen
    and by the HostAgent to restore session state on re-arrival.
    """

    id: str
    locked: bool            # True if the screen is currently locked
    active_apps: list[str]  # Names of currently running applications
    session_urls: list[str] # Open browser tab URLs (for session restore)
    node_type: NodeType = dataclasses.field(
        default=NodeType.DESKTOP, init=False
    )


# Union type — used as the value type of CognitiveMap's internal dict
Node = PhysicalNode | IoTNode | WebNode | DesktopNode
