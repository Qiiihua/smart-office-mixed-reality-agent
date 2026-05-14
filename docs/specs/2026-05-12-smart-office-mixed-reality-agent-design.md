# Smart Office Mixed-Reality Agent — Design Specification

**Date:** 2026-05-12  
**Course:** Masterpraktikum SS26 — Autonomous Agents, TUM  
**Team:** 3 persons, 1 semester  
**Advisor:** Habtom Kahsay Gidey, Alexander Lenz, Alois Knoll (TUM)

---

## 1. Problem Statement

### 1.1 What Exists Today

Current Computer-Using Agents (CUAs) — such as UFO2 (Zhang et al., 2026) — operate exclusively in the **digital domain**: they perceive GUI screenshots, accessibility trees, and DOM structures, and execute keyboard/mouse actions on web browsers and desktop applications. The observation space is defined as `{screenshot, DOM, A11y tree}`.

Similarly, affordance-based world models (Gidey et al., 2025) construct a **Cognitive Map** from structured digital inputs (DOM trees, WoT Thing Descriptions accessed via web hyperlinks) but explicitly exclude physical sensor streams: *"Vision is excluded; only structured inputs are considered."*

### 1.2 The Gap

Three concrete research gaps motivate this project:

1. **Physical blindness of CUAs** — Sager et al. (2026) identify a *"mismatch between the assumptions regarding ACUs and their operational environments made during research and the actual conditions encountered during real-world deployment."* Real office environments include presence, temperature, CO₂, and lighting — none of which enter the agent's world model today, representing an instance of this broader deployment gap.

2. **No physical-digital world model fusion** — Agentic World Modeling (Chu et al., 2025) treats physical and digital world models as separate research tracks (L2 Simulator: Physical World vs. Digital World) with no fusion framework.

3. **No physical agent in desktop AgentOS** — UFO2's HostAgent + AppAgent hierarchy has no concept of a physical endpoint. IoT devices are not first-class citizens alongside desktop applications.

### 1.3 Research Question

> How can a CUA agent integrate physical sensory streams (presence, temperature, CO₂, lighting) with digital context (calendar, weather, desktop state) into a unified Mixed-Reality Cognitive Map, and use it to orchestrate coherent cross-reality task execution in a Smart Office environment?

---

## 2. Use Case: Smart Office Agent

### 2.1 Overview

A user works in an office equipped with:
- **Physical sensors** (via WoT): thermostat, smart lights, CO₂ sensor, ventilation, door/presence sensor
- **Digital applications**: calendar (web), weather API (web), desktop (lock/unlock), Slack (status)

The agent continuously perceives both physical and digital state, maintains a unified world model, and autonomously orchestrates environment comfort and digital workspace — triggered by presence events, WoT sensor events, and scheduled digital context (calendar).

### 2.2 Scenario Walkthroughs

#### Scenario A: User Arrives

```
08:52 — Camera detects person=present
│
├── [Physical Scene Parser]   person=present, monitor=detected
├── [WoT Affordance Parser]   thermostat{temp:28°C}, lights{off}, CO₂{420ppm}
├── [AppAgent: Chrome]        Calendar → 10:00 video call (2h), 14:00 1:1
├── [AppAgent: Weather API]   Today max 36°C, hot outdoor
│
│   ← LLM Supervisor reasons over Mixed-Reality Cognitive Map:
│     "Hot day + video call at 10:00 → aggressive pre-cooling + video lighting"
│
├── [PhysicalAgent → WoT]     setTemperature(20°C)
├── [PhysicalAgent → WoT]     setLighting("focus-mode", brightness=80%)
├── [AppAgent: Desktop]       unlock screen, restore last session  [PiP background]
└── [AppAgent: Slack]         set status → "In Office 🟢"
```

#### Scenario B: WoT Event Interrupt

```
09:45 — WoT Event pushed: "CO₂ExceededThreshold" (1200ppm)
│
│   ← Reflex loop: rule match → immediate execution
├── [PhysicalAgent → WoT]     ventilation(on)
└── [AppAgent: Desktop]       desktop notification: "Ventilation activated, CO₂: 1200ppm"

09:58 — WoT Event pushed: "temperatureReached" (22°C)
│
│   ← Reflex: approaching video call
├── [PhysicalAgent → WoT]     setLighting("video-call-mode")
└── [AppAgent: Chrome]        surface calendar tab with meeting link
```

