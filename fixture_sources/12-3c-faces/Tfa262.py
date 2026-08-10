"""Tfa262 — Face outer bound whose bound slot holds the edge curve itself, two levels too deep.

Catalog claim: for a disc bounded by a single closed circular edge, the
writer points FACE_OUTER_BOUND's `bound` attribute straight at the
EDGE_CURVE — skipping BOTH the ORIENTED_EDGE and the EDGE_LOOP levels of
the boundary hierarchy. ISO 10303-42 declares that slot as a LOOP. The
sibling fixture with one skipped level exists separately; this is the
deeper flattening, and the file is otherwise minimal and fully referenced —
no orphan entities.

Canonical claimant for the face-outer-bound row of the wrong-type slot
table (structural-linter v3).

Geometry: a planar disc of radius 4 at z=0 bounded by one closed circular
edge. The chain is EDGE_CURVE('outer_bound_holds_edge_curve') <-
FACE_OUTER_BOUND <- ADVANCED_FACE; neither an ORIENTED_EDGE nor an
EDGE_LOOP appears anywhere in the file.

Byte assertions:
  - count_entity_def(b'FACE_OUTER_BOUND') == 1
  - count_entity_def(b'ORIENTED_EDGE') == 0
  - count_entity_def(b'EDGE_LOOP') == 0
  - contains(b'outer_bound_holds_edge_curve')

Structural assertion: struct == SLOT_TYPE
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tfa262",
    defect=(
        "FACE_OUTER_BOUND whose bound slot references the closed circular "
        "EDGE_CURVE('outer_bound_holds_edge_curve') directly — both the "
        "ORIENTED_EDGE and EDGE_LOOP levels of the boundary hierarchy are "
        "absent from the file. Disc of radius 4 on a plane at z=0; every "
        "entity is referenced"
    ),
)

R = 4.0
centre = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax = f.axis2_placement_3d(centre, zdir, xdir)
plane = f.plane(ax)
circ = f.circle(ax, R)

p_start = f.cartesian_point((R, 0.0, 0.0))
v = f.vertex_point(p_start)
ec = f.edge_curve(v, v, circ, name="outer_bound_holds_edge_curve")

# THE DEFECT: the bound slot holds the edge curve; no oriented edge, no loop.
bound = f.face_outer_bound(ec)
face = f.advanced_face([bound], plane, name="tfa262_disc")

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
