"""Twi285 — Two arbitrary, non-adjacent edges (in different faces) are
registered as touching via coincident-but-distinct VERTEX_POINT entities in a
broader connectivity graph.

Catalog claim: The general-purpose vertex-unification utility used by
shell/face sewing (ShapeFix_EdgeConnect::Add/Build) is not limited to a single
wire's own consecutive edges — it also has to reconcile vertices across
UNRELATED edges anywhere in the connectivity graph (e.g. two separate faces'
free boundaries that happen to touch). This fixture puts the defect at that
broader scope: two ADVANCED_FACEs whose outer wires both have a corner at
(0,0,0), each encoded with its OWN distinct VERTEX_POINT entity rather than a
shared one.

This deliberately differs from Twi050 (SplitCommonVertex): Twi050 reuses the
SAME VERTEX_POINT entity across both faces (too much sharing, must SPLIT).
Here each face has a DIFFERENT VERTEX_POINT entity at the same coordinate (no
sharing at all, must MERGE) — the mechanism this fixture targets is the
coincident-but-distinct-entity merge, not the over-shared-entity split, and
Twi009/Twi050 are cited as negative-space contrast, not reused.

Mechanism IS the two distinct VERTEX_POINT entities at (0,0,0) — #v0 (face 0's
corner) and #v1 (face 1's corner) — each wired into its own face's EDGE_LOOP →
FACE_OUTER_BOUND → ADVANCED_FACE inside one SHELL_BASED_SURFACE_MODEL; never
orphaned. The connectivity-graph builder must recognize the two vertices as
touching (same location, distinct entities) and merge them.

Byte assertions:
  - count_entity_def(b'VERTEX_POINT') >= 8
  - contains(b'(0.0,0.0,0.0)')

Tier-3 assertions:
  - n_edges_total >= 6
  - face[0].surface_type == "plane"
  - face[1].surface_type == "plane"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi285",
    defect=(
        "Two ADVANCED_FACEs on PLANEs, unrelated to each other except for a "
        "shared corner LOCATION; face 0's outer wire has a corner VERTEX_POINT "
        "#v0 at (0,0,0); face 1's outer wire has its OWN, DISTINCT VERTEX_POINT "
        "#v1 also at (0,0,0) — two coincident-but-distinct entities registered "
        "as 'touching' only via the broader connectivity graph, not via any "
        "shared wire or entity reuse; "
        "this differs from Twi050 (same entity reused across both wires); "
        "here NO entity is shared — both vertices are separate but coincident; "
        "the general-purpose connectivity-graph vertex-unification utility "
        "(ShapeFix_EdgeConnect::Add/Build) must recognize the pair and merge; "
        "both VERTEX_POINTs ARE wired into EDGE_LOOPs → FACE_OUTER_BOUNDs → "
        "ADVANCED_FACEs in a SHELL_BASED_SURFACE_MODEL — never orphaned"
    ),
)

# ── Face 0: 5x5 square in Z=0, corner at (0,0,0) via v0 ──────────────────────
pl0_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl0_zdir = f.direction((0.0, 0.0, 1.0))
pl0_xdir = f.direction((1.0, 0.0, 0.0))
pl0_plc  = f.axis2_placement_3d(pl0_orig, pl0_zdir, pl0_xdir)
plane0   = f.plane(pl0_plc)

v0     = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))   # face-0-owned corner
v0_br  = f.vertex_point(f.cartesian_point((5.0, 0.0, 0.0)))
v0_tr  = f.vertex_point(f.cartesian_point((5.0, 5.0, 0.0)))
v0_tl  = f.vertex_point(f.cartesian_point((0.0, 5.0, 0.0)))

e0_bot = f.edge_curve(v0, v0_br,
                       f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                              f.vector(f.direction((1.0, 0.0, 0.0)), 5.0)))
e0_rgt = f.edge_curve(v0_br, v0_tr,
                       f.line(f.cartesian_point((5.0, 0.0, 0.0)),
                              f.vector(f.direction((0.0, 1.0, 0.0)), 5.0)))
e0_top = f.edge_curve(v0_tr, v0_tl,
                       f.line(f.cartesian_point((5.0, 5.0, 0.0)),
                              f.vector(f.direction((-1.0, 0.0, 0.0)), 5.0)))
e0_lft = f.edge_curve(v0_tl, v0,
                       f.line(f.cartesian_point((0.0, 5.0, 0.0)),
                              f.vector(f.direction((0.0, -1.0, 0.0)), 5.0)))

loop0 = f.edge_loop([
    f.oriented_edge(e0_bot, True), f.oriented_edge(e0_rgt, True),
    f.oriented_edge(e0_top, True), f.oriented_edge(e0_lft, True),
])
fob0  = f.face_outer_bound(loop0)
face0 = f.advanced_face([fob0], plane0)

# ── Face 1: 5x5 square in Z=-10, corner ALSO at (0,0,-10)→ projected coord
# (0,0,0) in-plane, but the DEFECT VERTEX_POINT #v1 is placed at (0,0,0)
# (matching face-0's world coordinate exactly) rather than (0,0,-10) — a
# deliberately mislocated but genuinely DISTINCT entity from #v0, forcing
# the connectivity graph to treat the two faces' corners as touching. ──────
pl1_orig = f.cartesian_point((0.0, 0.0, -10.0))
pl1_zdir = f.direction((0.0, 0.0, 1.0))
pl1_xdir = f.direction((1.0, 0.0, 0.0))
pl1_plc  = f.axis2_placement_3d(pl1_orig, pl1_zdir, pl1_xdir)
plane1   = f.plane(pl1_plc)

# DEFECT: v1 is a DISTINCT entity (not #v0) but placed at the SAME coordinate
# (0,0,0) that v0 occupies, rather than the geometrically-correct (0,0,-10).
v1     = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v1_br  = f.vertex_point(f.cartesian_point((5.0, 0.0, -10.0)))
v1_tr  = f.vertex_point(f.cartesian_point((5.0, 5.0, -10.0)))
v1_tl  = f.vertex_point(f.cartesian_point((0.0, 5.0, -10.0)))

e1_bot = f.edge_curve(v1, v1_br,
                       f.line(f.cartesian_point((0.0, 0.0, -10.0)),
                              f.vector(f.direction((1.0, 0.0, 0.0)), 5.0)))
e1_rgt = f.edge_curve(v1_br, v1_tr,
                       f.line(f.cartesian_point((5.0, 0.0, -10.0)),
                              f.vector(f.direction((0.0, 1.0, 0.0)), 5.0)))
e1_top = f.edge_curve(v1_tr, v1_tl,
                       f.line(f.cartesian_point((5.0, 5.0, -10.0)),
                              f.vector(f.direction((-1.0, 0.0, 0.0)), 5.0)))
e1_lft = f.edge_curve(v1_tl, v1,
                       f.line(f.cartesian_point((0.0, 5.0, -10.0)),
                              f.vector(f.direction((0.0, -1.0, 0.0)), 5.0)))

loop1 = f.edge_loop([
    f.oriented_edge(e1_bot, True), f.oriented_edge(e1_rgt, True),
    f.oriented_edge(e1_top, True), f.oriented_edge(e1_lft, True),
])
fob1  = f.face_outer_bound(loop1)
face1 = f.advanced_face([fob1], plane1)

shell = f.shell_based_surface_model([f.closed_shell([face0, face1])])
f.add_product_chain(shell)
