"""Twi081 — Edge has multiple distinct 3D curves attached.

Catalog claim: A topological edge carries more than one 3D-curve representation
— two EDGE_CURVEs share endpoints V1/V2 but reference different curve geometries
(one a LINE, one an ARC/circle). Both are referenced by ORIENTED_EDGEs in the
same EDGE_LOOP. BRepCheck_Edge::Multiple3DCurve is triggered.

Reproducer recipe: Two distinct EDGE_CURVE entities sharing VERTEX_POINTs #V1
at (0,0,0) and #V2 at (1,0,0) but referencing different geometries: one a
straight LINE ('edge_with_line'), one a circular ARC ('edge_with_arc').
Both ORIENTED_EDGEs appear in the same EDGE_LOOP.

Mechanism IS a GEOMETRIC_CURVE_SET containing the EDGE_LOOP. OCC sees a
GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'edge_with_line')
  - contains(b'edge_with_arc')
  - count_entity_def(b'EDGE_CURVE') == 2

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi081",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 2 EDGE_CURVEs sharing "
        "the same VERTEX_POINT pair (#V1 at (0,0,0), #V2 at (1,0,0)) but "
        "referencing different 3D geometries; "
        "EDGE_CURVE 'edge_with_line': straight LINE from (0,0,0) to (1,0,0); "
        "EDGE_CURVE 'edge_with_arc': ARC (CIRCLE radius 0.5, centre (0.5,0,0)) "
        "spanning same endpoints; "
        "two distinct 3D curves on same vertex pair → BRepCheck Multiple3DCurve; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "both EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Shared VERTEX_POINTs: V1=(0,0,0), V2=(1,0,0) ────────────────────────────
v1 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v2 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))

# ── EDGE_CURVE 'edge_with_line': straight LINE from V1 to V2 ─────────────────
line_geom = f.line(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)
)
ec_line = f._emit_raw(
    f"EDGE_CURVE('edge_with_line',#{v1.eid},#{v2.eid},#{line_geom.eid},.T.)"
)
oe_line = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_line.eid},.T.)")

# ── EDGE_CURVE 'edge_with_arc': semi-circle ARC on CIRCLE r=0.5 ──────────────
# Circle centre at (0.5,0,0), radius 0.5, in XY plane.
# Axis placement: centre (0.5,0,0), normal +Z, ref-dir +X
arc_orig  = f.cartesian_point((0.5, 0.0, 0.0))
arc_zdir  = f.direction((0.0, 0.0, 1.0))
arc_xdir  = f.direction((1.0, 0.0, 0.0))
arc_plc   = f.axis2_placement_3d(arc_orig, arc_zdir, arc_xdir)
arc_geom  = f.circle(arc_plc, 0.5)
ec_arc = f._emit_raw(
    f"EDGE_CURVE('edge_with_arc',#{v1.eid},#{v2.eid},#{arc_geom.eid},.T.)"
)
oe_arc = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_arc.eid},.T.)")

# ── EDGE_LOOP: both edges on the same vertex pair (Multiple3DCurve defect) ───
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_line.eid},#{oe_arc.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi081.stp")
