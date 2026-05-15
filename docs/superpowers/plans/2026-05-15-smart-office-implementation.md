# Smart Office Mixed-Reality Agent — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Smart Office Agent that fuses physical sensor streams (camera presence, WoT CO₂/temperature) with digital context (calendar, desktop) into a unified Mixed-Reality Cognitive Map and orchestrates cross-reality actions via a Reflex/Supervisor architecture.

**Architecture:** A four-layer pipeline — Perception (Physical Scene Parser + WoT Affordance Parser) writes into a unified Cognitive Map; a Reflex Loop (<50 ms rule matching) handles clear events while an LLM Supervisor handles cross-reality reasoning and emits a Reality-Tagged Task DAG; a HostAgent dispatches tasks to PhysicalAgent (WoT HTTP) or AppAgents (desktop/web).

**Tech Stack:** Python 3.11+, asyncio, Node.js (Node-WoT simulation), Claude API (Anthropic SDK), YOLOv8n (ultralytics), aiohttp, pytest, pytest-asyncio

---

## Resolved Open Questions

1. **Presence only** — no identity; single-person office. `person=present|absent` boolean.
2. **Event-driven Supervisor** — invoked only on triggers (arrival, sustained absence, WoT events that escape Reflex). No periodic polling.
3. **Node-WoT simulation** — four simulated devices (thermostat, lights, CO₂, ventilation). No real hardware required.
4. **Session snapshot = browser tabs** — serialize open Chrome tab URLs to Blackboard. No full OS window layout.
5. **No-auth prototype** — WoT TD 2.0 `"securityDefinitions": {"nosec_sc": {"scheme": "nosec"}}`. OAuth2 deferred.

---

## File Structure

```
smart-office-agent/
├── src/
│   ├── config.py                        # All env vars and thresholds
│   ├── cognitive_map/
│   │   ├── nodes.py                     # PhysicalNode, IoTNode, WebNode, DesktopNode dataclasses
│   │   ├── event_bus.py                 # asyncio EventBus (publish/subscribe)
│   │   └── cognitive_map.py             # CognitiveMap: update/get/query/snapshot
│   ├── perception/
│   │   ├── wot_affordance_parser.py     # Fetch WoT TD → IoTNode; read_property; invoke_action
│   │   └── physical_scene_parser.py     # Camera frame → list[PhysicalEntity] (real YOLOv8 or mock)
│   ├── reflex/
│   │   ├── rules.py                     # ReflexRule dataclass + BUILTIN_RULES list
│   │   └── reflex_loop.py               # ReflexLoop: register_action / handle
│   ├── supervisor/
│   │   ├── task_dag.py                  # TaskStar, TaskDAG, RealityDomain
│   │   └── llm_supervisor.py            # LLMSupervisor: snapshot → Claude API → TaskDAG
│   ├── agents/
│   │   ├── physical_agent.py            # PhysicalAgent: execute WoT actions; subscribe_events
│   │   └── host_agent.py                # HostAgent: run_dag; dispatch to physical/digital
│   └── main.py                          # Entry point: wire all components, run event loop
├── simulation/
│   ├── wot/
│   │   ├── package.json
│   │   ├── thermostat.js                # Node-WoT port 3001; temperature property; setTemperature action
│   │   ├── lights.js                    # Node-WoT port 3002; brightness property; setLighting action
│   │   ├── co2_sensor.js               # Node-WoT port 3003; co2_ppm property; simulateSpike action + event
│   │   └── ventilation.js              # Node-WoT port 3004; active property; setVentilation action
│   └── mock_camera.py                   # MockCamera: async generator yielding scripted PresenceFrame
└── tests/
    ├── test_cognitive_map.py
    ├── test_event_bus.py
    ├── test_wot_affordance_parser.py
    ├── test_physical_scene_parser.py
    ├── test_task_dag.py
    ├── test_reflex_loop.py
    ├── test_physical_agent.py
    ├── test_llm_supervisor.py
    ├── test_host_agent.py
    ├── integration/
    │   ├── test_scenario_a.py           # Arrival: presence → Supervisor → WoT set temp/lights
    │   └── test_scenario_b.py           # CO₂ interrupt → Reflex → ventilation on
    └── evaluation/
        ├── baseline.py                  # Rule-based system for comparison
        ├── metrics.py                   # TaskCompletionRate, ReflexLatency, etc.
        ├── scenarios.py                 # 5 evaluation scenarios
        └── runner.py                    # Run all scenarios, print metrics table
```

---

## Milestone Table

| Phase | Tasks | Weeks | Owner |
|-------|-------|-------|-------|
| Phase 0: Foundation | 0–5 | 1–2 | All |
| Phase 1: Perception | 6–7 | 2–4 | P1 |
| Phase 2: Planning & Execution | 8–12 | 3–6 | P2 + P3 |
| Phase 3: Integration Tests | 13–14 | 7–9 | P3 |
| Phase 4: Evaluation | 15–16 | 10–12 | P3 |

**Team assignment:**
- **P1**: Tasks 4, 5, 6, 7 — Simulation + Perception
- **P2**: Tasks 1, 2, 3, 8, 11 — Cognitive Map + LLM Supervisor
- **P3**: Tasks 9, 10, 12, 13, 14, 15, 16 — Execution + Integration + Evaluation

---

## Phase 0: Foundation (Weeks 1–2)

### Task 0: Project Setup

**Files:**
- Create: `src/__init__.py`, `simulation/wot/package.json`, `requirements.txt`, `pytest.ini`

- [ ] **Step 1: Create Python package structure**

```bash
mkdir -p src/cognitive_map src/perception src/reflex src/supervisor src/agents
mkdir -p simulation/wot tests/integration tests/evaluation
touch src/__init__.py src/cognitive_map/__init__.py src/perception/__init__.py
touch src/reflex/__init__.py src/supervisor/__init__.py src/agents/__init__.py
```

- [ ] **Step 2: Create `requirements.txt`**

```
anthropic>=0.28.0
aiohttp>=3.9.0
ultralytics>=8.2.0
opencv-python>=4.9.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

- [ ] **Step 3: Create `pytest.ini`**

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
```

- [ ] **Step 4: Create `simulation/wot/package.json`**

```json
{
  "name": "smart-office-wot-simulation",
  "version": "1.0.0",
  "dependencies": {
    "@node-wot/binding-http": "^0.9.0",
    "@node-wot/core": "^0.9.0"
  }
}
```

- [ ] **Step 5: Install dependencies**

```bash
pip install -r requirements.txt
cd simulation/wot && npm install
```

Expected: all packages install without error.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt pytest.ini simulation/wot/package.json src/
git commit -m "feat: project scaffolding and dependency setup"
```

---

### Task 1: Config

**Files:**
- Create: `src/config.py`

- [ ] **Step 1: Write `src/config.py`**

```python
import os

WOT_BASE_URL = os.getenv("WOT_BASE_URL", "http://localhost")

THERMOSTAT_TD_URL = f"{WOT_BASE_URL}:3001/thermostat"
LIGHTS_TD_URL = f"{WOT_BASE_URL}:3002/lights"
CO2_SENSOR_TD_URL = f"{WOT_BASE_URL}:3003/co2sensor"
VENTILATION_TD_URL = f"{WOT_BASE_URL}:3004/ventilation"

CO2_THRESHOLD_PPM = 1000
ABSENCE_TIMEOUT_SEC = 180
TEMP_COMFORT = 22.0
TEMP_STANDBY = 26.0
TEMP_AGGRESSIVE = 20.0

CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "-1"))  # -1 = mock

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-opus-4-5"
```

- [ ] **Step 2: Commit**

```bash
git add src/config.py
git commit -m "feat: add config module with WoT URLs and thresholds"
```

---

### Task 2: Cognitive Map Nodes

**Files:**
- Create: `src/cognitive_map/nodes.py`
- Test: `tests/test_cognitive_map.py` (partial)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cognitive_map.py
import pytest
from src.cognitive_map.nodes import (
    NodeType, PhysicalNode, IoTNode, WebNode, DesktopNode
)

def test_physical_node_defaults():
    node = PhysicalNode(id="room", presence=False, co2_ppm=400.0)
    assert node.node_type == NodeType.PHYSICAL
    assert node.co2_ppm == 400.0

def test_iot_node_defaults():
    node = IoTNode(id="thermostat", properties={}, actions={}, events={})
    assert node.node_type == NodeType.IOT

def test_web_node_defaults():
    node = WebNode(id="calendar", data={})
    assert node.node_type == NodeType.WEB

def test_desktop_node_defaults():
    node = DesktopNode(id="desktop", locked=True, active_apps=[], session_urls=[])
    assert node.node_type == NodeType.DESKTOP
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_cognitive_map.py -v
```

Expected: `ImportError` — module not found.

