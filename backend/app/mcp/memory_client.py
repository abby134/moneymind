import json
import os
from pathlib import Path
from app.core.config import settings


def _get_memory_path(user_id: str) -> Path:
    base = Path(settings.memory_mcp_path).parent
    base.mkdir(parents=True, exist_ok=True)
    return base / f"user_{user_id}.json"


async def load_memory(user_id: str) -> str:
    """Load user's memory graph and return as formatted string for agent context."""
    path = _get_memory_path(user_id)

    if not path.exists():
        return "No previous financial history available. This is the first analysis."

    with open(path) as f:
        data = json.load(f)

    entities = data.get("entities", [])
    if not entities:
        return "No previous history found."

    lines = []
    for entity in entities:
        lines.append(f"\n[{entity['entityType'].upper()}] {entity['name']}")
        for obs in entity.get("observations", []):
            lines.append(f"  - {obs}")

    return "\n".join(lines)


async def save_memory(user_id: str, updates: list[dict]) -> None:
    """Persist new observations to the user's memory graph."""
    path = _get_memory_path(user_id)

    if path.exists():
        with open(path) as f:
            data = json.load(f)
    else:
        data = {"entities": [], "relations": []}

    entity_map = {e["name"]: e for e in data["entities"]}

    for update in updates:
        entity_name = f"{user_id}_{update['entity']}"
        obs = update["observation"]

        if entity_name in entity_map:
            existing_obs = entity_map[entity_name]["observations"]
            if obs not in existing_obs:
                existing_obs.append(obs)
                # Keep only last 20 observations per entity
                entity_map[entity_name]["observations"] = existing_obs[-20:]
        else:
            entity_map[entity_name] = {
                "name": entity_name,
                "entityType": update["entity"],
                "observations": [obs]
            }

    data["entities"] = list(entity_map.values())

    with open(path, "w") as f:
        json.dump(data, f, indent=2)
