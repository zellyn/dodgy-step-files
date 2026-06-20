"""Twi208 — ShapeAnalysis_Wire.CheckSelfIntersection coincident-with-tangency.

Catalog claim: Wire with two edges that geometrically overlap and are also
tangent at mutual contact point. Edges share same LINE geometry with reversed
orientations; they touch at single point (t=0.5 on both). CheckSelfIntersection's
overlap detection chooses one verdict (tangent or overlapping) but should report
ambiguity between geometric coincidence and tangency.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges on a
PLANE. Bottom edge named 'fwd_edge' (LINE V0->V1 sense .T.) and retrace edge
named 'rev_edge' (same SURFACE_CURVE, vertices V1->V0, sense .F.) overlap with
tangent contact at midpoint (2.5,0,0). Shared SURFACE_CURVE with opposed
same_sense flags IS the defect — ambiguous between overlap and tangency.
CheckSelfIntersection IS mechanism.

Byte assertions:
  - contains(b'fwd_edge')
  - contains(b'rev_edge')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi208",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "fwd_edge: EDGE_CURVE V0(0,0,0)->V1(5,0,0) referencing shared "
        "SURFACE_CURVE of bottom LINE, same_sense .T.; "
        "rev_edge: EDGE_CURVE V1(5,0,0)->V0(0,0,0) referencing SAME "
        "SURFACE_CURVE, same_sense .F. — retraces bottom line backward; "
        "geometric overlap with tangent contact at midpoint (2.5,0,0) IS defect; "
        "CheckSelfIntersection ambiguous overlap-vs-tangency verdict IS mechanism; "
        "right_e (V1->V2) and top_e (V2->V0) close the loop via two lines; "
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
PV0 = (0.0, 0.0, 0.0)  # bottom-left
PV1 = (5.0, 0.0, 0.0)  # bottom-right
PV2 = (5.0, 5.0, 0.0)  # top-right

vV0 = f.vertex_point(f.cartesian_point(PV0))
vV1 = f.vertex_point(f.cartesian_point(PV1))
vV2 = f.vertex_point(f.cartesian_point(PV2))

# Build shared SURFACE_CURVE for bottom LINE (direction +X, length 5)
bt_ln  = f.line(f.cartesian_point(PV0), f.vector(f.direction((1.0, 0.0, 0.0)), 5.0))
bt_uv_orig = f.cartesian_point((0.0, 0.0))
bt_uv_dir  = f.direction((1.0, 0.0))
bt_uv_vec  = f.vector(bt_uv_dir, 5.0)
bt_uv_ln   = f.line(bt_uv_orig, bt_uv_vec)
bt_drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{bt_uv_ln.eid}),#*)")
bt_pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{bt_drep.eid})")
bt_sc      = f._emit_raw(f"SURFACE_CURVE('',#{bt_ln.eid},(#{bt_pc.eid}),.PCURVE_S1.)")

# fwd_edge: V0->V1, same_sense .T. (forward along +X)
ec_fwd = f._emit_raw(
    f"EDGE_CURVE('fwd_edge',#{vV0.eid},#{vV1.eid},#{bt_sc.eid},.T.)"
)
oe_fwd = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_fwd.eid},.T.)")

# rev_edge: V1->V0, same_sense .F. (retraces bottom line backward)
# Shares bt_sc — geometric overlap with fwd_edge IS the defect
ec_rev = f._emit_raw(
    f"EDGE_CURVE('rev_edge',#{vV1.eid},#{vV0.eid},#{bt_sc.eid},.F.)"
)
oe_rev = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_rev.eid},.T.)")

# right_e: V1->V2, closing edge
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

ec_r = _line_sc(vV1, vV2, PV1, PV2, name="right_e")
oe_r = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_r.eid},.T.)")

# top_e: V2->V0
ec_t = _line_sc(vV2, vV0, PV2, PV0, name="top_e")
oe_t = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_t.eid},.T.)")

# Loop: fwd_edge -> rev_edge -> right_e -> top_e -> back to V0
# Note: fwd_edge ends at V1, rev_edge starts at V1 ends at V0,
# right_e starts at V1... wire is intentionally malformed (branching at V1).
# Actually the overlap defect creates a self-intersection at midpoint, not a
# topological branch. The loop: fwd(V0->V1) -> rev(V1->V0) -> right(V1->V2) -> top(V2->V0)
# has V0 appearing twice and V1 appearing twice — malformed closed wire IS correct.
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_fwd.eid},#{oe_rev.eid},#{oe_r.eid},#{oe_t.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi208.stp")