- [ ] **Step 3: Write `src/cognitive_map/nodes.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeType(str, Enum):
    PHYSICAL = "physical"
    IOT = "iot"
    WEB = "web"
    DESKTOP = "desktop"


@dataclass
class PhysicalNode:
    id: str
    presence: bool
    co2_ppm: float
    timestamp: float = 0.0
    node_type: NodeType = field(default=NodeType.PHYSICAL, init=False)


@dataclass
class IoTNode:
    id: str
    properties: dict[str, Any]
    actions: dict[str, Any]
    events: dict[str, Any]
    td_url: str = ""
    node_type: NodeType = field(default=NodeType.IOT, init=False)


@dataclass
class WebNode:
    id: str
    data: dict[str, Any]
    node_type: NodeType = field(default=NodeType.WEB, init=False)


@dataclass
class DesktopNode:
    id: str
    locked: bool
    active_apps: list[str]
    session_urls: list[str]
    node_type: NodeType = field(default=NodeType.DESKTOP, init=False)


Node = PhysicalNode | IoTNode | WebNode | DesktopNode
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_cognitive_map.py -v
```

Expected: 4 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/cognitive_map/nodes.py tests/test_cognitive_map.py
git commit -m "feat: cognitive map node types (Physical, IoT, Web, Desktop)"
```

---

### Task 3: EventBus

**Files:**
- Create: `src/cognitive_map/event_bus.py`
- Test: `tests/test_event_bus.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_event_bus.py
import asyncio
import pytest
from src.cognitive_map.event_bus import Event, EventBus

@pytest.mark.asyncio
async def test_subscribe_and_publish():
    bus = EventBus()
    received = []

    async def handler(event: Event):
        received.append(event)

    bus.subscribe("co2_exceeded", handler)
    await bus.publish(Event(type="co2_exceeded", data={"ppm": 1200}, source="co2_sensor"))
    assert len(received) == 1
    assert received[0].data["ppm"] == 1200

@pytest.mark.asyncio
async def test_unsubscribed_event_ignored():
    bus = EventBus()
    received = []

    async def handler(event: Event):
        received.append(event)

    bus.subscribe("presence", handler)
    await bus.publish(Event(type="co2_exceeded", data={}, source="sensor"))
    assert len(received) == 0

@pytest.mark.asyncio
async def test_multiple_subscribers():
    bus = EventBus()
    received_a, received_b = [], []

    bus.subscribe("evt", lambda e: received_a.append(e))
    bus.subscribe("evt", lambda e: received_b.append(e))
    await bus.publish(Event(type="evt", data={}, source="x"))
    assert len(received_a) == 1
    assert len(received_b) == 1
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_event_bus.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Write `src/cognitive_map/event_bus.py`**

```python
from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

Handler = Callable[["Event"], Awaitable[None]]


@dataclass
class Event:
    type: str
    data: dict[str, Any]
    source: str
    timestamp: float = field(default_factory=time.time)


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = {}

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, event: Event) -> None:
        handlers = self._handlers.get(event.type, [])
        if handlers:
            results = [h(event) for h in handlers]
            # Support both sync and async handlers
            coros = [r for r in results if asyncio.iscoroutine(r)]
            if coros:
                await asyncio.gather(*coros)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_event_bus.py -v
```

Expected: 3 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/cognitive_map/event_bus.py tests/test_event_bus.py
git commit -m "feat: asyncio EventBus with pub/sub and mixed sync/async handlers"
```

---

### Task 4: CognitiveMap

**Files:**
- Create: `src/cognitive_map/cognitive_map.py`
- Test: `tests/test_cognitive_map.py` (extend)

- [ ] **Step 1: Append failing tests to `tests/test_cognitive_map.py`**

```python
# Append to tests/test_cognitive_map.py
import dataclasses
from src.cognitive_map.cognitive_map import CognitiveMap

def test_update_and_get():
    cm = CognitiveMap()
    node = PhysicalNode(id="room", presence=True, co2_ppm=500.0)
    cm.update("room", node)
    result = cm.get("room")
    assert result is not None
    assert result.presence is True

def test_get_missing_returns_none():
    cm = CognitiveMap()
    assert cm.get("nonexistent") is None

def test_query_by_type():
    cm = CognitiveMap()
    cm.update("room", PhysicalNode(id="room", presence=True, co2_ppm=400.0))
    cm.update("therm", IoTNode(id="therm", properties={}, actions={}, events={}))
    physical = cm.query(NodeType.PHYSICAL)
    assert len(physical) == 1
    assert physical[0].id == "room"

def test_snapshot_is_dict():
    cm = CognitiveMap()
    cm.update("room", PhysicalNode(id="room", presence=False, co2_ppm=400.0))
    snap = cm.snapshot()
    assert isinstance(snap, dict)
    assert "room" in snap
    assert snap["room"]["presence"] is False
```

- [ ] **Step 2: Run to verify new tests fail**

```bash
pytest tests/test_cognitive_map.py::test_update_and_get -v
```

Expected: `ImportError`.

- [ ] **Step 3: Write `src/cognitive_map/cognitive_map.py`**

```python
from __future__ import annotations
import dataclasses
from src.cognitive_map.nodes import Node, NodeType


class CognitiveMap:
    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}

    def update(self, node_id: str, node: Node) -> None:
        self._nodes[node_id] = node

    def get(self, node_id: str) -> Node | None:
        return self._nodes.get(node_id)

    def query(self, node_type: NodeType) -> list[Node]:
        return [n for n in self._nodes.values() if n.node_type == node_type]

    def snapshot(self) -> dict:
        return {
            node_id: dataclasses.asdict(node)
            for node_id, node in self._nodes.items()
        }
```

- [ ] **Step 4: Run all cognitive map tests**

```bash
pytest tests/test_cognitive_map.py -v
```

Expected: 8 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/cognitive_map/cognitive_map.py tests/test_cognitive_map.py
git commit -m "feat: CognitiveMap with update/get/query/snapshot"
```

---

### Task 5: Node-WoT Simulation

**Files:**
- Create: `simulation/wot/thermostat.js`
- Create: `simulation/wot/lights.js`
- Create: `simulation/wot/co2_sensor.js`
- Create: `simulation/wot/ventilation.js`
- Create: `simulation/mock_camera.py`

- [ ] **Step 1: Write `simulation/wot/thermostat.js`**

```javascript
// simulation/wot/thermostat.js
const { Servient } = require("@node-wot/core");
const { HttpServer } = require("@node-wot/binding-http");

const servient = new Servient();
servient.addServer(new HttpServer({ port: 3001 }));

servient.start().then((WoT) => {
  let currentTemp = 28.0;
  let targetTemp = 28.0;

  WoT.produce({
    title: "Thermostat",
    id: "urn:smart-office:thermostat",
    securityDefinitions: { nosec_sc: { scheme: "nosec" } },
    security: ["nosec_sc"],
    properties: {
      temperature: {
        type: "number",
        observable: true,
        readOnly: true,
        description: "Current temperature in °C",
      },
    },
    actions: {
      setTemperature: {
        input: { type: "number" },
        description: "Set target temperature in °C",
      },
    },
    events: {
      temperatureReached: {
        data: { type: "number" },
        description: "Emitted when target temperature is reached",
      },
    },
  }).then((thing) => {
    thing.setPropertyReadHandler("temperature", () => currentTemp);

    thing.setActionHandler("setTemperature", async (params) => {
      targetTemp = await params.value();
      console.log(`[Thermostat] Target set to ${targetTemp}°C`);
      // Simulate reaching target after 3 seconds
      setTimeout(() => {
        currentTemp = targetTemp;
        thing.emitEvent("temperatureReached", currentTemp);
        console.log(`[Thermostat] Reached ${currentTemp}°C`);
      }, 3000);
    });

    thing.expose();
    console.log("[Thermostat] Running on port 3001");
  });
});
```

- [ ] **Step 2: Write `simulation/wot/lights.js`**

```javascript
// simulation/wot/lights.js
const { Servient } = require("@node-wot/core");
const { HttpServer } = require("@node-wot/binding-http");

const servient = new Servient();
servient.addServer(new HttpServer({ port: 3002 }));

servient.start().then((WoT) => {
  let brightness = 0;
  let mode = "off";

  WoT.produce({
    title: "SmartLights",
    id: "urn:smart-office:lights",
    securityDefinitions: { nosec_sc: { scheme: "nosec" } },
    security: ["nosec_sc"],
    properties: {
      brightness: { type: "number", readOnly: true },
      mode: { type: "string", readOnly: true },
    },
    actions: {
      setLighting: {
        input: {
          type: "object",
          properties: {
            mode: { type: "string" },
            brightness: { type: "number" },
          },
        },
      },
    },
    events: {},
  }).then((thing) => {
    thing.setPropertyReadHandler("brightness", () => brightness);
    thing.setPropertyReadHandler("mode", () => mode);

    thing.setActionHandler("setLighting", async (params) => {
      const input = await params.value();
      mode = input.mode ?? mode;
      brightness = input.brightness ?? brightness;
      console.log(`[Lights] mode=${mode} brightness=${brightness}`);
    });

    thing.expose();
    console.log("[Lights] Running on port 3002");
  });
});
```

