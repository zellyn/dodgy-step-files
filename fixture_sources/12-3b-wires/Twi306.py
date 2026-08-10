"""Twi306 — Vertex whose geometry slot holds a direction where a point is declared.

Catalog claim: VERTEX_POINT's `vertex_geometry` attribute is a POINT; the
writer emits a DIRECTION reference instead — a point-versus-direction slot
swap, plausible in any writer that keys both entity kinds by index into one
geometry table. One corner of an otherwise-correct square face carries the
swap; the three coordinates of the direction even LOOK like a position, so
nothing about the file's shape hints at the mistake before the reference
is type-checked.

Canonical claimant for the vertex-geometry row of the wrong-type slot table
(structural-linter v3): every prior point-slot carrier in the corpus
mis-types a line's origin, never a vertex.

Geometry: a 10x10 square face on the plane z=0. Vertex 0's VERTEX_POINT
('vertex_holds_direction') references DIRECTION (1,0,0) — the same
direction entity the bottom edge legitimately uses for its line — instead
of the corner point (0,0,0), which remains in the file as the line origins'
anchor. Both edges incident to that corner inherit the poisoned vertex, so
the defect is wired into the wire.

Byte assertions:
  - count_entity_def(b'VERTEX_POINT') == 4
  - contains(b'vertex_holds_direction')

Structural assertion: struct == SLOT_TYPE
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi306",
    defect=(
        "VERTEX_POINT('vertex_holds_direction') whose vertex_geometry slot "
        "references the DIRECTION (1,0,0) shared with the bottom edge's "
        "line, instead of the corner CARTESIAN_POINT (0,0,0) which is still "
        "present as a line origin. Both edges meeting at that corner of a "
        "10x10 square face use the poisoned vertex, so the wrong-typed "
        "reference is wired into the wire"
    ),
)

S = 10.0
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((S, 0.0, 0.0))
p2 = f.cartesian_point((S, S, 0.0))
p3 = f.cartesian_point((0.0, S, 0.0))

dx = f.direction((1.0, 0.0, 0.0))
dy = f.direction((0.0, 1.0, 0.0))
dnx = f.direction((-1.0, 0.0, 0.0))
dny = f.direction((0.0, -1.0, 0.0))

# THE DEFECT: v0's geometry slot holds the x-direction, not the corner point.
v0 = f.vertex_point(dx, name="vertex_holds_direction")
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)


def edge(va, vb, origin, d):
    return f.edge_curve(va, vb, f.line(origin, f.vector(d, S)))


e0 = edge(v0, v1, p0, dx)
e1 = edge(v1, v2, p1, dy)
e2 = edge(v2, v3, p2, dnx)
e3 = edge(v3, v0, p3, dny)

loop = f.edge_loop([f.oriented_edge(e, True) for e in (e0, e1, e2, e3)])
zdir = f.direction((0.0, 0.0, 1.0))
plane = f.plane(f.axis2_placement_3d(p0, zdir, dx))
face = f.advanced_face([f.face_outer_bound(loop)], plane, name="twi306_square")

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
