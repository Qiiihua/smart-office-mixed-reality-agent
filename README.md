# Smart Office Mixed-Reality Agent

**TUM Masterpraktikum SS26 — Autonomous Agents**  
**Advisor:** Habtom Kahsay Gidey, Alexander Lenz, Alois Knoll (TUM)  
**Team:** 3 persons, 1 semester

---

## Project Overview

This project builds an LLM-powered agent that bridges the **physical office environment** (presence detection, temperature, CO₂, lighting via WoT IoT) and **digital workspace** (calendar, weather, desktop, Slack) into a unified **Mixed-Reality Cognitive Map**.

The agent autonomously orchestrates cross-reality task chains — e.g., detecting a user's arrival, checking the calendar for upcoming meetings, pre-cooling the room via WoT thermostat, and restoring the desktop session — all without disrupting the user's workflow.

---

## Research Contribution

We extend three lines of existing work:

| Contribution | Extends |
|---|---|
| Physical Scene Parser | OmniParser V1 methodology → physical domain |
| Mixed-Reality Cognitive Map | Gidey (2025) Cognitive Map → fuses physical + digital |
| PhysicalAgent | UFO2 AppAgent → first-class physical endpoint |
| Mixed-Reality Blackboard | UFO2 Blackboard → includes physical sensor state |
| WoT Events as Reflex Triggers | icsa2026Gidey Reflex loop → physical interrupts |
| Reality-Tagged Task DAG | UFO3 TaskConstellation → adds `reality_domain` |
| Physical-to-Digital Affordance Bridge | Gidey (2025) WoT pattern → camera-triggered discovery |

---

## Key Papers

- Gidey et al. (2025) — *Affordance Representation and Recognition for Autonomous Agents*
- Gidey et al. (2026) — *A Pattern Language for Resilient Visual Agents* (ICSA 2026)
- Zhang et al. (2026) — *UFO2: The Desktop AgentOS*
- Zhang et al. (2025) — *UFO3: Weaving the Digital Agent Galaxy*
- Lu et al. (2024) — *OmniParser for Pure Vision Based GUI Agent*
- Sager et al. (2026) — *A Comprehensive Survey of Agents for Computer Use*
- W3C (2025) — *Web of Things (WoT) Thing Description 2.0*
- W3C (2026) — *Web of Things (WoT): Use Cases and Requirements*

---

## Repository Structure

```
├── docs/
│   └── specs/
│       └── 2026-05-12-smart-office-mixed-reality-agent-design.md  ← Start here
├── src/          (coming soon)
└── README.md
```

---

## Architecture (Overview)

```
Perception Layer
├── Physical Scene Parser    (camera → structured entities)
├── DOM Transducer           (web → Page Affordance Model)
├── Hybrid Desktop Detector  (UIA + OmniParser)
└── WoT Affordance Parser    (Thing Descriptions + Events)
        ↓
Mixed-Reality Cognitive Map  (unified world model)
        ↓
Reflex / Supervisor
├── Reflex Loop   (WoT Events + UI triggers → fast rules)
└── LLM Supervisor (cross-reality reasoning → Task DAG)
        ↓
Agent Execution Layer
├── HostAgent      (Mixed-Reality Orchestrator)
├── AppAgents      (Chrome, Desktop, Slack)
└── PhysicalAgent  (WoT HTTP/MQTT executor)  ← NEW
```

---

## Getting Started

### Prerequisites

- [Anaconda](https://www.anaconda.com/download) or Miniconda
- Python 3.11
- Node.js ≥ 18 (for WoT device simulation)

### 1. Create the Python environment

```bash
conda create -n smart-office python=3.11 -y
conda activate smart-office
```

### 2. Install Python dependencies

```bash
pip install aiohttp anthropic pytest pytest-asyncio
```

> `ultralytics` and `opencv-python` (listed in `requirements.txt`) are only needed
> for real camera mode. Skip them during development — mock mode works without them.

### 3. Install Node-WoT simulation dependencies

```bash
cd simulation/wot
npm install
cd ../..
```

### 4. Set environment variables

```bash
export ANTHROPIC_API_KEY="your-key-here"   # required for LLM Supervisor
# Optional overrides (defaults shown):
export WOT_BASE_URL="http://localhost"
export CAMERA_INDEX="-1"                   # -1 = mock mode, no real camera
```

---

### Running the tests

```bash
# Activate the environment first
conda activate smart-office

# Run all unit tests
python -m pytest tests/ --ignore=tests/integration --ignore=tests/evaluation -v

# Run a single test file
python -m pytest tests/test_nodes.py -v
```

### Running the agent (mock mode)

Start the WoT device simulators in one terminal:

```bash
conda activate smart-office
cd simulation/wot
node thermostat.js & node lights.js & node co2_sensor.js & node ventilation.js &
```

Run the agent in another terminal:

```bash
conda activate smart-office
python -m src.main --mock
```

### Running integration tests

Requires the WoT simulators to be running (see above).

```bash
python -m pytest tests/integration/ -v -m integration
```

### Running the evaluation baseline

```bash
python -m tests.evaluation.runner
```

---

> Full design specification: [`docs/specs/`](docs/specs/)

---

## Team

| Person | Module |
|--------|--------|
| P1 | Perception Layer (Physical Scene Parser + WoT Affordance Parser) |
| P2 | World Model + LLM Planner (Cognitive Map + Task DAG) |
| P3 | Execution Layer + Evaluation (PhysicalAgent + AppAgents + eval) |