#### Scenario C: User Leaves and Returns

```
17:30 — Camera: person=absent (sustained 3 min)
│
│   ← Reflex: departure rules
├── [PhysicalAgent → WoT]     setTemperature(26°C), lights(off)
├── [AppAgent: Desktop]       lock screen, save session snapshot → Blackboard
└── [AppAgent: Slack]         set status → "Left Office 🔴"

17:34 — Camera: person=present again
│
│   ← Supervisor: Blackboard has snapshot → restore
├── [PhysicalAgent → WoT]     resume temperature target 22°C
├── [AppAgent: Desktop]       unlock, restore previous window layout
└── Notification: "Welcome back — environment restored"
```

---

## 3. System Architecture

### 3.1 Layer Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                         PERCEPTION LAYER                              │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │ Physical Scene   │  │  DOM Transducer  │  │  Hybrid Desktop  │   │
│  │ Parser [NEW]     │  │ (Gidey 2025)     │  │  Detector (UFO2) │   │
│  │ Camera frame →   │  │ Web → Page       │  │  UIA Tree +      │   │
│  │ {person, device} │  │ Affordance Model │  │  OmniParser V1   │   │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘   │
│           │                     │                      │             │
│           ▼                     │                      │             │
│  ┌──────────────────────────┐   │                      │             │
│  │  WoT Affordance Parser   │   │                      │             │
│  │  (Gidey 2025 + WoT TD2.0)│   │                      │             │
│  │  TD→{Prop, Action, Event}│   │                      │             │
│  │  WoT Events→async signals│   │                      │             │
│  └──────────────┬───────────┘   │                      │             │
│                 └───────────────┴──────────────────────┘             │
│                                 ▼                                     │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Unified Affordance Catalog                                    │  │
│  │  {Physical, Web, Desktop} → single queryable affordance space  │  │
│  └────────────────────────────────┬───────────────────────────────┘  │
└───────────────────────────────────│──────────────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 MIXED-REALITY COGNITIVE MAP                          │
│         (extends Gidey 2025 Cognitive Map + UFO2 Blackboard)        │
│                                                                      │
│   Physical Layer         IoT Layer            Digital Layer         │
│  ┌───────────────┐   ┌───────────────────┐  ┌──────────────────┐   │
│  │ Room {        │   │ Thermostat[TD] {  │  │ Calendar {       │   │
│  │  presence: ✓  │   │  temp: 28→20°C }  │  │  10:00 videocall │   │
│  │  CO₂: 420ppm  │   │ Lights[TD] {      │  │  14:00 1:1 }     │   │
│  │  time: 08:52  │   │  mode: focus }    │  │ Weather {36°C}   │   │
│  │ }             │   │ Ventilation[TD]   │  │ Desktop {        │   │
│  └───────────────┘   └───────────────────┘  │  locked: false } │   │
│                                             └──────────────────┘   │
│  Unified Mixed-Reality Scene Graph (extends icsa2026Gidey)          │
│  → physical entities + GUI elements share one queryable interface   │
└─────────────────────────────────┬───────────────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    REFLEX / SUPERVISOR                               │
│                    (icsa2026Gidey pattern language)                  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Reflex Loop (System 1)  — target < 50ms                     │   │
│  │  Triggers: WoT Events (physical) + UI state change (digital) │   │
│  │  "person=present"     → unlock screen      [rule: clear]     │   │
│  │  "CO₂ exceeded"       → ventilation on     [rule: clear]     │   │
│  │  "temp reached"       → lighting update    [rule: clear]     │   │
│  └──────────────────────────┬─────────────────────────────────┘    │
│                             │ no clear rule / cross-reality conflict │
│                             ▼                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  LLM Supervisor (System 2) — cross-reality reasoning         │   │
│  │  Input:  Mixed-Reality Cognitive Map snapshot                 │   │
│  │  Output: Reality-Tagged Task DAG  (extends UFO3)             │   │
│  │  { task: "pre-cool",      domain: "physical", deps: [] }     │   │
│  │  { task: "check_calendar",domain: "digital",  deps: [] }     │   │
│  │  { task: "set_lighting",  domain: "physical",                │   │
│  │    deps: ["check_calendar"] }  ← physical depends on digital  │   │
│  └──────────────────────────┬─────────────────────────────────┘    │
└─────────────────────────────│───────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENT EXECUTION LAYER                             │
│              (extends UFO2 HostAgent + AppAgent hierarchy)           │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  HostAgent (Mixed-Reality Orchestrator)                     │     │
│  │  • Maintains Mixed-Reality Blackboard                       │     │
│  │  • Dispatches Reality-Tagged Tasks to correct agent type    │     │
│  │  • Manages cross-reality dependencies                       │     │
│  └──────────┬────────────────────────┬──────────────────────┘      │
│             │                        │                               │
│  ┌──────────▼──────────┐  ┌──────────▼───────────────────────┐     │
│  │  AppAgents (UFO2)   │  │  PhysicalAgent [NEW]              │     │
│  │  Chrome (calendar,  │  │  • WoT HTTP / MQTT execution      │     │
│  │    weather)         │  │  • Subscribes to WoT Events(TD2.0)│     │
│  │  Desktop (lock/     │  │  • Writes sensor state to         │     │
│  │    unlock, session) │  │    Blackboard in real-time        │     │
│  │  Slack (status)     │  │  • Serves Reflex loop directly    │     │
│  │  ─────────────────  │  └───────────────────────────────────┘     │
│  │  Hybrid Detection:  │                                             │
│  │  UIA + OmniParser   │   Non-disruptive: PiP virtual desktop (UFO2)│
│  └─────────────────────┘                                             │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

