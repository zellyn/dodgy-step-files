"""Tfa212 — ShapeFix_Face.FixMissingSeam.bspline-non-periodic-rejection

Non-periodic B-spline surface (knot vectors [0.0,1.0]) with closed EDGE_LOOP.
FixMissingSeam must reject seam synthesis on non-periodic surfaces, delegating
to wire-fix path instead.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a B_SPLINE_SURFACE_WITH_KNOTS.
The surface is degree-1 bilinear (2×2 control net), with knot vectors [0.0,1.0]
and multiplicities [2,2] in both U and V. The u_closed and v_closed flags are
False, making this explicitly a non-periodic surface. The face has a closed
quad EDGE_LOOP (4 edges forming a unit square). The OCCT FixMissingSeam code
path at line 1744 checks the IsClosed() / IsUPeriodic() / IsVPeriodic() flags;
for this B-spline surface both return False, so seam synthesis is skipped and
the wire-fix path is invoked instead.

Byte assertions:
  - contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa212",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on B_SPLINE_SURFACE_WITH_KNOTS; "
        "degree 1 bilinear, 2×2 control net, knots [0.0,1.0] × [0.0,1.0]; "
        "u_closed=False, v_closed=False: explicitly non-periodic surface; "
        "closed quad EDGE_LOOP on non-periodic B-spline surface; "
        "FixMissingSeam line 1744: conformance-probe detects non-periodic flags; "
        "skips seam synthesis, delegates to wire-fix path; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── Non-periodic B_SPLINE_SURFACE_WITH_KNOTS: degree 1, 2×2 control net ──────
# Flat unit square in XY plane: control points at corners
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))

# degree=1, nu=2, nv=2:
# sum(u_mults) = nu + u_degree + 1 = 2 + 1 + 1 = 4 → [2, 2]
# sum(v_mults) = nv + v_degree + 1 = 2 + 1 + 1 = 4 → [2, 2]
bspline_surf = f.b_spline_surface_with_knots(
    1, 1,
    [[p00, p01], [p10, p11]],
    [2, 2], [2, 2],
    [0.0, 1.0], [0.0, 1.0],
    surface_form="UNSPECIFIED",
    u_closed=False,    # non-periodic: FixMissingSeam rejects seam synthesis
    v_closed=False,    # non-periodic
    self_intersect=False,
)

# ── Closed quad EDGE_LOOP on the unit square ──────────────────────────────────
p_ll = f.cartesian_point((0.0, 0.0, 0.0))
p_lr = f.cartesian_point((1.0, 0.0, 0.0))
p_ur = f.cartesian_point((1.0, 1.0, 0.0))
p_ul = f.cartesian_point((0.0, 1.0, 0.0))

v_ll = f.vertex_point(p_ll)
v_lr = f.vertex_point(p_lr)
v_ur = f.vertex_point(p_ur)
v_ul = f.vertex_point(p_ul)

e_bot = f.edge_curve(v_ll, v_lr, f.line(p_ll, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
e_rgt = f.edge_curve(v_lr, v_ur, f.line(p_lr, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
e_top = f.edge_curve(v_ur, v_ul, f.line(p_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_lft = f.edge_curve(v_ul, v_ll, f.line(p_ul, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

face_loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], bspline_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa212.stp")
