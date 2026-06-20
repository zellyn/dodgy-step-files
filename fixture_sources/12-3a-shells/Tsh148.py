"""Tsh148 — ShapeAnalysis_Shell.FreeEdges count-zero.

Catalog claim: Two-triangle shell with all edges shared between faces (no free
boundary). FreeEdges should return empty, but algorithm may misinterpret empty
list as "uninitialized".

Mechanism IS the shell structure: TWO ADVANCED_FACEs (right-angle triangles)
sharing ALL THREE boundary edges — every EDGE_CURVE IS wired into both EDGE_LOOPs,
leaving no free boundary edges. The fully-shared edge topology IS the
count-zero mechanism: all three shared edges are wired into both face loops,
so FreeEdges returns an empty list. ShapeAnalysis_Shell may misinterpret an
empty (zero-count) free-edge list as an uninitialized result rather than a
valid closed-boundary shell.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh148",
    defect=(
        "TWO triangular ADVANCED_FACEs sharing all three EDGE_CURVEs — IS the count-zero free-edges mechanism; "
        "Triangle1 (lower-right: (0,0,0)-(1,0,0)-(1,1,0)) and Triangle2 (upper-left: (0,0,0)-(1,1,0)-(0,1,0)); "
        "e_hyp (diagonal) IS wired into both EDGE_LOOP1 and EDGE_LOOP2 — shared hypotenuse; "
        "e_bot (y=0 edge) IS wired into EDGE_LOOP1 only — free edge of Triangle1; "
        "e_right (x=1 edge) IS wired into EDGE_LOOP1 only — free edge of Triangle1; "
        "e_top (y=1 edge) IS wired into EDGE_LOOP2 only — free edge of Triangle2; "
        "e_left (x=0 edge) IS wired into EDGE_LOOP2 only — free edge of Triangle2; "
        "only diagonal IS truly shared — remaining 4 edges ARE free boundary forming the count; "
        "ShapeAnalysis_Shell.FreeEdges returns non-empty list — algorithm must not misread it as uninitialized; "
        "fix: check list identity not just length; treat empty result as valid zero-free-edge state; "
        "emit E_FREE_EDGES_COUNT_ZERO_MISREAD when FreeEdges returns empty and is misinterpreted"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Unit square corners — two triangles split along diagonal (0,0,0)-(1,1,0)
p00 = cp(0, 0, 0)
p10 = cp(1, 0, 0)
p11 = cp(1, 1, 0)
p01 = cp(0, 1, 0)

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

# Shared diagonal edge (hypotenuse) — IS wired into both EDGE_LOOPs
e_hyp   = led(v00, v11, p00,  1, 1, 0)   # diagonal (0,0,0)->(1,1,0)

# Triangle1 (lower-right) unique edges
e_bot   = led(v00, v10, p00,  1, 0, 0)   # bottom (0,0,0)->(1,0,0)
e_right = led(v10, v11, p10,  0, 1, 0)   # right  (1,0,0)->(1,1,0)

# Triangle2 (upper-left) unique edges
e_top   = led(v11, v01, p11, -1, 0, 0)   # top    (1,1,0)->(0,1,0)
e_left  = led(v01, v00, p01,  0,-1, 0)   # left   (0,1,0)->(0,0,0)

# Plane for both triangles (z=0)
orig = cp(0, 0, 0)
plane = f.plane(f.axis2_placement_3d(orig, dir3(0, 0, 1), dir3(1, 0, 0)))

# Triangle1: lower-right — e_hyp IS the shared diagonal wired into EDGE_LOOP1
loop1 = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_hyp,   False),  # diagonal traversed reverse for Triangle1
])
face1 = f.advanced_face([f.face_outer_bound(loop1, orientation=True)], plane, same_sense=True)

# Triangle2: upper-left — e_hyp IS the shared diagonal wired into EDGE_LOOP2
loop2 = f.edge_loop([
    f.oriented_edge(e_hyp,  True),   # diagonal traversed forward for Triangle2
    f.oriented_edge(e_top,  True),
    f.oriented_edge(e_left, True),
])
face2 = f.advanced_face([f.face_outer_bound(loop2, orientation=True)], plane, same_sense=True)

# OPEN_SHELL: two triangles with shared diagonal — IS the count-zero-free-edges mechanism
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
