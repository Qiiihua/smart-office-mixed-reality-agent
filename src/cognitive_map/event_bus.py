"""
event_bus.py — Asyncio pub/sub event bus for the Smart Office Agent.

The EventBus decouples event producers (WoT devices, camera) from event
consumers (Reflex Loop, Supervisor) so neither side needs to know about
the other directly.

Usage:
    bus = EventBus()

    # Subscriber side
    async def on_co2(event: Event):
        print(f"CO2 level: {event.data['ppm']} ppm")

    bus.subscribe("co2_exceeded", on_co2)

    # Producer side
    await bus.publish(Event(type="co2_exceeded", data={"ppm": 1200}, source="co2_sensor"))
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

# A handler can be either a plain function or a coroutine function
Handler = Callable[["Event"], Any]


@dataclass
class Event:
    """
    A single event published on the bus.

    Attributes:
        type      : Event identifier, e.g. "co2_exceeded", "presence"
        data      : Arbitrary payload dict — content depends on event type
        source    : ID of the component that produced the event
        timestamp : Unix time when the event was created (set automatically)
    """

    type: str
    data: dict[str, Any]
    source: str
    timestamp: float = field(default_factory=time.time)


class EventBus:
    """
    Simple asyncio pub/sub bus.

    - subscribe() registers a handler for a given event type.
    - publish() delivers the event to all registered handlers concurrently.
    - Both sync and async handlers are supported.
    - Publishing to an event type with no subscribers is a no-op.
    """

    def __init__(self) -> None:
        # Maps event_type → list of handler callables
        self._handlers: dict[str, list[Handler]] = {}

    def subscribe(self, event_type: str, handler: Handler) -> None:
        """Register `handler` to be called whenever `event_type` is published."""
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, event: Event) -> None:
        """
        Deliver `event` to all subscribers registered for its type.

        Async handlers are gathered and awaited concurrently.
        Sync handlers are called inline (they are expected to be fast).
        """
        handlers = self._handlers.get(event.type, [])
        if not handlers:
            return

        coros = []
        for handler in handlers:
            result = handler(event)
            if asyncio.iscoroutine(result):
                coros.append(result)

        if coros:
            await asyncio.gather(*coros)
