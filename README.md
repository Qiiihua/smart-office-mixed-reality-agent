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

> Implementation in progress. See [`docs/specs/`](docs/specs/) for the full design specification.

---

## Team

| Person | Module |
|--------|--------|
| P1 | Perception Layer (Physical Scene Parser + WoT Affordance Parser) |
| P2 | World Model + LLM Planner (Cognitive Map + Task DAG) |
| P3 | Execution Layer + Evaluation (PhysicalAgent + AppAgents + eval) |
