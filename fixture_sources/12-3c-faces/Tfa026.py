"""Tfa026 — OFFSET_SURFACE used (out of AP214 scope).

Catalog claim: An ADVANCED_FACE references an OFFSET_SURFACE whose basis is
a complex B_SPLINE_SURFACE aggregate. Translator emits warning; iso evaluation
through offset+extrusion chain raises exception. File is outside AP214 scope
but OCC accepts it (OCC auto-repair is stronger than the catalog's
reject-only stance).

Mechanism: OPEN_SHELL with TWO ADVANCED_FACEs, both on OFFSET_SURFACE
entities. Each OFFSET_SURFACE wraps a B_SPLINE_SURFACE_WITH_KNOTS flat patch
(degree 1, 2x2 control net, offset distance 5.0). Both faces are 4×4 squares
in the xy-plane.

Tier-3 assertions:
  face[0].surface_type == "offset"
  face[1].surface_type == "offset"

Expected: occt=shape(1)/shape(1) gmsh=shape(2) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa026",
    defect=(
        "OPEN_SHELL: two ADVANCED_FACEs each referencing an OFFSET_SURFACE "
        "wrapping a B_SPLINE_SURFACE_WITH_KNOTS flat patch (degree 1, 2x2 net, offset=5.0); "
        "OFFSET_SURFACE is out of AP214 scope — translator must warn; "
        "UIso/VIso evaluation through offset+b-spline chain may raise exception; "
        "face[0]: 4x4 patch at (0,0), face[1]: 4x4 patch at (5,0); "
        "both faces on OFFSET_SURFACE — defect IS on live traversal path; "
        "OCC auto-heals; conservative kernels should reject"
    ),
)


def make_bspline_patch(x_origin, y_origin):
    """Flat 2x2 degree-1 B-spline patch (just a bilinear quad) at given origin."""
    p00 = f.cartesian_point((x_origin + 0.0, y_origin + 0.0, 0.0))
    p01 = f.cartesian_point((x_origin + 4.0, y_origin + 0.0, 0.0))
    p10 = f.cartesian_point((x_origin + 0.0, y_origin + 4.0, 0.0))
    p11 = f.cartesian_point((x_origin + 4.0, y_origin + 4.0, 0.0))
    # degree 1, 2x2 control net → u_mults (2,2), v_mults (2,2), knots (0,1)
    return f.b_spline_surface_with_knots(
        1, 1,
        [[p00, p01], [p10, p11]],
        [2, 2], [2, 2],
        [0.0, 1.0], [0.0, 1.0],
        surface_form="UNSPECIFIED",
        name="",
    )


def make_offset_surf(bspline):
    """Wrap bspline in an OFFSET_SURFACE with distance 5.0."""
    return f._emit_raw(
        f"OFFSET_SURFACE('',#{bspline.eid},5.0,.F.)"
    )


def make_face(x0, y0, surf):
    """Build a 4×4 ADVANCED_FACE at (x0, y0, 0) referencing surf."""
    pa = f.cartesian_point((x0 + 0.0, y0 + 0.0, 0.0))
    pb = f.cartesian_point((x0 + 4.0, y0 + 0.0, 0.0))
    pc = f.cartesian_point((x0 + 4.0, y0 + 4.0, 0.0))
    pd = f.cartesian_point((x0 + 0.0, y0 + 4.0, 0.0))
    va = f.vertex_point(pa)
    vb = f.vertex_point(pb)
    vc = f.vertex_point(pc)
    vd = f.vertex_point(pd)
    ec0 = f.edge_curve(va, vb, f.line(pa, f.vector(f.direction(( 1.0, 0.0, 0.0)), 4.0)))
    ec1 = f.edge_curve(vb, vc, f.line(pb, f.vector(f.direction(( 0.0, 1.0, 0.0)), 4.0)))
    ec2 = f.edge_curve(vc, vd, f.line(pc, f.vector(f.direction((-1.0, 0.0, 0.0)), 4.0)))
    ec3 = f.edge_curve(vd, va, f.line(pd, f.vector(f.direction(( 0.0,-1.0, 0.0)), 4.0)))
    loop = f.edge_loop([
        f.oriented_edge(ec0, True),
        f.oriented_edge(ec1, True),
        f.oriented_edge(ec2, True),
        f.oriented_edge(ec3, True),
    ])
    return f.advanced_face([f.face_outer_bound(loop)], surf)


# ── face[0]: OFFSET_SURFACE at x=0 ──────────────────────────────────────────
bs0   = make_bspline_patch(0.0, 0.0)
off0  = make_offset_surf(bs0)
face0 = make_face(0.0, 0.0, off0)

# ── face[1]: OFFSET_SURFACE at x=5 ──────────────────────────────────────────
bs1   = make_bspline_patch(5.0, 0.0)
off1  = make_offset_surf(bs1)
face1 = make_face(5.0, 0.0, off1)

# ── Both on OPEN_SHELL → SBSM → product chain ────────────────────────────────
shell = f.open_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa026.stp")
