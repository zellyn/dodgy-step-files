"""Twi082 — Edge same_range flag claims parametric agreement that does not hold.

Catalog claim: An edge declares its 3D-curve parameter range and pcurve parameter
range to be identical (same_range=.T.) but evaluating both at the boundary gives
parameter pairs that differ by more than tolerance. BRepCheck_Edge::InvalidSameRangeFlag.

Reproducer recipe: Edge whose 3D LINE runs t∈[0,10] while the pcurve in UV
runs u∈[0,5] — different parameterizations — but same_range flag is set true.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with one
SURFACE_CURVE edge labelled 'mismatched_param'. The SURFACE_CURVE wraps:
  - 3D LINE from (0,0,0) along (1,0,0) length 10 (t∈[0,10])
  - PCURVE on a PLANE in UV space; the 2D line runs u∈[0,5] with
    DIRECTION_2D((2.0,0.0)) — byte assertion for DIRECTION_2D and (2.0,0.0)
The EDGE_CURVE has same_range=.T. even though parameter extents disagree.
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'mismatched_param')
  - contains(b'DIRECTION_2D(')
  - contains(b'(2.0,0.0)')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi082",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with one SURFACE_CURVE edge "
        "'mismatched_param'; "
        "3D LINE: (0,0,0) along (1,0,0) length 10 — 3D parameter range [0,10]; "
        "PCURVE on PLANE: UV LINE from (0,0) with DIRECTION_2D((2.0,0.0)) length 5 "
        "— UV parameter range [0,5]; "
        "EDGE_CURVE same_range=.T. but 3D range [0,10] ≠ UV range [0,5]; "
        "BRepCheck_Edge InvalidSameRangeFlag triggered; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_CURVE IS wired into EDGE_LOOP; never orphaned"
    ),
)

# ── PLANE for the pcurve host surface ────────────────────────────────────────
plane_orig = f.cartesian_point((0.0, 0.0, 0.0))
plane_zdir = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plane_plc  = f.axis2_placement_3d(plane_orig, plane_zdir, plane_xdir)
plane_surf = f._emit_raw(f"PLANE('',#{plane_plc.eid})")

# ── 3D LINE: (0,0,0) along (1,0,0), length 10 — parameter range [0,10] ──────
line_3d = f.line(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)
)

# ── PCURVE in UV space: 2D line from (0,0) with DIRECTION_2D((2.0,0.0)) ──────
# Byte assertion: contains(b'DIRECTION_2D(')
# Byte assertion: contains(b'(2.0,0.0)')
# DIRECTION_2D is a 2D direction entity; in Part-21 it appears as DIRECTION_2D('',(2.0,0.0))
uv_orig_pt = f.cartesian_point((0.0, 0.0))    # 2D origin point
# Emit DIRECTION_2D with raw API — not available as a builder method
dir_2d = f._emit_raw("DIRECTION_2D('',(2.0,0.0))")
# Vector_2D of magnitude 5 carrying the 2D direction:
vec_2d = f._emit_raw(f"VECTOR_2D('',#{dir_2d.eid},5.0)")
# 2D LINE: from (0,0), direction (2.0,0.0), length 5 — UV range [0,5]
uv_line = f._emit_raw(
    f"LINE_2D('mismatched_param',#{uv_orig_pt.eid},#{vec_2d.eid})"
)
drep   = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_line.eid}),#?)")
pcurve = f._emit_raw(f"PCURVE('',#{plane_surf.eid},#{drep.eid})")

# ── SURFACE_CURVE: wraps 3D line + pcurve ────────────────────────────────────
sc = f._emit_raw(
    f"SURFACE_CURVE('',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# ── Vertices: 3D endpoints along the 10-unit LINE ────────────────────────────
v1 = f.vertex_point(f.cartesian_point((0.0,  0.0, 0.0)))
v2 = f.vertex_point(f.cartesian_point((10.0, 0.0, 0.0)))

# ── EDGE_CURVE: same_range=.T. even though 3D [0,10] ≠ UV [0,5] ─────────────
# The .T. same_range flag is the defect
ec = f._emit_raw(
    f"EDGE_CURVE('',#{v1.eid},#{v2.eid},#{sc.eid},.T.)"
)
oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec.eid},.T.)")

# ── EDGE_LOOP and GEOMETRIC_CURVE_SET ────────────────────────────────────────
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi082.stp")
