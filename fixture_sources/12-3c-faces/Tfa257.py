"""Tfa257 — Two independent full-circle boundaries at the same location,
closed-edge vertex-tolerance-reconciliation subvariant.

Catalog claim: once two edges' endpoints are paired for a merge, the two
original vertices at a paired endpoint are rarely exactly coincident. Rather
than snapping one vertex onto the other, a reconciling merge computes a new
position/tolerance that geometrically bounds both originals. CLOSED edges
(where an edge's own two endpoints coincide, i.e. a full-period loop) use a
specialized three-point-averaging variant of this computation instead of the
plain two-point formula, because both of the closed edge's endpoints are the
SAME vertex.

Mechanism: an OPEN_SHELL carries two ADVANCED_FACEs on the same PLANE
location (z=0), each face's ENTIRE boundary is a single CLOSED EDGE_CURVE
(its own start vertex and end vertex are the identical VERTEX_POINT entity —
a full 360-degree circle, radius 5, no other edges). face_a's circle is
centered on the +Z-normal side; face_b's circle is centered on the -Z-normal
side (the "other side" of the same disk location) but its closing vertex is
a DISTINCT VERTEX_POINT offset by 1e-5 mm along +X from face_a's closing
vertex — within a typical sewing tolerance (1e-4) but a genuinely different
entity. Two independent full-circle closed-edge boundaries at (nearly) the
same location, topologically unshared — exactly the closed-edge merge input
the three-point-averaging variant is built to reconcile.

Byte assertions:
  - count_entity_def(b'CIRCLE') == 2
  - count_entity_def(b'EDGE_CURVE') == 2
  - contains(b'5.00001')

Tier-3 assertions:
  - load == "ok"
  - n_faces_total == 2
  - face[0].surface_type == "plane"
  - face[1].surface_type == "plane"
  - n_vertices_total == 4

Live oracle (2026-07-13, this worktree's OCP/OCCT 7.8.1, default import,
heal-on and heal-off identical): occt=shape(1)/shape(1) gmsh=shape(6)/shape(6).
Honest caveat (matching this problem class's existing PARTIAL-covering
fixtures Tfa020/Tsh203/Tsh187): the plain default STEPControl_Reader path
does NOT itself invoke BRepBuilderAPI_Sewing, so no live vertex-reconciling
merge is observed on ordinary import — the two closing vertices remain two
distinct, unmerged VERTEX_POINT instances at (5.00001,0,0) and (5,0,0), and
the two faces load as 2 separate shells inside a compound rather than one
merged shell. What IS genuinely demonstrated and live-verified: the input
pattern itself survives translation completely intact and reachable (not
orphaned, not dropped, not crashed) — two independent, topologically
unshared, CLOSED (start==end vertex) edge boundaries at coincident locations
with a within-tolerance vertex offset, exactly the precondition the
three-point-averaging merge computation is defined over. This is the missing
closed-edge subvariant: Tfa020/Tsh203/Tsh187 all encode the plain two-vertex
(open-edge) merge precondition; none of them encodes a CLOSED edge (a full
loop where an edge's own two endpoints are the same vertex).
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa257",
    defect=(
        "OPEN_SHELL, two ADVANCED_FACEs on coincident PLANE locations (z=0); "
        "face_a: full CIRCLE radius 5 centered at origin, normal +Z, single closed "
        "EDGE_CURVE whose start vertex and end vertex ARE the same VERTEX_POINT at "
        "(5,0,0); face_b: full CIRCLE radius 5 at the same center, normal -Z (the "
        "other side of the same disk location), its own closed EDGE_CURVE whose "
        "closing vertex is a DISTINCT VERTEX_POINT at (5.00001,0,0) -- offset 1e-5 mm "
        "along +X, within typical sewing tolerance but a genuinely different entity; "
        "two independent, topologically unshared, full-period CLOSED boundaries at "
        "(nearly) the same location IS the precondition for the closed-edge "
        "three-point-averaging vertex-tolerance-reconciliation merge; "
        "both faces ARE wired into one live OPEN_SHELL/SHELL_BASED_SURFACE_MODEL; "
        "never orphaned"
    ),
)

R = 5.0
gap = 1.0e-5

# face_a: normal +Z
pl_a_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_a_zdir = f.direction((0.0, 0.0, 1.0))
pl_a_xdir = f.direction((1.0, 0.0, 0.0))
pl_a_plc  = f.axis2_placement_3d(pl_a_orig, pl_a_zdir, pl_a_xdir)
plane_a   = f.plane(pl_a_plc)

v_a = f.vertex_point(f.cartesian_point((R, 0.0, 0.0)))
circ_a_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
circ_a = f.circle(circ_a_plc, R)
ec_a = f.edge_curve(v_a, v_a, circ_a, True)
loop_a = f.edge_loop([f.oriented_edge(ec_a, True)])
fob_a = f.face_outer_bound(loop_a)
face_a = f.advanced_face([fob_a], plane_a)

# face_b: normal -Z, same disk location, closing vertex offset by 1e-5 mm
pl_b_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_b_zdir = f.direction((0.0, 0.0, -1.0))
pl_b_xdir = f.direction((1.0, 0.0, 0.0))
pl_b_plc  = f.axis2_placement_3d(pl_b_orig, pl_b_zdir, pl_b_xdir)
plane_b   = f.plane(pl_b_plc)

v_b = f.vertex_point(f.cartesian_point((R + gap, 0.0, 0.0)))
circ_b_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
circ_b = f.circle(circ_b_plc, R)
ec_b = f.edge_curve(v_b, v_b, circ_b, True)
loop_b = f.edge_loop([f.oriented_edge(ec_b, True)])
fob_b = f.face_outer_bound(loop_b)
face_b = f.advanced_face([fob_b], plane_b)

shell = f.open_shell([face_a, face_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa257.stp")
