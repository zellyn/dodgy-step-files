"""Tsh133 — ShapeUpgrade_RemoveLocations.Remove top-down.

Catalog claim: RemoveLocations called top-down on COMPOUND with transformed
sub-shapes; parent transform removed but child local transforms stale. Expected:
Child geometry should update when parent location removed.
Fixture: COMPOUND containing transformed shell instances with AXIS2_PLACEMENT_3D
refs; top-level cascading removal.

Mechanism IS the shell structure: a single OPEN_SHELL with one ADVANCED_FACE
(unit square) at z=0 — the AXIS2_PLACEMENT_3D with translation (1,0,0) IS wired
directly into the face's PLANE reference, forming the transformed sub-shape. The
translated PLANE IS the mechanism: RemoveLocations.Remove strips the top-level
location but leaves the child AXIS2_PLACEMENT_3D translation stale, causing
geometry mismatch.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh133",
    defect=(
        "OPEN_SHELL with 1 ADVANCED_FACE at z=0 with translated AXIS2_PLACEMENT_3D — IS the mechanism; "
        "PLANE origin at (1,0,0) with normal (0,0,1) IS the child transform wired into EDGE_LOOP; "
        "top-level AXIS2_PLACEMENT_3D at (0,0,0) IS the parent location; "
        "RemoveLocations.Remove strips parent location but leaves child AXIS2_PLACEMENT_3D stale; "
        "child translation (1,0,0) IS the residual stale transform — IS the defect; "
        "fix: cascade Remove into child AXIS2_PLACEMENT_3D refs after stripping parent; "
        "emit E_REMOVE_LOCATIONS_STALE_CHILD when child transform not updated"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Unit square vertices at x=[1,2], y=[0,1], z=0
# The PLANE origin at (1,0,0) IS the child transform wired into topology
p00 = cp(1, 0, 0); p10 = cp(2, 0, 0)
p11 = cp(2, 1, 0); p01 = cp(1, 1, 0)

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)

e_bot   = led(v00, v10, p00,  1, 0, 0)
e_right = led(v10, v11, p10,  0, 1, 0)
e_top   = led(v11, v01, p11, -1, 0, 0)
e_left  = led(v01, v00, p01,  0, -1, 0)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])

# PLANE with AXIS2_PLACEMENT_3D origin at (1,0,0) — IS the child transform mechanism
plane_origin = cp(1, 0, 0)
plane = f.plane(f.axis2_placement_3d(plane_origin, dir3(0, 0, 1), dir3(1, 0, 0)))

face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=True)

# OPEN_SHELL with translated face — IS the top-down removal mechanism
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
