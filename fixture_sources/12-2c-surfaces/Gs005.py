"""Gs005 — Surface periodicity not declared but actually closed.

Catalog claim: A B_SPLINE_SURFACE_WITH_KNOTS whose first and last control rows
coincide is geometrically closed but u_closed is set to .F. Receivers that do
not explicitly test for geometric closure fall back to non-periodic cases and
produce wrong results at the wraparound.

OCC behavior: silently accepts (no diagnostic, empty result).
Expected: occt=empty. Closure intent: reject.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS u_closed=.F. IS the ADVANCED_FACE.face_geometry.
    First control row (y=0) coincides with last control row (y=0) within 1e-7.
    Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS('),
                     count(b'(10.0,0.0,0.0)') >= 2.
  - Tier-3 assertion: shape_null == True.
  - Four line edges with SURFACE_CURVE/PCURVE wire the surface into the face.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS with u_closed=.F. but
    rows[i,0] == rows[i,N] IS the ADVANCED_FACE.face_geometry; inconsistency
    between declared flag and geometric closure drives shape_null=True.
  - shape_null driver: kernel enforcing heal-or-reject on inconsistent periodicity
    flag produces null shape.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs005",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS u_closed=.F. but first/last control rows "
        "coincide at (10.0,0.0,0.0) within 1e-7; declared non-periodic but "
        "geometrically closed; IS ADVANCED_FACE.face_geometry; shape_null=True"
    ),
)

# ── CATALOG MECHANISM: BSpline surface, u_closed=.F., first==last row ────────
# Degree 1×1, 5×2 control net.
# U direction has 5 rows; row[0] and row[4] both at y=0 → geometrically u-closed.
# Byte assertion: (10.0,0.0,0.0) appears at least twice (row[0][1] and row[4][1]).
# Row layout (u along first index, v along second):
#   u=0:   (0,0,0), (10,0,0)
#   u=pi/2: (0,5,0), (10,5,0)
#   u=pi:   (0,0,5), (10,0,5)
#   u=3pi/2:(0,-5,0),(10,-5,0)
#   u=2pi:  (0,0,0), (10,0,0)   ← same as u=0 → closed but .F. declared

def cp(x, y, z):
    return f.cartesian_point((x, y, z))

# Rows 0..4 in U, 2 columns in V
r0 = [cp(0.0,  0.0, 0.0), cp(10.0,  0.0, 0.0)]
r1 = [cp(0.0,  5.0, 0.0), cp(10.0,  5.0, 0.0)]
r2 = [cp(0.0,  0.0, 5.0), cp(10.0,  0.0, 5.0)]
r3 = [cp(0.0, -5.0, 0.0), cp(10.0, -5.0, 0.0)]
r4 = [cp(0.0,  0.0, 0.0), cp(10.0,  0.0, 0.0)]  # == r0 → geom closed

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)},{row_ids(r3)},{row_ids(r4)})"

# Degree 1 in U (5 rows → knots (0,1,2,3,4) mults (2,1,1,1,2) sum=8=1+5+1+1=8 ✓)
# Degree 1 in V (2 cols → knots (0,1) mults (2,2) sum=4=1+2+1 ✓)
# u_closed=.F. despite rows[0]==rows[4] — this is the declared defect
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs005_notclosed',1,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,1,1,1,2),(2,2),"
    f"(0.0,1.0,2.0,3.0,4.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Four line edges wiring the face loop ─────────────────────────────────────
# Use a small rectangular patch on the surface, u in [0,1], v in [0,1].
# Corner 3D coords (u=0,v=0)=(0,0,0); (u=1,v=0)=(0,5,0); (u=1,v=1)=(10,5,0); (u=0,v=1)=(10,0,0)
corners_3d = [
    (0.0,  0.0, 0.0),
    (0.0,  5.0, 0.0),
    (10.0, 5.0, 0.0),
    (10.0, 0.0, 0.0),
]
corners_uv = [
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0),
]

verts = [f.vertex_point(f.cartesian_point(c)) for c in corners_3d]

def mk_line_edge(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

# Bottom: v0→v1 (u: 0→1, v=0)
e0 = mk_line_edge(verts[0], verts[1],
    (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 5.0,
    (0.0, 0.0),      (1.0, 0.0),       1.0)
# Right: v1→v2 (v: 0→1, u=1)
e1 = mk_line_edge(verts[1], verts[2],
    (0.0, 5.0, 0.0), (1.0, 0.0, 0.0), 10.0,
    (1.0, 0.0),      (0.0, 1.0),       1.0)
# Top: v2→v3 (u: 1→0, v=1)
e2 = mk_line_edge(verts[2], verts[3],
    (10.0, 5.0, 0.0), (0.0, -1.0, 0.0), 5.0,
    (1.0, 1.0),        (-1.0, 0.0),       1.0)
# Left: v3→v0 (v: 1→0, u=0)
e3 = mk_line_edge(verts[3], verts[0],
    (10.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 10.0,
    (0.0, 1.0),        (0.0, -1.0),       1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
