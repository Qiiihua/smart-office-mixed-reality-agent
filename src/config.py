"""
config.py — Central configuration for the Smart Office Agent.

All environment variables and threshold constants are defined here.
Every other module should import from this file rather than defining
its own constants, so values can be changed in one place.
"""

import os

# ---------------------------------------------------------------------------
# WoT Device URLs
# Override WOT_BASE_URL to point at real hardware instead of the simulator.
# ---------------------------------------------------------------------------

WOT_BASE_URL = os.getenv("WOT_BASE_URL", "http://localhost")

THERMOSTAT_TD_URL = f"{WOT_BASE_URL}:3001/thermostat"
LIGHTS_TD_URL = f"{WOT_BASE_URL}:3002/lights"
CO2_SENSOR_TD_URL = f"{WOT_BASE_URL}:3003/co2sensor"
VENTILATION_TD_URL = f"{WOT_BASE_URL}:3004/ventilation"

# ---------------------------------------------------------------------------
# Physical thresholds
# ---------------------------------------------------------------------------

# CO₂ level (ppm) above which the Reflex Loop triggers ventilation
CO2_THRESHOLD_PPM: int = 1000

# How long (seconds) a person must be absent before the departure rule fires
ABSENCE_TIMEOUT_SEC: int = 180

# ---------------------------------------------------------------------------
# Temperature setpoints (°C)
# ---------------------------------------------------------------------------

# Comfortable working temperature
TEMP_COMFORT: float = 22.0

# Energy-saving temperature when the office is unoccupied
TEMP_STANDBY: float = 26.0

# Aggressive pre-cooling target on hot days with an upcoming video call
TEMP_AGGRESSIVE: float = 20.0

# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------

# OpenCV camera index. Set to -1 to use mock mode (no real camera required).
CAMERA_INDEX: int = int(os.getenv("CAMERA_INDEX", "-1"))

# ---------------------------------------------------------------------------
# LLM Supervisor (Anthropic Claude)
# ---------------------------------------------------------------------------

ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL: str = "claude-opus-4-5"
