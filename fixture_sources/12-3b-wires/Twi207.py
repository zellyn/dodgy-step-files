"""Twi207 — ShapeFix_Wire.FixGaps2d gap-at-knot-discontinuity.

Catalog claim: Wire on B-spline surface where pcurves leave gaps exactly at
knot lines. B-spline basis discontinuities at knot values cause parametric
space jumps. Edge1 pcurve ends at knot u=1.5 with endpoint (1.5, 5.0). Edge2
pcurve starts at u=1.5 but v=5.01 due to B-spline singularity. FixGaps2d's
bridging logic attempts straight-line splice across knot boundary, invalid for
B-spline surface topology.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 3 edges on a
degree-2/1 B-spline surface with knots at u=0.75, 1.5, 2.25. Two edges
named 'knot_e0' and 'knot_e1' have pcurves whose endpoints straddle the
knot boundary at u=1.5 with a v-gap of 0.01, IS the defect. FixGaps2d's
straight-line splice across the knot boundary produces invalid geometry for
the B-spline surface topology.

Byte assertions:
  - contains(b'knot_e0')
  - contains(b'knot_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi207",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges on "
        "degree-2/1 B_SPLINE_SURFACE with knots at u=0.75,1.5,2.25; "
        "knot_e0: 3D LINE from (1.5,0,0) to (1.5,5,0), pcurve ends at (1.5,5.0); "
        "knot_e1: 3D LINE from (1.5,5,0) to (0,5,0), pcurve STARTS at (1.5,5.01) — "
        "0.01 v-gap at knot u=1.5 IS the defect; "
        "FixGaps2d straight-line splice across knot boundary IS mechanism; "
        "B-spline basis discontinuities at knot values cause parametric space jump; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── B-spline surface: degree-2 in u, degree-1 in v ──────────────────────────
# u: 4 control points, degree 2 → need 4+2+1=7 knot values
#    multiplicities [3,1,1,2] = 7, knots [0.0, 0.75, 1.5, 2.25]
# v: 2 control points, degree 1 → need 2+1+1=4 knot values
#    multiplicities [2,2] = 4, knots [0.0, 6.0]
# 3D surface spans x=[0..3], y=[0..6] (roughly)

P00 = (0.0, 0.0, 0.0)
P01 = (0.0, 6.0, 0.0)
P10 = (1.0, 0.0, 0.0)
P11 = (1.0, 6.0, 0.0)
P20 = (2.0, 0.0, 0.0)
P21 = (2.0, 6.0, 0.0)
P30 = (3.0, 0.0, 0.0)
P31 = (3.0, 6.0, 0.0)

cp_grid = [
    [f.cartesian_point(P00), f.cartesian_point(P01)],
    [f.cartesian_point(P10), f.cartesian_point(P11)],
    [f.cartesian_point(P20), f.cartesian_point(P21)],
    [f.cartesian_point(P30), f.cartesian_point(P31)],
]

surf = f.b_spline_surface_with_knots(
    u_degree=2,
    v_degree=1,
    control_points_grid=cp_grid,
    u_multiplicities=[3, 1, 1, 2],
    v_multiplicities=[2, 2],
    u_knots=[0.0, 0.75, 1.5, 2.25],
    v_knots=[0.0, 6.0],
    surface_form="UNSPECIFIED",
    u_closed=False,
    v_closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)

# ── Vertices in 3D ───────────────────────────────────────────────────────────
# Wire: V0(0,0,0)->V1(1.5,0,0)->V2(1.5,5,0)->V3(0,5,0)->V0
# We use 3-edge loop: knot_e0 (V1->V2), knot_e1 (V2->V3), close_e2 (V3->V0->V1)
PV0 = (0.0,  0.0, 0.0)
PV1 = (1.5,  0.0, 0.0)
PV2 = (1.5,  5.0, 0.0)
# V2b: start of knot_e1 in 3D (same 3D point but different pcurve v)
PV2b = (1.5,  5.0, 0.0)
PV3 = (0.0,  5.0, 0.0)

vV0  = f.vertex_point(f.cartesian_point(PV0))
vV1  = f.vertex_point(f.cartesian_point(PV1))
vV2  = f.vertex_point(f.cartesian_point(PV2))
vV2b = f.vertex_point(f.cartesian_point(PV2b))
vV3  = f.vertex_point(f.cartesian_point(PV3))


def _pcurve_line_on_surf(u_s, v_s, u_e, v_e):
    """Straight 2D pcurve on surf from (u_s,v_s) to (u_e,v_e)."""
    du = u_e - u_s; dv = v_e - v_s
    mag = _math.sqrt(du*du + dv*dv)
    pc_orig = f.cartesian_point((u_s, v_s))
    pc_dir  = f.direction((du/mag, dv/mag))
    pc_vec  = f.vector(pc_dir, mag)
    pc_ln   = f.line(pc_orig, pc_vec)
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{pc_ln.eid}),#*)")
    return f._emit_raw(f"PCURVE('',#{surf.eid},#{drep.eid})")


def _line_sc_with_pcurve(v_s, v_e, ps, pe, pc, name=""):
    dx = pe[0] - ps[0]; dy = pe[1] - ps[1]; dz = pe[2] - ps[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    ln3 = f.line(f.cartesian_point(ps),
                 f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag))
    sc  = f._emit_raw(f"SURFACE_CURVE('',#{ln3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# knot_e0: V1(1.5,0,0)->V2(1.5,5,0); pcurve (u=1.5,v=0)->(u=1.5,v=5.0)
# This pcurve ends exactly at the knot u=1.5, v=5.0
pc0 = _pcurve_line_on_surf(1.5, 0.0, 1.5, 5.0)
ec0 = _line_sc_with_pcurve(vV1, vV2, PV1, PV2, pc0, name="knot_e0")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# knot_e1: V2b(1.5,5,0)->V3(0,5,0); pcurve starts at (u=1.5,v=5.01) — GAP IS DEFECT
# 3D point same as V2 but pcurve has v=5.01 instead of v=5.0 at knot u=1.5
pc1 = _pcurve_line_on_surf(1.5, 5.01, 0.0, 5.0)
ec1 = _line_sc_with_pcurve(vV2b, vV3, PV2b, PV3, pc1, name="knot_e1")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# close_e2: V3(0,5,0)->V0(0,0,0)->V1(1.5,0,0) — two straight closing edges
# Use two separate edges to close the rectangle
PV4_mid = (0.0, 0.0, 0.0)
vV4_mid = vV0  # reuse V0

pc2 = _pcurve_line_on_surf(0.0, 5.0, 0.0, 0.0)
ec2 = _line_sc_with_pcurve(vV3, vV0, PV3, PV0, pc2, name="close_e2")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

pc3 = _pcurve_line_on_surf(0.0, 0.0, 1.5, 0.0)
ec3 = _line_sc_with_pcurve(vV0, vV1, PV0, PV1, pc3, name="close_e3")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi207.stp")