1. **Perception** → Physical Scene Parser + DOM Transducer + Hybrid Desktop Detector + WoT Affordance Parser all write into the **Mixed-Reality Cognitive Map** (Blackboard).
2. **WoT Events** arrive asynchronously and are pushed directly to the **Reflex Loop**.
3. **Reflex Loop** handles clear-rule cases immediately. Ambiguous or cross-reality situations escalate to **LLM Supervisor**.
4. **LLM Supervisor** reads the full Cognitive Map snapshot and produces a **Reality-Tagged Task DAG**.
5. **HostAgent** schedules the DAG, dispatching digital tasks to **AppAgents** and physical tasks to **PhysicalAgent**.
6. Execution results are written back to the **Blackboard**, closing the loop.

---

## 4. Key Components

### 4.1 Physical Scene Parser (New Contribution)

**Inspiration:** OmniParser V1 (Lu et al., 2024) parses GUI screenshots into structured `{element_id, type, bbox, semantic_label}` lists. We apply the same methodology to the physical domain.

**Input:** Camera frame (RGB)  
**Output:** Structured physical entity list, e.g.:
```json
{
  "entities": [
    {"id": "p1", "type": "person", "state": "present", "confidence": 0.94},
    {"id": "d1", "type": "monitor", "state": "off"},
    {"id": "d2", "type": "thermostat", "wot_discovery_hint": true}
  ]
}
```

**Pipeline:**
1. Object detection (YOLOv8 fine-tuned or zero-shot with Grounding DINO)
2. State classification per entity (present/absent, on/off)
3. WoT discovery hint: if a known device type is detected, trigger WoT TDD lookup for its Thing Description

**Novel aspect:** The `wot_discovery_hint` bridges physical observation to digital affordance discovery — the Physical-to-Digital Affordance Bridge pattern, the inverse of Gidey's web-hyperlink-based WoT discovery.

### 4.2 Mixed-Reality Cognitive Map

**Extension of:** Gidey (2025) Cognitive Map + UFO2 Blackboard

**Structure:** A unified graph with four node types:

| Node Type | Source | Example |
|-----------|--------|---------|
| Physical Entity | Physical Scene Parser | `Room{presence, CO₂, time}` |
| IoT Affordance | WoT Affordance Parser | `Thermostat{currentTemp, setTemperature(), tempReached[event]}` |
| Web Affordance | DOM Transducer | `CalendarApp{events[], bookSlot()}` |
| Desktop State | Hybrid Detector (UIA+OmniParser) | `Desktop{locked, activeApps[], sessionSnapshot}` |

**Key property:** All node types are addressable through a single query interface. The LLM Supervisor can ask: *"What is the current room temperature?"* and *"What is the next calendar event?"* using identical API calls.

### 4.3 PhysicalAgent (New Contribution)

**Extension of:** UFO2 AppAgent pattern, made physical.

**Responsibilities:**
- Parse WoT Thing Descriptions from the Cognitive Map affordance catalog
- Execute WoT Actions via HTTP/MQTT Protocol Bindings (WoT TD 2.0)
- Subscribe to WoT Events and push them to the Reflex loop interrupt bus
- Write real-time sensor Property values back to the Blackboard