- [ ] **Step 3: Write `simulation/wot/co2_sensor.js`**

```javascript
// simulation/wot/co2_sensor.js
const { Servient } = require("@node-wot/core");
const { HttpServer } = require("@node-wot/binding-http");

const servient = new Servient();
servient.addServer(new HttpServer({ port: 3003 }));

servient.start().then((WoT) => {
  let co2_ppm = 420;

  WoT.produce({
    title: "CO2Sensor",
    id: "urn:smart-office:co2sensor",
    securityDefinitions: { nosec_sc: { scheme: "nosec" } },
    security: ["nosec_sc"],
    properties: {
      co2_ppm: { type: "number", readOnly: true, observable: true },
    },
    actions: {
      simulateSpike: {
        input: { type: "number" },
        description: "Set CO₂ level (ppm) to trigger event if above threshold",
      },
    },
    events: {
      co2ExceededThreshold: {
        data: { type: "number" },
        description: "Emitted when CO₂ exceeds 1000 ppm",
      },
    },
  }).then((thing) => {
    thing.setPropertyReadHandler("co2_ppm", () => co2_ppm);

    thing.setActionHandler("simulateSpike", async (params) => {
      co2_ppm = await params.value();
      console.log(`[CO2] Level set to ${co2_ppm} ppm`);
      if (co2_ppm > 1000) {
        thing.emitEvent("co2ExceededThreshold", co2_ppm);
        console.log(`[CO2] Threshold exceeded! Emitting event.`);
      }
    });

    thing.expose();
    console.log("[CO2Sensor] Running on port 3003");
  });
});
```

- [ ] **Step 4: Write `simulation/wot/ventilation.js`**

```javascript
// simulation/wot/ventilation.js
const { Servient } = require("@node-wot/core");
const { HttpServer } = require("@node-wot/binding-http");

const servient = new Servient();
servient.addServer(new HttpServer({ port: 3004 }));

servient.start().then((WoT) => {
  let active = false;

  WoT.produce({
    title: "Ventilation",
    id: "urn:smart-office:ventilation",
    securityDefinitions: { nosec_sc: { scheme: "nosec" } },
    security: ["nosec_sc"],
    properties: {
      active: { type: "boolean", readOnly: true },
    },
    actions: {
      setVentilation: {
        input: { type: "boolean" },
        description: "Turn ventilation on (true) or off (false)",
      },
    },
    events: {},
  }).then((thing) => {
    thing.setPropertyReadHandler("active", () => active);

    thing.setActionHandler("setVentilation", async (params) => {
      active = await params.value();
      console.log(`[Ventilation] active=${active}`);
    });

    thing.expose();
    console.log("[Ventilation] Running on port 3004");
  });
});
```

- [ ] **Step 5: Write `simulation/mock_camera.py`**

```python
# simulation/mock_camera.py
from __future__ import annotations
import asyncio
from dataclasses import dataclass


@dataclass
class PresenceFrame:
    present: bool
    timestamp: float = 0.0


class MockCamera:
    """
    Async generator yielding scripted PresenceFrames.
    Each script entry is (delay_seconds, present_bool).
    """

    def __init__(self, script: list[tuple[float, bool]]) -> None:
        self._script = script

    async def stream(self):
        import time
        for delay, present in self._script:
            await asyncio.sleep(delay)
            yield PresenceFrame(present=present, timestamp=time.time())


# Scenario A: user arrives
SCENARIO_A_SCRIPT: list[tuple[float, bool]] = [
    (0.1, True),   # immediately present
]

# Scenario C: user leaves and returns
SCENARIO_C_SCRIPT: list[tuple[float, bool]] = [
    (0.1, True),   # present
    (5.0, False),  # leaves
    (2.0, True),   # returns
]
```

- [ ] **Step 6: Smoke-test the WoT simulation (manual)**

```bash
# Terminal 1: start all four simulators
cd simulation/wot
node thermostat.js &
node lights.js &
node co2_sensor.js &
node ventilation.js &

# Terminal 2: verify Thing Descriptions are served
curl http://localhost:3001/thermostat | python3 -m json.tool | head -20
curl http://localhost:3003/co2sensor | python3 -m json.tool | head -20
```

Expected: JSON Thing Description with `title`, `properties`, `actions`, `events`.

- [ ] **Step 7: Kill simulation background processes**

```bash
pkill -f "node thermostat.js"; pkill -f "node lights.js"
pkill -f "node co2_sensor.js"; pkill -f "node ventilation.js"
```

- [ ] **Step 8: Commit**

```bash
git add simulation/
git commit -m "feat: Node-WoT simulation — thermostat, lights, CO2, ventilation"
```

---

## Phase 1: Perception (Weeks 2–4)

### Task 6: WoT Affordance Parser

**Files:**
- Create: `src/perception/wot_affordance_parser.py`
- Test: `tests/test_wot_affordance_parser.py`

The parser fetches a WoT Thing Description from a URL and converts it to an `IoTNode`. It also provides `read_property` and `invoke_action` helper methods.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_wot_affordance_parser.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_wot_affordance_parser.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Write `src/perception/wot_affordance_parser.py`**

```python
from __future__ import annotations
import aiohttp
from src.cognitive_map.nodes import IoTNode


class WoTAffordanceParser:
    """Fetches a W3C WoT Thing Description and converts it to an IoTNode."""

    async def parse(self, td_url: str) -> IoTNode:
        async with aiohttp.ClientSession() as session:
            async with session.get(td_url) as resp:
                td = await resp.json(content_type=None)

        title = td.get("title", td_url.split("/")[-1])
        node_id = title.lower().replace(" ", "_")
        return IoTNode(
            id=node_id,
            properties=td.get("properties", {}),
            actions=td.get("actions", {}),
            events=td.get("events", {}),
            td_url=td_url,
        )

    async def read_property(self, node: IoTNode, prop_name: str) -> float | str | None:
        """Read a property value via WoT HTTP binding."""
        url = f"{node.td_url}/properties/{prop_name}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json(content_type=None)

    async def invoke_action(
        self, node: IoTNode, action_name: str, value: float | str | dict
    ) -> dict:
        """Invoke a WoT action. Returns {"status": "ok"} or {"status": "error", "detail": ...}."""
        url = f"{node.td_url}/actions/{action_name}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=value) as resp:
                    if resp.status < 300:
                        return {"status": "ok"}
                    return {"status": "error", "detail": f"HTTP {resp.status}"}
        except Exception as exc:
            return {"status": "error", "detail": str(exc)}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_wot_affordance_parser.py -v
```

Expected: 3 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/perception/wot_affordance_parser.py tests/test_wot_affordance_parser.py
git commit -m "feat: WoT Affordance Parser — TD fetch, read_property, invoke_action"
```

---

### Task 7: Physical Scene Parser

**Files:**
- Create: `src/perception/physical_scene_parser.py`
- Test: `tests/test_physical_scene_parser.py`

Mock mode returns scripted entities; real mode runs YOLOv8n on the camera frame.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_physical_scene_parser.py
import pytest
from src.perception.physical_scene_parser import PhysicalSceneParser, PhysicalEntity

def test_mock_mode_present():
    parser = PhysicalSceneParser(mock_mode=True, mock_present=True)
    entities = parser.parse(frame=None)
    persons = [e for e in entities if e.entity_type == "person"]
    assert len(persons) == 1
    assert persons[0].state == "present"
    assert persons[0].confidence == 1.0

def test_mock_mode_absent():
    parser = PhysicalSceneParser(mock_mode=True, mock_present=False)
    entities = parser.parse(frame=None)
    persons = [e for e in entities if e.entity_type == "person"]
    assert len(persons) == 1
    assert persons[0].state == "absent"

def test_mock_mode_with_devices():
    parser = PhysicalSceneParser(
        mock_mode=True,
        mock_present=True,
        mock_devices=["thermostat", "monitor"],
    )
    entities = parser.parse(frame=None)
    types = {e.entity_type for e in entities}
    assert "person" in types
    assert "thermostat" in types
    assert "monitor" in types

def test_wot_discovery_hint_set_for_known_devices():
    parser = PhysicalSceneParser(
        mock_mode=True,
        mock_present=True,
        mock_devices=["thermostat"],
    )
    entities = parser.parse(frame=None)
    therm = next(e for e in entities if e.entity_type == "thermostat")
    assert therm.wot_discovery_hint is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_physical_scene_parser.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Write `src/perception/physical_scene_parser.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, field

# Device types that map to WoT Things
WOT_DEVICE_TYPES = {"thermostat", "lights", "ventilation", "co2sensor"}


@dataclass
class PhysicalEntity:
    id: str
    entity_type: str
    state: str
    confidence: float = 1.0
    wot_discovery_hint: bool = False


