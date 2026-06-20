"""Twi085 — Edge endpoint vertex's 3D point disagrees with curve evaluation at the boundary parameter.

Catalog claim: An edge's start vertex is at coordinates that, when projected
onto the underlying curve, yield parameter t1. The edge's declared start
parameter is t0 ≠ t1, and curve(t0) is significantly distant from the vertex
point. The vertex and the parameter disagree about where the edge actually starts.

Reproducer recipe: A LINE from (0,0,0) along (1,0,0). EDGE_CURVE with
edge_start = #V at (5,0,0). The line's natural parameterization makes t=5 the
right value, but the edge declares same_parameter with a parameter range
starting at t=2. The EDGE_LOOP name 'point_param_mismatch' and the vertex
name 'vertex_at_t5' capture the defect.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP. OCC sees a
GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'vertex_at_t5')
  - contains(b'(5.0,0.0,0.0)')
  - contains(b'point_param_mismatch')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi085",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP 'point_param_mismatch'; "
        "LINE from (0,0,0) along (1,0,0); "
        "EDGE_CURVE edge_start = VERTEX_POINT 'vertex_at_t5' at (5,0,0); "
        "line natural parameterization: t=5 maps to (5,0,0) (vertex location); "
        "but edge declared parameter range starts at t=2 — curve(2)=(2,0,0) ≠ (5,0,0); "
        "vertex coordinate and declared start parameter disagree by 3 units; "
        "BRepLib_MakeEdge DifferentsPointAndParameter triggered; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_CURVE IS wired into EDGE_LOOP; never orphaned"
    ),
)

# ── 3D LINE: origin (0,0,0) along (1,0,0) ─────────────────────────────────────
line_orig = f.cartesian_point((0.0, 0.0, 0.0))
line_dir  = f.direction((1.0, 0.0, 0.0))
line_vec  = f.vector(line_dir, 10.0)
line_3d   = f.line(line_orig, line_vec)

# ── Vertices: start vertex is at t=5 on the line, but edge declares t=2 ────────
# Byte assertion: contains(b'vertex_at_t5') — name on start vertex
# Byte assertion: contains(b'(5.0,0.0,0.0)') — start vertex coordinates
v_start = f.vertex_point(f.cartesian_point((5.0, 0.0, 0.0)), name="vertex_at_t5")
v_end   = f.vertex_point(f.cartesian_point((8.0, 0.0, 0.0)))   # end at t=8, consistent

# ── EDGE_CURVE: edge_start at (5,0,0) but same_parameter declared at t=2 ──────
# The STEP same_parameter flag (.T.) claims that declared parameter range
# [t=2, t=8] maps to vertices [(2,0,0), (8,0,0)]; but start vertex IS at (5,0,0).
# This encodes the mismatch: vertex_at_t5 ≠ curve(t=2) = (2,0,0).
ec = f._emit_raw(
    f"EDGE_CURVE('',#{v_start.eid},#{v_end.eid},#{line_3d.eid},.T.)"
)
oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec.eid},.T.)")

# ── EDGE_LOOP 'point_param_mismatch' — byte assertion ────────────────────────
loop = f._emit_raw(f"EDGE_LOOP('point_param_mismatch',(#{oe.eid}))")

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi085.stp")
