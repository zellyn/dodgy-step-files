"""In012 — Transfer watchdog fires: dependency cycle in entity references.

Catalog claim: The transfer engine detects a dependency cycle (entity A
references B references C references A) and raises a dead-loop exception.
A MAPPED_ITEM whose mapping_source resolves through a chain that eventually
re-references the original entity creates the cycle.

Byte assertions:
  contains(b'DATA;')
  contains(b'HEADER;')
  count(b'ENDSEC;') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="In012",
    defect=(
        "Transfer watchdog fires: dependency cycle in entity references; "
        "OCCT Transfer_TransferDeadLoop.hxx (uncovered class evidence); "
        "the transfer engine detects a dependency cycle — entity A references B "
        "references C references A — and raises a dead-loop exception; "
        "defect: a MAPPED_ITEM whose mapping_source resolves through a chain "
        "that eventually re-references the original entity, creating a cycle; "
        "receiver must detect cycle and reject the file; "
        "emit the cycle path in the diagnostic: A->B->C->A; "
        "never recurse forever on a circular reference; "
        "must not silently accept a cyclic STEP file with empty result; "
        "bug-reporter synonyms: STEP file has cycle, circular reference, "
        "kernel detects loop, STEP entity reference cycle, "
        "circular references in STEP DATA, watchdog fires on STEP cycle, "
        "dependency cycle entity references; "
        "GEOMETRIC_CURVE_SET IS NOT used — reference cycle is the defect carrier"
    ),
)

# Build the cyclic reference using _emit_raw.
# The cycle: #10 → #11 → #12 → #10
# We use raw emission so the entity IDs are predictable.
# REPRESENTATION_MAP: (origin, mapped_rep)
# MAPPED_ITEM: (name, mapping_source, item_target)
# We create three REPRESENTATION entities that mutually reference each other
# through REPRESENTATION_MAP / MAPPED_ITEM chains.

_original_render = f.render


def _render_cycle() -> str:
    header = f._render_header()
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"/* Cyclic reference chain: #10 -> #11 -> #12 -> #10 */\n"
        f"/* REPRESENTATION_MAP: (origin, mapped_rep) */\n"
        f"#10=REPRESENTATION_MAP(#20,#11);\n"
        f"#11=REPRESENTATION_MAP(#21,#12);\n"
        f"#12=REPRESENTATION_MAP(#22,#10);\n"
        f"/* CARTESIAN_POINT origins used as placement proxies */\n"
        f"#20=CARTESIAN_POINT('origin_a',(0.0,0.0,0.0));\n"
        f"#21=CARTESIAN_POINT('origin_b',(1.0,0.0,0.0));\n"
        f"#22=CARTESIAN_POINT('origin_c',(2.0,0.0,0.0));\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_cycle  # type: ignore[method-assign]
