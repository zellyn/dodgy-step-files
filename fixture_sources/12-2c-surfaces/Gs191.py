"""Gs191 — Slicer chord-deflection defect on small-radius `B_SPLINE_SURFACE_WITH_KNOTS`.

Catalog claim: STEP file with a `SHELL_BASED_SURFACE_MODEL` containing two
`ADVANCED_FACE` entities, each on a `B_SPLINE_SURFACE_WITH_KNOTS` — one
approximating a large-radius cylindrical patch (R=50 mm) and one approximating a
small-radius cylindrical patch (R=1.5 mm). Both faces are correctly parameterized
per AP214. The two surfaces are independent (placed side-by-side in X) and the
patch's angular sweep is identical (60°), so the arc length differs by a factor
of ≈33×. OCCT (`BRepMesh` with configurable `LinearDeflection`) meshes both faces
smoothly at 0.01 mm chord tolerance; slicers that hard-code
`LinearDeflection = 0.1 mm` produce visible faceting on the small-radius (R=1.5)
face while the large-radius face still looks smooth.

Source: https://github.com/bambulab/BambuStudio/issues/3437 (B4 wave-7 DEF-HH).
LGPL-clean — pattern only, no upstream bytes copied.

Mechanism: both `B_SPLINE_SURFACE_WITH_KNOTS` entities are `ADVANCED_FACE.face_geometry`.
Slicers with fixed 0.1 mm chord deflection produce ≈36-facet coverage on the
R=50 face (chord error acceptable) and ≈4-facet coverage on the R=1.5 face
(chord error > radius, i.e. visibly faceted). The defect is that the reader's
tessellation parameter is not sized to the geometry present in the file.

Byte assertions:
  count_entity_def(b'B_SPLINE_SURFACE_WITH_KNOTS') == 2
  count_entity_def(b'ADVANCED_FACE') == 2

Tier-3 assertion: n_faces_total == 2
Expected: occt=shape(1)/shape(1) gmsh=shape(2) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs191",
    defect=(
        "Two B_SPLINE_SURFACE_WITH_KNOTS ADVANCED_FACEs: R=50 mm (large) and "
        "R=1.5 mm (small) cylindrical patches, each subtending 60 deg; correctly "
        "parameterized per AP214; both are ADVANCED_FACE.face_geometry; slicers "
        "with hard-coded LinearDeflection=0.1 mm produce visibly faceted mesh on "
        "the R=1.5 face while the R=50 face remains smooth; OCCT with "
        "configurable chord deflection (0.01 mm) meshes both smoothly; "
        "BambuStudio 3437 DEF-HH; OCC yields shape(1) shell with 2 faces"
    ),
)

# ── Parametric representation context (2D, shared by both faces) ─────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)


def build_bspline_arc_face(R: float, x_offset: float, tag: str):
    """Build one ADVANCED_FACE on a B_SPLINE_SURFACE_WITH_KNOTS approximating
    a cylindrical arc of radius ``R`` subtending 60 degrees, extruded along Z.

    The B-spline is degree 2 in U (arc direction) and degree 1 in V (extrusion),
    with 3 control-point rows × 2 columns. The middle control point uses a
    rational weight; here we approximate with a non-rational B-spline whose
    3-point net is (start, tangent-intersect / cos(alpha), end). The chord
    error for slicers with fixed deflection scales with R × (1 - cos(theta/2N)),
    so R=1.5 yields visible faceting while R=50 does not.

    Returns the ADVANCED_FACE entity.
    """
    # 60-degree arc, centred on the +X axis. Half-angle = 30 deg.
    alpha = math.radians(30.0)
    # Tangent-intersect control point at (R/cos(alpha), 0).
    R_ctrl = R / math.cos(alpha)
    # Start and end in 3D (arc bottom and top of X-Y disc, z=0 and z=1)
    x_start = x_offset + R * math.cos(alpha)
    y_start = -R * math.sin(alpha)
    x_end   = x_offset + R * math.cos(alpha)
    y_end   = +R * math.sin(alpha)
    x_mid   = x_offset + R_ctrl
    y_mid   = 0.0

    # Extrude along Z from z=0 to z=1 (V direction).
    def cp(x, y, z):
        return f.cartesian_point((x, y, z))

    # U direction (arc): 3 control points; V direction: 2 (extrusion endpoints)
    r0 = [cp(x_start, y_start, 0.0), cp(x_start, y_start, 1.0)]
    r1 = [cp(x_mid,   y_mid,   0.0), cp(x_mid,   y_mid,   1.0)]
    r2 = [cp(x_end,   y_end,   0.0), cp(x_end,   y_end,   1.0)]

    def row_ids(row):
        return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

    cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)})"

    # Degree 2 in U (3 poles → knots (0,1) mults (3,3) sum=6=3+2+1 ✓)
    # Degree 1 in V (2 poles → knots (0,1) mults (2,2) sum=4=2+1+1 ✓)
    surf = f._emit_raw(
        f"B_SPLINE_SURFACE_WITH_KNOTS('{tag}_bsp',2,1,"
        f"{cp_net},"
        f".UNSPECIFIED.,.F.,.F.,.F.,"
        f"(3,3),(2,2),"
        f"(0.0,1.0),(0.0,1.0),"
        f".UNSPECIFIED.)"
    )

    # ── Four boundary edges wiring the face rectangular loop ──────────────────
    p_ll = f.cartesian_point((x_start, y_start, 0.0))
    p_lr = f.cartesian_point((x_end,   y_end,   0.0))
    p_ur = f.cartesian_point((x_end,   y_end,   1.0))
    p_ul = f.cartesian_point((x_start, y_start, 1.0))
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

    # Bottom seam (u sweep at v=0): approximated as straight line in 3D
    e0 = mk_edge(v_ll, v_lr,
        (x_start, y_start, 0.0), (1.0, 0.0, 0.0), 1.0,
        (0.0, 0.0),              (1.0, 0.0),      1.0)
    # Right edge (v extrusion at u=1)
    e1 = mk_edge(v_lr, v_ur,
        (x_end, y_end, 0.0),     (0.0, 0.0, 1.0), 1.0,
        (1.0, 0.0),              (0.0, 1.0),      1.0)
    # Top seam (u sweep at v=1), reversed
    e2 = mk_edge(v_ur, v_ul,
        (x_end, y_end, 1.0),     (-1.0, 0.0, 0.0), 1.0,
        (1.0, 1.0),              (-1.0, 0.0),      1.0)
    # Left edge (v extrusion at u=0), reversed
    e3 = mk_edge(v_ul, v_ll,
        (x_start, y_start, 1.0), (0.0, 0.0, -1.0), 1.0,
        (0.0, 1.0),              (0.0, -1.0),      1.0)

    loop = f.edge_loop([
        f.oriented_edge(e0, True),
        f.oriented_edge(e1, True),
        f.oriented_edge(e2, True),
        f.oriented_edge(e3, True),
    ])
    return f.advanced_face([f.face_outer_bound(loop)], surf)


# ── Large-radius face (R = 50 mm, at x_offset = 0) ─────────────────────────────
face_large = build_bspline_arc_face(R=50.0, x_offset=0.0, tag="gs191_R50")

# ── Small-radius face (R = 1.5 mm, at x_offset = 200) ──────────────────────────
# Byte assertion: count_entity_def(b'B_SPLINE_SURFACE_WITH_KNOTS') == 2
# Byte assertion: count_entity_def(b'ADVANCED_FACE') == 2
face_small = build_bspline_arc_face(R=1.5, x_offset=200.0, tag="gs191_R1p5")

# ── Wrap in an OPEN_SHELL / SHELL_BASED_SURFACE_MODEL ─────────────────────────
shell = f.open_shell([face_large, face_small])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
