"""Gs058 — SURFACE_PATCH transition_code / u_sense / v_sense parsed but ignored.

Catalog claim: SURFACE_PATCH carries u_transition / v_transition
(CONT_SAME_GRADIENT_SAME_CURVATURE) and u_sense / v_sense booleans that
specify C2-continuity at patch boundaries.  BRL-CAD step-g parses both into
class members via Load but never reads them back in LoadONBrep; correct knot
multiplicity (degree-2 at C2 boundaries) is never applied.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - RECTANGULAR_COMPOSITE_SURFACE(segments=((SURFACE_PATCH,...))) IS the
    ADVANCED_FACE.face_geometry; SURFACE_PATCH with
    transition_code=CONT_SAME_GRADIENT_SAME_CURVATURE IS the defect entity
    whose continuity metadata is parsed but never applied; defect IS wired
    into face topology.
  - Byte assertions: contains(b'SURFACE_PATCH'),
                     contains(b'CONT_SAME_GRADIENT_SAME_CURVATURE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: RECTANGULAR_COMPOSITE_SURFACE IS the ADVANCED_FACE.face_geometry;
    SURFACE_PATCH(.CONT_SAME_GRADIENT_SAME_CURVATURE.,.CONT_SAME_GRADIENT_SAME_CURVATURE.,.T.,.F.)
    IS the defect whose transition metadata is ignored; ignored continuity IS
    wired into face topology; kink introduced at C2 boundary.
  - shape_null driver: incorrect knot multiplicity → wrong surface; strict
    warn-and-proceed kernels reject or emit empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs058",
    defect=(
        "RECTANGULAR_COMPOSITE_SURFACE IS ADVANCED_FACE.face_geometry; "
        "SURFACE_PATCH(.CONT_SAME_GRADIENT_SAME_CURVATURE.,.CONT_SAME_GRADIENT_SAME_CURVATURE.,.T.,.F.) "
        "IS defect entity whose C2 continuity metadata is parsed but never applied; "
        "ignored transition_code IS wired into face topology; shape_null (strict reject)"
    ),
)

# ── Two B-spline patches (degree-3 in U, degree-1 in V) ──────────────────────
# Patch 0: [0,1]×[0,1] — cubic in U so C2 promotion at U=1 requires mult=degree-2=1
p0_cp = [
    [f.cartesian_point((float(u), float(v), 0.0)) for v in range(2)]
    for u in range(4)
]
# Flatten control points row-major for the raw emit
cp0_str = "(" + ",".join(
    "(" + ",".join(f"#{p.eid}" for p in row) + ")"
    for row in p0_cp
) + ")"
patch0_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs058_p0',3,1,"
    f"{cp0_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,4),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

# Patch 1: [1,2]×[0,1]
p1_cp = [
    [f.cartesian_point((float(u)+1.0, float(v), 0.0)) for v in range(2)]
    for u in range(4)
]
cp1_str = "(" + ",".join(
    "(" + ",".join(f"#{p.eid}" for p in row) + ")"
    for row in p1_cp
) + ")"
patch1_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs058_p1',3,1,"
    f"{cp1_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,4),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

# ── SURFACE_PATCHes: C2 continuity declared but will be ignored ───────────────
# Byte assertion: contains(b'SURFACE_PATCH')
# Byte assertion: contains(b'CONT_SAME_GRADIENT_SAME_CURVATURE')
sp0 = f._emit_raw(
    f"SURFACE_PATCH(#{patch0_surf.eid},"
    f".CONT_SAME_GRADIENT_SAME_CURVATURE.,.CONT_SAME_GRADIENT_SAME_CURVATURE.,.T.,.F.)"
)
sp1 = f._emit_raw(
    f"SURFACE_PATCH(#{patch1_surf.eid},"
    f".CONT_SAME_GRADIENT_SAME_CURVATURE.,.CONT_SAME_GRADIENT_SAME_CURVATURE.,.T.,.F.)"
)

# ── RECTANGULAR_COMPOSITE_SURFACE: 1×2 patch grid ────────────────────────────
rcs = f._emit_raw(
    f"RECTANGULAR_COMPOSITE_SURFACE('gs058_rcs',((#{sp0.eid},#{sp1.eid})))"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the RECTANGULAR_COMPOSITE_SURFACE ────────────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((2.0, 0.0, 0.0))
p_C = f.cartesian_point((2.0, 1.0, 0.0))
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
    pc  = f._emit_raw(f"PCURVE('pc',#{rcs.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e0 = mk_edge_line(v_A, v_B, (0.0,0.0,0.0), (1.0,0.0,0.0), 2.0, (0.0,0.0), (1.0,0.0), 2.0)
e1 = mk_edge_line(v_B, v_C, (2.0,0.0,0.0), (0.0,1.0,0.0), 1.0, (2.0,0.0), (0.0,1.0), 1.0)
e2 = mk_edge_line(v_C, v_D, (2.0,1.0,0.0), (-1.0,0.0,0.0), 2.0, (2.0,1.0), (-1.0,0.0), 2.0)
e3 = mk_edge_line(v_D, v_A, (0.0,1.0,0.0), (0.0,-1.0,0.0), 1.0, (0.0,1.0), (0.0,-1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RECTANGULAR_COMPOSITE_SURFACE IS the face_geometry; ignored C2 metadata IS the face surface defect.
face  = f.advanced_face([f.face_outer_bound(loop)], rcs)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
