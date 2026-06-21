"""Ls006 — Numeric literal with embedded underscore digit-grouping.

Catalog claim: Modern languages tolerate `1_000_000`. Some in-house
exporters borrow this and emit `IFCREAL(1_000.0)`. ISO 10303-21
disallows underscores in numerics.

Reproducer recipe: #1=IFCREAL(1_000.0);

Byte assertions:
  matches(rb'\\d_\\d')
  count(b'_') >= 2 or matches(rb'\\d_\\d{3}')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls006",
    defect=(
        "Numeric literal with embedded underscore digit-grouping in STEP REAL; "
        "modern languages (Python, Rust, Swift) tolerate 1_000_000 for readability; "
        "some in-house exporters borrow this and emit underscored numerics in STEP; "
        "ISO 10303-21 disallows underscores in numeric literals; "
        "defect: DIRECTION('',(1_000.0,2_500.0,0.)) — underscore digit-grouping "
        "in the first two coordinate values; "
        "also VECTOR magnitude uses 1_000.0 (a second underscore-numeric); "
        "strict readers must reject with 'underscore not permitted in numeric literal'; "
        "OCC silently accepts with diagnostic but loads empty result — "
        "receivers enforcing the spec must reject this fixture; "
        "synonyms: underscore in numeric literal, 1_000_000 in STEP REAL, "
        "digit grouping in STEP number, Python-style underscore in STEP, "
        "thousands separator inside number; "
        "GEOMETRIC_CURVE_SET IS NOT used — DIRECTION entity is the defect carrier"
    ),
)

_original_render = f.render


def _render_underscore_numeric() -> str:
    header = f._render_header()
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"/* Defect: underscore digit-grouping in numeric literals. */\n"
        f"/* ISO 10303-21 does not permit underscores in REAL or INTEGER tokens. */\n"
        f"/* Python/Rust-style 1_000_000 borrowed by some in-house exporters. */\n"
        f"#1=DIRECTION('',(1_000.0,2_500.0,0.));\n"
        f"#2=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        f"#3=VECTOR('v',#1,1_000.0);\n"
        f"#4=LINE('l',#2,#3);\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_underscore_numeric  # type: ignore[method-assign]
