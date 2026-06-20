"""Tsh196 — ShapeFix_Shell.FixFaceOrientation multi-connected edge unbounded loop.

Catalog claim: Face with edge appearing more than twice in edge loop.
FixFaceOrientation cannot determine loop closure; produces malformed
FACE_OUTER_BOUND. Edge traversal unbounded.

Mechanism IS the shell structure: AN OPEN_SHELL containing ONE ADVANCED_FACE
whose FACE_OUTER_BOUND references ONE EDGE_LOOP in which THE SAME EDGE_CURVE
(e_shared) appears TWICE via two distinct ORIENTED_EDGEs IS the defect trigger.
FixFaceOrientation IS the defect path: it encounters e_shared with edge-count > 2
(shared-in-loop twice, once forward once reversed) and cannot determine closure;
the loop becomes malformed — IS the unbounded traversal defect.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh196",
    defect=(
        "OPEN_SHELL with ONE ADVANCED_FACE whose EDGE_LOOP references THE SAME EDGE_CURVE TWICE IS the multi-connected edge loop defect trigger; "
        "e_shared IS EDGE_CURVE from v00 to v10 — IS the multi-connected edge; "
        "the face loop includes e_shared forward (orientation=True) at position 0 — IS the first reference; "
        "the face loop includes e_shared reversed (orientation=False) at position 2 — IS the second reference; "
        "edge count for e_shared IS 2 within a single face loop — IS the repeated-edge condition; "
        "FixFaceOrientation IS the defect path: it cannot determine loop closure when e_shared appears twice; "
        "FACE_OUTER_BOUND produced IS malformed — IS the undefined closure outcome; "
        "edge traversal IS unbounded due to unguarded loop on repeated edge — IS the defect; "
        "fix: FixFaceOrientation must detect intra-loop repeated edges and reject or bound traversal; "
        "emit E_MULTICONNECT_LOOP_UNBOUNDED when edge appears more than once in a single face loop"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Square corners — IS the face geometry
p00 = cp(0, 0, 0); v00 = f.vertex_point(p00)
p10 = cp(1, 0, 0); v10 = f.vertex_point(p10)
p11 = cp(1, 1, 0); v11 = f.vertex_point(p11)
p01 = cp(0, 1, 0); v01 = f.vertex_point(p01)

# e_shared: THE edge that appears TWICE in the loop — IS the repeated multi-connected edge
e_shared = led(v00, v10, p00,  1, 0, 0)   # bottom: v00 -> v10
e_rgt    = led(v10, v11, p10,  0, 1, 0)   # right
e_top    = led(v11, v01, p11, -1, 0, 0)   # top

# Edge loop: e_shared appears forward at index 0 and reversed at index 3 — IS the repeated-edge loop
loop = f.edge_loop([
    f.oriented_edge(e_shared, True),    # forward: v00 -> v10 — IS first reference
    f.oriented_edge(e_rgt,    True),    # v10 -> v11
    f.oriented_edge(e_top,    True),    # v11 -> v01
    f.oriented_edge(e_shared, False),   # reversed: v10 -> v00 — IS second reference (defect)
])
plane = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=True)

# OPEN_SHELL: one face with repeated edge in loop — IS the multi-connected edge unbounded mechanism
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
