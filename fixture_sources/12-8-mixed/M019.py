"""M019 — TRIANGLE_STRIP / TRIANGLE_FAN in COMPLEX_TRIANGULATED_FACE mis-decoded.

Catalog claim: STEP COMPLEX_TRIANGULATED_FACE with strip/fan topology was
incorrectly imported (indices misaligned).

Reproducer recipe: AP242e2 file with mixed triangle_strip + triangle_fan +
plain triangles.

Byte assertions:
  contains(b'COMPLEX_TRIANGULATED_FACE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M019",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing COMPLEX_TRIANGULATED_FACE with mixed "
        "triangle_strip and triangle_fan topology; "
        "input: AP242e2 STEP file where COMPLEX_TRIANGULATED_FACE encodes geometry "
        "with strip/fan index packing; "
        "OCCT 588ee92 (Mantis 0033491) mis-decoded indices — strips and fans were "
        "misaligned, producing incorrect facets; "
        "kernel must heal: correctly unfold strips/fans to individual triangles "
        "preserving orientation; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: TRIANGLE_STRIP indices misaligned, fan strip mis-decoded, "
        "complex_triangulated_face strip wrong, tessellation strip topology mishandled"
    ),
)

# ── Five vertices for a fan+strip mesh ───────────────────────────────────────
# Layout: center at (5,5,0), ring at (0,0,0),(10,0,0),(10,10,0),(0,10,0)
# triangle_fan: center + ring (4 triangles)
# triangle_strip: two triangles along the base edge
coords = f._emit_raw(
    "COORDINATES_LIST('strip_fan_verts',3,"
    "((5.,5.,0.),(0.,0.,0.),(10.,0.,0.),(10.,10.,0.),(0.,10.,0.),"
    "(20.,0.,0.),(20.,10.,0.)))"
)

# COMPLEX_TRIANGULATED_FACE encodes:
#   pnmax (max index+1 = 7)
#   triangle_strips: one strip of 4 vertices (indices 1,2,5,6 => 2 triangles)
#   triangle_fans: one fan center=0, ring=1,2,3,4 (=> 4 triangles)
#   triangles: one plain triple (0,2,3)
# Byte assertion: contains(b'COMPLEX_TRIANGULATED_FACE')
ctf = f._emit_raw(
    f"COMPLEX_TRIANGULATED_FACE('strip_fan_face',#{coords.eid},$,"
    f"((.FALSE.,.FALSE.,.FALSE.,.FALSE.,.FALSE.,.FALSE.,.FALSE.)),"
    f"((1,2,5,6)),"
    f"((0,(1,2,3,4))),"
    f"((0,2,3)))"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('complex-triangulated-face-strip-fan',(#{ctf.eid}))"
)
f.add_product_chain(gcs, uncertainty_literal="LENGTH_MEASURE(1.0E-7)")  # bare typed real, not enum-wrapped (scaffolding-artifact fix)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M019.stp")