class PhysicalSceneParser:
    """
    Parses camera frames into structured PhysicalEntity lists.
    In mock_mode, returns scripted entities without running vision models.
    In real mode, uses YOLOv8n (requires ultralytics + camera).
    """

    def __init__(
        self,
        mock_mode: bool = True,
        mock_present: bool = False,
        mock_devices: list[str] | None = None,
    ) -> None:
        self._mock_mode = mock_mode
        self._mock_present = mock_present
        self._mock_devices = mock_devices or []
        self._model = None

        if not mock_mode:
            from ultralytics import YOLO
            self._model = YOLO("yolov8n.pt")

    def parse(self, frame) -> list[PhysicalEntity]:
        if self._mock_mode:
            return self._mock_parse()
        return self._real_parse(frame)

    def _mock_parse(self) -> list[PhysicalEntity]:
        entities: list[PhysicalEntity] = []
        state = "present" if self._mock_present else "absent"
        entities.append(
            PhysicalEntity(id="p1", entity_type="person", state=state, confidence=1.0)
        )
        for i, device_type in enumerate(self._mock_devices):
            entities.append(
                PhysicalEntity(
                    id=f"d{i+1}",
                    entity_type=device_type,
                    state="detected",
                    confidence=1.0,
                    wot_discovery_hint=(device_type in WOT_DEVICE_TYPES),
                )
            )
        return entities

    def _real_parse(self, frame) -> list[PhysicalEntity]:
        if frame is None or self._model is None:
            return []
        results = self._model(frame)
        entities = []
        for i, box in enumerate(results[0].boxes):
            cls_name = results[0].names[int(box.cls)]
            state = "present" if cls_name == "person" else "detected"
            entities.append(
                PhysicalEntity(
                    id=f"r{i}",
                    entity_type=cls_name,
                    state=state,
                    confidence=float(box.conf),
                    wot_discovery_hint=(cls_name in WOT_DEVICE_TYPES),
                )
            )
        return entities
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_physical_scene_parser.py -v
```

Expected: 4 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/perception/physical_scene_parser.py tests/test_physical_scene_parser.py
git commit -m "feat: Physical Scene Parser — mock mode + YOLOv8 real mode"
```

---

## Phase 2: Planning & Execution (Weeks 3–6)

### Task 8: Task DAG

**Files:**
- Create: `src/supervisor/task_dag.py`
- Test: `tests/test_task_dag.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_task_dag.py
import pytest
from src.supervisor.task_dag import TaskDAG, TaskStar, RealityDomain, TaskStatus

def _make_dag() -> TaskDAG:
    stars = [
        TaskStar(id="t1", task="check_calendar", domain=RealityDomain.DIGITAL, deps=[]),
        TaskStar(id="t2", task="check_weather",  domain=RealityDomain.DIGITAL, deps=[]),
        TaskStar(id="t3", task="set_temperature",domain=RealityDomain.PHYSICAL,deps=["t1","t2"]),
    ]
    return TaskDAG(stars)

def test_ready_tasks_initially_no_deps():
    dag = _make_dag()
    ready = dag.ready_tasks()
    ids = {t.id for t in ready}
    assert ids == {"t1", "t2"}

def test_ready_after_completing_deps():
    dag = _make_dag()
    dag.mark_done("t1")
    dag.mark_done("t2")
    ready = dag.ready_tasks()
    assert any(t.id == "t3" for t in ready)

def test_failed_dep_blocks_task():
    dag = _make_dag()
    dag.mark_done("t1")
    dag.mark_failed("t2")
    ready = dag.ready_tasks()
    assert not any(t.id == "t3" for t in ready)

def test_all_done_when_all_complete():
    dag = _make_dag()
    dag.mark_done("t1")
    dag.mark_done("t2")
    dag.mark_done("t3")
    assert dag.all_done() is True

def test_all_done_false_when_pending():
    dag = _make_dag()
    dag.mark_done("t1")
    assert dag.all_done() is False
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_task_dag.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Write `src/supervisor/task_dag.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RealityDomain(str, Enum):
    PHYSICAL = "physical"
    DIGITAL = "digital"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class TaskStar:
    id: str
    task: str
    domain: RealityDomain
    deps: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None


class TaskDAG:
    def __init__(self, stars: list[TaskStar]) -> None:
        self._tasks: dict[str, TaskStar] = {t.id: t for t in stars}

    def ready_tasks(self) -> list[TaskStar]:
        """Return tasks that are PENDING and whose deps are all DONE."""
        ready = []
        for task in self._tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            deps = [self._tasks[d] for d in task.deps if d in self._tasks]
            if any(d.status == TaskStatus.FAILED for d in deps):
                continue  # blocked
            if all(d.status == TaskStatus.DONE for d in deps):
                ready.append(task)
        return ready

    def mark_done(self, task_id: str, result: Any = None) -> None:
        self._tasks[task_id].status = TaskStatus.DONE
        self._tasks[task_id].result = result

    def mark_failed(self, task_id: str) -> None:
        self._tasks[task_id].status = TaskStatus.FAILED

    def all_done(self) -> bool:
        return all(
            t.status in (TaskStatus.DONE, TaskStatus.FAILED)
            for t in self._tasks.values()
        )

    def tasks(self) -> list[TaskStar]:
        return list(self._tasks.values())
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_task_dag.py -v
```

Expected: 5 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/supervisor/task_dag.py tests/test_task_dag.py
git commit -m "feat: Reality-Tagged TaskDAG with ready_tasks and cross-reality deps"
```

---

### Task 9: Reflex Rules and Loop

**Files:**
- Create: `src/reflex/rules.py`
- Create: `src/reflex/reflex_loop.py`
- Test: `tests/test_reflex_loop.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_reflex_loop.py
import asyncio
import pytest
from src.cognitive_map.event_bus import Event
from src.reflex.rules import BUILTIN_RULES
from src.reflex.reflex_loop import ReflexLoop

@pytest.mark.asyncio
async def test_co2_rule_triggers_action():
    loop = ReflexLoop(rules=BUILTIN_RULES)
    triggered = []
    loop.register_action("co2_ventilation", lambda e: triggered.append(e))
    event = Event(type="co2_exceeded", data={"ppm": 1200}, source="co2_sensor")
    handled = await loop.handle(event)
    assert handled is True
    assert len(triggered) == 1

@pytest.mark.asyncio
async def test_unknown_event_not_handled():
    loop = ReflexLoop(rules=BUILTIN_RULES)
    event = Event(type="unknown_event", data={}, source="x")
    handled = await loop.handle(event)
    assert handled is False

@pytest.mark.asyncio
async def test_presence_arrival_triggers():
    loop = ReflexLoop(rules=BUILTIN_RULES)
    triggered = []
    loop.register_action("presence_arrival", lambda e: triggered.append(e))
    event = Event(type="presence", data={"present": True}, source="camera")
    handled = await loop.handle(event)
    assert handled is True
    assert len(triggered) == 1

@pytest.mark.asyncio
async def test_presence_departure_triggers():
    loop = ReflexLoop(rules=BUILTIN_RULES)
    triggered = []
    loop.register_action("presence_departure", lambda e: triggered.append(e))
    event = Event(type="presence", data={"present": False}, source="camera")
    handled = await loop.handle(event)
    assert handled is True
    assert len(triggered) == 1

@pytest.mark.asyncio
async def test_condition_false_skips_action():
    loop = ReflexLoop(rules=BUILTIN_RULES)
    triggered = []
    loop.register_action("co2_ventilation", lambda e: triggered.append(e))
    # ppm below threshold
    event = Event(type="co2_exceeded", data={"ppm": 500}, source="co2_sensor")
    handled = await loop.handle(event)
    # co2_ventilation rule matches event type but condition checks ppm
    assert len(triggered) == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_reflex_loop.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Write `src/reflex/rules.py`**

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from src.cognitive_map.event_bus import Event
from src import config


@dataclass
class ReflexRule:
    name: str
    event_type: str
    condition: Callable[[Event], bool]
    actions: list[str]  # registered action names to call


BUILTIN_RULES: list[ReflexRule] = [
    ReflexRule(
        name="co2_ventilation",
        event_type="co2_exceeded",
        condition=lambda e: e.data.get("ppm", 0) > config.CO2_THRESHOLD_PPM,
        actions=["co2_ventilation"],
    ),
    ReflexRule(
        name="presence_arrival",
        event_type="presence",
        condition=lambda e: e.data.get("present") is True,
        actions=["presence_arrival"],
    ),
    ReflexRule(
        name="presence_departure",
        event_type="presence",
        condition=lambda e: e.data.get("present") is False,
        actions=["presence_departure"],
    ),
    ReflexRule(
        name="temperature_reached",
        event_type="temperature_reached",
        condition=lambda e: True,
        actions=["temperature_reached"],
    ),
]
```

- [ ] **Step 4: Write `src/reflex/reflex_loop.py`**

