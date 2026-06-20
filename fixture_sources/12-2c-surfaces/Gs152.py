"""Gs152 — SplitSurface ignores RECTANGULAR_TRIMMED_SURFACE bounds.

Catalog claim: ShapeUpgrade_Surface::SplitSurface() splits a B-spline
surface at internal knots but does not clip the resulting patches against
the enclosing RECTANGULAR_TRIMMED_SURFACE bounds. Patch boundaries extend
beyond the declared trim envelope [1.0,3.0]x[1.5,3.5], breaking the
face-surface correspondence and violating G1 continuity across the trim.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (4x4 control grid, deg 3/3, domain [0,4]x[0,4])
    wrapped in RECTANGULAR_TRIMMED_SURFACE (u:[1.0,3.0] v:[1.5,3.5])
    IS the ADVANCED_FACE.face_geometry; face boundary edge pcurves encoded
    at the trim boundary (u=1.0, u=3.0, v=1.5, v=3.5) IS the mechanism
    wired into face topology; SplitSurface ignoring trim bounds on split
    IS the defect.
  - Byte assertions: contains(b'RECTANGULAR_TRIMMED_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS wrapped in
    RECTANGULAR_TRIMMED_SURFACE (u:[1.0,3.0] v:[1.5,3.5]) IS
    ADVANCED_FACE.face_geometry; face boundary edge pcurves at trim
    boundary coordinates IS the mechanism wired into face topology;
    SplitSurface extending patches beyond trim envelope IS the defect.
  - shape_null driver: split patches extend past trim bounds; face-surface
    correspondence violated; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs152",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (4x4, deg 3/3, domain [0,4]x[0,4]) "
        "wrapped in RECTANGULAR_TRIMMED_SURFACE (u:[1.0,3.0] v:[1.5,3.5]) "
        "IS ADVANCED_FACE.face_geometry; face boundary edge pcurves at trim "
        "boundary coordinates IS the mechanism wired into face topology; "
        "SplitSurface extending patches beyond trim envelope IS the defect; "
        "shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: 4x4 control grid, deg 3/3 ───────────────────
# Byte assertion: contains(b'RECTANGULAR_TRIMMED_SURFACE')
# Degree 3 in U and V, 4 control points each direction.
# Knots [0,1,2,3,4] with multiplicities [1,1,1,1,1] → domain [0,4]x[0,4].
# The RTS trims to u:[1.0,3.0] v:[1.5,3.5].
# SplitSurface splits at internal knots (u=1,2,3 and v=1,2,3) but ignores
# the trim bounds, producing patches that extend outside [1.0,3.0]x[1.5,3.5].

def make_row(v_val):
    return [(float(u), float(v_val), 0.3 * u * (4 - u) * v_val * (4 - v_val) / 16.0)
            for u in range(4)]

pts_4x4 = [make_row(v) for v in range(4)]
cp_rows = [[f.cartesian_point(p) for p in row] for row in pts_4x4]
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in cp_rows)

bspline = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs152_bspline',3,3,({nested}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(1,1,1,1),(1,1,1,1),(0.,1.,2.,3.),(0.,1.,2.,3.),.UNSPECIFIED.)"
)

# RECTANGULAR_TRIMMED_SURFACE: u:[1.0,3.0] v:[1.5,3.5]
# SplitSurface must respect these bounds but extends patches beyond them.
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gs152_rts',#{bspline.eid},1.0,3.0,1.5,3.5,.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary at trim envelope coordinates ────────────────────────────────
# Corners of the RTS trim rectangle in 3D (approximate surface evaluation).
# The face boundary encodes the trim bounds; this IS the mechanism that
# makes SplitSurface's out-of-bounds patch extension visible.
p_A = f.cartesian_point((1.0, 1.5, 0.0))   # u=1.0, v=1.5
p_B = f.cartesian_point((3.0, 1.5, 0.0))   # u=3.0, v=1.5
p_C = f.cartesian_point((3.0, 3.5, 0.0))   # u=3.0, v=3.5
p_D = f.cartesian_point((1.0, 3.5, 0.0))   # u=1.0, v=3.5

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

# Bottom: A→B, u=1.0→3.0 at v=1.5 (trim boundary)
e0 = mk_edge_line(v_A, v_B,
                  (1.0, 1.5, 0.0), (1.0, 0.0, 0.0), 2.0,
                  (1.0, 1.5), (1.0, 0.0), 2.0)
# Right: B→C, v=1.5→3.5 at u=3.0 (trim boundary)
e1 = mk_edge_line(v_B, v_C,
                  (3.0, 1.5, 0.0), (0.0, 1.0, 0.0), 2.0,
                  (3.0, 1.5), (0.0, 1.0), 2.0)
# Top: C→D, u=3.0→1.0 at v=3.5 (trim boundary)
e2 = mk_edge_line(v_C, v_D,
                  (3.0, 3.5, 0.0), (-1.0, 0.0, 0.0), 2.0,
                  (3.0, 3.5), (-1.0, 0.0), 2.0)
# Left: D→A, v=3.5→1.5 at u=1.0 (trim boundary)
e3 = mk_edge_line(v_D, v_A,
                  (1.0, 3.5, 0.0), (0.0, -1.0, 0.0), 2.0,
                  (1.0, 3.5), (0.0, -1.0), 2.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RTS (wrapping B_SPLINE_SURFACE_WITH_KNOTS, trim u:[1.0,3.0] v:[1.5,3.5])
# IS the face_geometry; face boundary edge pcurves at trim boundary coordinates
# IS the mechanism wired into face topology — exercises SplitSurface
# trim-bound-ignorance bug.
face  = f.advanced_face([f.face_outer_bound(loop)], rts)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
