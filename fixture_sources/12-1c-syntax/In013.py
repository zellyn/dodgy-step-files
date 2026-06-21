"""In013 — Transfer Status remains Void after Defined was expected: unknown entity type.

Catalog claim: A transfer process expected to produce a Defined result for
an entity, but the result remains Void because no actor handled the entity
type. The DATA section contains a made-up future type
(HYPOTHETICAL_AP242_ED2_FUTURE_ENTITY) that no standard schema defines and
no kernel actor recognizes; the reader silently skips it.

Byte assertions:
  contains(b'DATA;')
  contains(b'HEADER;')
  count(b'ENDSEC;') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="In013",
    defect=(
        "Transfer Status remains Void after Defined was expected: unknown entity type "
        "in DATA section silently skipped; "
        "OCCT Transfer_StatusResult Void/Defined transitions (uncovered class evidence); "
        "a transfer process expected to produce a Defined result for an entity, "
        "but the result remains Void because no actor handled the entity type; "
        "the transfer log does not flag the void as an error; "
        "defect: DATA section contains HYPOTHETICAL_AP242_ED2_FUTURE_ENTITY — "
        "a made-up future type no standard schema defines and no kernel actor recognizes; "
        "the reader silently skips it; "
        "receiver must emit no-actor-for-entity-type-X warning; "
        "track unrecognized types in a per-file summary; "
        "never silently skip unknown entity types with no diagnostic; "
        "bug-reporter synonyms: entity type not transferred, kernel skipped entity silently, "
        "unknown entity type ignored, STEP entity skipped without warning, "
        "future-schema entity Void after transfer, transfer Status remains Void; "
        "GEOMETRIC_CURVE_SET IS NOT used — unknown entity type is the defect carrier"
    ),
)

# Override render() to inject the made-up future entity type.
_original_render = f.render


def _render_unknown_entity() -> str:
    header = f._render_header()
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"/* Made-up future-schema entity: no kernel actor recognizes this type. */\n"
        f"/* Transfer status stays Void with no diagnostic emitted. */\n"
        f"#1=HYPOTHETICAL_AP242_ED2_FUTURE_ENTITY('future_001',42,'schema_version_9999',"
        f"(1.0,2.0,3.0),.UNKNOWN_ENUM_VALUE.);\n"
        f"/* A second unknown entity to confirm the per-file summary lists both. */\n"
        f"#2=HYPOTHETICAL_AP242_ED2_FUTURE_ENTITY('future_002',99,'schema_version_9999',"
        f"(4.0,5.0,6.0),.ANOTHER_UNKNOWN_VALUE.);\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_unknown_entity  # type: ignore[method-assign]
