"""Twi210 — ShapeAnalysis_Wire.CheckClosed near-closed-with-perpendicular-distance.

Catalog claim: Wire geometrically open but nearly closed: first vertex (0,0,0),
last vertex (0.0001, 0.0001, 0). 3D distance ~0.000141 units below nominal
tolerance. CheckClosed uses 3D distance metric, not perpendicular distance. Wire
appears closed in 3D but fails perpendicular-distance semantics for valid closure
on surface.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 5 edges on a
PLANE. Square-ish path from V0(0,0,0) with tiny gap-closure edge as the 5th
edge. Last vertex V5 is offset from V0 by (0.0001, 0.0001, 0), so 3D distance
~1.41e-4. The gap edge e5 from V4->V5 does NOT return to V0 — the wire is open
at V0 vs V5. CheckClosed uses 3D distance which passes but perpendicular-distance
semantics fails — IS the mechanism.

Byte assertions:
  - contains(b'gap_e5')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi210",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 5 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "Wire: V0(0,0,0)->V1(5,0,0)->V2(5,5,0)->V3(0,5,0)->V4(0,0.0001,0)->V5(0.0001,0.0001,0); "
        "gap_e5: LINE V4->V5 — last vertex V5 offset from V0 by (0.0001,0.0001,0), "
        "3D distance ~1.41e-4; wire is OPEN (V5 != V0); "
        "CheckClosed 3D-distance passes but perpendicular-distance fails IS defect; "
        "sub-tolerance gap IS the mechanism — EDGE_LOOP NOT properly closed; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# PLANE: normal +Z
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# Vertices
PV0 = (0.0,    0.0,    0.0)   # first vertex
PV1 = (5.0,    0.0,    0.0)
PV2 = (5.0,    5.0,    0.0)
PV3 = (0.0,    5.0,    0.0)
PV4 = (0.0,    0.0001, 0.0)   # nearly back at V0 left edge
PV5 = (0.0001, 0.0001, 0.0)   # last vertex: offset 1.41e-4 from V0 IS gap

vV0 = f.vertex_point(f.cartesian_point(PV0))
vV1 = f.vertex_point(f.cartesian_point(PV1))
vV2 = f.vertex_point(f.cartesian_point(PV2))
vV3 = f.vertex_point(f.cartesian_point(PV3))
vV4 = f.vertex_point(f.cartesian_point(PV4))
vV5 = f.vertex_point(f.cartesian_point(PV5))


def _line_sc(v_s, v_e, ps, pe, name=""):
    dx = pe[0] - ps[0]; dy = pe[1] - ps[1]; dz = pe[2] - ps[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    ln3 = f.line(f.cartesian_point(ps),
                 f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag))
    uv_orig = f.cartesian_point((ps[0], ps[1]))
    uv_dir  = f.direction((dx/mag, dy/mag))
    uv_vec  = f.vector(uv_dir, mag)
    uv_ln   = f.line(uv_orig, uv_vec)
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln.eid}),#*)")
    pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")
    sc      = f._emit_raw(f"SURFACE_CURVE('',#{ln3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# e1: V0->V1 (bottom)
ec1 = _line_sc(vV0, vV1, PV0, PV1, name="e1")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: V1->V2 (right)
ec2 = _line_sc(vV1, vV2, PV1, PV2, name="e2")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: V2->V3 (top)
ec3 = _line_sc(vV2, vV3, PV2, PV3, name="e3")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# e4: V3->V4 (left, nearly back to start)
ec4 = _line_sc(vV3, vV4, PV3, PV4, name="e4")
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")

# gap_e5: V4->V5, tiny diagonal — last vertex offset from V0 IS the gap defect
ec5 = _line_sc(vV4, vV5, PV4, PV5, name="gap_e5")
oe5 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec5.eid},.T.)")

# EDGE_LOOP: wire ends at V5, not V0 — intentionally open (gap defect)
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid},#{oe5.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi210.stp")
