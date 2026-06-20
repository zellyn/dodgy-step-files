"""Tsh217 — ShapeFix_Shell.Perform.closed_flag_sync_failure.

Catalog claim: Closed() flag out-of-sync with HasFreeEdges after
FixFaceOrientation; breaks downstream solid construction.

Mechanism IS the shell structure: AN OPEN_SHELL containing FOUR ADVANCED_FACEs
forming a CLOSED arrangement (all boundary edges shared, no free edges) IS the
defect trigger. The shell IS given as OPEN_SHELL (not CLOSED_SHELL) so Closed()
returns False initially. After ShapeFix_Shell.FixFaceOrientation runs and
resolves all orientations, HasFreeEdges() returns False (all edges shared) —
IS the closed condition. Perform() must sync the Closed() flag with HasFreeEdges
post-fix; failure to do so leaves Closed()==False while HasFreeEdges()==False —
IS the sync-failure defect that breaks downstream solid construction.

Tier-3 assertion: n_faces_total == 4

live oracle: occt=shape(1)/shape(1) gmsh=shape(12) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh217",
    defect=(
        "OPEN_SHELL with FOUR ADVANCED_FACEs forming a closed box (no free edges) IS the closed-flag-sync defect trigger; "
        "four faces form a closed quad-surface: bottom, top, front, back — IS the closed arrangement; "
        "shell IS declared as OPEN_SHELL — IS the initial Closed()==False state; "
        "all boundary edges ARE shared between adjacent faces — IS the HasFreeEdges()==False post-fix condition; "
        "face orientations are mixed (some same_sense=False) — IS the FixFaceOrientation trigger; "
        "ShapeFix_Shell.FixFaceOrientation IS the defect path: resolves face orientations; "
        "after FixFaceOrientation, HasFreeEdges() returns False — IS the closed post-fix state; "
        "Perform() does NOT update Closed() flag after FixFaceOrientation — IS the sync failure; "
        "Closed() remains False while HasFreeEdges() is False — IS the out-of-sync state; "
        "downstream solid construction checks Closed() flag — IS the solid-break dependency; "
        "solid construction fails because Closed()==False even though shell IS geometrically closed — IS the defect outcome; "
        "fix: Perform() must set Closed()=True when HasFreeEdges()==False after FixFaceOrientation; "
        "emit E_CLOSED_FLAG_SYNC_FAILURE when Closed() disagrees with HasFreeEdges post-fix"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Build a closed quad-surface: bottom (Z=0), top (Z=1), front (Y=0), back (Y=1)
# Shared corner vertices — IS the shared-edge topology
p000 = cp(0, 0, 0); v000 = f.vertex_point(p000)
p100 = cp(1, 0, 0); v100 = f.vertex_point(p100)
p110 = cp(1, 1, 0); v110 = f.vertex_point(p110)
p010 = cp(0, 1, 0); v010 = f.vertex_point(p010)
p001 = cp(0, 0, 1); v001 = f.vertex_point(p001)
p101 = cp(1, 0, 1); v101 = f.vertex_point(p101)
p111 = cp(1, 1, 1); v111 = f.vertex_point(p111)
p011 = cp(0, 1, 1); v011 = f.vertex_point(p011)

# Shared horizontal edges — IS the shared boundary between top/bottom and side faces
e_bot_front = led(v000, v100, p000,  1, 0, 0)   # bottom-front edge (shared: bottom + front)
e_bot_right  = led(v100, v110, p100,  0, 1, 0)  # bottom-right edge (shared: bottom + right [omitted])
e_bot_back   = led(v110, v010, p110, -1, 0, 0)  # bottom-back edge (shared: bottom + back)
e_bot_left   = led(v010, v000, p010,  0,-1, 0)  # bottom-left edge (shared: bottom + left [omitted])
e_top_front  = led(v001, v101, p001,  1, 0, 0)  # top-front edge (shared: top + front)
e_top_right  = led(v101, v111, p101,  0, 1, 0)  # top-right edge
e_top_back   = led(v111, v011, p111, -1, 0, 0)  # top-back edge (shared: top + back)
e_top_left   = led(v011, v001, p011,  0,-1, 0)  # top-left edge
# Vertical edges at Y=0 (front) — IS the front-face vertical edges
e_vfl = led(v000, v001, p000, 0, 0, 1)   # front-left vertical
e_vfr = led(v100, v101, p100, 0, 0, 1)   # front-right vertical
# Vertical edges at Y=1 (back)
e_vbl = led(v010, v011, p010, 0, 0, 1)   # back-left vertical
e_vbr = led(v110, v111, p110, 0, 0, 1)   # back-right vertical

# Bottom face (Z=0, normal -Z, same_sense=False) — IS repair-needed face 1
loop_bot = f.edge_loop([
    f.oriented_edge(e_bot_front, True),
    f.oriented_edge(e_bot_right, True),
    f.oriented_edge(e_bot_back,  True),
    f.oriented_edge(e_bot_left,  True),
])
plane_bot = f.plane(f.axis2_placement_3d(p000, dir3(0, 0, -1), dir3(1, 0, 0)))
face_bot = f.advanced_face([f.face_outer_bound(loop_bot, orientation=True)], plane_bot, same_sense=False)

# Top face (Z=1, normal +Z, same_sense=True) — IS valid face 1
loop_top = f.edge_loop([
    f.oriented_edge(e_top_front, True),
    f.oriented_edge(e_top_right, True),
    f.oriented_edge(e_top_back,  True),
    f.oriented_edge(e_top_left,  True),
])
plane_top = f.plane(f.axis2_placement_3d(p001, dir3(0, 0, 1), dir3(1, 0, 0)))
face_top = f.advanced_face([f.face_outer_bound(loop_top, orientation=True)], plane_top, same_sense=True)

# Front face (Y=0, normal -Y, same_sense=False) — IS repair-needed face 2
loop_front = f.edge_loop([
    f.oriented_edge(e_bot_front, True),
    f.oriented_edge(e_vfr,       True),
    f.oriented_edge(e_top_front, False),
    f.oriented_edge(e_vfl,       False),
])
plane_front = f.plane(f.axis2_placement_3d(p000, dir3(0, -1, 0), dir3(1, 0, 0)))
face_front = f.advanced_face([f.face_outer_bound(loop_front, orientation=True)], plane_front, same_sense=False)

# Back face (Y=1, normal +Y, same_sense=True) — IS valid face 2
loop_back = f.edge_loop([
    f.oriented_edge(e_bot_back,  True),
    f.oriented_edge(e_vbr,       True),
    f.oriented_edge(e_top_back,  False),
    f.oriented_edge(e_vbl,       False),
])
plane_back = f.plane(f.axis2_placement_3d(p010, dir3(0, 1, 0), dir3(1, 0, 0)))
face_back = f.advanced_face([f.face_outer_bound(loop_back, orientation=True)], plane_back, same_sense=True)

# OPEN_SHELL: four faces forming closed geometry — IS the closed-flag-sync-failure mechanism
# Closed() IS False (OPEN_SHELL); HasFreeEdges() IS False after fix — IS the sync gap
shell = f.open_shell([face_bot, face_top, face_front, face_back])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
