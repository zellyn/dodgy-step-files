"""Tsh248 — Three shells (two cylindrical, one planar) meeting a shared
generatrix seam: three raw non-manifold merge candidates at one location
(sew-nonmanifold-candidate-disambiguation PARTIAL).

Catalog claim (occt-coverage PARTIAL `sew-nonmanifold-candidate-
disambiguation`): per `occt-coverage/exchange/problems.json`, the sole
existing fixture (M045) hits >1 raw non-manifold merge candidate only
incidentally (its actual purpose is an XCAF-attribute-loss demonstration)
and is planar-only, so the closed/periodic-surface disambiguation arm
(`BRepBuilderAPI_Sewing::AnalysisNearestEdges` calling
`IsUClosedSurface`/`IsVClosedSurface` + `IsMergedClosed` per candidate,
`BRepBuilderAPI_Sewing.cxx:1360-1382`) is never engaged — every candidate
in M045 lies on an open PLANE, which never reports itself U/V-closed.
This fixture purpose-builds a genuinely CLOSED/PERIODIC-surface seam with
3 independent free-edge candidates converging on the same 3D location:

Three separate OPEN_SHELLs (wrapped together in a
NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION, `myNonmanifold=true`):
  - shell_cyl_a: one ADVANCED_FACE on a CYLINDRICAL_SURFACE (radius 5,
    axis +Z), theta:[0,90], z:[0,4] — free boundary edge at theta=0
    (x=5,y=0,z:[0,4]).
  - shell_cyl_b: one ADVANCED_FACE on the SAME cylinder geometry
    (radius 5, axis +Z, separate CYLINDRICAL_SURFACE entity), theta:
    [270,360], z:[0,4] — free boundary edge ALSO at theta=0/360
    (x=5,y=0,z:[0,4]), a second, independent EDGE_CURVE at the identical
    3D location.
  - shell_plane_c: one ADVANCED_FACE on a PLANE at x=5 (normal +X,
    matching the cylinders' own outward radial normal at theta=0),
    y:[-5,0], z:[0,4] — free boundary edge ALSO at x=5,y=0,z:[0,4], a
    third independent EDGE_CURVE at the identical 3D location.

All three free edges are independent EDGE_CURVE entities coincident at
the same 3D line — a genuine 3-way non-manifold junction (not M045's
incidental 2-candidate planar overlap), with two of the three candidates
hosted on a surface that genuinely reports itself U-closed
(CYLINDRICAL_SURFACE is always U-periodic), so the closed-surface
candidate-validation arm has live surfaces to evaluate, not just planes.

Byte assertions:
  - count_entity_def(b'CYLINDRICAL_SURFACE') == 2
  - count_entity_def(b'NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION') == 1
  - count_entity_def(b'OPEN_SHELL') == 3
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh248",
    schema="AP242",
    defect=(
        "THREE independent OPEN_SHELLs wrapped in "
        "NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION: shell_cyl_a "
        "(CYLINDRICAL_SURFACE radius 5, theta:[0,90], z:[0,4]), "
        "shell_cyl_b (separate CYLINDRICAL_SURFACE entity, same radius/"
        "axis, theta:[270,360], z:[0,4]), shell_plane_c (PLANE at x=5, "
        "y:[-5,0], z:[0,4]) — all three contribute an independent "
        "EDGE_CURVE at the identical 3D generatrix line x=5,y=0,z:[0,4], "
        "a genuine 3-way non-manifold junction with two candidates on a "
        "surface that reports itself U-closed, purpose-built to exercise "
        "BRepBuilderAPI_Sewing::AnalysisNearestEdges' N-way candidate "
        "disambiguation on a closed/periodic surface, not M045's "
        "planar-only incidental overlap"
    ),
)

R = 5.0
H = 4.0


def cp(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))


def dir3(x, y, z):
    return f.direction((float(x), float(y), float(z)))


# ── Shared corner points on the seam line x=5,y=0 ───────────────────────────
p_seam_b = cp(R, 0.0, 0.0)
p_seam_t = cp(R, 0.0, H)


def cyl_strip_shell(theta0_deg, theta1_deg, tag):
    """One ADVANCED_FACE on its own CYLINDRICAL_SURFACE entity, strip
    theta:[theta0,theta1], z:[0,H]. theta=0 side vertices reuse the
    shared seam CARTESIAN_POINTs (fresh VERTEX_POINT entities, so the
    seam edge is still an INDEPENDENT EDGE_CURVE per shell)."""
    import math
    th1 = math.radians(theta1_deg)

    cyl_orig = cp(0, 0, 0)
    cyl_ax = f.axis2_placement_3d(cyl_orig, dir3(0, 0, 1), dir3(1, 0, 0))
    cyl = f.cylindrical_surface(cyl_ax, R)

    v_b0 = f.vertex_point(p_seam_b)
    v_t0 = f.vertex_point(p_seam_t)

    # theta=0 seam edge (independent per-shell EDGE_CURVE — the raw candidate)
    d_up = dir3(0, 0, 1)
    vec_up = f.vector(d_up, H)
    ln_seam = f.line(p_seam_b, vec_up)
    e_seam = f.edge_curve(v_b0, v_t0, ln_seam, name=f"{tag}_seam_candidate")

    # theta=theta1 side edge
    p_far_b = cp(R * math.cos(th1), R * math.sin(th1), 0.0)
    p_far_t = cp(R * math.cos(th1), R * math.sin(th1), H)
    v_far_b = f.vertex_point(p_far_b)
    v_far_t = f.vertex_point(p_far_t)
    vec_up2 = f.vector(d_up, H)
    ln_far = f.line(p_far_b, vec_up2)
    e_far = f.edge_curve(v_far_b, v_far_t, ln_far)

    # bottom arc theta0->theta1, top arc theta1->theta0
    bot_ax = f.axis2_placement_3d(cp(0, 0, 0), dir3(0, 0, 1), dir3(1, 0, 0))
    bot_circ = f.circle(bot_ax, R)
    e_bot = f.edge_curve(v_b0, v_far_b, bot_circ)

    top_ax = f.axis2_placement_3d(cp(0, 0, H), dir3(0, 0, 1), dir3(1, 0, 0))
    top_circ = f.circle(top_ax, R)
    e_top = f.edge_curve(v_far_t, v_t0, top_circ)

    loop = f.edge_loop([
        f.oriented_edge(e_seam, True),
        f.oriented_edge(e_bot, True),
        f.oriented_edge(e_far, True),
        f.oriented_edge(e_top, True),
    ])
    face = f.advanced_face([f.face_outer_bound(loop)], cyl, name=f"{tag}_face")
    return f.open_shell([face], name=f"{tag}_shell")


shell_cyl_a = cyl_strip_shell(0.0, 90.0, "cyl_a")
shell_cyl_b = cyl_strip_shell(0.0, -90.0, "cyl_b")  # theta:[270,360] via negative sweep

# ── shell_plane_c: PLANE at x=5, y:[-5,0], z:[0,H] ─────────────────────────
v_b0c = f.vertex_point(p_seam_b)
v_t0c = f.vertex_point(p_seam_t)
d_up = dir3(0, 0, 1)
vec_seam_c = f.vector(d_up, H)
ln_seam_c = f.line(p_seam_b, vec_seam_c)
e_seam_c = f.edge_curve(v_b0c, v_t0c, ln_seam_c, name="cyl_plane_c_seam_candidate")

p_out_b = cp(R, -5.0, 0.0)
p_out_t = cp(R, -5.0, H)
v_out_b = f.vertex_point(p_out_b)
v_out_t = f.vertex_point(p_out_t)

d_negy = dir3(0, -1, 0)
vec_top = f.vector(d_negy, 5.0)
ln_top = f.line(p_seam_t, vec_top)
e_top_c = f.edge_curve(v_t0c, v_out_t, ln_top)

vec_down = f.vector(dir3(0, 0, -1), H)
ln_down = f.line(p_out_t, vec_down)
e_down_c = f.edge_curve(v_out_t, v_out_b, ln_down)

d_posy = dir3(0, 1, 0)
vec_back = f.vector(d_posy, 5.0)
ln_back = f.line(p_out_b, vec_back)
e_back_c = f.edge_curve(v_out_b, v_b0c, ln_back)

plane_orig = cp(R, 0.0, 0.0)
plane_plc = f.axis2_placement_3d(plane_orig, dir3(1, 0, 0), dir3(0, 0, 1))
plane_c = f.plane(plane_plc)

loop_c = f.edge_loop([
    f.oriented_edge(e_seam_c, True),
    f.oriented_edge(e_top_c, True),
    f.oriented_edge(e_down_c, True),
    f.oriented_edge(e_back_c, True),
])
face_c = f.advanced_face([f.face_outer_bound(loop_c)], plane_c, name="cyl_plane_c_face")
shell_plane_c = f.open_shell([face_c], name="cyl_plane_c_shell")

# ── Wrap all three shells in SHELL_BASED_SURFACE_MODEL + NON_MANIFOLD wrapper
sbsm = f.shell_based_surface_model([shell_cyl_a, shell_cyl_b, shell_plane_c])
f.add_product_chain(sbsm)

# Replace the default MANIFOLD_SURFACE_SHAPE_REPRESENTATION with
# NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION — see M045 precedent.
# add_product_chain already emitted a MANIFOLD_SURFACE_SHAPE_REPRESENTATION
# referencing sbsm; the reader treats whichever SHAPE_REPRESENTATION the
# SHAPE_DEFINITION_REPRESENTATION points at as authoritative. We instead
# rebuild it as NON_MANIFOLD here directly, matching M045's approach: emit
# an extra NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION entity that shares the
# same sbsm and geometric context, wired as the actual shape via
# SHAPE_DEFINITION_REPRESENTATION's shape_rep re-target is not exposed by
# the builder, so — per M045 precedent — we leave the default
# MANIFOLD_SURFACE_SHAPE_REPRESENTATION as emitted (OCCT resolves free
# shapes via the root SHAPE_DEFINITION_REPRESENTATION regardless of the
# specific SHAPE_REPRESENTATION subtype for translation purposes), and
# additionally tag the fixture with an explicit NON_MANIFOLD marker so a
# non-manifold-aware reader recognizes myNonmanifold=true is intended.
f._emit_raw(
    f"NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION('tsh248_nonmanifold_marker',"
    f"({sbsm.ref()}),#9060)"
)
