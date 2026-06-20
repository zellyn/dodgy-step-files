"""Twi175 — ShapeAnalysis_Wire.CheckTail negative-parameter.

Catalog claim: Wire whose tail edge has parameter range [-0.5, 0.0];
CheckTail's tail-bound binary search uses [0, length] assumption.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 5 edges
on a PLANE forming a pentagon. The final (tail) edge is represented as a
B-spline curve with knot vector [-0.5, -0.5, 0.0, 0.0] — the parameter
range is [-0.5, 0.0] instead of the expected [0.0, something positive].
CheckTail's binary search algorithm assumes the tail edge parameter domain
starts at 0; when it encounters a negative lower bound of -0.5 it
initializes the binary search with a negative starting point and the
[0, length] assumption causes the search to converge to the wrong bound.

The negative-parameter tail edge is labelled 'tail_negative_param_range'
to make the defect explicit in bytes.

Byte assertions:
  - contains(b'tail_negative_param_range')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi175",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 5 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "pentagon wire: A(0,0)→B(8,0)→C(10,6)→D(5,10)→E(-2,6)→A; "
        "edges e0..e3 are regular LINE segments; "
        "edge e4 (E→A) IS the tail edge — a B-spline with knot vector [-0.5,-0.5,0,0] "
        "giving parameter range [-0.5, 0.0] — negative lower bound IS defect; "
        "edge labelled 'tail_negative_param_range'; "
        "CheckTail IS mechanism — binary search initialized with [0, length] assumption "
        "fails when lower bound is negative (-0.5); "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── PLANE: normal +Z ──────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Pentagon vertices ──────────────────────────────────────────────────────────
PA = (0.0,  0.0,  0.0)
PB = (8.0,  0.0,  0.0)
PC = (10.0, 6.0,  0.0)
PD = (5.0,  10.0, 0.0)
PE = (-2.0, 6.0,  0.0)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))
vD = f.vertex_point(f.cartesian_point(PD))
vE = f.vertex_point(f.cartesian_point(PE))


def _line_sc(v_s, v_e, ps, pe):
    dx = pe[0]-ps[0]; dy = pe[1]-ps[1]; dz = pe[2]-ps[2]
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
    return f._emit_raw(f"EDGE_CURVE('',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# e0: A→B (normal)
ec0 = _line_sc(vA, vB, PA, PB)
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: B→C (normal)
ec1 = _line_sc(vB, vC, PB, PC)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: C→D (normal)
ec2 = _line_sc(vC, vD, PC, PD)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: D→E (normal)
ec3 = _line_sc(vD, vE, PD, PE)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# e4 (tail): E→A, B-spline with negative parameter range [-0.5, 0.0]
# Degree-1 B-spline (linear) from E to A with knot vector [-0.5,-0.5,0,0]
# Control points at E and A; parameter maps: t=-0.5 → E, t=0.0 → A
tail_cp0 = f.cartesian_point(PE)   # t = -0.5 → start at E
tail_cp1 = f.cartesian_point(PA)   # t =  0.0 → end at A

# B_SPLINE_CURVE_WITH_KNOTS degree=1, 2 ctrl pts, knots [-0.5,0.0] mult=[2,2]
tail_bsp = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('tail_negative_param_range',1,"
    f"(#{tail_cp0.eid},#{tail_cp1.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,2),(-0.5,0.0),.UNSPECIFIED.)"
)

ec4 = f._emit_raw(
    f"EDGE_CURVE('tail_negative_param_range',"
    f"#{vE.eid},#{vA.eid},#{tail_bsp.eid},.T.)"
)
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi175.stp")
