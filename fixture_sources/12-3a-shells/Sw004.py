"""Sw004 — Fast-sewing face has null surface reference.

Catalog claim: An input face passed to a fast-sewing path has a null
surface reference. Reproducer recipe (per catalog): an ADVANCED_FACE
whose `face_geometry` slot is `$` (null), passed as input to a
fast-sewing pipeline, alongside real geometry (OPEN_SHELL context).
Byte assertion: matches on ADVANCED_FACE(name, empty-bounds, dollar-surface, ...)
Byte assertion: contains(b'OPEN_SHELL')
Tier-3: shape_null == False, n_faces_total == 1, n_edges_total == 4,
        n_vertices_total == 8

Previously this fixture built only ONE ordinary ADVANCED_FACE with a
real PLANE reference -- NOT a null-surface face at all. Byte-verified
rejection from the OCCT exchange-layer coverage audit
(occt-coverage/exchange/, bc-no-surface): "Sw004 ('null surface')
references a real PLANE".

Fixed here: the shell now carries TWO ADVANCED_FACEs --
  face_good: the original valid unit-square face (real PLANE, real
    bounds) -- this is what the sewer/translator keeps, giving
    n_faces_total == 1 in the translated shape (matching the recorded
    Tier-3/Expected baseline unchanged).
  face_null_surface: `ADVANCED_FACE('null_surface_face',(),$,.T.)` --
    empty bound list, null (`$`) face_geometry -- genuinely encodes the
    catalog's exact reproducer recipe. Per "Expected kernel behavior"
    (skip the face with a diagnostic, or fall back to slow sewing), the
    reader is expected to drop this face, leaving the good face's
    topology counts (n_faces=1, n_edges=4, n_vertices=8) intact.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Sw004", defect=(
    "OPEN_SHELL carries one valid unit-square ADVANCED_FACE plus one "
    "genuinely null-surface ADVANCED_FACE ('null_surface_face',(),$,.T.) "
    "-- fast-sewing input with a real face_geometry==$ null reference"
))

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

p0 = f.cartesian_point((0.0, 0.0, 0.0)); p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0)); p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), 1.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)
loop = f.edge_loop([f.oriented_edge(e0, True), f.oriented_edge(e1, True),
                   f.oriented_edge(e2, True), f.oriented_edge(e3, True)])
face_good = f.advanced_face([f.face_outer_bound(loop)], plane)

# THE DEFECT: a second face with an empty bound list and a null (`$`)
# surface reference -- genuinely matches the catalog's reproducer recipe
# and its byte assertion regex.
face_null_surface = f.advanced_face([], None, name="null_surface_face")

all_faces = [face_good, face_null_surface]

shell = f.open_shell(all_faces)
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# A "null-surface" face — emit a face whose surface reference is unusable.

