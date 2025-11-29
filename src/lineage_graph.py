import sys
from pathlib import Path
from typing import List, Optional

import networkx as nx
from pyvis.network import Network

from src.yaml_loader import load_yaml_entities
from src.schema_models import SchemaEntity


def build_lineage_graph(
    entities: List[SchemaEntity],
    focus_entity: Optional[str] = None,
    output_path: str = "lineage.html",
) -> None:
    """
    Build an interactive lineage graph and save it as an HTML file.
    - Nodes: schema entities (tables, events, etc.)
    - Edges: upstream -> downstream dependencies
    """

    # Map name -> entity for quick lookup
    entity_dict = {e.name: e for e in entities}

    # Build a directed graph
    G = nx.DiGraph()

    # Add nodes
    for e in entities:
        label = f"{e.name}\n({e.entity_type})"

        # Choose color based on type
        if e.entity_type.lower() == "table":
            color = "#1f77b4"  # blue
        elif e.entity_type.lower() == "event":
            color = "#ff7f0e"  # orange
        else:
            color = "#2ca02c"  # green

        # Highlight focus entity
        if focus_entity and e.name == focus_entity:
            color = "#d62728"  # red

        G.add_node(
            e.name,
            label=label,
            color=color,
            title=e.raw_text or e.to_document_text(),
        )

    # Add edges from upstream -> this entity
    for e in entities:
        for upstream_name in e.upstream:
            if upstream_name in entity_dict:
                G.add_edge(upstream_name, e.name)

    # Create a PyVis network (nice interactive HTML)
        net = Network(
        height="700px",
        width="100%",
        directed=True,
        bgcolor="#111111",
        font_color="white",
    )

    net.from_nx(G)

    # Enable slider-like physics for nicer layout
    net.toggle_physics(True)

    # Save to HTML (no auto-open, no notebook mode)
    out_path = Path(output_path)
    net.write_html(str(out_path), open_browser=False)

    print(f"Lineage graph saved to: {out_path.resolve()}")



def main():
    # Load entities from YAML
    entities = load_yaml_entities("data/schemas")

    # Optional: focus entity name from command line
    focus = sys.argv[1] if len(sys.argv) > 1 else None

    build_lineage_graph(
        entities=entities,
        focus_entity=focus,
        output_path="lineage.html",
    )


if __name__ == "__main__":
    main()
