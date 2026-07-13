"""Twi304 — Multi-face shared full-circle edge (start==end vertex, zero
naive endpoint distance) that must NOT be collapsed as a "small edge"
(tkshh-wire-small-edge, PARTIAL, missing subvariant "small edge shared by
faces where a circle-like closed curve must NOT be collapsed, protection
case").

Catalog claim: ShapeAnalysis_Wire::CheckSmall's midpoint test
(ShapeAnalysis_Wire.cxx:733-749) distinguishes a genuinely small/sliver
edge (endpoints AND curve midpoint all coincide within tolerance) from an
edge that "leaves and returns" -- a closed curve whose two endpoints are
the SAME vertex (naive endpoint-distance == 0) but whose midpoint sits far
from that vertex. Only the former should be dropped/merged by
ShapeFix_Wireframe::MergeSmallEdges; the latter must be protected and kept
even though a naive "distance(V1,V2)==0" check alone would misclassify it
as small. This fixture makes the protection case MULTI-FACE and
genuinely shared: the SAME full-circle EDGE_CURVE (radius 0.02, small
relative to the model's 1x1 bounding box) is used as BOTH the FACE_BOUND
(hole) of a big square face AND the FACE_OUTER_BOUND of a small disk face
-- dropping it would corrupt TWO faces at once (the big face loses its
hole, the disk face loses its entire boundary), not just one, raising the
stakes of the protection beyond Twi013/N010/N014/Twi138/Twi237/Twi184's
single-face sliver cases.

Mechanism: a PLANE (z=0). big_face: FACE_OUTER_BOUND = 1x1 square
(4 edges), FACE_BOUND = shared_small_circle_edge (reversed, as an inner
hole) at center (0.5, 0.5), radius 0.02. disk_face: FACE_OUTER_BOUND =
the SAME shared_small_circle_edge (forward) -- a genuinely shared
EDGE_CURVE entity (same #id referenced by both ADVANCED_FACEs' loops, not
independently duplicated). Both ADVANCED_FACEs sit in one OPEN_SHELL.
shared_small_circle_edge's start==end vertex (naive distance 0) but its
midpoint (the antipodal point on the circle, 2*radius=0.04 away from the
vertex) is far enough from the vertex that CheckSmall's midpoint test must
correctly NOT flag it as a small/degenerate edge.

Byte assertions:
  - contains(b'shared_small_circle_edge')
  - count_entity_def(b'EDGE_CURVE') == 5
  - count_entity_def(b'ADVANCED_FACE') == 2
  - count_entity_def(b'CIRCLE') == 1

Tier-3 assertions:
  - n_faces_total == 2
  - brepcheck.valid == True

live oracle (2026-07-13, this worktree, OCP/OCCT 7.8.1): occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi304",
    defect=(
        "OPEN_SHELL with TWO ADVANCED_FACEs on the SAME PLANE (z=0, "
        "normal +Z): big_face (FACE_OUTER_BOUND = 1x1 square, FACE_BOUND = "
        "shared_small_circle_edge reversed, hole at center (0.5,0.5) "
        "radius 0.02) and disk_face (FACE_OUTER_BOUND = the SAME "
        "shared_small_circle_edge, forward) -- a genuinely SHARED "
        "EDGE_CURVE entity (not independently duplicated) referenced by "
        "BOTH faces' loops; shared_small_circle_edge is a full CIRCLE, "
        "start==end at one VERTEX_POINT (naive endpoint distance 0) but "
        "midpoint is 0.04 away (2x radius) from that vertex -- "
        "ShapeAnalysis_Wire::CheckSmall's midpoint test must protect it "
        "from being dropped as a small/degenerate edge despite the naive "
        "zero endpoint distance; dropping it would corrupt BOTH faces at "
        "once; EDGE_LOOPs IS wired into FACE_OUTER_BOUND/FACE_BOUND, "
        "ADVANCED_FACE, OPEN_SHELL; never orphaned"
    ),
)

CX, CY = 0.5, 0.5
R_HOLE = 0.02

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Big 1x1 square outer boundary ─────────────────────────────────────────────
def mk_edge(pa, pb, va, vb, name=""):
    dx, dy = pb[0] - pa[0], pb[1] - pa[1]
    mag = math.hypot(dx, dy)
    d = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, mag)
    ln = f._emit_raw(f"LINE('{name}',#{f.cartesian_point(pa).eid},#{vec.eid})")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{va.eid},#{vb.eid},#{ln.eid},.T.)")


sq_A = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
sq_B = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
sq_C = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))
sq_D = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))

e_ab = mk_edge((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), sq_A, sq_B, "sq_bottom")
e_bc = mk_edge((1.0, 0.0, 0.0), (1.0, 1.0, 0.0), sq_B, sq_C, "sq_right")
e_cd = mk_edge((1.0, 1.0, 0.0), (0.0, 1.0, 0.0), sq_C, sq_D, "sq_top")
e_da = mk_edge((0.0, 1.0, 0.0), (0.0, 0.0, 0.0), sq_D, sq_A, "sq_left")

sq_loop = f.edge_loop([
    f.oriented_edge(e_ab, True),
    f.oriented_edge(e_bc, True),
    f.oriented_edge(e_cd, True),
    f.oriented_edge(e_da, True),
])

# ── Shared full-circle edge: start==end at one vertex, radius R_HOLE ─────────
circ_v = f.vertex_point(f.cartesian_point((CX + R_HOLE, CY, 0.0)))
circ_plc = f.axis2_placement_3d(f.cartesian_point((CX, CY, 0.0)), zdir, xdir)
circ_geom = f._emit_raw(f"CIRCLE('',#{circ_plc.eid},{R_HOLE:.10f})")
shared_circle_edge = f._emit_raw(
    f"EDGE_CURVE('shared_small_circle_edge',#{circ_v.eid},#{circ_v.eid},#{circ_geom.eid},.T.)"
)

# Hole loop (reversed orientation, standard inner-boundary convention)
oe_hole = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{shared_circle_edge.eid},.F.)")
hole_loop = f._emit_raw(f"EDGE_LOOP('',(#{oe_hole.eid}))")

big_fob = f.face_outer_bound(sq_loop)
big_fb_hole = f._emit_raw(f"FACE_BOUND('',#{hole_loop.eid},.F.)")
big_face = f._emit_raw(f"ADVANCED_FACE('',(#{big_fob.eid},#{big_fb_hole.eid}),#{plane.eid},.T.)")

# Disk face: outer boundary IS the same shared circle edge, forward orientation.
oe_disk = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{shared_circle_edge.eid},.T.)")
disk_loop = f._emit_raw(f"EDGE_LOOP('',(#{oe_disk.eid}))")
disk_fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{disk_loop.eid},.T.)")
disk_face = f._emit_raw(f"ADVANCED_FACE('',(#{disk_fob.eid}),#{plane.eid},.T.)")

shell = f.open_shell([big_face, disk_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
