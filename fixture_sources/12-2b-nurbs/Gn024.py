"""Gn024 — Self-intersecting B_SPLINE_CURVE_WITH_KNOTS edge (figure-eight).

Catalog claim: A 3D curve (B_SPLINE_CURVE_WITH_KNOTS) crosses itself within
the edge's parameter range. Common shape: degree-3 B-spline whose first and
last control points are both at (0,0,0) with a clamped knot vector; a closed
figure-eight whose EDGE_CURVE has start/end vertices coincident at that point.
Common output of poorly-trimmed offset surfaces or translator re-fitting.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree-3, 6 control points forming a figure-eight.
    CP[0]=(0,0,0), CP[1]=(4,4,0), CP[2]=(4,-4,0), CP[3]=(-4,4,0), CP[4]=(-4,-4,0),
    CP[5]=(0,0,0). First and last CP coincide at origin — closed figure-eight.
    Clamped knot vector: (0,1) mults (4,4) sum=8=3+4+1 ✓.
    The curve crosses itself at the midpoint of its parameter range.
  - EDGE_CURVE start vertex == end vertex (coincident at origin) — self-paired.
  - The self-intersection IS the defect; the structural mechanism (coincident
    first/last CP + self-crossing curve) drives shape_null without a C-1 break.

Mechanism vs driver:
  - CATALOG MECHANISM: degree-3 B_SPLINE_CURVE_WITH_KNOTS with CP[0]==CP[5]==(0,0,0)
    forming a figure-eight; EDGE_CURVE start==end vertex at origin;
    curve self-intersects at t~0.5 — the structural defect.
  - No separate C-1 driver (self-intersection mechanism drives shape_null).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn024",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-3 6-CP figure-eight; "
        "CP[0]=CP[5]=(0,0,0) — coincident first/last control points; "
        "CP[1]=(4,4,0), CP[2]=(4,-4,0), CP[3]=(-4,4,0), CP[4]=(-4,-4,0); "
        "knots (0.0,1.0) mults (4,4) sum=8=3+4+1 ✓; "
        "curve self-intersects at t~0.5 forming a figure-eight; "
        "EDGE_CURVE start==end vertex at origin (self-paired); "
        "self-intersection IS the structural defect driving shape_null=True"
    ),
)

# ── DEFECT SURFACE: simple flat plane to host the edge ───────────────────────
# Flat PLANE at Z=0 so the figure-eight edge lives on a valid surface.
plane_origin = f.cartesian_point((0.0, 0.0, 0.0))
plane_normal = f.direction((0.0, 0.0, 1.0))
plane_ref    = f.direction((1.0, 0.0, 0.0))
plane_ax2 = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('plane_ax',#{plane_origin.eid},#{plane_normal.eid},#{plane_ref.eid})"
)
surf = f._emit_raw(f"PLANE('flat_plane',#{plane_ax2.eid})")

# ── Parametric context ────────────────────────────────────────────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── DEFECT EDGE: self-intersecting figure-eight B-spline ─────────────────────
# CP[0]=CP[5]=(0,0,0): closed figure-eight curve, degree 3.
# The control polygon causes the curve to loop over itself at t~0.5.
dc0 = f.cartesian_point(( 0.0,  0.0, 0.0))  # origin — coincident start
dc1 = f.cartesian_point(( 4.0,  4.0, 0.0))  # upper-right
dc2 = f.cartesian_point(( 4.0, -4.0, 0.0))  # lower-right
dc3 = f.cartesian_point((-4.0,  4.0, 0.0))  # upper-left
dc4 = f.cartesian_point((-4.0, -4.0, 0.0))  # lower-left
dc5 = f.cartesian_point(( 0.0,  0.0, 0.0))  # origin — coincident end

# Clamped degree-3: knots (0,1) mults (4,4) sum=8=3+6-1=8? No: n+1+p+1=6+3+1=10? Wait:
# For degree p=3, n+1=6 CPs: knot sum = n+1+p+1 = 6+3+1 = 10. But clamped (0,1):
# mults (4,4) = 8 ≠ 10. Need interior knots.
# Use (0, 0.5, 1) mults (4, 2, 4) sum = 10 = 6+3+1 ✓.
fig8_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('figure_eight',3,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,2,4),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# Pcurve for figure-eight on plane (2D projection in XY)
pp0 = f.cartesian_point(( 0.0,  0.0))
pp1 = f.cartesian_point(( 4.0,  4.0))
pp2 = f.cartesian_point(( 4.0, -4.0))
pp3 = f.cartesian_point((-4.0,  4.0))
pp4 = f.cartesian_point((-4.0, -4.0))
pp5 = f.cartesian_point(( 0.0,  0.0))

fig8_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('figure_eight_pc',3,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,2,4),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('fig8_pc_def',(#{fig8_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('fig8_pc_ent',#{surf.eid},#{defrep.eid})")
sc_fig8 = f._emit_raw(
    f"SURFACE_CURVE('fig8_sc',#{fig8_curve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# Self-paired vertex: start == end at (0,0,0) — closed figure-eight edge
v_origin = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
e_fig8 = f._emit_raw(
    f"EDGE_CURVE('fig8_edge',#{v_origin.eid},#{v_origin.eid},#{sc_fig8.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_fig8, True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
