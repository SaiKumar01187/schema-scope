from pathlib import Path
from typing import Dict, Set, List
import yaml

import sqlglot
from sqlglot import exp


def extract_lineage_from_sql(sql_text: str) -> Dict[str, Set[str]]:
    """
    Very simple lineage extractor.

    Looks for statements like:
      CREATE VIEW target AS SELECT ... FROM src1 JOIN src2 ...

    Returns: { target_name: {src1, src2, ...}, ... }
    """
    lineage: Dict[str, Set[str]] = {}

    # Parse SQL into expressions
    expressions = sqlglot.parse(sql_text)

    for expression in expressions:
        # We only handle CREATE VIEW / CREATE TABLE AS SELECT for now
        if isinstance(expression, exp.Create) and isinstance(
            expression.this, exp.Table
        ):
            target_table = expression.this.name  # view/table being created

            # find all source tables in the SELECT part
            # expression.find_all(exp.Table) will include the target itself,
            # so we filter that out
            sources: Set[str] = set()
            for table in expression.find_all(exp.Table):
                name = table.name
                if name and name != target_table:
                    sources.add(name)

            if target_table not in lineage:
                lineage[target_table] = set()

            lineage[target_table].update(sources)

    return lineage


def build_yaml_entities_from_lineage(
    lineage: Dict[str, Set[str]]
) -> List[dict]:
    """
    Convert lineage mapping into YAML 'entities' list.
    We don't infer fields here, only upstream/downstream.
    """
    # First, build upstream list
    entities: Dict[str, dict] = {}
    for target, sources in lineage.items():
        # ensure entity exists
        ent = entities.setdefault(
            target,
            {
                "name": target,
                "entity_type": "view",  # default, you can tweak
                "upstream": [],
                "downstream": [],
                "fields": [],
            },
        )
        ent["upstream"] = sorted(list(set(ent["upstream"]).union(sources)))

        # for each source, add downstream info
        for s in sources:
            src_ent = entities.setdefault(
                s,
                {
                    "name": s,
                    "entity_type": "table",  # guess
                    "upstream": [],
                    "downstream": [],
                    "fields": [],
                },
            )
            if target not in src_ent["downstream"]:
                src_ent["downstream"].append(target)

    return list(entities.values())


def generate_lineage_yaml_from_folder(
    sql_folder: str = "sql", output_path: str = "data/schemas/sql_lineage.yml"
) -> None:
    """
    Read all .sql files in a folder, extract simple lineage,
    and write a YAML file compatible with your existing loader.
    """
    base = Path(sql_folder)
    all_sql = ""

    for file in base.glob("*.sql"):
        all_sql += file.read_text(encoding="utf-8") + "\n"

    if not all_sql.strip():
        print("No SQL found in folder:", sql_folder)
        return

    lineage = extract_lineage_from_sql(all_sql)
    entities = build_yaml_entities_from_lineage(lineage)

    data = {"entities": entities}

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    print(f"Wrote lineage YAML to {out_path.resolve()}")


if __name__ == "__main__":
    generate_lineage_yaml_from_folder()
