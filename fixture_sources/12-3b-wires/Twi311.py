"""Twi311 — Vertex loop whose vertex slot holds an empty aggregate.

Catalog claim: a face bound references
`VERTEX_LOOP('vloop_no_vertex',())` — the loop-vertex slot holding an
empty aggregate instead of a vertex reference. A vertex loop exists to
name exactly ONE vertex (bounding a face at a single point, as on a cone
apex or sphere pole); with the slot empty the bound names nothing at all,
yet the entity chain above it is fully wired.

Canonical claimant for the vertex-loop row of the nonempty-aggregate table
(structural-linter v4) — the corpus's existing vertex-loop fixtures all
carry a REAL vertex.

Geometry: a planar disc of radius 5 with a correct circular outer bound;
the face's second bound wraps the empty vertex loop.

Byte assertions:
  - contains(b"VERTEX_LOOP('vloop_no_vertex',())")
  - count_entity_def(b'FACE_BOUND') == 1

Structural assertion: struct == EMPTY_AGGREGATE
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi311",
    defect=(
        "a FACE_BOUND wrapping VERTEX_LOOP('vloop_no_vertex',()) — the "
        "loop-vertex slot holds an empty aggregate instead of the single "
        "vertex reference a vertex loop exists to carry. The disc's outer "
        "circular bound is correct; the empty vertex loop is the file's "
        "only anomaly and is reachable through the face's bounds list"
    ),
)

R = 5.0
centre = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax = f.axis2_placement_3d(centre, zdir, xdir)
plane = f.plane(ax)
circ = f.circle(ax, R)

p_start = f.cartesian_point((R, 0.0, 0.0))
v = f.vertex_point(p_start)
ec = f.edge_curve(v, v, circ)
outer = f.face_outer_bound(f.edge_loop([f.oriented_edge(ec, True)]))

# THE DEFECT: empty aggregate where the loop's single vertex belongs.
vloop = f._emit_raw("VERTEX_LOOP('vloop_no_vertex',())")
inner = f.face_bound(vloop)

face = f.advanced_face([outer, inner], plane, name="twi311_disc")
sbsm = f.shell_based_surface_model([f.open_shell([face])])
f.add_product_chain(sbsm)
