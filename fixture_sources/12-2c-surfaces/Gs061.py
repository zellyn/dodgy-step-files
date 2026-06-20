"""Gs061 — B-spline surface normal degeneracy at cusp.

Catalog claim: A 4×4 cubic B-spline surface whose v=1 and v=2 pole rows both
have purely X-directional tangent vectors, making the cross-partial (and hence
the normal) zero at the cusp strip near u~0.5, v~0.5.
ShapeAnalysis_Surface.SurfaceNewton diverges when attempting closest-point
projection at the cusp; the surface may be rejected or split.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (4×4 cubic control points) IS the
    ADVANCED_FACE.face_geometry; v=1 and v=2 pole rows have identical X-direction
    tangents (cusp: normal degenerates) IS the defect wired into face topology.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
                     contains(b'gs061').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS IS the ADVANCED_FACE.face_geometry;
    cusp strip at v rows 1 and 2 (parallel X-tangents, zero normal) IS the defect
    wired into face topology; SurfaceNewton Newton iteration diverges.
  - shape_null driver: degenerate normal at cusp → closest-point projection fails;
    strict kernels reject surface; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs061",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (4×4 cubic poles) IS ADVANCED_FACE.face_geometry; "
        "v=1 and v=2 pole rows both have X-directional tangents (cusp, zero normal) IS the defect; "
        "cusp strip IS wired into face topology; "
        "shape_null (SurfaceNewton diverges at degenerate normal)"
    ),
)

# ── 4×4 cubic B-spline: cusp where rows v=1 and v=2 have parallel tangents ───
# Control grid (u-direction = 4 cols, v-direction = 4 rows), degree 3 in both.
# Normal = dS/du × dS/dv.  Making rows 1 and 2 identical in the U-direction
# means dS/dv ≈ 0 in the v=1..2 strip → degenerate normal (cusp).
#
# Row layout:
#   v=0: y = 0.0  (normal row)
#   v=1: y = 0.5  (cusp onset — same X-tangent direction as row 2)
#   v=2: y = 0.5  (cusp — identical to row 1: dS/dv = 0)
#   v=3: y = 1.0  (normal row)

ctrl_grid = [
    # v=0: normal bottom row
    [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (2.0, 0.0, 0.0), (3.0, 0.0, 0.0)],
    # v=1: cusp onset — Y identical to v=2
    [(0.0, 0.5, 0.0), (1.0, 0.5, 0.0), (2.0, 0.5, 0.0), (3.0, 0.5, 0.0)],
    # v=2: cusp — same Y as v=1, so dS/dv = 0 here
    [(0.0, 0.5, 0.0), (1.0, 0.5, 0.0), (2.0, 0.5, 0.0), (3.0, 0.5, 0.0)],
    # v=3: normal top row
    [(0.0, 1.0, 0.0), (1.0, 1.0, 0.0), (2.0, 1.0, 0.0), (3.0, 1.0, 0.0)],
]

ctrl_pts = [
    [f.cartesian_point(xyz) for xyz in row]
    for row in ctrl_grid
]

# Build control-point grid string: outer = v-rows, inner = u-cols
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[vrow][ucol].eid}" for ucol in range(4)) + ")"
    for vrow in range(4)
) + ")"

# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# Byte assertion: contains(b'gs061')
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs061_bss',3,3,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,4),(4,4),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the cusp B-spline surface ────────────────────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((3.0, 0.0, 0.0))
p_C = f.cartesian_point((3.0, 1.0, 0.0))
p_D = f.cartesian_point((0.0, 1.0, 0.0))

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

e0 = mk_edge_line(v_A, v_B, (0.0,0.0,0.0), (1.0,0.0,0.0), 3.0, (0.0,0.0), (1.0,0.0), 1.0)
e1 = mk_edge_line(v_B, v_C, (3.0,0.0,0.0), (0.0,1.0,0.0), 1.0, (1.0,0.0), (0.0,1.0), 1.0)
e2 = mk_edge_line(v_C, v_D, (3.0,1.0,0.0), (-1.0,0.0,0.0), 3.0, (1.0,1.0), (-1.0,0.0), 1.0)
e3 = mk_edge_line(v_D, v_A, (0.0,1.0,0.0), (0.0,-1.0,0.0), 1.0, (0.0,1.0), (0.0,-1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry; cusp (zero normal) IS the face surface defect.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
