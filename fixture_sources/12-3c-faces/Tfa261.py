"""Tfa261 — Face bound whose bound slot holds an oriented edge where an edge loop is declared.

Catalog claim: for a disc bounded by a single closed circular edge, the
writer judges the loop wrapper redundant and points FACE_BOUND's `bound`
attribute straight at the ORIENTED_EDGE. ISO 10303-42 declares that slot as
a LOOP; a single closed edge is exactly the case where a writer is tempted
to skip the one-element EDGE_LOOP, so the mistake ships in a file that is
otherwise minimal and fully referenced — no orphan entities at all.

Canonical claimant for the face-bound row of the wrong-type slot table
(structural-linter v3).

Geometry: a planar disc of radius 6 at z=0, bounded by one closed circular
edge (same vertex at both ends). The chain is
ORIENTED_EDGE('bound_holds_oriented_edge') <- FACE_BOUND <- ADVANCED_FACE;
the EDGE_LOOP level is simply absent from the file.

Byte assertions:
  - count_entity_def(b'FACE_BOUND') == 1
  - count_entity_def(b'EDGE_LOOP') == 0
  - contains(b'bound_holds_oriented_edge')

Structural assertion: struct == SLOT_TYPE
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tfa261",
    defect=(
        "FACE_BOUND whose bound slot references the "
        "ORIENTED_EDGE('bound_holds_oriented_edge') of a single closed "
        "circular edge directly — the one-element EDGE_LOOP wrapper the "
        "schema requires is absent from the file. Disc of radius 6 on a "
        "plane at z=0; every entity is referenced; the loop level is the "
        "only thing missing"
    ),
)

R = 6.0
centre = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax = f.axis2_placement_3d(centre, zdir, xdir)
plane = f.plane(ax)
circ = f.circle(ax, R)

p_start = f.cartesian_point((R, 0.0, 0.0))
v = f.vertex_point(p_start)
ec = f.edge_curve(v, v, circ)
oe = f.oriented_edge(ec, True, name="bound_holds_oriented_edge")

# THE DEFECT: the bound slot holds the oriented edge; no EDGE_LOOP exists.
bound = f.face_bound(oe)
face = f.advanced_face([bound], plane, name="tfa261_disc")

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
