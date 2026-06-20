"""Tsh174 — ShapeFix_Shell.FixFaceOrientation with-empty-shell-after-fix.

Catalog claim: Shell where Perform removes all faces; FixFaceOrientation
runs on the empty shell and reports success without detecting the void.

Mechanism IS the shell structure: TWO ADVANCED_FACEs with degenerate
zero-area geometry (line-like loops) ARE wired into an OPEN_SHELL. Each
face IS a degenerate triangle where all three vertices are collinear —
the face area IS zero. face_degen_a uses vertices at (0,0,0), (1,0,0),
(2,0,0) all on the x-axis; face_degen_b uses vertices at (0,0,0),
(-1,0,0), (-2,0,0) in the opposite direction. Both faces have their
EDGE_LOOPs wired into the OPEN_SHELL. Perform() detects degenerate
faces via topological validation and removes them. After removal the
shell IS empty. FixFaceOrientation() then runs on the empty shell and
returns success — IS the masked defect: empty-shell fix success
IS indistinguishable from valid-shell fix success.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(8) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh174",
    defect=(
        "TWO degenerate ADVANCED_FACEs in ONE OPEN_SHELL — IS the empty-shell-after-fix mechanism; "
        "face_degen_a IS a collinear triangle (0,0,0)→(1,0,0)→(2,0,0) — zero-area degenerate face; "
        "face_degen_b IS a collinear triangle (0,0,0)→(-1,0,0)→(-2,0,0) — zero-area opposite direction; "
        "both faces ARE wired with closed EDGE_LOOPs into OPEN_SHELL — IS valid topology with invalid geometry; "
        "Perform() detects zero-area geometry and removes both faces from the shell; "
        "shell IS empty after Perform() — IS the void condition; "
        "FixFaceOrientation() runs on empty shell and reports success — IS the masked defect; "
        "success on empty shell IS indistinguishable from success on valid shell; "
        "fix: check shell face count before reporting FixFaceOrientation success; "
        "emit E_FIX_ORIENTATION_EMPTY_SHELL when face count after Perform is zero"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# face_degen_a: collinear triangle on x-axis — zero-area degenerate face
# Vertices: (0,0,0), (1,0,0), (2,0,0) — all on x-axis, collinear
pa0 = cp(0, 0, 0); pa1 = cp(1, 0, 0); pa2 = cp(2, 0, 0)
va0 = f.vertex_point(pa0); va1 = f.vertex_point(pa1); va2 = f.vertex_point(pa2)
ea_01 = led(va0, va1, pa0,  1, 0, 0)   # (0,0,0)→(1,0,0)
ea_12 = led(va1, va2, pa1,  1, 0, 0)   # (1,0,0)→(2,0,0)
ea_20 = led(va2, va0, pa2, -1, 0, 0)   # (2,0,0)→(0,0,0)
loop_a = f.edge_loop([
    f.oriented_edge(ea_01, True),
    f.oriented_edge(ea_12, True),
    f.oriented_edge(ea_20, True),
])
# Plane normal +Z but face IS degenerate (collinear vertices = zero area)
plane_a = f.plane(f.axis2_placement_3d(pa0, dir3(0, 0, 1), dir3(1, 0, 0)))
face_degen_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], plane_a, same_sense=True)

# face_degen_b: collinear triangle on x-axis in opposite direction — zero-area
# Vertices: (0,0,0), (-1,0,0), (-2,0,0) — all on x-axis, collinear
pb0 = cp(0, 0, 0); pb1 = cp(-1, 0, 0); pb2 = cp(-2, 0, 0)
vb0 = f.vertex_point(pb0); vb1 = f.vertex_point(pb1); vb2 = f.vertex_point(pb2)
eb_01 = led(vb0, vb1, pb0, -1, 0, 0)   # (0,0,0)→(-1,0,0)
eb_12 = led(vb1, vb2, pb1, -1, 0, 0)   # (-1,0,0)→(-2,0,0)
eb_20 = led(vb2, vb0, pb2,  1, 0, 0)   # (-2,0,0)→(0,0,0)
loop_b = f.edge_loop([
    f.oriented_edge(eb_01, True),
    f.oriented_edge(eb_12, True),
    f.oriented_edge(eb_20, True),
])
plane_b = f.plane(f.axis2_placement_3d(pb0, dir3(0, 0, 1), dir3(-1, 0, 0)))
face_degen_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], plane_b, same_sense=True)

# OPEN_SHELL: two degenerate zero-area faces — IS the empty-shell-after-fix mechanism
# Perform() removes both faces; FixFaceOrientation() succeeds on empty shell — IS the defect
shell = f.open_shell([face_degen_a, face_degen_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
