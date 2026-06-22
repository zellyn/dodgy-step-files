"""Ad031 — Malformed FILE_DESCRIPTION (missing implementation_level argument).

Catalog claim: parser opens header parsing context, frees on ENDSEC;, but a
deferred diagnostic emitter still holds a pointer to a string copied from the
header. Trigger: FILE_DESCRIPTION with only one positional argument supplied
(implementation_level missing) → deferred diagnostic fires after ENDSEC;,
referencing freed memory → UAF.

Byte assertions:
  matches(rb"FILE_DESCRIPTION\\(\\([^;]*\\)\\s*\\)\\s*;")
  matches(rb'FILE_DESCRIPTION\\(\\([^)]+\\)\\s*\\)\\s*;')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad031",
    defect=(
        "malformed FILE_DESCRIPTION: missing implementation_level second argument; "
        "deferred diagnostic holds pointer into freed header allocator → UAF; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Override _render_header to emit the malformed FILE_DESCRIPTION.
# The standard form is: FILE_DESCRIPTION(('desc'),'2;1');
# The attack form omits the second argument (implementation_level):
#   FILE_DESCRIPTION(('Ad031'));   ← only one positional argument
# This matches: FILE_DESCRIPTION\(\([^)]+\)\s*\)\s*;
def _render_header():
    return (
        "HEADER;\n"
        f"FILE_DESCRIPTION(('{f.catalog_id}'));\n"
        f"FILE_NAME('{f.catalog_id}.stp','{f.timestamp}',(''),(''),"
        f"'cad-research-suite','','');\n"
        f"FILE_SCHEMA(('AUTOMOTIVE_DESIGN {{ 1 0 10303 214 3 1 1 }}'));\n"
        "ENDSEC;"
    )

f._render_header = _render_header  # type: ignore[method-assign]

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
