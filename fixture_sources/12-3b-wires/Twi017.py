"""Twi017 — Closed 3D curve with two distinct VERTEX_POINTs (single-edge closed).

Catalog claim: EDGE_CURVE whose 3D curve is a closed full CIRCLE but cites two
distinct VERTEX_POINTs as start and end; per STEP/OCCT, a closed curve must
reuse the same vertex at both ends.

Mechanism IS the EDGE_CURVE with two distinct VERTEX_POINTs on a closed circle:
the EDGE_CURVE is emitted via _emit_raw so that #v1 ≠ #v2 despite the
underlying CIRCLE being a full 360° loop. The defect EDGE_CURVE IS referenced
in an EDGE_LOOP, which IS referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE
in an OPEN_SHELL; never orphaned. The edge-transfer pass must detect the
closed-curve case and reuse the first vertex on both ends, regardless of how
many distinct vertex entities the file references.

Reproducer: EDGE_CURVE('',#v1,#v2,#circle_geom,.T.) where #circle_geom is a
full CIRCLE and #v1, #v2 are distinct VERTEX_POINT entities.

Byte assertions:
  - count_entity_def(b'VERTEX_POINT') == 2
  - contains(b'CIRCLE')

Tier-3 assertions:
  - n_edges_total == 1
  - n_vertices_total == 2
  - face[0].surface_type == "plane"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi017",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with a single ORIENTED_EDGE "
        "wrapping an EDGE_CURVE whose underlying curve is a full CIRCLE (360°) "
        "but start vertex #v1 and end vertex #v2 are two distinct VERTEX_POINT entities; "
        "two distinct VERTEX_POINTs on a closed circle IS the mechanism; "
        "translator must detect closed-curve case and reuse first vertex on both ends; "
        "both VERTEX_POINTs wired into EDGE_CURVE, EDGE_LOOP, FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Full CIRCLE geometry (radius 1, centre at origin, in z=0 plane) ──────────
c_orig = f.cartesian_point((0.0, 0.0, 0.0))
c_zdir = f.direction((0.0, 0.0, 1.0))
c_xdir = f.direction((1.0, 0.0, 0.0))
c_plc  = f.axis2_placement_3d(c_orig, c_zdir, c_xdir)
circle = f._emit_raw(f"CIRCLE('',#{c_plc.eid},1.0)")

# ── Two DISTINCT VERTEX_POINTs: IS the defect ─────────────────────────────────
# Both sit at (1,0,0) — the parametric start of the full circle — but are
# separate VERTEX_POINT entities, which is illegal for a closed curve.
p_v1 = f.cartesian_point((1.0, 0.0, 0.0))
v1   = f.vertex_point(p_v1)
p_v2 = f.cartesian_point((1.0, 0.0, 0.0))
v2   = f.vertex_point(p_v2)

# EDGE_CURVE with #v1 ≠ #v2 on a closed CIRCLE: this IS the mechanism.
edge_curve = f._emit_raw(
    f"EDGE_CURVE('',#{v1.eid},#{v2.eid},#{circle.eid},.T.)"
)

# ORIENTED_EDGE → EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE → OPEN_SHELL
oe   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{edge_curve.eid},.T.)")
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe.eid}))")
fob  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
