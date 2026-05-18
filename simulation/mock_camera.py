"""
mock_camera.py — Scripted async camera for testing without real hardware.

MockCamera is an async generator that yields PresenceFrame objects according
to a predefined script. Each script entry is (delay_seconds, present_bool).

This lets integration and unit tests simulate presence detection scenarios
without requiring a physical camera or running YOLOv8.

Usage:
    from simulation.mock_camera import MockCamera, SCENARIO_A_SCRIPT

    camera = MockCamera(script=SCENARIO_A_SCRIPT)
    async for frame in camera.stream():
        print(frame.present, frame.timestamp)
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass


@dataclass
class PresenceFrame:
    """A single camera frame reduced to a presence boolean."""

    present: bool    # True if a person is detected in this frame
    timestamp: float # Unix timestamp when the frame was captured


class MockCamera:
    """
    Async camera that yields scripted PresenceFrames.

    Each entry in the script is (delay_seconds, present):
      - delay_seconds : how long to wait before yielding this frame
      - present       : the presence value of the frame

    The generator ends after the last script entry.
    """

    def __init__(self, script: list[tuple[float, bool]]) -> None:
        self._script = script

    async def stream(self):
        """Yield PresenceFrames according to the script, with asyncio delays."""
        for delay, present in self._script:
            await asyncio.sleep(delay)
            yield PresenceFrame(present=present, timestamp=time.time())


# ---------------------------------------------------------------------------
# Pre-built scenario scripts
# ---------------------------------------------------------------------------

# Scenario A: user arrives and stays
# Used to test: presence detection → Supervisor → set temperature + lighting
SCENARIO_A_SCRIPT: list[tuple[float, bool]] = [
    (0.1, True),   # person appears after 0.1 s
]

# Scenario B: CO₂ interrupt — no camera involvement (WoT event only)
# MockCamera not needed for Scenario B; the event is injected directly.

# Scenario C: user leaves and returns
# Used to test: departure rules → standby mode → return → session restore
SCENARIO_C_SCRIPT: list[tuple[float, bool]] = [
    (0.1, True),   # person present
    (5.0, False),  # person leaves after 5 s
    (2.0, True),   # person returns after 2 more seconds
]
