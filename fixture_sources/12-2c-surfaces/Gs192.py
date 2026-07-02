"""Gs192 — OCCT STEP export duplicates `B_SPLINE_SURFACE_WITH_KNOTS` instances.

Catalog claim: STEP file with two `ADVANCED_FACE` entities pointing to two
distinct `B_SPLINE_SURFACE_WITH_KNOTS` entity IDs that carry numerically
identical control-point and knot data — the structure that OCCT 7.4.x's STEP
writer emits after `BRepBuilderAPI_Sewing` on adjacent faces that share a
single `Geom_BSplineSurface` handle in memory. Rather than emit one shared
`B_SPLINE_SURFACE_WITH_KNOTS` referenced from both `ADVANCED_FACE` entities,
the writer duplicates the surface: two entity IDs, identical parameters.

Source: https://tracker.dev.opencascade.org/view.php?id=32132 (OCCT MANTIS
0032132, "STEP writer duplicates shared B-spline surfaces"). B4 wave-7 DEF-NN.
LGPL-clean — pattern only, no upstream bytes copied.

Mechanism: instance-identity readers (any reader that checks entity IDs to
detect shared surfaces) see two independent surfaces and cannot recover the
"shared parent" relationship; geometric-equality readers (readers that hash
control-point / knot data) recognize the surfaces as equal and can restore the
sharing. STEP structural validators may flag the redundancy as a well-formedness
issue since two distinct entities carry identical numeric content.

Byte assertions:
  count_entity_def(b'B_SPLINE_SURFACE_WITH_KNOTS') == 2
  count_entity_def(b'ADVANCED_FACE') == 2

Tier-3 assertion: n_faces_total == 2
Expected: occt=shape(1)/shape(1) gmsh=shape(2) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs192",
    defect=(
        "Two ADVANCED_FACE entities point to two distinct "
        "B_SPLINE_SURFACE_WITH_KNOTS entity IDs whose control-point and knot "
        "data are numerically identical — the pattern OCCT 7.4.x's STEP writer "
        "emits after BRepBuilderAPI_Sewing on adjacent faces sharing a single "
        "Geom_BSplineSurface handle; instance-identity readers see two "
        "independent surfaces, geometric-equality readers recognize them as "
        "shared; structural redundancy — OCCT MANTIS 0032132 DEF-NN; OCC yields "
        "shape(1)/shape(1) surface model with 2 faces"
    ),
)

# ── Parametric representation context (2D, shared by pcurves) ─────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)


def build_bspline_face(x_offset: float, tag: str):
    """Build one ADVANCED_FACE on a B_SPLINE_SURFACE_WITH_KNOTS.

    The B-spline is degree 1×1 with a 2×2 control-point net. The four control
    points are placed at the corners of a 1 mm × 1 mm patch in the XY plane,
    Z = 0. The two calls to this builder emit two entity IDs but the SURFACE
    (control-point coordinates + knot vector) is byte-identical between them —
    the essence of the DEF-NN defect.

    A different ``x_offset`` shifts the face-boundary and pcurve endpoints, but
    the B_SPLINE_SURFACE_WITH_KNOTS entity itself is placed in the SAME location
    (control points at (0,0)-(1,1)) so its byte-content is duplicated exactly.
    """
    # ── Four control points at corners of a 1 mm × 1 mm patch ────────────
    # NOTE: coords are IDENTICAL between the two calls — the duplication that
    # OCCT MANTIS 0032132 reports is over surface entities whose numeric
    # data matches byte-for-byte.
    p00 = f.cartesian_point((0.0, 0.0, 0.0))
    p01 = f.cartesian_point((0.0, 1.0, 0.0))
    p10 = f.cartesian_point((1.0, 0.0, 0.0))
    p11 = f.cartesian_point((1.0, 1.0, 0.0))

    # Degree 1×1, 2×2 net → knots (0,1)/(0,1) with mults (2,2)/(2,2)
    cp_net = f"((#{p00.eid},#{p01.eid}),(#{p10.eid},#{p11.eid}))"
    surf = f._emit_raw(
        f"B_SPLINE_SURFACE_WITH_KNOTS('{tag}_bsp',1,1,"
        f"{cp_net},"
        f".UNSPECIFIED.,.F.,.F.,.F.,"
        f"(2,2),(2,2),"
        f"(0.0,1.0),(0.0,1.0),"
        f".UNSPECIFIED.)"
    )

    # ── Face-boundary edges in 3D placed at x_offset so the two faces are
    # spatially distinct (side-by-side), while the underlying surfaces are
    # entity-duplicate. This mirrors the sewing scenario where the two faces
    # occupy adjacent regions but share the parent surface handle.
    x0 = x_offset
    x1 = x_offset + 1.0
    p_ll = f.cartesian_point((x0, 0.0, 0.0))
    p_lr = f.cartesian_point((x1, 0.0, 0.0))
    p_ur = f.cartesian_point((x1, 1.0, 0.0))
    p_ul = f.cartesian_point((x0, 1.0, 0.0))
    v_ll = f.vertex_point(p_ll)
    v_lr = f.vertex_point(p_lr)
    v_ur = f.vertex_point(p_ur)
    v_ul = f.vertex_point(p_ul)

    def mk_edge(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
        p3e = f.cartesian_point(p3_start)
        d3e = f.direction(d3t)
        v3e = f.vector(d3e, p3_len)
        l3e = f.line(p3e, v3e)
        p2e = f.cartesian_point(p2_start)
        d2e = f.direction(d2t)
        v2e = f.vector(d2e, p2_len)
        l2e = f.line(p2e, v2e)
        pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
        pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
        sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
        return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

    # Bottom seam (v=0): U sweep, straight in 3D
    e0 = mk_edge(v_ll, v_lr,
        (x0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
        (0.0, 0.0),     (1.0, 0.0),      1.0)
    # Right edge (u=1): V sweep
    e1 = mk_edge(v_lr, v_ur,
        (x1, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
        (1.0, 0.0),     (0.0, 1.0),      1.0)
    # Top seam (v=1), reversed U
    e2 = mk_edge(v_ur, v_ul,
        (x1, 1.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
        (1.0, 1.0),     (-1.0, 0.0),      1.0)
    # Left edge (u=0), reversed V
    e3 = mk_edge(v_ul, v_ll,
        (x0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
        (0.0, 1.0),     (0.0, -1.0),      1.0)

    loop = f.edge_loop([
        f.oriented_edge(e0, True),
        f.oriented_edge(e1, True),
        f.oriented_edge(e2, True),
        f.oriented_edge(e3, True),
    ])
    return f.advanced_face([f.face_outer_bound(loop)], surf)


# ── Face A at x_offset=0, its own B_SPLINE_SURFACE_WITH_KNOTS entity ──────────
# Byte assertion: count_entity_def(b'B_SPLINE_SURFACE_WITH_KNOTS') == 2
# Byte assertion: count_entity_def(b'ADVANCED_FACE') == 2
face_a = build_bspline_face(x_offset=0.0, tag="gs192_faceA")

# ── Face B at x_offset=2, its own B_SPLINE_SURFACE_WITH_KNOTS entity, whose
# control-point / knot data is byte-identical to Face A's surface.  This is
# the MANTIS 0032132 defect: two distinct surface entity IDs carrying the
# same numeric data.
face_b = build_bspline_face(x_offset=2.0, tag="gs192_faceB")

# ── Wrap in an OPEN_SHELL / SHELL_BASED_SURFACE_MODEL ─────────────────────────
shell = f.open_shell([face_a, face_b])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