**Interface with HostAgent:**
```json
{
  "task": "setTemperature",
  "domain": "physical",
  "target": "thermostat_roomA",
  "parameters": {"value": 20, "unit": "°C"}
}
```

### 4.4 Reality-Tagged Task DAG (New Contribution)

**Extension of:** UFO3 TaskConstellation (Zhang et al., 2025)

UFO3 TaskStars have a `device` field (which digital device executes the task). We add a `reality_domain` attribute that explicitly marks each task node:

```json
{
  "constellation": [
    {"id": "t1", "task": "check_calendar", "domain": "digital",   "deps": []},
    {"id": "t2", "task": "check_weather",  "domain": "digital",   "deps": []},
    {"id": "t3", "task": "set_temperature","domain": "physical",  "deps": ["t1","t2"]},
    {"id": "t4", "task": "set_lighting",   "domain": "physical",  "deps": ["t1"]},
    {"id": "t5", "task": "unlock_screen",  "domain": "digital",   "deps": []}
  ]
}
```

Cross-reality dependencies are explicit: physical task `t3` waits for digital tasks `t1` and `t2` before executing, ensuring the temperature strategy is informed by calendar and weather context.

### 4.5 Reflex / Supervisor Architecture

**Source:** icsa2026Gidey pattern language, extended to physical triggers.

| Trigger Source | Type | Handler |
|----------------|------|---------|
| WoT Event: `CO₂ExceededThreshold` | Physical interrupt | Reflex (clear rule) |
| WoT Event: `temperatureReached` | Physical interrupt | Reflex (clear rule) |
| Camera: `person=present` | Physical interrupt | Reflex (clear rule) |
| Camera: `person=absent` (3 min) | Physical interrupt | Reflex (clear rule) |
| Calendar: meeting in 5 min | Digital poll | Supervisor (context-dependent) |
| `person=present` + no calendar + late hour | Cross-reality ambiguity | Supervisor |

**Cost model (from icsa2026Gidey):**
```
Avg_Cost = Cost_Reflex + (P_exception × Cost_Supervisor)
```
Most presence/departure events hit Reflex (< 50ms). Supervisor is invoked only for ambiguous cross-reality situations (~5% of events), keeping average latency low.

---

## 5. Team Responsibilities

| Person | Module | Key Deliverable |
|--------|--------|-----------------|
| **P1** | Perception Layer | Physical Scene Parser (camera → structured entities), WoT Affordance Parser (TD → affordance catalog + Events subscription) |
| **P2** | World Model + Planner | Mixed-Reality Cognitive Map (unified graph), LLM Supervisor (cross-reality reasoning), Reality-Tagged Task DAG generation |
| **P3** | Execution Layer + Evaluation | PhysicalAgent (WoT HTTP/MQTT), AppAgent integration (UFO2), Reflex loop, Evaluation pipeline |

**Integration point:** The Mixed-Reality Cognitive Map (Blackboard) is the shared state between all three modules. P1 writes to it, P2 reads from and reasons over it, P3 executes and writes results back.

---

## 6. Technology Stack

| Component | Technology |
|-----------|------------|
| Physical Scene Parser | Python, YOLOv8 / Grounding DINO, OpenCV |
| WoT Affordance Parser | Node-WoT (node-wot npm), Python `requests` |
| IoT Simulation | Node-WoT servient (simulated thermostat, lights, CO₂) |
| Mixed-Reality Cognitive Map | Python, NetworkX or in-memory dict + Redis |
| LLM Supervisor | Claude / GPT-4o via API, LangChain |
| AppAgents (Desktop) | UFO2 framework (Python), pyautogui, Playwright |
| AppAgents (Web) | Playwright, OmniParser V1 (screen parsing) |
| Reflex Loop | Python asyncio event bus |
| HostAgent | Python, adapted from UFO2 HostAgent |
| Evaluation | Python scripts, LLM-based evaluator (UFO2 pattern) |

---

## 7. Evaluation Plan

### 7.1 Baseline
A rule-based system (traditional smart office automation): hardcoded `if presence → adjust temperature` rules, no cross-reality reasoning, no dynamic WoT discovery.

