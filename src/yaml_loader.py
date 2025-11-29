from pathlib import Path
from typing import List, Dict
import yaml

from src.schema_models import SchemaEntity, FieldDef


def load_yaml_entities(path: str = "data/schemas") -> List[SchemaEntity]:
    """Load all SchemaEntity objects from YAML files in the given folder."""
    base = Path(path)
    entities: List[SchemaEntity] = []

    # Load all YAML definitions
    for file in base.glob("*.yml"):
        with file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        raw_entities = data.get("entities", [])
        for e in raw_entities:
            # Parse fields
            fields = []
            for fdef in e.get("fields", []):
                fields.append(
                    FieldDef(
                        name=fdef["name"],
                        type=fdef.get("type"),
                        required=bool(fdef.get("required", False)),
                        pii=bool(fdef.get("pii", False)),
                        description=fdef.get("description"),
                    )
                )

            # Create SchemaEntity
            entity = SchemaEntity(
                name=e["name"],
                entity_type=e.get("entity_type", "table"),
                fields=fields,
                upstream=e.get("upstream", []),
                downstream=e.get("downstream", []),
            )

            # Initial document text
            entity.raw_text = entity.to_document_text()

            entities.append(entity)

    # -----------------------------
    # SECOND PASS: Build lineage graph context
    # -----------------------------
    entity_dict: Dict[str, SchemaEntity] = {e.name: e for e in entities}

    for entity in entities:
        upstream = entity.upstream or ["None"]
        downstream = entity.downstream or ["None"]

        impact_text = f"""
Impact Analysis for {entity.name}:

Upstream systems: {", ".join(upstream)}
Downstream systems: {", ".join(downstream)}

"""

        # Append lineage info to raw text for better RAG retrieval
        entity.raw_text += "\n\n" + impact_text

    return entities
