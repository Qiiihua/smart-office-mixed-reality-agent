"""
Tests for the asyncio EventBus.

The EventBus must:
- Deliver published events to all subscribers of that event type
- Not deliver events to subscribers of a different event type
- Support multiple subscribers on the same event type
- Support both sync and async handler functions
"""

import asyncio
import pytest
from src.cognitive_map.event_bus import Event, EventBus


class TestSubscribeAndPublish:
    async def test_handler_is_called_on_matching_event(self):
        bus = EventBus()
        received = []

        async def handler(event: Event):
            received.append(event)

        bus.subscribe("co2_exceeded", handler)
        await bus.publish(Event(type="co2_exceeded", data={"ppm": 1200}, source="co2_sensor"))

        assert len(received) == 1
        assert received[0].data["ppm"] == 1200

    async def test_handler_is_not_called_for_different_event_type(self):
        bus = EventBus()
        received = []

        async def handler(event: Event):
            received.append(event)

        bus.subscribe("presence", handler)
        await bus.publish(Event(type="co2_exceeded", data={"ppm": 1200}, source="co2_sensor"))

        assert len(received) == 0

    async def test_multiple_subscribers_all_receive_event(self):
        bus = EventBus()
        received_a, received_b = [], []

        async def handler_a(event: Event):
            received_a.append(event)

        async def handler_b(event: Event):
            received_b.append(event)

        bus.subscribe("presence", handler_a)
        bus.subscribe("presence", handler_b)
        await bus.publish(Event(type="presence", data={"present": True}, source="camera"))

        assert len(received_a) == 1
        assert len(received_b) == 1

    async def test_sync_handler_is_also_supported(self):
        """EventBus must accept plain (non-async) handler functions."""
        bus = EventBus()
        received = []

        # Intentionally a sync function, not async
        def sync_handler(event: Event):
            received.append(event)

        bus.subscribe("temperature_reached", sync_handler)
        await bus.publish(Event(type="temperature_reached", data={"temp": 22.0}, source="thermostat"))

        assert len(received) == 1

    async def test_event_carries_correct_source(self):
        bus = EventBus()
        received = []

        async def handler(event: Event):
            received.append(event)

        bus.subscribe("co2_exceeded", handler)
        await bus.publish(Event(type="co2_exceeded", data={}, source="co2_sensor"))

        assert received[0].source == "co2_sensor"

    async def test_publish_with_no_subscribers_does_not_raise(self):
        """Publishing to an event type with no subscribers must silently succeed."""
        bus = EventBus()
        # No subscribers registered — should not raise any exception
        await bus.publish(Event(type="orphan_event", data={}, source="x"))

    async def test_event_timestamp_is_set_automatically(self):
        event = Event(type="presence", data={}, source="camera")
        assert event.timestamp > 0
