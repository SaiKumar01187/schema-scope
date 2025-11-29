from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class FieldDef(BaseModel):
    name: str
    type: Optional[str] = None
    required: bool = False
    pii: bool = False
    description: Optional[str] = None


class SchemaEntity(BaseModel):
    name: str
    entity_type: str  # "table", "event", "contract"
    fields: List[FieldDef] = Field(default_factory=list)

    # For dependency graph
    upstream: List[str] = Field(default_factory=list)
    downstream: List[str] = Field(default_factory=list)

    # For RAG text representation
    raw_text: Optional[str] = None

    def to_document_text(self) -> str:
        """Convert the entity to a plain text document for embeddings."""
        lines = [f"Entity: {self.name} ({self.entity_type})"]
        lines.append("Fields:")

        for f in self.fields:
            flags = []
            if f.required:
                flags.append("required")
            if f.pii:
                flags.append("PII")

            flags_text = f" [{' ,'.join(flags)}]" if flags else ""
            desc = f" - {f.description}" if f.description else ""

            lines.append(f"- {f.name}: {f.type}{flags_text}{desc}")

        if self.upstream:
            lines.append(f"Upstream: {', '.join(self.upstream)}")
        if self.downstream:
            lines.append(f"Downstream: {', '.join(self.downstream)}")

        return "\n".join(lines)

    # ----------------------------------------------------------------------
    # NEW: Impact Analysis Utilities
    # ----------------------------------------------------------------------

    def get_impacted_entities(self, all_entities: Dict[str, "SchemaEntity"]) -> List["SchemaEntity"]:
        """
        Return all entities directly impacted if *this* entity changes.
        This includes immediate upstream and downstream links.
        """
        impacted = set()

        # Upstream systems affected if this entity changes
        for u in self.upstream:
            if u in all_entities:
                impacted.add(all_entities[u])

        # Downstream systems affected
        for d in self.downstream:
            if d in all_entities:
                impacted.add(all_entities[d])

        return list(impacted)

    def get_full_lineage(self, all_entities: Dict[str, "SchemaEntity"]) -> Dict[str, List[str]]:
        """
        Returns full recursive upstream and downstream lineage.
        Useful for drawing lineage graphs or answering complex questions.
        """
        visited_up = set()
        visited_down = set()

        # Depth-first traversal
        def dfs_up(name):
            if name in visited_up:
                return
            visited_up.add(name)
            ent = all_entities.get(name)
            if ent:
                for parent in ent.upstream:
                    dfs_up(parent)

        def dfs_down(name):
            if name in visited_down:
                return
            visited_down.add(name)
            ent = all_entities.get(name)
            if ent:
                for child in ent.downstream:
                    dfs_down(child)

        dfs_up(self.name)
        dfs_down(self.name)

        visited_up.discard(self.name)
        visited_down.discard(self.name)

        return {
            "full_upstream": list(visited_up),
            "full_downstream": list(visited_down),
        }
