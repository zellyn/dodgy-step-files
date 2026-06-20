"""Tsh169 — ShapeFix_Shell.Perform shell-with-floating-faces.

Catalog claim: Shell containing disconnected faces not reachable from main
topology. Perform() fails to isolate floating face; output shell retains
unpredictable adjacency.

Mechanism IS the shell structure: TWO ADVANCED_FACEs wired into ONE OPEN_SHELL —
face_main IS a unit square with a complete 4-edge EDGE_LOOP; face_float IS a
second unit square at x=3 (gap of 2 units) with its own complete EDGE_LOOP but
NO shared edges with face_main. Both faces ARE wired into the same OPEN_SHELL
entity. The geometric gap between them IS the "floating" condition: face_float
is topologically inside the shell but IS not reachable via edge adjacency from
face_main. Perform() traverses edge adjacency to find connected components;
face_float IS unreachable via that traversal. The two-face single-shell with
a floating disconnected face IS the minimal structure that exposes the
adjacency-isolation failure.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh169",
    defect=(
        "TWO ADVANCED_FACEs in ONE OPEN_SHELL with no shared edges — "
        "IS the floating-face mechanism; "
        "face_main IS wired with loop_main (4 edges, unit square x=[0,1]) — IS main component; "
        "face_float IS wired with loop_float (4 edges, unit square x=[3,4]) — IS floating face; "
        "gap of 2 units between face_main and face_float IS the disconnection; "
        "no edge IS shared between face_main and face_float — IS the floating condition; "
        "both faces ARE wired into the same OPEN_SHELL entity; "
        "Perform() traverses edge adjacency from any start face; "
        "face_float IS not reachable via edge adjacency from face_main; "
        "floating face isolation failure: Perform() retains face_float in output shell; "
        "output shell adjacency IS unpredictable — IS the defect manifestation; "
        "fix: detect disconnected face components; isolate floating faces to separate shells; "
        "emit E_PERFORM_FLOATING_FACE when shell has unreachable face component"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# face_main: unit square x=[0,1], y=[0,1], z=0 — IS the main connected face
p00m = cp(0, 0, 0); p10m = cp(1, 0, 0); p11m = cp(1, 1, 0); p01m = cp(0, 1, 0)
v00m = f.vertex_point(p00m); v10m = f.vertex_point(p10m)
v11m = f.vertex_point(p11m); v01m = f.vertex_point(p01m)
e_m_bot   = led(v00m, v10m, p00m,  1, 0, 0)
e_m_right = led(v10m, v11m, p10m,  0, 1, 0)
e_m_top   = led(v01m, v11m, p01m,  1, 0, 0)
e_m_left  = led(v00m, v01m, p00m,  0, 1, 0)
loop_main = f.edge_loop([
    f.oriented_edge(e_m_bot,   True),
    f.oriented_edge(e_m_right, True),
    f.oriented_edge(e_m_top,   False),
    f.oriented_edge(e_m_left,  False),
])
plane_main = f.plane(f.axis2_placement_3d(p00m, dir3(0, 0, 1), dir3(1, 0, 0)))
face_main = f.advanced_face([f.face_outer_bound(loop_main, orientation=True)], plane_main, same_sense=True)

# face_float: unit square x=[3,4], y=[0,1], z=0 — IS the floating disconnected face
# gap of 2 units at x=[1,3] ensures no shared edges with face_main
p00f = cp(3, 0, 0); p10f = cp(4, 0, 0); p11f = cp(4, 1, 0); p01f = cp(3, 1, 0)
v00f = f.vertex_point(p00f); v10f = f.vertex_point(p10f)
v11f = f.vertex_point(p11f); v01f = f.vertex_point(p01f)
e_f_bot   = led(v00f, v10f, p00f,  1, 0, 0)
e_f_right = led(v10f, v11f, p10f,  0, 1, 0)
e_f_top   = led(v01f, v11f, p01f,  1, 0, 0)
e_f_left  = led(v00f, v01f, p00f,  0, 1, 0)
loop_float = f.edge_loop([
    f.oriented_edge(e_f_bot,   True),
    f.oriented_edge(e_f_right, True),
    f.oriented_edge(e_f_top,   False),
    f.oriented_edge(e_f_left,  False),
])
plane_float = f.plane(f.axis2_placement_3d(p00f, dir3(0, 0, 1), dir3(1, 0, 0)))
face_float = f.advanced_face([f.face_outer_bound(loop_float, orientation=True)], plane_float, same_sense=True)

# ONE OPEN_SHELL containing both faces, no shared edges — IS the floating mechanism
shell = f.open_shell([face_main, face_float])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
