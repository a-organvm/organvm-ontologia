from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ontologia.entity.identity import EntityIdentity
    from ontologia.registry.store import RegistryStore


def search_entities(query: str, store: RegistryStore) -> list[EntityIdentity]:
    """Search for entities by partial or fuzzy name matching.

    Matches against both current and historical names.
    Results are sorted by relevance:
      1. Exact match (case-insensitive)
      2. Prefix match (case-insensitive)
      3. Substring match (case-insensitive)

    Args:
        query: The search string.
        store: The registry store to search within.

    Returns:
        List of matching EntityIdentity objects.
    """
    if not query:
        return []

    query_lower = query.lower()
    best_scores: dict[str, int] = {}

    name_index = store._name_index
    for entity_id, records in name_index._by_entity.items():
        score = 4
        for record in records:
            name_lower = record.display_name.lower()
            if name_lower == query_lower:
                score = min(score, 1)
            elif name_lower.startswith(query_lower):
                score = min(score, 2)
            elif query_lower in name_lower:
                score = min(score, 3)

        if score < 4:
            best_scores[entity_id] = score

    # Sort by score, then by entity_id for stable sorting
    sorted_ids = sorted(best_scores.keys(), key=lambda eid: (best_scores[eid], eid))

    results = []
    for eid in sorted_ids:
        entity = store.get_entity(eid)
        if entity:
            results.append(entity)

    return results
