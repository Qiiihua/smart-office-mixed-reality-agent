# CLAUDE.md — Smart Office Mixed-Reality Agent

This file is read automatically by Claude Code when opening this project.
It gives Claude the context needed to assist any team member effectively.

---

## What This Project Is

A **Smart Office Agent** that fuses physical sensor streams (camera presence,
CO₂, temperature) with digital context (calendar, weather, desktop state) into
a unified **Mixed-Reality Cognitive Map**, then orchestrates cross-reality actions
via a **Reflex/Supervisor** architecture.

**Course:** Masterpraktikum SS26 — Autonomous Agents, TUM
**Team:** 3 persons, 1 semester
**Key papers:** UFO2 (Zhang 2026), Gidey (2025) affordance model, WoT TD 2.0, OmniParser V1

Full design spec: `docs/specs/2026-05-12-smart-office-mixed-reality-agent-design.md`
Full implementation plan: `docs/superpowers/plans/2026-05-15-smart-office-implementation.md`

---

## Architecture in One Picture

```
Camera / WoT Sensors
        ↓
[Physical Scene Parser]   [WoT Affordance Parser]   [AppAgent: Chrome/Desktop]
        ↓                          ↓                           ↓
        └──────────────────────────┴───────────────────────────┘
                                   ↓
                       [Mixed-Reality Cognitive Map]   ← unified world model
                                   ↓
                              [EventBus]
                                   ↓
                    ┌──────────────┴──────────────┐
                    ↓                             ↓
            [Reflex Loop]               [LLM Supervisor]
            fast rules <50ms            Claude API, cross-reality reasoning
                    ↓                             ↓
                    └──────────────┬──────────────┘
                                   ↓
                            [HostAgent]
                          dispatches TaskDAG
                                   ↓
                    ┌──────────────┴──────────────┐
                    ↓                             ↓
            [PhysicalAgent]               [AppAgents]
            WoT HTTP actions          desktop / web actions
```

---

## Module Responsibilities

| File | What it does | Owner |
|------|-------------|-------|
| `src/config.py` | All constants: WoT URLs, thresholds, API keys | All |
| `src/cognitive_map/nodes.py` | Dataclasses: PhysicalNode, IoTNode, WebNode, DesktopNode | P2 |
| `src/cognitive_map/event_bus.py` | Asyncio pub/sub bus connecting all components | P2 |
| `src/cognitive_map/cognitive_map.py` | Unified world model: update/get/query/snapshot | P2 |
| `src/perception/wot_affordance_parser.py` | Fetch WoT Thing Description → IoTNode; read/invoke | P1 |
| `src/perception/physical_scene_parser.py` | Camera frame → list[PhysicalEntity]; YOLOv8 or mock | P1 |
| `src/reflex/rules.py` | ReflexRule dataclass + BUILTIN_RULES list | P3 |
| `src/reflex/reflex_loop.py` | System 1: fast rule matching, returns True/False | P3 |
| `src/supervisor/task_dag.py` | Reality-Tagged TaskDAG with cross-reality deps | P2 |
| `src/supervisor/llm_supervisor.py` | System 2: Claude API → TaskDAG JSON | P2 |
| `src/agents/physical_agent.py` | Execute WoT actions; subscribe to WoT Events | P3 |
| `src/agents/host_agent.py` | Orchestrate TaskDAG; dispatch to physical/digital | P3 |
| `src/main.py` | Entry point: wire all components, run event loop | P3 |
| `simulation/wot/*.js` | Node-WoT virtual devices (thermostat/lights/co2/ventilation) | P1 |
| `simulation/mock_camera.py` | Scripted async camera for tests (no real hardware needed) | P1 |

---

## Key Design Decisions

**1. EventBus is the integration point.**
Components never call each other directly. Everything goes through
`bus.publish(Event(...))`. This means P1, P2, P3 can develop independently
without merge conflicts on shared function calls.

**2. Cognitive Map is the shared blackboard.**
P1 writes perception data in. P2 reads and reasons over it. P3 reads the
resulting TaskDAG and writes execution results back. The `snapshot()` method
returns a plain dict passed directly to Claude as context.

**3. Reflex first, Supervisor second.**
`reflex_loop.handle(event)` returns `True` (handled) or `False` (escalate).
Only escalate to Claude when no clear rule matches — keeps latency low and
API costs down.

**4. Reality-Tagged TaskDAG.**
Every task carries `domain: "physical" | "digital"`. The HostAgent routes
physical tasks to PhysicalAgent (WoT HTTP) and digital tasks to AppAgents.
Cross-reality dependencies are explicit in `deps: ["t1", "t2"]`.

**5. Mock-first development.**
`CAMERA_INDEX = -1` uses MockCamera (no real camera needed).
All integration tests skip automatically if Node-WoT is not running.
This means all unit tests always pass on any machine.

---

## Team Responsibilities

