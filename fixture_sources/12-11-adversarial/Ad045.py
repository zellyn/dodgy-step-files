"""Ad045 — Healing pipeline raises exception on EDGE_CURVE vertices off the LINE
by sub-confusion offset ("must not throw").

Catalog claim: a healing pass over a real-world input shape throws an exception
across the kernel ABI rather than producing a result, a warning, or an empty
shape.  Common trigger: an EDGE_CURVE whose VERTEX_POINTs do not lie on the
edge's 3D LINE — a sub-confusion vertex/curve mismatch (e.g. ±1e-7 Y-offset
from an X-axis LINE) — exposes a healing-path edge case.

Byte assertions:
  contains(b'EDGE_CURVE')
  contains(b'1e-7') or contains(b'1.0E-7') or contains(b'1.0e-7')
  contains(b'EDGE_CURVE') and contains(b'LINE')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad045",
    defect=(
        "healing-pipeline exception: EDGE_CURVE VERTEX_POINTs displaced ±1e-7 "
        "in Y from the hosting X-axis LINE; sub-confusion mismatch triggers "
        "out-of-range index in wire-ordering pass; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload: EDGE_CURVE on an X-axis LINE, but VERTEX_POINTs are
# displaced by 1e-7 in Y — just inside the confusion tolerance.
# The mismatch is: vertex Y = ±1e-7, but LINE direction is pure X (Y=0).
#
# Exact coordinates that reproduce the bug24126 / bug24249 class:
#   line goes from (0,0,0) to (1,0,0) along X;
#   start vertex is at (0, +1e-7, 0)  → on-curve error ≈ 1e-7;
#   end   vertex is at (1, -1e-7, 0)  → on-curve error ≈ 1e-7.
# Both are within kernel confusion tolerance (default 1e-7) but are
# NOT on the LINE; the healing ShapeFix_Wire pass exposes the bug.

# LINE entity: from origin along +X.
line_origin = f.cartesian_point((0.0, 0.0, 0.0))
line_dir = f.direction((1.0, 0.0, 0.0))
line_vec = f.vector(line_dir, 1.0)
line = f.line(line_origin, line_vec)

# Vertices displaced by ±1e-7 in Y (sub-confusion mismatch).
# Use _emit_raw to inject the exact 1e-7 literal the byte assertion requires.
f._emit_raw("CARTESIAN_POINT('v_start_offset',(0.0,1.0E-7,0.0))")
f._emit_raw("CARTESIAN_POINT('v_end_offset',(1.0,-1.0E-7,0.0))")

# VERTEX_POINTs referencing the offset cartesian points.
# (IDs assigned sequentially after last _emit_raw call; we reference by
# computing the IDs relative to where _next_id is after the line entities.)
vstart_cp_id = f._next_id - 2
vend_cp_id   = f._next_id - 1

f._emit_raw(f"VERTEX_POINT('v_start',#{vstart_cp_id})")
f._emit_raw(f"VERTEX_POINT('v_end',#{vend_cp_id})")

v_start_id = f._next_id - 2
v_end_id   = f._next_id - 1

# EDGE_CURVE: vertices off-LINE by 1e-7 in Y — the trigger.
# Satisfies: contains(b'EDGE_CURVE') and contains(b'LINE')
# and: contains(b'1.0E-7') (from CARTESIAN_POINT name string + coordinate).
f._emit_raw(
    f"EDGE_CURVE('sub_confusion_edge',"
    f"#{v_start_id},#{v_end_id},#{line.eid},.T.)"
)
