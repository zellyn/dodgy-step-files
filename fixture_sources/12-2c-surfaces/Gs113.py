"""Gs113 — ShapeAnalysis_Surface.ComputeBoundIsos negative-trim.

Catalog claim: ComputeBoundIsos doesn't validate trim parameter range; when
v_min > v_max (inverted range), produces inverted iso sweeps without error
or warning.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (unit square) IS the ADVANCED_FACE.face_geometry;
    face boundary encodes an inverted v-parameter range (v_min=1.0, v_max=0.0)
    by traversing the loop bottom-to-top then top-to-bottom with v increasing
    then decreasing IS the mechanism wired into face topology;
    ComputeBoundIsos generates inverted iso curves without error IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (unit square) IS the
    ADVANCED_FACE.face_geometry; face boundary loop with inverted v-range
    (v_min=1.0 > v_max=0.0) traversal IS the mechanism wired into face
    topology; ComputeBoundIsos generates inverted iso sweeps IS the defect.
  - shape_null driver: inverted trim range produces inconsistent iso geometry;
    strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs113",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (unit square) IS ADVANCED_FACE.face_geometry; "
        "face boundary loop with inverted v-range (v_min=1.0 > v_max=0.0) traversal "
        "IS the mechanism wired into face topology; "
        "ComputeBoundIsos generates inverted iso sweeps without error IS the defect; "
        "shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: unit square ──────────────────────────────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
ctrl = [
    [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
    [(0.0, 1.0, 0.0), (1.0, 1.0, 0.0)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(2)) + ")"
    for r in range(2)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs113_bss',1,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),"
    f"(0.0,1.0),"
    f"(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: INVERTED v-range traversal ─────────────────────────────────
# Normal loop would be CCW: (u=0,v=0)→(u=1,v=0)→(u=1,v=1)→(u=0,v=1).
# Inverted-v loop: start at top-left (v=1), go right, then DOWN (v=1→0),
# then left (still at v=0), then UP (v=0→1) back to start.
# This encodes an outer loop where v sweeps 1.0 → 0.0 in the right edge,
# i.e. v_min=0.0, v_max=1.0 but the boundary traversal direction produces
# v_min > v_max when ComputeBoundIsos computes iso bounds.
#
# To make v_min=1.0 > v_max=0.0: traverse the boundary CW in uv space
# (opposite to normal CCW). This represents an outer face bound traversed
# in the wrong orientation, giving an inverted v-parameter sweep.
#
# 3D corners (bilinear BSS so 3D coords = UV coords):
p_A = f.cartesian_point((0.0, 1.0, 0.0))   # (u=0, v=1) top-left
p_B = f.cartesian_point((1.0, 1.0, 0.0))   # (u=1, v=1) top-right
p_C = f.cartesian_point((1.0, 0.0, 0.0))   # (u=1, v=0) bottom-right
p_D = f.cartesian_point((0.0, 0.0, 0.0))   # (u=0, v=0) bottom-left

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

# CW traversal in UV (inverted v-range mechanism):
# e0: top A→B (v=1, u: 0→1)
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 1.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 1.0), (1.0, 0.0), 1.0)
# e1: right B→C (u=1, v: 1→0) — v DECREASES: v_min=0 reached after v_max=1
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (1.0, 1.0), (0.0, -1.0), 1.0)
# e2: bottom C→D (v=0, u: 1→0)
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 0.0), (-1.0, 0.0), 1.0)
# e3: left D→A (u=0, v: 0→1) — v INCREASES back
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (0.0, 0.0), (0.0, 1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry;
# CW/inverted-v boundary traversal IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