| Person | Modules | Tasks (from plan) |
|--------|---------|-------------------|
| **P1** | Perception: Physical Scene Parser, WoT Affordance Parser, Node-WoT simulation | T4, T5, T6, T7 |
| **P2** | World Model: nodes, EventBus, CognitiveMap, TaskDAG, LLM Supervisor | T1, T2, T3, T8, T11 |
| **P3** | Execution: ReflexLoop, PhysicalAgent, HostAgent, integration tests, evaluation | T9, T10, T12, T13–T16 |

---

## Development Rules

**Always use TDD:**
1. Write the failing test first
2. Run it — confirm it fails with the expected error
3. Write the minimal implementation to make it pass
4. Run all tests — confirm nothing is broken
5. Commit

**Commit format:**
```
feat: add X           ← new feature or file
fix: correct Y        ← bug fix
test: add tests for Z ← tests only, no implementation
chore: update config  ← tooling, dependencies, config
docs: update CLAUDE   ← documentation
refactor: simplify W  ← no behavior change
```

**Code style:**
- All comments and docstrings in **English**
- Type hints on every function signature
- `from __future__ import annotations` at the top of every file
- Prefer small focused files — each file has one clear responsibility
- Never hardcode URLs or numbers — always use `src/config.py`

---

## How to Run

**Setup (first time):**
```bash
conda activate smart-office
pip install -r requirements.txt
cd simulation/wot && npm install && cd ../..
```

**Run all unit tests:**
```bash
python -m pytest tests/ -v --ignore=tests/integration --ignore=tests/evaluation
```

**Start WoT simulators (needed for integration tests):**
```bash
cd simulation/wot
node thermostat.js &
node lights.js &
node co2_sensor.js &
node ventilation.js &
```

**Verify a simulator is running:**
```bash
curl http://localhost:3001/thermostat | python -m json.tool
```

**Run integration tests (requires simulators running):**
```bash
python -m pytest tests/integration/ -v -m integration
```

**Run the agent in mock mode (no camera, no simulators needed):**
```bash
python -m src.main --mock
```

---

## Current Progress

> **Update this section when you complete a task.**

| Task | File | Status | Owner |
|------|------|--------|-------|
| T0 | Project structure, requirements.txt, pytest.ini, .gitignore | ✅ Done | All |
| T1 | `src/config.py` | ✅ Done | P2 |
| T2 | `src/cognitive_map/nodes.py` + tests | ✅ Done | P2 |
| T3 | `src/cognitive_map/event_bus.py` + tests | ✅ Done | P2 |
| T4 | `src/cognitive_map/cognitive_map.py` + tests | ✅ Done | — |
| T5 | `simulation/wot/*.js` + `simulation/mock_camera.py` | ✅ Done | — |
| T6 | `src/perception/wot_affordance_parser.py` + tests | ⏳ Pending | P1 |
| T7 | `src/perception/physical_scene_parser.py` + tests | ⏳ Pending | P1 |
| T8 | `src/supervisor/task_dag.py` + tests | ⏳ Pending | P2 |
| T9 | `src/reflex/rules.py` + `reflex_loop.py` + tests | ⏳ Pending | P3 |
| T10 | `src/agents/physical_agent.py` + tests | ⏳ Pending | P3 |
| T11 | `src/supervisor/llm_supervisor.py` + tests | ⏳ Pending | P2 |
| T12 | `src/agents/host_agent.py` + tests | ⏳ Pending | P3 |
| T13 | `tests/integration/test_scenario_a.py` | ⏳ Pending | P3 |
| T14 | `tests/integration/test_scenario_b.py` | ⏳ Pending | P3 |
| T15 | `tests/evaluation/` baseline + metrics + scenarios | ⏳ Pending | P3 |
| T16 | `tests/evaluation/runner.py` + `src/main.py` | ⏳ Pending | P3 |

---

## WoT Device Reference

| Device | Port | Key property | Key action | Key event |
|--------|------|-------------|------------|-----------|
| Thermostat | 3001 | `temperature` (°C) | `setTemperature(value)` | `temperatureReached` |
| Lights | 3002 | `brightness`, `mode` | `setLighting({mode, brightness})` | — |
| CO₂ Sensor | 3003 | `co2_ppm` | `simulateSpike(value)` | `co2ExceededThreshold` |
| Ventilation | 3004 | `active` (bool) | `setVentilation(bool)` | — |

Thing Description URL format: `http://localhost:{port}/{device_name}`
Property read: `GET http://localhost:{port}/{device}/properties/{prop}`
Action invoke: `POST http://localhost:{port}/{device}/actions/{action}`

---

## Asking Claude for Help

**If you are P1, ask:**
> "I am P1. My tasks are T5, T6, T7. The next pending task is T5 (Node-WoT simulation).
> Read CLAUDE.md and the implementation plan, then help me implement it."

**If you are P2, ask:**
> "I am P2. My next task is T4 (cognitive_map.py TDD).
> Read CLAUDE.md and continue from where we left off."

**If you are P3, ask:**
> "I am P3. My tasks start at T9. Read CLAUDE.md and the implementation plan,
> then walk me through T9 (ReflexLoop)."

**To update progress after completing a task:**
> "I finished T5. Update the progress table in CLAUDE.md."
