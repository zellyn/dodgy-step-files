"""Gs100 — SplitSurface trim-aware split: splits base not trimmed wrapper.

Catalog claim: ShapeUpgrade_SplitSurface.Build() processes
RECTANGULAR_TRIMMED_SURFACE by extracting and splitting the base surface,
ignoring the trim bounds. Result: split patches extend beyond original trim,
creating invalid geometry.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - RECTANGULAR_TRIMMED_SURFACE wrapping a B_SPLINE_SURFACE_WITH_KNOTS
    (trimmed to [0.25, 0.75]×[0.25, 0.75]) IS the ADVANCED_FACE.face_geometry;
    face boundary follows the trim bounds IS the mechanism wired into face
    topology; SplitSurface.Build() splits the base B-spline at u=0.5 ignoring
    trim, producing patches that extend to [0,0.5]×[0,1] and [0.5,1]×[0,1]
    rather than respecting [0.25,0.75]×[0.25,0.75] IS the defect.
  - Byte assertions: contains(b'RECTANGULAR_TRIMMED_SURFACE'),
                     contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: RECTANGULAR_TRIMMED_SURFACE (u1=0.25, u2=0.75, v1=0.25,
    v2=0.75) wrapping B_SPLINE_SURFACE_WITH_KNOTS IS the
    ADVANCED_FACE.face_geometry; face boundary on trimmed domain IS the
    mechanism wired into face topology; SplitSurface ignores trim, splits base
    surface, produces out-of-trim patches IS the defect.
  - shape_null driver: split patches violate trim bounds; strict kernels
    reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs100",
    defect=(
        "RECTANGULAR_TRIMMED_SURFACE (u1=0.25,u2=0.75,v1=0.25,v2=0.75) "
        "wrapping B_SPLINE_SURFACE_WITH_KNOTS IS ADVANCED_FACE.face_geometry; "
        "face boundary on trimmed domain IS the mechanism wired into face "
        "topology; SplitSurface.Build() splits base ignoring trim, producing "
        "out-of-trim patches IS the defect; shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: unit square base surface ─────────────────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
ctrl = [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(2)) + ")"
    for r in range(2)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs100_bss',1,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),"
    f"(0.0,1.0),"
    f"(0.0,1.0),.UNSPECIFIED.)"
)

# ── RECTANGULAR_TRIMMED_SURFACE: trim to [0.25,0.75]×[0.25,0.75] ─────────────
# Byte assertion: contains(b'RECTANGULAR_TRIMMED_SURFACE')
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gs100_rts',#{bss.eid},0.25,0.75,0.25,0.75,.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: rectangle on trimmed domain [0.25,0.75]×[0.25,0.75] ───────
# 3D points corresponding to trimmed surface corners (bilinear, so 3D = UV):
p_A = f.cartesian_point((0.25, 0.25, 0.0))
p_B = f.cartesian_point((0.75, 0.25, 0.0))
p_C = f.cartesian_point((0.75, 0.75, 0.0))
p_D = f.cartesian_point((0.25, 0.75, 0.0))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{rts.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# e0: bottom A→B (v=0.25, u: 0.25→0.75)
e0 = mk_edge_line(v_A, v_B,
                  (0.25, 0.25, 0.0), (1.0, 0.0, 0.0), 0.5,
                  (0.25, 0.25), (1.0, 0.0), 0.5)
# e1: right B→C (u=0.75, v: 0.25→0.75)
e1 = mk_edge_line(v_B, v_C,
                  (0.75, 0.25, 0.0), (0.0, 1.0, 0.0), 0.5,
                  (0.75, 0.25), (0.0, 1.0), 0.5)
# e2: top C→D (v=0.75, u: 0.75→0.25)
e2 = mk_edge_line(v_C, v_D,
                  (0.75, 0.75, 0.0), (-1.0, 0.0, 0.0), 0.5,
                  (0.75, 0.75), (-1.0, 0.0), 0.5)
# e3: left D→A (u=0.25, v: 0.75→0.25)
e3 = mk_edge_line(v_D, v_A,
                  (0.25, 0.75, 0.0), (0.0, -1.0, 0.0), 0.5,
                  (0.25, 0.75), (0.0, -1.0), 0.5)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RECTANGULAR_TRIMMED_SURFACE IS the face_geometry; trimmed-domain boundary IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], rts)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
