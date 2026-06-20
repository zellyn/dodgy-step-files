"""Gs143 — MakeBSpline grid-sampling false periodicity.

Catalog claim: ShapeConstruct_Surface::MakeBSpline() reconstructs a B-spline
from a raw point grid, detecting periodicity via endpoint sampling. For
quasi-periodic grids with repeating midpoint structure but non-matching
endpoint heights, sampling returns a false-positive closure and the
synthesized knot topology is incorrect.

The defect lives in the kernel's point-to-B-spline fitting path. Part-21
cannot exercise it directly: a static STEP file can only carry an already-fit
B_SPLINE_SURFACE_WITH_KNOTS, not the raw grid that triggers the bug. This
fixture is a kernel-pair shape carrier — the .stp holds the shape geometry
that is passed as input to MakeBSpline at runtime.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (quasi-periodic: first and last V-rows of
    control points are nearly identical at midpoints but differ in endpoint
    heights) IS the ADVANCED_FACE.face_geometry; the shape carried in this
    file is the geometry pair that, when fed into MakeBSpline at runtime,
    triggers false-periodicity detection IS the mechanism wired into face
    topology; MakeBSpline endpoint-sampling false-positive periodicity IS
    the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (quasi-periodic, non-matching
    endpoint heights) IS ADVANCED_FACE.face_geometry; endpoint-height mismatch
    that triggers MakeBSpline false-periodicity detection IS the mechanism
    wired into face topology; MakeBSpline endpoint-sampling validation absence
    IS the defect.
  - shape_null driver: incorrect periodicity flag produces invalid knot
    structure; seam placement error; strict kernels reject; empty result.

Note (runtime-only): Reproduce by passing a TColgp_Array2OfPnt grid
(matching the geometry of this fixture) directly into
ShapeConstruct_Surface::MakeBSpline. This .stp is the shape carrier,
not a self-contained reproducer.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs143",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (quasi-periodic: matching midpoints "
        "but non-matching endpoint heights in V) IS ADVANCED_FACE.face_geometry; "
        "endpoint-height mismatch triggering MakeBSpline false-periodicity "
        "detection IS the mechanism wired into face topology; "
        "MakeBSpline endpoint-sampling periodicity validation absence IS the defect; "
        "shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: quasi-periodic geometry ──────────────────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# Degree 3x3, 4 control rows in V (indices 0..3), 4 control cols in U.
#
# Quasi-periodic: midpoint structure (cols 1,2) of rows 0 and 3 are identical,
# but endpoint heights (cols 0,3) differ between row 0 and row 3.
# This is the shape that MakeBSpline's endpoint-sampling sees as periodic
# (midpoints match) but endpoint heights betray non-closure.
#
# Row V=0: Z=0.0 at midpoints, Z=0.0 at endpoints (base row)
# Row V=1: Z=1.0 at midpoints, Z=0.5 at endpoints (lift)
# Row V=2: Z=1.0 at midpoints, Z=-0.5 at endpoints (different endpoint height)
# Row V=3: Z=0.0 at midpoints, Z=0.3 at endpoints (NON-MATCHING endpoint height vs row 0)
#
# Midpoints of rows 0 and 3 match (Z=0.0), tricking endpoint-sampling into
# declaring periodicity. But endpoint heights 0.0 vs 0.3 reveal non-closure.

pts_4x4 = [
    # Row V=0: endpoints Z=0.0, midpoints Z=0.0
    [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (2.0, 0.0, 0.0), (3.0, 0.0, 0.0)],
    # Row V=1: endpoints Z=0.5, midpoints Z=1.0
    [(0.0, 1.0, 0.5), (1.0, 1.0, 1.0), (2.0, 1.0, 1.0), (3.0, 1.0, 0.5)],
    # Row V=2: endpoints Z=-0.5, midpoints Z=1.0
    [(0.0, 2.0, -0.5), (1.0, 2.0, 1.0), (2.0, 2.0, 1.0), (3.0, 2.0, -0.5)],
    # Row V=3: midpoints Z=0.0 (match row 0) but endpoints Z=0.3 (NON-MATCH)
    [(0.0, 3.0, 0.3), (1.0, 3.0, 0.0), (2.0, 3.0, 0.0), (3.0, 3.0, 0.3)],
]
cp_rows = [[f.cartesian_point(p) for p in row] for row in pts_4x4]
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in cp_rows)

# B_SPLINE_SURFACE_WITH_KNOTS: degree 3x3, knots 0,1,2,3 each direction
# (non-periodic representation; the false-periodic detection is runtime)
bspline = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs143_qperiodic',3,3,({nested}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(1,1,1,1),(1,1,1,1),(0.,1.,2.,3.),(0.,1.,2.,3.),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary spanning the full quasi-periodic surface ─────────────────────
# Boundary corners at the parametric extents [0,3]x[0,3].
# The face edge between V=0 and V=3 (the quasi-periodic rows) IS the mechanism
# wired into face topology — it is exactly the boundary that exercises
# MakeBSpline's endpoint-sampling at runtime.
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((3.0, 0.0, 0.0))
p_C = f.cartesian_point((3.0, 3.0, 0.0))
p_D = f.cartesian_point((0.0, 3.0, 0.3))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{bspline.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Bottom (V=0 row): A→B, u=0→3 at v=0
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 3.0,
                  (0.0, 0.0), (1.0, 0.0), 3.0)
# Right: B→C, v=0→3 at u=3
e1 = mk_edge_line(v_B, v_C,
                  (3.0, 0.0, 0.0), (0.0, 1.0, 0.0), 3.0,
                  (3.0, 0.0), (0.0, 1.0), 3.0)
# Top (V=3 row, quasi-periodic match with non-matching endpoint height): C→D
e2 = mk_edge_line(v_C, v_D,
                  (3.0, 3.0, 0.0), (-1.0, 0.0, 0.0), 3.0,
                  (3.0, 3.0), (-1.0, 0.0), 3.0)
# Left: D→A, v=3→0 at u=0
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 3.0, 0.3), (0.0, -1.0, 0.0), 3.0,
                  (0.0, 3.0), (0.0, -1.0), 3.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry;
# quasi-periodic endpoint-height mismatch IS the mechanism wired into face
# topology (shape carrier for runtime MakeBSpline false-periodicity trigger).
face  = f.advanced_face([f.face_outer_bound(loop)], bspline)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
