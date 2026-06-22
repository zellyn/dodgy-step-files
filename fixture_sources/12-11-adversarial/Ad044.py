"""Ad044 — EDGE_CURVE.same_sense boolean read uninitialised.

Catalog claim: STEP files where same_sense boolean is missing or illegally
formatted leave a C++ bool uninitialised → non-deterministic edge direction.
GCC 4.9 regression (Mantis 0029944).

Reproducer recipe: EDGE_CURVE with stripped or .U. same_sense.

Byte assertions:
  matches(rb'EDGE_CURVE\\([^;]*,\\s*\\.U\\.\\s*\\)')
  contains(b'.U.')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad044",
    defect=(
        "EDGE_CURVE.same_sense = .U. (unknown/uninitialised boolean); "
        "leaves C++ bool uninitialised → non-deterministic edge direction; "
        "GCC 4.9 regression Mantis 0029944; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Build the vertex/curve infrastructure needed for EDGE_CURVE.
p1 = f.cartesian_point((0.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 0.0, 0.0))
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1.0)
line = f.line(p1, vec)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)

# Attack payload: EDGE_CURVE with same_sense = .U. (unknown enum literal).
# .U. is not a valid BOOLEAN per ISO 10303-11; it triggers the uninit-bool
# code path in older OCCT/GCC.
# Satisfies: matches(rb'EDGE_CURVE\([^;]*,\s*\.U\.\s*\)')
# and: contains(b'.U.')
f._emit_raw(
    f"EDGE_CURVE('',#{v1.eid},#{v2.eid},#{line.eid},.U.)"
)

# Second instance with missing same_sense (omitted, rendered as $).
# This exercises the "stripped" variant mentioned in the catalog.
f._emit_raw(
    f"EDGE_CURVE('missing_sense',#{v1.eid},#{v2.eid},#{line.eid},$)"
)
