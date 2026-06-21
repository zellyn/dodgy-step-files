"""Ls005 — Explicit positive sign on numeric literal (`+1.0`).

Catalog claim: Some generators write `+1.0` for positive REAL. The
Part-21 BNF arguably disallows leading `+` for INTEGER but admits it for
REAL; uniform handling preferred.

Reproducer recipe: #1=IFCDIRECTION((+1.,+0.,+0.));

Byte assertions:
  matches(rb'\\(\\s*\\+\\d')
  matches(rb'\\(\\+\\d')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls005",
    defect=(
        "Explicit positive sign on numeric literal in STEP REAL; "
        "some generators write +1.0 for positive REAL; "
        "the Part-21 BNF arguably disallows leading plus for INTEGER "
        "but admits it for REAL; uniform handling is preferred; "
        "defect: DIRECTION('',(+1.,+0.,+0.)) — explicit leading plus on every "
        "coordinate value; VECTOR magnitude uses +1. (another leading-plus REAL); "
        "OCC silently strips the leading plus sign with no diagnostic; "
        "conforming kernel must accept signed reals and integers uniformly "
        "and never silently strip the sign; "
        "synonyms: plus sign on positive REAL, +1.0 in STEP literal, "
        "explicit positive sign on numeric, STEP rejects leading plus, "
        "INTEGER with explicit plus; "
        "GEOMETRIC_CURVE_SET IS NOT used — DIRECTION entity is the defect carrier"
    ),
)

_original_render = f.render


def _render_leading_plus() -> str:
    header = f._render_header()
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"/* Defect: explicit positive sign on numeric literals. */\n"
        f"/* Part-21 BNF is ambiguous on leading +; uniform handling required. */\n"
        f"/* OCC silently strips leading + — conformant kernel must not. */\n"
        f"#1=DIRECTION('',(+1.,+0.,+0.));\n"
        f"#2=CARTESIAN_POINT('origin',(+0.,+0.,+0.));\n"
        f"#3=VECTOR('v',#1,+1.);\n"
        f"#4=LINE('l',#2,#3);\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_leading_plus  # type: ignore[method-assign]
