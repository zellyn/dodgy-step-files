"""Tfa263 — Face whose bounds list holds a bare edge loop where face-bound wrappers are declared.

Catalog claim: FACE_SURFACE's `bounds` attribute is a set of FACE_BOUNDs;
the writer puts the EDGE_LOOP into that list directly, skipping the
FACE_BOUND wrapper (and with it the bound's orientation flag). The loop
itself is complete and correctly built from an oriented edge over a closed
circle, so the only anomaly in the file is one list element sitting one
level too deep in the boundary hierarchy.

Canonical claimant for the face-bounds-list row of the wrong-type slot
table (structural-linter v3) — and the corpus's first mis-typed FACE_SURFACE:
all prior carriers of this list shape exercise the advanced-face spelling.

Geometry: a planar disc of radius 5 at z=0. Chain:
CIRCLE <- EDGE_CURVE <- ORIENTED_EDGE <- EDGE_LOOP('loop_listed_as_bound')
<- FACE_SURFACE bounds list (no FACE_BOUND anywhere in the file).

Byte assertions:
  - count_entity_def(b'FACE_SURFACE') == 1
  - count_entity_def(b'FACE_BOUND') == 0
  - count_entity_def(b'FACE_OUTER_BOUND') == 0
  - contains(b'loop_listed_as_bound')

Structural assertion: struct == SLOT_TYPE
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tfa263",
    defect=(
        "FACE_SURFACE whose bounds list is (EDGE_LOOP('loop_listed_as_bound')) "
        "— the loop sits directly in a list ISO 10303-42 declares as a set of "
        "FACE_BOUNDs; the wrapper level (and its orientation flag) is absent. "
        "Disc of radius 5 on a plane at z=0; the loop chain below the defect "
        "is complete and every entity is referenced"
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
oe = f.oriented_edge(ec, True)
loop = f.edge_loop([oe], name="loop_listed_as_bound")

# THE DEFECT: the loop sits directly in the bounds list; no FACE_BOUND exists.
face = f._emit_raw(f"FACE_SURFACE('tfa263_disc',(#{loop.eid}),#{plane.eid},.T.)")

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
