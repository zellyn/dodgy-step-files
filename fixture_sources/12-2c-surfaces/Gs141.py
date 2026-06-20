"""Gs141 — FixMissingSeam RectangularTrimmedSurface bound mismatch.

Catalog claim: FixMissingSeam() wraps base surface in RECTANGULAR_TRIMMED_SURFACE
using computed bounds [u1,u2]x[v1,v2]. For base surfaces with non-unit-range
knot structure, RTS bounds mismatch parametric extents, placing seam at wrong
location. Geometry distorted.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS with non-unit knot range [0,3]x[0,3] IS the
    ADVANCED_FACE.face_geometry (wrapped in RECTANGULAR_TRIMMED_SURFACE with
    bounds matching unit range [0,1]x[0,1] that mismatch the parametric extents);
    seam placement at wrong UV location IS the mechanism wired into face topology;
    FixMissingSeam RTS-bounds mismatch IS the defect.
  - Byte assertions: contains(b'RECTANGULAR_TRIMMED_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (knot range [0,3]x[0,3])
    IS face_geometry via RECTANGULAR_TRIMMED_SURFACE with mismatched bounds
    [0,1]x[0,1] IS the mechanism wired into face topology;
    FixMissingSeam RTS parametric-range mismatch IS the defect.
  - shape_null driver: seam at wrong UV; boundary distortion; strict kernels
    reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs141",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (non-unit knot range [0,3]x[0,3]) "
        "IS ADVANCED_FACE.face_geometry via RECTANGULAR_TRIMMED_SURFACE "
        "with mismatched unit bounds [0,1]x[0,1] "
        "IS the mechanism wired into face topology; "
        "FixMissingSeam RTS parametric-range mismatch IS the defect; shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: non-unit knot range [0,3]x[0,3] ──────────────
# Byte assertion: contains(b'RECTANGULAR_TRIMMED_SURFACE')
# Degree 2x2, 3x3 control points, knots [0,1,2,3] in each direction.
# This gives parametric range [0,3] in U and V.
# FixMissingSeam wraps it in RTS with bounds [0,1]x[0,1] — mismatch.
pts_3x3 = [
    [(0.0, 0.0, 0.0), (1.5, 0.0, 0.5), (3.0, 0.0, 0.0)],
    [(0.0, 1.5, 0.5), (1.5, 1.5, 1.0), (3.0, 1.5, 0.5)],
    [(0.0, 3.0, 0.0), (1.5, 3.0, 0.5), (3.0, 3.0, 0.0)],
]
cp_rows = [[f.cartesian_point(p) for p in row] for row in pts_3x3]
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in cp_rows)

# B_SPLINE_SURFACE_WITH_KNOTS: degree 2x2, knots [0,1,2,3] multiplicities [1,1,1,1]
# This gives parametric domain [0,3] not [0,1].
bspline = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs141_bspline',2,2,({nested}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(1,1,1),(1,1,1),(0.,1.,2.,3.),(0.,1.,2.,3.),.UNSPECIFIED.)"
)

# RECTANGULAR_TRIMMED_SURFACE wrapping the B-spline with unit bounds [0,1]x[0,1]
# This mismatches the actual parametric range [0,3]x[0,3].
# FixMissingSeam uses these wrong bounds to place the seam.
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gs141_rts',#{bspline.eid},0.,1.,0.,1.,.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square in parameter space (matching RTS bounds) ────────
# Face boundary uses the RTS's stated bounds [0,1]x[0,1], which places the
# seam at u=1 — but parametrically this is only 1/3 of the actual surface.
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((3.0, 0.0, 0.0))
p_C = f.cartesian_point((3.0, 3.0, 0.0))
p_D = f.cartesian_point((0.0, 3.0, 0.0))

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

# Boundary edges at RTS stated bounds [0,1]x[0,1] — but actual knot range is [0,3]
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 3.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
e1 = mk_edge_line(v_B, v_C,
                  (3.0, 0.0, 0.0), (0.0, 1.0, 0.0), 3.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
e2 = mk_edge_line(v_C, v_D,
                  (3.0, 3.0, 0.0), (-1.0, 0.0, 0.0), 3.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 3.0, 0.0), (0.0, -1.0, 0.0), 3.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RTS (wrapping B_SPLINE_SURFACE_WITH_KNOTS with non-unit knot range)
# IS the face_geometry; mismatched RTS bounds IS the mechanism wired into
# face topology.
face  = f.advanced_face([f.face_outer_bound(loop)], rts)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