### 7.2 Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Task Completion Rate** | % of cross-reality task chains fully completed correctly (standard agent benchmark metric \[ufo2, cuAgentsSurvey2026\]) | > 80% |
| **Cross-Reality Coordination Accuracy** | Physical and digital actions correctly aligned (e.g., temperature strategy matches calendar) \[icsa2026Gidey\] | > 75% |
| **Reflex Latency** | Time from WoT Event push to physical action executed; reflex rule target < 50 ms \[icsa2026Gidey\] | < 500ms |
| **Supervisor Latency** | Time from ambiguous trigger to full Task DAG executed \[ufo2, ufo3\] | < 15s |
| **Affordance Discovery Time** | New WoT device added → agent integrates without code change via dynamic TD discovery \[WoTTD2\] | < 30s |
| **Non-disruption** | % of digital tasks executed in PiP without visible interruption \[ufo2\] | 100% |

### 7.3 Test Scenarios
1. Standard arrival (hot day + morning meeting)
2. Standard departure and unexpected return
3. CO₂ interrupt during active digital task
4. New WoT device hot-plugged (zero-shot discovery)
5. Conflicting signals (calendar says "focus block" but person detected absent)

---

## 8. Novel Contributions Summary

| Contribution | Extends | Gap Filled |
|---|---|---|
| **Physical Scene Parser** | OmniParser V1 methodology | Physical domain has no structured affordance parser |
| **Mixed-Reality Cognitive Map** | Gidey (2025) Cognitive Map | Digital-only world model |
| **Mixed-Reality Scene Graph** | icsa2026Gidey Scene Graph | GUI-only scene graph |
| **PhysicalAgent** | UFO2 AppAgent | No physical endpoints in desktop AgentOS |
| **Mixed-Reality Blackboard** | UFO2 Blackboard | Digital-only shared state |
| **WoT Events as Reflex Triggers** | icsa2026Gidey Reflex loop | Physical interrupts not in agent loop |
| **Reality-Tagged Task DAG** | UFO3 TaskConstellation | No reality_domain in task scheduling |
| **Physical-to-Digital Affordance Bridge** | Gidey (2025) WoT pattern | Discovery only web-hyperlink-driven |

---

## 9. Paper Reference Map

| Paper | Role in Project |
|-------|----------------|
| Gidey et al. (2025) — *Affordance Representation* | DOM Transducer, WoT Affordance Parser, Cognitive Map baseline |
| Gidey et al. (2026) — *Resilient Visual Agents* (icsa2026) | Reflex/Supervisor architecture, Scene Graph, Hybrid Affordance Integration |
| Gidey et al. (2023) — *Towards Cognitive Bots* (AGI2023) | Conceptual foundation: affordance-based cognition |
| Lu et al. (2024) — *OmniParser V1* | Methodology for Physical Scene Parser; digital GUI parsing |
| Zhang et al. (2026) — *UFO2: Desktop AgentOS* | HostAgent+AppAgent hierarchy, Blackboard, PiP, Hybrid Detection |
| Zhang et al. (2025) — *UFO3* | TaskConstellation DAG → Reality-Tagged Task DAG |
| Chu et al. (2025) — *Agentic World Modeling* | L1/L2/L3 framework; physical-digital fusion gap |
| Sager et al. (2026) — *CUA Survey* | Research gap: practical disconnect; CUA observation space |
| Nguyen et al. (2025) — *GUI Agents Survey* | POMDP formalization of agent-environment interaction |
| W3C (2025) — *WoT Thing Description 2.0* | Formal standard for IoT affordances; Events spec |
| W3C (2026) — *WoT Use Cases & Requirements* | Smart Building use cases 3.2.4 / 3.3.2 / 3.3.3 validate scenario |
| Yu et al. (2025) — *OmniParser V2* | Visual parsing generality (background reference) |

---

## 10. Open Questions (for team to resolve)

1. **Physical Scene Parser granularity**: Do we need person *identity* (multi-person office) or just presence? Identity adds complexity but enables personalization.
2. **LLM Supervisor frequency**: Event-driven (only on triggers) or periodic polling (every N seconds)? Trade-off: responsiveness vs. API cost.
3. **WoT simulation fidelity**: Use Node-WoT simulator or integrate real hardware (if available in lab)? Simulator is lower risk for semester timeline.
4. **Session snapshot format**: What does "restore last session" mean concretely? Browser tabs only, or full OS window layout?
5. **Security boundary**: WoT TD 2.0 defines security schemes. Should the prototype implement OAuth2/Bearer or use no-auth for simplicity?