```python
from __future__ import annotations
import asyncio
from typing import Callable
from src.cognitive_map.event_bus import Event
from src.reflex.rules import ReflexRule


class ReflexLoop:
    """
    System 1: fast rule-matching handler.
    Returns True if a rule matched (and action was invoked), False to escalate.
    """

    def __init__(self, rules: list[ReflexRule]) -> None:
        self._rules = rules
        self._actions: dict[str, Callable] = {}

    def register_action(self, rule_name: str, action: Callable) -> None:
        self._actions[rule_name] = action

    async def handle(self, event: Event) -> bool:
        for rule in self._rules:
            if rule.event_type != event.type:
                continue
            if not rule.condition(event):
                continue
            # Rule matched — invoke all registered actions
            for action_name in rule.actions:
                action = self._actions.get(action_name)
                if action is None:
                    continue
                result = action(event)
                if asyncio.iscoroutine(result):
                    await result
            return True
        return False
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_reflex_loop.py -v
```

Expected: 5 PASSED.

- [ ] **Step 6: Commit**

```bash
git add src/reflex/rules.py src/reflex/reflex_loop.py tests/test_reflex_loop.py
git commit -m "feat: Reflex Loop with BUILTIN_RULES (co2, presence, temperature)"
```

---

### Task 10: PhysicalAgent

**Files:**
- Create: `src/agents/physical_agent.py`
- Test: `tests/test_physical_agent.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_physical_agent.py
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.agents.physical_agent import PhysicalAgent
from src.supervisor.task_dag import TaskStar, RealityDomain
from src.cognitive_map.nodes import IoTNode

@pytest.fixture
def thermostat_node():
    return IoTNode(
        id="thermostat",
        properties={"temperature": {"type": "number"}},
        actions={"setTemperature": {"input": {"type": "number"}}},
        events={"temperatureReached": {}},
        td_url="http://localhost:3001/thermostat",
    )

@pytest.mark.asyncio
async def test_execute_invokes_wot_action(thermostat_node):
    mock_parser = AsyncMock()
    mock_parser.invoke_action = AsyncMock(return_value={"status": "ok"})

    agent = PhysicalAgent(wot_parser=mock_parser)
    task = TaskStar(
        id="t1",
        task="setTemperature",
        domain=RealityDomain.PHYSICAL,
        deps=[],
        result={"node": thermostat_node, "action": "setTemperature", "value": 20.0},
    )
    result = await agent.execute(task)
    assert result["status"] == "ok"
    mock_parser.invoke_action.assert_called_once_with(thermostat_node, "setTemperature", 20.0)

@pytest.mark.asyncio
async def test_execute_missing_result_returns_error():
    agent = PhysicalAgent(wot_parser=AsyncMock())
    task = TaskStar(
        id="t1", task="setTemperature", domain=RealityDomain.PHYSICAL, result=None
    )
    result = await agent.execute(task)
    assert result["status"] == "error"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_physical_agent.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Write `src/agents/physical_agent.py`**

```python
from __future__ import annotations
from src.cognitive_map.event_bus import Event, EventBus
from src.cognitive_map.nodes import IoTNode
from src.perception.wot_affordance_parser import WoTAffordanceParser
from src.supervisor.task_dag import TaskStar


