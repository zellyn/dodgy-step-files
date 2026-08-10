"""Tfa264 — Face whose geometry slot holds an axis placement where a surface is declared.

Catalog claim: FACE_SURFACE's `face_geometry` attribute is a SURFACE; the
writer emits the AXIS2_PLACEMENT_3D it would have built the plane FROM,
and the PLANE entity itself never appears in the file. The boundary chain
(oriented edge over a closed circle, wrapped in an edge loop and a face
outer bound) is complete and correct, so the face is fully recoverable —
the placement pins down the intended plane exactly — but as written, a
surface slot holds a placement.

Canonical claimant for the face-geometry row of the wrong-type slot table
(structural-linter v3). Same defect family as the corpus's
surface-of-revolution axis carriers (a placement-vs-declared-type
confusion), on the face's own geometry slot.

Geometry: a disc of radius 3 whose face geometry SHOULD be the plane at
z=0; the file carries only `placement_as_face_geometry`, the placement.

Byte assertions:
  - count_entity_def(b'FACE_SURFACE') == 1
  - count_entity_def(b'PLANE') == 0
  - contains(b'placement_as_face_geometry')

Structural assertion: struct == SLOT_TYPE
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tfa264",
    defect=(
        "FACE_SURFACE whose face_geometry slot references "
        "AXIS2_PLACEMENT_3D('placement_as_face_geometry') — the placement "
        "the plane would have been built from — and no PLANE (or any other "
        "surface) exists in the file. The boundary chain (closed circle, "
        "oriented edge, edge loop, face outer bound) is complete; the "
        "surface level alone was dropped"
    ),
)

R = 3.0
centre = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax = f.axis2_placement_3d(centre, zdir, xdir, name="placement_as_face_geometry")
circ = f.circle(ax, R)

p_start = f.cartesian_point((R, 0.0, 0.0))
v = f.vertex_point(p_start)
ec = f.edge_curve(v, v, circ)
oe = f.oriented_edge(ec, True)
loop = f.edge_loop([oe])
bound = f.face_outer_bound(loop)

# THE DEFECT: face_geometry holds the placement; no surface entity exists.
face = f._emit_raw(f"FACE_SURFACE('tfa264_disc',(#{bound.eid}),#{ax.eid},.T.)")

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
