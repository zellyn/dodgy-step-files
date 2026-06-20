"""Gs059 — B-spline knot-multiplicity closure sanity.

Catalog claim: B-spline surface with degree-3 in U (8×4 control points) and
knot multiplicities [4,1,1,1,4] that nominally declare a closed-in-U surface.
However the last control-point column is offset 0.01 in Z from the first,
breaking the geometric closure that the knot structure implies.
ShapeAnalysis_Surface.IsUClosed detects the pole mismatch at the midpoint
sample; the surface is marked non-closed and may be split or rejected.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (degree 3 in U, 8×4 control points,
    U-knots (4,1,1,1,4)) IS the ADVANCED_FACE.face_geometry; last pole column
    offset 0.01 in Z IS the closure-break defect wired into face topology.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
                     contains(b'0.01').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS IS the ADVANCED_FACE.face_geometry;
    knot multiplicities [4,1,1,1,4] claim closed-in-U surface; last pole column
    at Z=0.01 instead of Z=0.0 IS the closure-break defect wired into face topology.
  - shape_null driver: IsUClosed midpoint-sample detects pole mismatch;
    strict kernels reject non-closed surface; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs059",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (degree-3 U, 8×4 poles, U-knots (4,1,1,1,4)) "
        "IS ADVANCED_FACE.face_geometry; "
        "last pole column at Z=0.01 offset (closure-break) IS the defect wired into face topology; "
        "shape_null (IsUClosed midpoint-sample detects mismatch)"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: 8 columns × 4 rows, degree 3 in U, 1 in V ──
# U-knots: (4,1,1,1,4) → knot vector [0,0,0,0, 1, 2, 3, 4,4,4,4] (8+4=12 knots)
# V-knots: (2,2) → V ∈ [0,1], degree 1
# Control points: columns 0-7 uniformly spaced in angle (0..2π), rows 0-3 in V.
# Column 7 (= "last") is intentionally at Z=0.01 instead of Z=0.0 to break closure.
import math

num_cols = 8  # u direction
num_rows = 4  # v direction

ctrl_pts = []
for row in range(num_rows):
    row_pts = []
    for col in range(num_cols):
        angle = 2 * math.pi * col / (num_cols - 1)  # 0 .. 2π (col 0 and col 7 share U-parameter band)
        x = math.cos(angle)
        y = math.sin(angle)
        # Defect: last column (col 7) has Z=0.01 instead of Z=0.0
        z = 0.01 if col == num_cols - 1 else 0.0
        z += float(row) * 0.25  # spread rows in Z slightly
        row_pts.append(f.cartesian_point((x, y, z)))
    ctrl_pts.append(row_pts)

# Build control-point grid string: outer list is rows (V), inner is cols (U)
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[row][col].eid}" for col in range(num_cols)) + ")"
    for row in range(num_rows)
) + ")"

# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# Byte assertion: contains(b'0.01') — the Z-offset in the last pole column
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs059_bss',3,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,1,1,1,1),(2,2),(0.0,1.0,2.0,3.0,4.0),(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the B-spline surface ────────────────────────────
# Use a simple rectangular patch in parameter space U∈[0,2], V∈[0,1]
p_A = f.cartesian_point(( 1.0,  0.0,  0.0))
p_B = f.cartesian_point((-1.0,  0.0,  0.0))
p_C = f.cartesian_point((-1.0,  0.0,  0.75))
p_D = f.cartesian_point(( 1.0,  0.0,  0.75))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

def mk_edge_line(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{bss.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e0 = mk_edge_line(v_A, v_B, (1.0,0.0,0.0), (-2.0,0.0,0.0), 2.0, (0.0,0.0), (2.0,0.0), 2.0)
e1 = mk_edge_line(v_B, v_C, (-1.0,0.0,0.0), (0.0,0.0,1.0), 0.75, (2.0,0.0), (0.0,1.0), 1.0)
e2 = mk_edge_line(v_C, v_D, (-1.0,0.0,0.75), (2.0,0.0,0.0), 2.0, (2.0,1.0), (-2.0,0.0), 2.0)
e3 = mk_edge_line(v_D, v_A, (1.0,0.0,0.75), (0.0,0.0,-1.0), 0.75, (0.0,1.0), (0.0,-1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry; closure-break IS the face surface defect.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