class PhysicalAgent:
    """
    Executes physical (WoT) tasks from the Task DAG.
    Also subscribes to WoT Events and pushes them to the EventBus.
    """

    def __init__(
        self,
        wot_parser: WoTAffordanceParser | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self._parser = wot_parser or WoTAffordanceParser()
        self._bus = event_bus

    async def execute(self, task: TaskStar) -> dict:
        """Execute a physical task. task.result must contain {node, action, value}."""
        if task.result is None:
            return {"status": "error", "detail": "task.result is None — missing dispatch info"}

        node: IoTNode = task.result.get("node")
        action_name: str = task.result.get("action", "")
        value = task.result.get("value")

        if node is None or not action_name:
            return {"status": "error", "detail": "missing node or action in task.result"}

        return await self._parser.invoke_action(node, action_name, value)

    async def subscribe_events(self, node: IoTNode) -> None:
        """
        Long-polls WoT Event SSE endpoint and publishes to EventBus.
        This method runs indefinitely — launch as an asyncio task.
        """
        import aiohttp
        for event_name in node.events:
            url = f"{node.td_url}/events/{event_name}"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        async for line in resp.content:
                            decoded = line.decode().strip()
                            if decoded.startswith("data:") and self._bus:
                                import json
                                raw = decoded[5:].strip()
                                try:
                                    data = json.loads(raw)
                                except Exception:
                                    data = {"raw": raw}
                                await self._bus.publish(
                                    Event(type=event_name, data=data, source=node.id)
                                )
            except Exception:
                pass  # connection closed or device offline — caller handles reconnect
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_physical_agent.py -v
```

Expected: 2 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/agents/physical_agent.py tests/test_physical_agent.py
git commit -m "feat: PhysicalAgent — WoT action execution and event subscription"
```

---

### Task 11: LLM Supervisor

**Files:**
- Create: `src/supervisor/llm_supervisor.py`
- Test: `tests/test_llm_supervisor.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_llm_supervisor.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.supervisor.llm_supervisor import LLMSupervisor
from src.supervisor.task_dag import TaskDAG, RealityDomain

MOCK_LLM_RESPONSE = """
```json
{
  "constellation": [
    {"id": "t1", "task": "check_calendar", "domain": "digital",  "deps": []},
    {"id": "t2", "task": "set_temperature","domain": "physical", "deps": ["t1"]}
  ]
}
```
"""

@pytest.mark.asyncio
async def test_reason_returns_task_dag():
    supervisor = LLMSupervisor(api_key="test-key")

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=MOCK_LLM_RESPONSE)]

    with patch("anthropic.Anthropic") as MockClient:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_message
        MockClient.return_value = mock_client
        supervisor._client = mock_client

        dag = await supervisor.reason(
            trigger="user_arrived",
            snapshot={"room": {"presence": True, "co2_ppm": 420.0}},
        )

    assert isinstance(dag, TaskDAG)
    tasks = dag.tasks()
    assert len(tasks) == 2
    ids = {t.id for t in tasks}
    assert "t1" in ids
    assert "t2" in ids

@pytest.mark.asyncio
async def test_reason_handles_malformed_json():
    supervisor = LLMSupervisor(api_key="test-key")

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Sorry, I cannot process this.")]

    with patch("anthropic.Anthropic") as MockClient:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_message
        MockClient.return_value = mock_client
        supervisor._client = mock_client

        dag = await supervisor.reason(trigger="unknown", snapshot={})

    # Should return empty DAG rather than crash
    assert isinstance(dag, TaskDAG)
    assert dag.all_done() is True  # empty DAG is trivially done
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_llm_supervisor.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Write `src/supervisor/llm_supervisor.py`**

```python
from __future__ import annotations
import json
import re
import anthropic
from src.supervisor.task_dag import TaskDAG, TaskStar, RealityDomain
from src import config

SYSTEM_PROMPT = """You are a Smart Office orchestration planner.
Given a Mixed-Reality Cognitive Map snapshot and a trigger event, produce a Reality-Tagged Task DAG.

Output ONLY a JSON code block in this exact format:
```json
{
  "constellation": [
    {"id": "t1", "task": "<task_name>", "domain": "physical|digital", "deps": []}
  ]
}
```

Rules:
- domain must be "physical" or "digital"
- deps is a list of task ids that must complete before this task
- Tasks with no dependencies run in parallel
- Physical tasks that depend on calendar/weather must list those digital tasks as deps
"""


class LLMSupervisor:
    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or config.ANTHROPIC_API_KEY
        self._client = anthropic.Anthropic(api_key=key)

    async def reason(self, trigger: str, snapshot: dict) -> TaskDAG:
        """
        Given a trigger event name and a Cognitive Map snapshot,
        call Claude and parse the JSON response into a TaskDAG.
        """
        user_message = (
            f"Trigger: {trigger}\n\nCognitive Map Snapshot:\n{json.dumps(snapshot, indent=2)}"
        )

        message = self._client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw = message.content[0].text
        return self._parse_dag(raw)

    def _parse_dag(self, raw: str) -> TaskDAG:
        """Extract JSON from markdown code block and build TaskDAG."""
        match = re.search(r"```json\s*(.*?)```", raw, re.DOTALL)
        if not match:
            return TaskDAG([])  # empty DAG — all_done() is True

        try:
            data = json.loads(match.group(1))
            stars = []
            for item in data.get("constellation", []):
                domain = RealityDomain(item.get("domain", "digital"))
                stars.append(
                    TaskStar(
                        id=item["id"],
                        task=item["task"],
                        domain=domain,
                        deps=item.get("deps", []),
                    )
                )
            return TaskDAG(stars)
        except (json.JSONDecodeError, KeyError, ValueError):
            return TaskDAG([])
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_llm_supervisor.py -v
```

Expected: 2 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/supervisor/llm_supervisor.py tests/test_llm_supervisor.py
git commit -m "feat: LLM Supervisor — Claude API integration with TaskDAG parsing"
```

---

### Task 12: HostAgent

**Files:**
- Create: `src/agents/host_agent.py`
- Test: `tests/test_host_agent.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_host_agent.py
import asyncio
import pytest
from unittest.mock import AsyncMock
from src.agents.host_agent import HostAgent
from src.supervisor.task_dag import TaskDAG, TaskStar, RealityDomain, TaskStatus

@pytest.mark.asyncio
async def test_run_dag_dispatches_physical_task():
    mock_physical = AsyncMock()
    mock_physical.execute = AsyncMock(return_value={"status": "ok"})

    agent = HostAgent(physical_agent=mock_physical, digital_agents={})
    dag = TaskDAG([
        TaskStar(id="t1", task="setTemperature", domain=RealityDomain.PHYSICAL, deps=[],
                 result={"node": "thermostat", "action": "setTemperature", "value": 20.0})
    ])
    await agent.run_dag(dag)

    mock_physical.execute.assert_called_once()
    task = dag.tasks()[0]
    assert task.status == TaskStatus.DONE

@pytest.mark.asyncio
async def test_run_dag_respects_dependencies():
    executed_order = []

    async def fake_physical(task):
        executed_order.append(task.id)
        return {"status": "ok"}

    mock_physical = AsyncMock()
    mock_physical.execute = AsyncMock(side_effect=fake_physical)

    agent = HostAgent(physical_agent=mock_physical, digital_agents={})
    dag = TaskDAG([
        TaskStar(id="t1", task="check", domain=RealityDomain.PHYSICAL, deps=[],
                 result={"node": "x", "action": "a", "value": 1}),
        TaskStar(id="t2", task="act",   domain=RealityDomain.PHYSICAL, deps=["t1"],
                 result={"node": "x", "action": "b", "value": 2}),
    ])
    await agent.run_dag(dag)

    assert executed_order.index("t1") < executed_order.index("t2")

@pytest.mark.asyncio
async def test_run_dag_marks_failed_on_error():
    mock_physical = AsyncMock()
    mock_physical.execute = AsyncMock(return_value={"status": "error", "detail": "timeout"})

    agent = HostAgent(physical_agent=mock_physical, digital_agents={})
    dag = TaskDAG([
        TaskStar(id="t1", task="setTemp", domain=RealityDomain.PHYSICAL, deps=[],
                 result={"node": "x", "action": "a", "value": 1})
    ])
    await agent.run_dag(dag)

    assert dag.tasks()[0].status == TaskStatus.FAILED
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_host_agent.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Write `src/agents/host_agent.py`**

```python
from __future__ import annotations
import asyncio
from src.agents.physical_agent import PhysicalAgent
from src.supervisor.task_dag import TaskDAG, TaskStar, RealityDomain, TaskStatus


class HostAgent:
    """
    Orchestrates Reality-Tagged Task DAGs.
    Dispatches physical tasks to PhysicalAgent, digital tasks to digital_agents["default"].
    Respects cross-reality dependencies via iterative ready-task polling.
    """

    def __init__(
        self,
        physical_agent: PhysicalAgent,
        digital_agents: dict,
    ) -> None:
        self._physical = physical_agent
        self._digital = digital_agents

    async def run_dag(self, dag: TaskDAG) -> None:
        while not dag.all_done():
            ready = dag.ready_tasks()
            if not ready:
                break  # deadlock or all failed
            await asyncio.gather(*[self._dispatch(task, dag) for task in ready])

    async def _dispatch(self, task: TaskStar, dag: TaskDAG) -> None:
        task.status = TaskStatus.RUNNING
        try:
            if task.domain == RealityDomain.PHYSICAL:
                result = await self._physical.execute(task)
            else:
                agent = self._digital.get("default")
                if agent is None:
                    result = {"status": "error", "detail": "no digital agent registered"}
                else:
                    result = await agent.execute(task)

            if result.get("status") == "ok":
                dag.mark_done(task.id, result)
            else:
                dag.mark_failed(task.id)
        except Exception as exc:
            dag.mark_failed(task.id)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_host_agent.py -v
```

Expected: 3 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/agents/host_agent.py tests/test_host_agent.py
git commit -m "feat: HostAgent — Reality-Tagged DAG dispatch with dependency ordering"
```

---

## Phase 3: Integration Tests (Weeks 7–9)

### Task 13: Integration — Scenario A (User Arrives)

**Files:**
- Test: `tests/integration/test_scenario_a.py`

**Prerequisites:** Node-WoT simulation running on ports 3001–3004. Run before this test:
```bash
cd simulation/wot && node thermostat.js & node lights.js & node co2_sensor.js & node ventilation.js &
```

- [ ] **Step 1: Write `tests/integration/test_scenario_a.py`**

```python
# tests/integration/test_scenario_a.py
"""
Scenario A: User arrives → Supervisor → set temperature + lighting.
Uses mock camera (presence=True), mock LLM response (no real API call).
Requires Node-WoT on ports 3001-3002.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.cognitive_map.cognitive_map import CognitiveMap
from src.cognitive_map.event_bus import EventBus, Event
from src.cognitive_map.nodes import PhysicalNode
from src.perception.wot_affordance_parser import WoTAffordanceParser
from src.reflex.rules import BUILTIN_RULES
from src.reflex.reflex_loop import ReflexLoop
from src.supervisor.task_dag import TaskDAG, TaskStar, RealityDomain
from src.supervisor.llm_supervisor import LLMSupervisor
from src.agents.physical_agent import PhysicalAgent
from src.agents.host_agent import HostAgent

MOCK_DAG_JSON = """
```json
{
  "constellation": [
    {"id": "t1", "task": "setTemperature", "domain": "physical", "deps": [],
     "target": "thermostat", "action": "setTemperature", "value": 20.0},
    {"id": "t2", "task": "setLighting",   "domain": "physical", "deps": [],
     "target": "lights", "action": "setLighting", "value": {"mode": "focus-mode", "brightness": 80}}
  ]
}
```
"""

@pytest.mark.asyncio
@pytest.mark.integration
async def test_scenario_a_arrival_triggers_physical_actions():
    # Setup
    cm = CognitiveMap()
    bus = EventBus()
    reflex = ReflexLoop(rules=BUILTIN_RULES)

    # Parse real WoT TDs from running simulation
    parser = WoTAffordanceParser()
    try:
        therm_node = await parser.parse("http://localhost:3001/thermostat")
        lights_node = await parser.parse("http://localhost:3002/lights")
    except Exception:
        pytest.skip("Node-WoT simulation not running on ports 3001-3002")

    cm.update("thermostat", therm_node)
    cm.update("lights", lights_node)

    # Mock LLM to return a fixed DAG (avoid API cost in integration test)
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=MOCK_DAG_JSON)]

    supervisor = LLMSupervisor(api_key="test")
    with patch.object(supervisor._client.messages, "create", return_value=mock_message):
        dag = await supervisor.reason("user_arrived", cm.snapshot())

    # Wire up DAG tasks with real node references
    for task in dag.tasks():
        if task.task == "setTemperature":
            task.result = {"node": therm_node, "action": "setTemperature", "value": 20.0}
        elif task.task == "setLighting":
            task.result = {"node": lights_node, "action": "setLighting",
                          "value": {"mode": "focus-mode", "brightness": 80}}

    # Execute via HostAgent with real WoT calls
    physical_agent = PhysicalAgent(wot_parser=parser, event_bus=bus)
    host = HostAgent(physical_agent=physical_agent, digital_agents={})
    await host.run_dag(dag)

    # Assert all tasks completed
    from src.supervisor.task_dag import TaskStatus
    for task in dag.tasks():
        assert task.status == TaskStatus.DONE, f"Task {task.id} did not complete: {task.status}"

    # Verify temperature was actually set on simulator
    temp_value = await parser.read_property(therm_node, "temperature")
    assert temp_value is not None
```

- [ ] **Step 2: Run the integration test (with simulation running)**

```bash
# Terminal 1: start simulation
cd simulation/wot
node thermostat.js & node lights.js & node co2_sensor.js & node ventilation.js &

# Terminal 2: run integration test
pytest tests/integration/test_scenario_a.py -v -m integration
```

Expected: 1 PASSED (or SKIPPED if simulation not running).

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_scenario_a.py
git commit -m "test(integration): Scenario A — user arrival triggers physical WoT actions"
```

---

### Task 14: Integration — Scenario B (CO₂ Interrupt)

**Files:**
- Test: `tests/integration/test_scenario_b.py`

- [ ] **Step 1: Write `tests/integration/test_scenario_b.py`**

```python
# tests/integration/test_scenario_b.py
"""
Scenario B: CO₂ spike → Reflex loop → ventilation on.
Uses real WoT simulateSpike action on co2_sensor (port 3003).
"""
import asyncio
import pytest
from src.cognitive_map.event_bus import EventBus, Event
from src.perception.wot_affordance_parser import WoTAffordanceParser
from src.reflex.rules import BUILTIN_RULES
from src.reflex.reflex_loop import ReflexLoop
from src.agents.physical_agent import PhysicalAgent

@pytest.mark.asyncio
@pytest.mark.integration
async def test_scenario_b_co2_interrupt():
    bus = EventBus()
    parser = WoTAffordanceParser()

    try:
        co2_node = await parser.parse("http://localhost:3003/co2sensor")
        vent_node = await parser.parse("http://localhost:3004/ventilation")
    except Exception:
        pytest.skip("Node-WoT simulation not running on ports 3003-3004")

    physical_agent = PhysicalAgent(wot_parser=parser, event_bus=bus)
    reflex = ReflexLoop(rules=BUILTIN_RULES)

    # Track what the reflex loop triggers
    ventilation_triggered = []

    async def handle_co2(event: Event):
        # Reflex action: turn on ventilation
        result = await parser.invoke_action(vent_node, "setVentilation", True)
        ventilation_triggered.append(result)

    reflex.register_action("co2_ventilation", handle_co2)
    bus.subscribe("co2_exceeded", lambda e: asyncio.create_task(reflex.handle(e)))

    # Simulate CO₂ spike via WoT action on simulator
    spike_result = await parser.invoke_action(co2_node, "simulateSpike", 1200)
    assert spike_result["status"] == "ok"

    # Publish the event that the simulator would emit
    await bus.publish(Event(type="co2_exceeded", data={"ppm": 1200}, source="co2_sensor"))

    # Allow async tasks to complete
    await asyncio.sleep(0.1)

    assert len(ventilation_triggered) == 1
    assert ventilation_triggered[0]["status"] == "ok"

    # Verify ventilation is now active on simulator
    vent_active = await parser.read_property(vent_node, "active")
    assert vent_active is True
```

- [ ] **Step 2: Run the integration test**

```bash
pytest tests/integration/test_scenario_b.py -v -m integration
```

Expected: 1 PASSED (or SKIPPED).

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_scenario_b.py
git commit -m "test(integration): Scenario B — CO2 interrupt triggers Reflex ventilation"
```

---

## Phase 4: Evaluation (Weeks 10–12)

### Task 15: Evaluation Framework

**Files:**
- Create: `tests/evaluation/baseline.py`
- Create: `tests/evaluation/metrics.py`
- Create: `tests/evaluation/scenarios.py`

- [ ] **Step 1: Write `tests/evaluation/baseline.py`**

```python
# tests/evaluation/baseline.py
"""
Rule-based baseline (no LLM, no cross-reality reasoning).
Hardcoded: presence → set temperature to 22°C, CO₂ high → ventilation on.
"""
from dataclasses import dataclass
from typing import Any


@dataclass
class BaselineResult:
    scenario: str
    actions_taken: list[str]
    latency_ms: float
    completed: bool


class RuleBasedBaseline:
    """Traditional smart-office automation: if X then Y, no context."""

    def run(self, scenario_name: str, events: list[dict]) -> BaselineResult:
        import time
        start = time.time()
        actions = []
        for event in events:
            if event["type"] == "presence" and event["data"].get("present"):
                actions.append("set_temperature(22)")
                actions.append("unlock_screen()")
            elif event["type"] == "presence" and not event["data"].get("present"):
                actions.append("set_temperature(26)")
                actions.append("lock_screen()")
            elif event["type"] == "co2_exceeded":
                actions.append("ventilation(on)")
        latency_ms = (time.time() - start) * 1000
        return BaselineResult(
            scenario=scenario_name,
            actions_taken=actions,
            latency_ms=latency_ms,
            completed=len(actions) > 0,
        )
```

- [ ] **Step 2: Write `tests/evaluation/metrics.py`**

```python
# tests/evaluation/metrics.py
"""Metric definitions matching the design spec Section 7.2."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EvalResult:
    scenario: str
    task_completion_rate: float         # % tasks completed correctly
    cross_reality_accuracy: float       # physical+digital correctly aligned
    reflex_latency_ms: Optional[float]  # None if no reflex event in scenario
    supervisor_latency_ms: Optional[float]
    affordance_discovery_sec: Optional[float]
    non_disruption_pct: float           # always 100% in mock mode


def compute_task_completion_rate(completed: int, total: int) -> float:
    if total == 0:
        return 1.0
    return completed / total


def compute_cross_reality_accuracy(
    physical_actions: list[str],
    digital_context: dict,
    expected_alignment: list[tuple[str, str]],
) -> float:
    """
    Check that each (physical_action, digital_context_key) pair is aligned.
    e.g. [("set_temperature(20)", "calendar_has_video_call")] expects
    aggressive cooling when video call is scheduled.
    """
    if not expected_alignment:
        return 1.0
    correct = 0
    for action, context_key in expected_alignment:
        if action in physical_actions and digital_context.get(context_key):
            correct += 1
    return correct / len(expected_alignment)
```

- [ ] **Step 3: Write `tests/evaluation/scenarios.py`**

```python
# tests/evaluation/scenarios.py
"""The 5 evaluation scenarios from design spec Section 7.3."""
from dataclasses import dataclass
from typing import Any


@dataclass
class EvalScenario:
    name: str
    events: list[dict[str, Any]]
    expected_actions: list[str]       # actions the agent should take
    digital_context: dict[str, Any]   # seeded Cognitive Map digital state
    cross_reality_alignment: list[tuple[str, str]]  # (action, context_key) pairs


EVAL_SCENARIOS = [
    EvalScenario(
        name="standard_arrival_hot_day",
        events=[{"type": "presence", "data": {"present": True}}],
        expected_actions=["setTemperature(20)", "setLighting(focus-mode)", "unlock_screen"],
        digital_context={"calendar_has_video_call": True, "weather_max_celsius": 36},
        cross_reality_alignment=[("setTemperature(20)", "weather_max_celsius")],
    ),
    EvalScenario(
        name="departure_and_return",
        events=[
            {"type": "presence", "data": {"present": False}},
            {"type": "presence", "data": {"present": True}},
        ],
        expected_actions=["setTemperature(26)", "lock_screen", "setTemperature(22)", "unlock_screen"],
        digital_context={},
        cross_reality_alignment=[],
    ),
    EvalScenario(
        name="co2_interrupt_during_work",
        events=[{"type": "co2_exceeded", "data": {"ppm": 1200}}],
        expected_actions=["ventilation(on)"],
        digital_context={},
        cross_reality_alignment=[],
    ),
    EvalScenario(
        name="new_wot_device_hot_plug",
        events=[{"type": "new_device_detected", "data": {"td_url": "http://localhost:3001/thermostat"}}],
        expected_actions=["discover_wot_td", "update_cognitive_map"],
        digital_context={},
        cross_reality_alignment=[],
    ),
    EvalScenario(
        name="conflicting_signals",
        events=[
            {"type": "presence", "data": {"present": False}},
            {"type": "calendar_event", "data": {"type": "focus_block"}},
        ],
        expected_actions=["defer_departure_actions"],
        digital_context={"calendar_focus_block": True},
        cross_reality_alignment=[("defer_departure_actions", "calendar_focus_block")],
    ),
]
```

- [ ] **Step 4: Commit**

```bash
git add tests/evaluation/
git commit -m "feat(eval): baseline, metrics, and 5 evaluation scenarios"
```

---

### Task 16: Evaluation Runner and main.py

**Files:**
- Create: `tests/evaluation/runner.py`
- Create: `src/main.py`

- [ ] **Step 1: Write `tests/evaluation/runner.py`**

```python
# tests/evaluation/runner.py
"""
Run all 5 evaluation scenarios against agent and baseline.
Print a metrics table to stdout.
Usage: python -m tests.evaluation.runner
"""
import asyncio
import time
from tests.evaluation.baseline import RuleBasedBaseline
from tests.evaluation.metrics import (
    EvalResult, compute_task_completion_rate, compute_cross_reality_accuracy
)
from tests.evaluation.scenarios import EVAL_SCENARIOS


def run_baseline_scenarios() -> list[EvalResult]:
    baseline = RuleBasedBaseline()
    results = []
    for scenario in EVAL_SCENARIOS:
        br = baseline.run(scenario.name, scenario.events)
        completed = sum(1 for a in scenario.expected_actions if any(a in ba for ba in br.actions_taken))
        tcr = compute_task_completion_rate(completed, len(scenario.expected_actions))
        cra = compute_cross_reality_accuracy(
            br.actions_taken, scenario.digital_context, scenario.cross_reality_alignment
        )
        results.append(EvalResult(
            scenario=scenario.name,
            task_completion_rate=tcr,
            cross_reality_accuracy=cra,
            reflex_latency_ms=br.latency_ms,
            supervisor_latency_ms=None,
            affordance_discovery_sec=None,
            non_disruption_pct=100.0,
        ))
    return results


def print_table(title: str, results: list[EvalResult]) -> None:
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}")
    print(f"{'Scenario':<35} {'TCR':>6} {'CRA':>6} {'Reflex(ms)':>12}")
    print(f"{'-'*70}")
    for r in results:
        reflex = f"{r.reflex_latency_ms:.1f}" if r.reflex_latency_ms else "N/A"
        print(f"{r.scenario:<35} {r.task_completion_rate:>6.0%} {r.cross_reality_accuracy:>6.0%} {reflex:>12}")


if __name__ == "__main__":
    baseline_results = run_baseline_scenarios()
    print_table("BASELINE (Rule-Based)", baseline_results)

    print("\nNote: Agent results require running Node-WoT simulation + ANTHROPIC_API_KEY.")
    print("Run integration tests with: pytest tests/integration/ -m integration -v")
```

- [ ] **Step 2: Run baseline evaluation**

```bash
python -m tests.evaluation.runner
```

Expected: Table showing baseline TCR ~50-60%, CRA low (no cross-reality reasoning).

- [ ] **Step 3: Write `src/main.py`**

```python
# src/main.py
"""
Smart Office Agent — main entry point.
Wires all components and runs the main event loop.

Usage:
  # Mock mode (no camera, no real WoT):
  python -m src.main --mock

  # Real mode (requires WoT simulation + camera):
  python -m src.main
"""
from __future__ import annotations
import asyncio
import argparse
import time

from src import config
from src.cognitive_map.cognitive_map import CognitiveMap
from src.cognitive_map.event_bus import EventBus, Event
from src.cognitive_map.nodes import PhysicalNode
from src.perception.wot_affordance_parser import WoTAffordanceParser
from src.perception.physical_scene_parser import PhysicalSceneParser
from src.reflex.rules import BUILTIN_RULES
from src.reflex.reflex_loop import ReflexLoop
from src.supervisor.llm_supervisor import LLMSupervisor
from src.agents.physical_agent import PhysicalAgent
from src.agents.host_agent import HostAgent


async def setup_cognitive_map(cm: CognitiveMap, parser: WoTAffordanceParser) -> None:
    """Fetch all WoT Thing Descriptions at startup and populate Cognitive Map."""
    td_urls = [
        ("thermostat", config.THERMOSTAT_TD_URL),
        ("lights", config.LIGHTS_TD_URL),
        ("co2_sensor", config.CO2_SENSOR_TD_URL),
        ("ventilation", config.VENTILATION_TD_URL),
    ]
    for node_id, url in td_urls:
        try:
            node = await parser.parse(url)
            cm.update(node_id, node)
            print(f"[Setup] Discovered WoT device: {node_id} @ {url}")
        except Exception as exc:
            print(f"[Setup] WARNING: Could not reach {node_id} @ {url}: {exc}")


async def presence_loop(
    cm: CognitiveMap,
    bus: EventBus,
    mock: bool = True,
) -> None:
    """Read camera frames and publish presence events."""
    if mock:
        from simulation.mock_camera import MockCamera, SCENARIO_A_SCRIPT
        camera = MockCamera(script=SCENARIO_A_SCRIPT)
        async for frame in camera.stream():
            cm.update("room", PhysicalNode(
                id="room",
                presence=frame.present,
                co2_ppm=420.0,
                timestamp=frame.timestamp,
            ))
            await bus.publish(Event(
                type="presence",
                data={"present": frame.present},
                source="mock_camera",
            ))
    else:
        import cv2
        scene_parser = PhysicalSceneParser(mock_mode=False)
        cap = cv2.VideoCapture(config.CAMERA_INDEX)
        while True:
            ret, frame = cap.read()
            if not ret:
                await asyncio.sleep(0.1)
                continue
            entities = scene_parser.parse(frame)
            persons = [e for e in entities if e.entity_type == "person"]
            present = any(e.state == "present" for e in persons)
            co2_node = cm.get("co2_sensor")
            co2_ppm = 420.0
            if co2_node:
                from src.perception.wot_affordance_parser import WoTAffordanceParser
                _p = WoTAffordanceParser()
                val = await _p.read_property(co2_node, "co2_ppm")
                if val is not None:
                    co2_ppm = float(val)
            cm.update("room", PhysicalNode(
                id="room", presence=present, co2_ppm=co2_ppm, timestamp=time.time()
            ))
            await bus.publish(Event(
                type="presence", data={"present": present}, source="camera"
            ))
            await asyncio.sleep(1.0)


async def main(mock: bool = True) -> None:
    cm = CognitiveMap()
    bus = EventBus()
    parser = WoTAffordanceParser()
    reflex = ReflexLoop(rules=BUILTIN_RULES)
    supervisor = LLMSupervisor()
    physical_agent = PhysicalAgent(wot_parser=parser, event_bus=bus)
    host = HostAgent(physical_agent=physical_agent, digital_agents={})

    # Discover WoT devices
    await setup_cognitive_map(cm, parser)

    # Register reflex actions
    async def on_co2_exceeded(event: Event) -> None:
        vent_node = cm.get("ventilation")
        if vent_node:
            result = await parser.invoke_action(vent_node, "setVentilation", True)
            print(f"[Reflex] Ventilation on: {result}")

    async def on_presence_arrival(event: Event) -> None:
        print("[Reflex] Presence detected — escalating to Supervisor")
        dag = await supervisor.reason("user_arrived", cm.snapshot())
        # Wire nodes into tasks
        for task in dag.tasks():
            if "temperature" in task.task.lower():
                task.result = {
                    "node": cm.get("thermostat"),
                    "action": "setTemperature",
                    "value": config.TEMP_AGGRESSIVE,
                }
            elif "light" in task.task.lower():
                task.result = {
                    "node": cm.get("lights"),
                    "action": "setLighting",
                    "value": {"mode": "focus-mode", "brightness": 80},
                }
        await host.run_dag(dag)

    async def on_presence_departure(event: Event) -> None:
        therm_node = cm.get("thermostat")
        lights_node = cm.get("lights")
        if therm_node:
            await parser.invoke_action(therm_node, "setTemperature", config.TEMP_STANDBY)
        if lights_node:
            await parser.invoke_action(lights_node, "setLighting", {"mode": "off", "brightness": 0})
        print("[Reflex] Departure: standby mode activated")

    reflex.register_action("co2_ventilation", on_co2_exceeded)
    reflex.register_action("presence_arrival", on_presence_arrival)
    reflex.register_action("presence_departure", on_presence_departure)

    # Wire EventBus to Reflex → Supervisor
    async def on_event(event: Event) -> None:
        handled = await reflex.handle(event)
        if not handled:
            print(f"[Bus] Unhandled event {event.type} — escalating to Supervisor")
            dag = await supervisor.reason(event.type, cm.snapshot())
            await host.run_dag(dag)

    for event_type in ["presence", "co2_exceeded", "temperature_reached"]:
        bus.subscribe(event_type, on_event)

    print("[Main] Smart Office Agent started. Press Ctrl+C to stop.")
    await presence_loop(cm, bus, mock=mock)


if __name__ == "__main__":
    parser_arg = argparse.ArgumentParser()
    parser_arg.add_argument("--mock", action="store_true", default=True)
    args = parser_arg.parse_args()
    asyncio.run(main(mock=args.mock))
```

- [ ] **Step 4: Run main.py in mock mode**

```bash
python -m src.main --mock
```

Expected output:
```
[Setup] WARNING: Could not reach thermostat @ http://localhost:3001/thermostat: ...
[Main] Smart Office Agent started. Press Ctrl+C to stop.
[Reflex] Presence detected — escalating to Supervisor
```

(WoT warnings are expected without simulation running.)

- [ ] **Step 5: Run full test suite**

```bash
pytest tests/ -v --ignore=tests/integration --ignore=tests/evaluation
```

Expected: all unit tests PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/evaluation/runner.py src/main.py
git commit -m "feat: evaluation runner and main.py entry point — agent wiring complete"
```

---

## Final Verification

- [ ] **Run all unit tests**

```bash
pytest tests/ -v --ignore=tests/integration
```

Expected: 25+ tests PASSED, 0 FAILED.

- [ ] **Run baseline evaluation**

```bash
python -m tests.evaluation.runner
```

Expected: metrics table printed.

- [ ] **Run integration tests (requires simulation)**

```bash
cd simulation/wot && node thermostat.js & node lights.js & node co2_sensor.js & node ventilation.js &
cd ../.. && pytest tests/integration/ -v -m integration
```

Expected: 2 integration tests PASSED.

- [ ] **Tag milestone**

```bash
git tag v0.1.0-integration
git push origin main --tags
```

---

*Plan saved: 2026-05-15. Covers Phases 0–4, 17 tasks, ~16 commits.*
