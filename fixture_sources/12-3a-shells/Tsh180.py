"""Tsh180 — ShapeAnalysis_Shell.CheckOrientedShells single-face zero-area.

Catalog claim: Shell containing single face with computed area exactly 0.0;
normal-based orientation test fails to classify orientation; CheckOrientedShells
raises exception or returns false instead of exception-free classification.

Mechanism IS the shell structure: ONE ADVANCED_FACE with all three vertices
COLLINEAR (on the X-axis) IS wired into a CLOSED_SHELL. The collinear triangle
IS the zero-area face: cross product of the two edge vectors yields zero vector,
so normal IS undefined. CheckOrientedShells IS the defect trigger: it attempts
normal-based orientation classification, computes zero-length normal,
encounters NaN/inf during determinant computation, and returns false instead of
graceful handling.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh180",
    defect=(
        "ONE ADVANCED_FACE with THREE COLLINEAR VERTICES (all on X-axis) IS the zero-area face; "
        "pa=(0,0,0), pb=(1,0,0), pc=(2,0,0) — collinear, zero cross-product — IS the defect trigger; "
        "CLOSED_SHELL with single zero-area face IS what CheckOrientedShells receives; "
        "normal computation yields zero vector — IS the NaN/inf source; "
        "CheckOrientedShells returns false instead of exception-free classification — IS the defect; "
        "fix: CheckOrientedShells must detect zero-area faces and skip normal test gracefully; "
        "emit E_CHECK_ORIENTED_ZERO_AREA when zero-area face detected in shell"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# THREE COLLINEAR vertices on X-axis — IS the zero-area mechanism
pa = cp(0, 0, 0)
pb = cp(1, 0, 0)
pc = cp(2, 0, 0)
va = f.vertex_point(pa)
vb = f.vertex_point(pb)
vc = f.vertex_point(pc)

# Edges along X-axis — triangle collapses to line segment
e_ab = led(va, vb, pa, 1, 0, 0)    # (0,0,0)→(1,0,0)
e_bc = led(vb, vc, pb, 1, 0, 0)    # (1,0,0)→(2,0,0)
e_ca = led(vc, va, pc, -1, 0, 0)   # (2,0,0)→(0,0,0)

# Degenerate face: collinear boundary — normal IS undefined (zero cross-product)
loop = f.edge_loop([
    f.oriented_edge(e_ab, True),
    f.oriented_edge(e_bc, True),
    f.oriented_edge(e_ca, True),
])
# Plane placed at origin with +Z normal (but face IS degenerate — zero area)
plane = f.plane(f.axis2_placement_3d(pa, dir3(0, 0, 1), dir3(1, 0, 0)))
face_zero_area = f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=True)

# CLOSED_SHELL with single zero-area face — IS the CheckOrientedShells defect trigger
shell = f.closed_shell([face_zero_area])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
