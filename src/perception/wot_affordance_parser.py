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