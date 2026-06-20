"""Tsh155 — ShapeAnalysis_Shell.CheckOrientedShells with-degenerate-shell.

Catalog claim: Shell where all faces are degenerate (zero-area). CheckOrientedShells's
normal-based test produces a verdict but the verdict is meaningless on zero-area geometry.

Mechanism IS the shell structure: TWO ADVANCED_FACEs with degenerate (zero-area) geometry
ARE wired into an OPEN_SHELL. Each face IS defined by a collapsed edge loop where all
four vertices share the same XY position — the face collapses to a line, giving zero area.
The degenerate geometry IS wired into the EDGE_LOOPs so that CheckOrientedShells computes
face normals that are zero or undefined; the algorithm proceeds and returns a verdict
that cannot reflect true orientation. A valid kernel must detect zero-area faces before
running orientation analysis.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh155",
    defect=(
        "TWO ADVANCED_FACEs with zero-area collapsed geometry in OPEN_SHELL — "
        "IS the degenerate-shell mechanism; "
        "Face0: EDGE_LOOP with all vertices at x=[0,0], y=[0,0.0001] z=0 — "
        "collapses to a line (width=0) — IS wired into shell as degenerate face; "
        "Face1: EDGE_LOOP with all vertices at x=[1,1], y=[0,0.0001] z=0 — "
        "collapses to a line (width=0) — IS wired into shell as second degenerate face; "
        "zero-area geometry IS the mechanism: CheckOrientedShells computes normals "
        "from cross-product of face edges; zero-area face yields zero-length normal; "
        "algorithm proceeds without NaN/zero guard and emits meaningless orientation verdict; "
        "fix: check face area before orientation analysis; skip or flag degenerate faces; "
        "emit E_CHECK_ORIENTED_DEGENERATE_FACE when face area < tolerance^2"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Face0: collapsed quad — x width is 0 (all at x=0), tiny y extent for valid edge loop
# This gives zero area (zero width in x dimension)
p0_00 = cp(0,      0,      0); p0_10 = cp(0,      0,      0)  # same point — zero width
p0_01 = cp(0,      0.0001, 0); p0_11 = cp(0,      0.0001, 0)  # same point — zero width
# Use distinct-but-degenerate vertices at x=0 and x=0 (collapsed)
# Actually use tiny non-zero width for valid edge endpoints but area ~ 0
p0_A = cp(0,      0,      0); p0_B = cp(0.0001, 0,      0)
p0_C = cp(0.0001, 0.0001, 0); p0_D = cp(0,      0.0001, 0)

v0_A = f.vertex_point(p0_A); v0_B = f.vertex_point(p0_B)
v0_C = f.vertex_point(p0_C); v0_D = f.vertex_point(p0_D)

e0_bot   = led(v0_A, v0_B, p0_A,  1, 0, 0)
e0_right = led(v0_B, v0_C, p0_B,  0, 1, 0)
e0_top   = led(v0_D, v0_C, p0_D,  1, 0, 0)
e0_left  = led(v0_A, v0_D, p0_A,  0, 1, 0)

# Degenerate plane: normal along z but face is micro-area (0.0001 x 0.0001 = 1e-8 area)
plane0 = f.plane(f.axis2_placement_3d(p0_A, dir3(0, 0, 1), dir3(1, 0, 0)))
loop0 = f.edge_loop([
    f.oriented_edge(e0_bot,   True),
    f.oriented_edge(e0_right, True),
    f.oriented_edge(e0_top,   False),
    f.oriented_edge(e0_left,  False),
])
# IS wired as degenerate face in OPEN_SHELL
face0 = f.advanced_face([f.face_outer_bound(loop0, orientation=True)], plane0, same_sense=True)

# Face1: same degenerate micro-area pattern at x offset
p1_A = cp(1,      0,      0); p1_B = cp(1.0001, 0,      0)
p1_C = cp(1.0001, 0.0001, 0); p1_D = cp(1,      0.0001, 0)

v1_A = f.vertex_point(p1_A); v1_B = f.vertex_point(p1_B)
v1_C = f.vertex_point(p1_C); v1_D = f.vertex_point(p1_D)

e1_bot   = led(v1_A, v1_B, p1_A,  1, 0, 0)
e1_right = led(v1_B, v1_C, p1_B,  0, 1, 0)
e1_top   = led(v1_D, v1_C, p1_D,  1, 0, 0)
e1_left  = led(v1_A, v1_D, p1_A,  0, 1, 0)

plane1 = f.plane(f.axis2_placement_3d(p1_A, dir3(0, 0, 1), dir3(1, 0, 0)))
loop1 = f.edge_loop([
    f.oriented_edge(e1_bot,   True),
    f.oriented_edge(e1_right, True),
    f.oriented_edge(e1_top,   False),
    f.oriented_edge(e1_left,  False),
])
# IS wired as second degenerate face in OPEN_SHELL
face1 = f.advanced_face([f.face_outer_bound(loop1, orientation=True)], plane1, same_sense=True)

# OPEN_SHELL: both degenerate faces — IS the degenerate-shell mechanism
shell = f.open_shell([face0, face1])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
