"""Tsh105 — ShapeAnalysis_Shell.CheckOrientedShells unconnected components.

Catalog claim: Shell with two disjoint sub-shells (not topologically connected);
CheckOrientedShells reports a single verdict instead of per-component. Contains
two isolated square faces (Component 1 at origin, Component 2 at x=10) with no
shared edges. CheckOrientedShells must detect and report orientation issues per
connected component.

Mechanism IS the shell structure: an OPEN_SHELL wraps two ADVANCED_FACEs that
share NO vertices, edges, or edge geometry — they are spatially separated (face1
at x=[0,1], face2 at x=[10,11]). The two disjoint connected-components ARE
directly wired into the single OPEN_SHELL entity. CheckOrientedShells iterates
faces within the shell to propagate orientation; the disjoint topology IS the
mechanism — propagation from Component 1 cannot reach Component 2, so the per-
component verdict is indeterminate.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh105",
    defect=(
        "OPEN_SHELL contains 2 ADVANCED_FACEs with NO shared edges or vertices — IS the mechanism; "
        "Face1 unit square at x=[0,1] y=[0,1] z=0 — IS Component 1 in shell topology; "
        "Face2 unit square at x=[10,11] y=[0,1] z=0 — IS Component 2 in shell topology; "
        "no edge or vertex IS shared between Face1 and Face2 in OPEN_SHELL; "
        "disjoint topology IS directly wired into single OPEN_SHELL entity; "
        "CheckOrientedShells propagates orientation graph from seed face; "
        "disconnected graph means propagation IS blocked from reaching Face2; "
        "single-verdict reported instead of per-component verdict IS the defect; "
        "fix: enumerate connected components before orientation check; "
        "emit E_UNCONNECTED_SHELL_COMPONENTS when propagation cannot reach all faces"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# ── Component 1: unit square at origin, x=[0,1], y=[0,1], z=0 ──────────────
p1_00 = cp(0, 0, 0); p1_10 = cp(1, 0, 0); p1_11 = cp(1, 1, 0); p1_01 = cp(0, 1, 0)
v1_00 = f.vertex_point(p1_00); v1_10 = f.vertex_point(p1_10)
v1_11 = f.vertex_point(p1_11); v1_01 = f.vertex_point(p1_01)

e1_bot   = led(v1_00, v1_10, p1_00,  1, 0, 0)
e1_right = led(v1_10, v1_11, p1_10,  0, 1, 0)
e1_top   = led(v1_11, v1_01, p1_11, -1, 0, 0)
e1_left  = led(v1_01, v1_00, p1_01,  0,-1, 0)
loop1 = f.edge_loop([
    f.oriented_edge(e1_bot,   True),
    f.oriented_edge(e1_right, True),
    f.oriented_edge(e1_top,   True),
    f.oriented_edge(e1_left,  True),
])
pl1 = f.plane(f.axis2_placement_3d(p1_00, dir3(0, 0, 1), dir3(1, 0, 0)))
face1 = f.advanced_face([f.face_outer_bound(loop1, orientation=True)], pl1, same_sense=True)

# ── Component 2: unit square at x=10, x=[10,11], y=[0,1], z=0 ──────────────
# No vertex or edge shared with Component 1 — IS the disjoint mechanism
p2_00 = cp(10, 0, 0); p2_10 = cp(11, 0, 0); p2_11 = cp(11, 1, 0); p2_01 = cp(10, 1, 0)
v2_00 = f.vertex_point(p2_00); v2_10 = f.vertex_point(p2_10)
v2_11 = f.vertex_point(p2_11); v2_01 = f.vertex_point(p2_01)

e2_bot   = led(v2_00, v2_10, p2_00,  1, 0, 0)
e2_right = led(v2_10, v2_11, p2_10,  0, 1, 0)
e2_top   = led(v2_11, v2_01, p2_11, -1, 0, 0)
e2_left  = led(v2_01, v2_00, p2_01,  0,-1, 0)
loop2 = f.edge_loop([
    f.oriented_edge(e2_bot,   True),
    f.oriented_edge(e2_right, True),
    f.oriented_edge(e2_top,   True),
    f.oriented_edge(e2_left,  True),
])
pl2 = f.plane(f.axis2_placement_3d(p2_00, dir3(0, 0, 1), dir3(1, 0, 0)))
face2 = f.advanced_face([f.face_outer_bound(loop2, orientation=True)], pl2, same_sense=True)

# OPEN_SHELL: both disjoint components in one shell — IS the mechanism
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
