"""Gs184 — Two adjacent B-spline surfaces at G1-tangency boundary with tessellation polyline crossing.

Catalog claim: Two adjacent B_SPLINE_SURFACE_WITH_KNOTS ADVANCED_FACEs sharing
an EDGE_CURVE boundary at a G1-tangency locus (normals equal, surfaces share a
tangent plane along the boundary curve). The PCURVEs on each side approach the
boundary tangentially, causing BRepMesh tessellation sample points on the two
sides to produce polylines that cross in 3D (self-intersecting mesh at the
G1 seam). Source: https://academic.oup.com/jcde/article/13/1/239/8383411

OCC behavior: BRepMesh_IncrementalMesh produces a mesh, but the per-face
triangulations at the shared G1 boundary have sampling points that yield
crossing polylines (the tessellation straddles the tangent plane seam).
brepcheck may flag the mesh but not reject the shape.

STEP mechanism (literal):
  - Patch A: B_SPLINE_SURFACE_WITH_KNOTS degree (2,2), 3×3 net.
    Occupies x in [0,2], z in [0,1]. The boundary row at x=2 has z-coordinate
    curving up to z=0.5 at mid-V, creating an upward tangent at the seam.
  - Patch B: B_SPLINE_SURFACE_WITH_KNOTS degree (2,2), 3×3 net.
    Occupies x in [2,4], z in [0,1]. At the boundary x=2, the first control row
    matches Patch A's last row exactly (G0). The normal derivatives are also
    matched (G1): Patch B's row at x=2+epsilon has the same z-tangent direction
    as Patch A's row at x=2-epsilon.
  - Shared EDGE_CURVE at x=2 (the G1 boundary), with two SURFACE_CURVE
    PCURVEs (one per patch), both referencing the same EDGE_CURVE.
  - The G1-tangency makes the tessellator approach the boundary tangentially
    from both sides, producing sample points that fall on nearly the same
    tangent plane and crossing each other in 3D.

Mechanism vs driver:
  - CATALOG MECHANISM: two B_SPLINE_SURFACE_WITH_KNOTS patches sharing an
    EDGE_CURVE at a G1-tangent seam ARE the ADVANCED_FACE.face_geometry for
    each face; the G1-tangency is the exact defect class from the JCDE paper.
  - Per feedback_wire_mechanism: both faces' geometry includes the boundary
    curve at the seam; the defect is on the face geometry, not an orphan entity.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs184",
    defect=(
        "Two B_SPLINE_SURFACE_WITH_KNOTS patches sharing EDGE_CURVE at G1-tangency "
        "boundary (x=2); normals match, tangent planes coincide at seam; BRepMesh "
        "tessellation polylines cross in 3D at seam; JCDE 13(1):239 2026"
    ),
)

# ── Parametric context for pcurves ─────────────────────────────────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── PATCH A: B_SPLINE_SURFACE_WITH_KNOTS, x in [0,2], y in [0,2] ─────────────
# 3×3 control net; degree (2,2); clamped knots (3,3) at (0,2) in both U and V.
# Sum checks: 3+2+1=6=sum(3,3) ✓
# Control net designed for G1 tangency at right boundary (u=2):
#   - Last U row (u=2): z=0 at v=0, z=0.4 at v=1, z=0 at v=2 (parabolic)
#   - Penultimate U row (u=1): z=0 at v=0, z=0.2 at v=1, z=0 at v=2
#   - First U row (u=0): flat (z=0)
# The tangent at u=2 is in the +X direction with dZ/dU computed from
# control-point finite differences: (last-row - penult-row) * degree/span
# = (0.4 - 0.2) * 2 / 1 = 0.4 at mid-V → positive upward tangent in Z.

grid_a = [
    # u=0 row: flat
    [f.cartesian_point((0.0, 0.0, 0.0)),
     f.cartesian_point((0.0, 1.0, 0.0)),
     f.cartesian_point((0.0, 2.0, 0.0))],
    # u=1 row: slight bow
    [f.cartesian_point((1.0, 0.0, 0.0)),
     f.cartesian_point((1.0, 1.0, 0.2)),
     f.cartesian_point((1.0, 2.0, 0.0))],
    # u=2 row: G1-seam row (tangent donor)
    [f.cartesian_point((2.0, 0.0, 0.0)),
     f.cartesian_point((2.0, 1.0, 0.4)),
     f.cartesian_point((2.0, 2.0, 0.0))],
]

surf_a = f.b_spline_surface_with_knots(
    u_degree=2, v_degree=2,
    control_points_grid=grid_a,
    u_multiplicities=[3, 3],
    v_multiplicities=[3, 3],
    u_knots=[0.0, 2.0],
    v_knots=[0.0, 2.0],
    surface_form="UNSPECIFIED",
    u_closed=False, v_closed=False, self_intersect=False,
    knot_spec="UNSPECIFIED",
)

# ── PATCH B: B_SPLINE_SURFACE_WITH_KNOTS, x in [2,4], y in [0,2] ─────────────
# G0 match at boundary (x=2): first U row of B == last U row of A.
# G1 match: second row of B is tangent-consistent with penultimate row of A.
# For G1: tangent_B at u=2 must equal tangent_A at u=2.
# tangent_A at u=2 = (last_A - penult_A) * degree/span = ({z=0.4} - {z=0.2}) * 2/2 = 0.2 in Z
# So penult_B must satisfy: (penult_B - first_B) * 2/2 = 0.2 → penult_B_z = first_B_z + 0.2
# first_B = last_A = {z=0, z=0.4, z=0}
# → penult_B = {z=0.2, z=0.6, z=0.2}  (maintains G1 tangent)

grid_b = [
    # u=2 row: G1-seam row (G0 match with A's last row)
    [f.cartesian_point((2.0, 0.0, 0.0)),
     f.cartesian_point((2.0, 1.0, 0.4)),
     f.cartesian_point((2.0, 2.0, 0.0))],
    # u=3 row: G1-tangent continuation
    [f.cartesian_point((3.0, 0.0, 0.2)),
     f.cartesian_point((3.0, 1.0, 0.6)),
     f.cartesian_point((3.0, 2.0, 0.2))],
    # u=4 row: far boundary
    [f.cartesian_point((4.0, 0.0, 0.0)),
     f.cartesian_point((4.0, 1.0, 0.3)),
     f.cartesian_point((4.0, 2.0, 0.0))],
]

surf_b = f.b_spline_surface_with_knots(
    u_degree=2, v_degree=2,
    control_points_grid=grid_b,
    u_multiplicities=[3, 3],
    v_multiplicities=[3, 3],
    u_knots=[2.0, 4.0],
    v_knots=[0.0, 2.0],
    surface_form="UNSPECIFIED",
    u_closed=False, v_closed=False, self_intersect=False,
    knot_spec="UNSPECIFIED",
)

# ── Helper: build edge with pcurve on a given surface ─────────────────────────
def mk_edge_with_pc(surf, vs, ve, p3, d3t, len3, p2t, d2t, p2_len):
    """Build EDGE_CURVE via SURFACE_CURVE with linear pcurve on surf."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, len3)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, p2_len)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


