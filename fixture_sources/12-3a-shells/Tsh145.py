"""Tsh145 — ShapeAnalysis_Shell.CheckOrientedShells one-face-shell-edge-cases.

Catalog claim: Single-face shell with orientation flag set to `.F.` (reversed).
CheckOrientedShells semantics for 1-face shells are undocumented; tests whether
solver correctly handles the edge case of a minimal manifold.

Mechanism IS the shell structure: a single ADVANCED_FACE (unit square) in an
OPEN_SHELL with same_sense=False — the inverted SAME_SENSE flag IS the mechanism
wired directly into the ADVANCED_FACE entity. A 1-face shell IS trivially
orientable (no adjacent face to compare against) but CheckOrientedShells must
decide what "oriented" means for a degenerate 1-face case. The SAME_SENSE=False
flag IS the reversed-orientation wired into the ADVANCED_FACE, forming the
minimal-manifold edge case.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh145",
    defect=(
        "OPEN_SHELL with 1 ADVANCED_FACE — IS the minimal-manifold mechanism; "
        "single unit square (x=[0,1] y=[0,1] z=0) IS wired into the OPEN_SHELL; "
        "ADVANCED_FACE SAME_SENSE=False IS the reversed orientation flag wired into the face entity; "
        "PLANE with normal (0,0,1) IS wired into the ADVANCED_FACE reference; "
        "1-face shell with inverted SAME_SENSE IS the one-face-shell edge-case topology; "
        "CheckOrientedShells has no adjacent face to compare against — semantics undefined for n==1; "
        "fix: special-case n==1 shell: treat any orientation as valid or require SAME_SENSE=True; "
        "emit E_ONE_FACE_SHELL_ORIENTATION_UNDEFINED when CheckOrientedShells receives 1-face shell"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Single unit square at z=0
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0)
p11 = cp(1, 1, 0); p01 = cp(0, 1, 0)

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

# PLANE normal (0,0,1) IS wired into the face
plane_orig = cp(0, 0, 0)
plane = f.plane(f.axis2_placement_3d(plane_orig, dir3(0, 0, 1), dir3(1, 0, 0)))

# ADVANCED_FACE with same_sense=False — IS the reversed-orientation mechanism wired into the face
face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=False)

# OPEN_SHELL with single reversed face — IS the one-face-shell edge-case mechanism
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