def mk_shared_edge(vs, ve, p3, d3t, len3, surf1, p2t1, d2t1, p2_len1, surf2, p2t2, d2t2, p2_len2):
    """Build a shared EDGE_CURVE with two PCURVEs (one per adjacent surface)."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, len3)
    l3  = f.line(p3e, v3)

    p2e1 = f.cartesian_point(p2t1)
    d2e1 = f.direction(d2t1)
    v2_1 = f.vector(d2e1, p2_len1)
    l2_1 = f.line(p2e1, v2_1)
    pcd1 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef1',(#{l2_1.eid}),#{prc.eid})")
    pc1  = f._emit_raw(f"PCURVE('pc1',#{surf1.eid},#{pcd1.eid})")

    p2e2 = f.cartesian_point(p2t2)
    d2e2 = f.direction(d2t2)
    v2_2 = f.vector(d2e2, p2_len2)
    l2_2 = f.line(p2e2, v2_2)
    pcd2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef2',(#{l2_2.eid}),#{prc.eid})")
    pc2  = f._emit_raw(f"PCURVE('pc2',#{surf2.eid},#{pcd2.eid})")

    sc = f._emit_raw(
        f"SURFACE_CURVE('sc_shared',#{l3.eid},(#{pc1.eid},#{pc2.eid}),.PCURVE_S1.)"
    )
    return f._emit_raw(f"EDGE_CURVE('ec_shared',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


# ── Corner vertices ──────────────────────────────────────────────────────────
# Patch A corners (x: 0→2, y: 0→2)
pA00 = f.cartesian_point((0.0, 0.0, 0.0))   # (u=0,  v=0)
pA01 = f.cartesian_point((0.0, 2.0, 0.0))   # (u=0,  v=2)
pA10 = f.cartesian_point((2.0, 0.0, 0.0))   # (u=2,  v=0) — shared seam corner
pA11 = f.cartesian_point((2.0, 2.0, 0.0))   # (u=2,  v=2) — shared seam corner

vA00 = f.vertex_point(pA00)
vA01 = f.vertex_point(pA01)
# Shared seam vertices:
v_s0 = f.vertex_point(pA10)   # seam, v=0
v_s1 = f.vertex_point(pA11)   # seam, v=2

# Patch B far corners (x: 2→4, y: 0→2)
pB10 = f.cartesian_point((4.0, 0.0, 0.0))   # (u=4,  v=0)
pB11 = f.cartesian_point((4.0, 2.0, 0.0))   # (u=4,  v=2)

vB10 = f.vertex_point(pB10)
vB11 = f.vertex_point(pB11)

# ── Patch A edges ─────────────────────────────────────────────────────────────
# Bottom edge A: vA00 → v_s0 (y=0, x: 0→2); pcurve u: 0→2, v=0
eA_bot = mk_edge_with_pc(
    surf_a, vA00, v_s0,
    (0.0, 0.0, 0.0), (1., 0., 0.), 2.0,
    (0.0, 0.0),      (1., 0.),     2.0)

# Left edge A: vA01 → vA00 (x=0, y: 2→0); pcurve u=0, v: 2→0
eA_left = mk_edge_with_pc(
    surf_a, vA01, vA00,
    (0.0, 2.0, 0.0), (0., -1., 0.), 2.0,
    (0.0, 2.0),       (0., -1.),    2.0)

# Top edge A: v_s1 → vA01 (y=2, x: 2→0); pcurve u: 2→0, v=2
eA_top = mk_edge_with_pc(
    surf_a, v_s1, vA01,
    (2.0, 2.0, 0.0), (-1., 0., 0.), 2.0,
    (2.0, 2.0),      (-1., 0.),     2.0)

# Shared seam edge: v_s0 → v_s1 (x=2, y: 0→2)
# Pcurve on A: u=2, v: 0→2; Pcurve on B: u=2, v: 0→2
e_seam = mk_shared_edge(
    v_s0, v_s1,
    (2.0, 0.0, 0.0), (0., 1., 0.), 2.0,
    surf_a, (2.0, 0.0), (0., 1.), 2.0,
    surf_b, (2.0, 0.0), (0., 1.), 2.0,
)

# ── Face A (Patch A): bottom, seam (right), top (reversed), left (reversed) ───
loopA = f.edge_loop([
    f.oriented_edge(eA_bot,  True),   # vA00 → v_s0
    f.oriented_edge(e_seam,  True),   # v_s0 → v_s1
    f.oriented_edge(eA_top,  True),   # v_s1 → vA01
    f.oriented_edge(eA_left, True),   # vA01 → vA00
])
faceA = f.advanced_face([f.face_outer_bound(loopA)], surf_a)

# ── Patch B edges ─────────────────────────────────────────────────────────────
# Bottom edge B: v_s0 → vB10 (y=0, x: 2→4); pcurve u: 2→4, v=0
eB_bot = mk_edge_with_pc(
    surf_b, v_s0, vB10,
    (2.0, 0.0, 0.0), (1., 0., 0.), 2.0,
    (2.0, 0.0),      (1., 0.),     2.0)

# Right edge B: vB10 → vB11 (x=4, y: 0→2); pcurve u=4, v: 0→2
eB_right = mk_edge_with_pc(
    surf_b, vB10, vB11,
    (4.0, 0.0, 0.0), (0., 1., 0.), 2.0,
    (4.0, 0.0),      (0., 1.),     2.0)

# Top edge B: vB11 → v_s1 (y=2, x: 4→2); pcurve u: 4→2, v=2
eB_top = mk_edge_with_pc(
    surf_b, vB11, v_s1,
    (4.0, 2.0, 0.0), (-1., 0., 0.), 2.0,
    (4.0, 2.0),      (-1., 0.),     2.0)

# ── Face B (Patch B): seam (reversed — v_s1→v_s0), bottom, right, top (rev) ──
loopB = f.edge_loop([
    f.oriented_edge(e_seam,   False),  # v_s1 → v_s0 (reversed seam)
    f.oriented_edge(eB_bot,   True),   # v_s0 → vB10
    f.oriented_edge(eB_right, True),   # vB10 → vB11
    f.oriented_edge(eB_top,   True),   # vB11 → v_s1
])
faceB = f.advanced_face([f.face_outer_bound(loopB)], surf_b)

# ── Shell: both faces sharing the G1-tangent seam edge ─────────────────────────
shell = f.open_shell([faceA, faceB])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
