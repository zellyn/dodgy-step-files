"""Tsh096 — ShapeAnalysis_Shell.CheckOrientedShells degenerate-face.

Catalog claim: Shell contains a degenerate face (zero-area, e.g. all vertices
collapsed to single point). CheckOrientedShells uses normal direction to classify
faces as inward/outward, but a degenerate face has no well-defined normal vector.

Mechanism IS the shell structure: The OPEN_SHELL contains one normal ADVANCED_FACE
(valid 2x2 quad) and one degenerate ADVANCED_FACE (all four VERTEX_POINTs at the
same location (1,1,0)). The degenerate face's EDGE_LOOP has zero-length edges —
all EDGE_CURVEs share the same start and end VERTEX_POINT. This zero-area face
with undefined normal IS directly wired into the shell's ADVANCED_FACE list.
CheckOrientedShells attempts normal-based orientation classification on the
degenerate face; the undefined normal IS the mechanism causing silent failure or
undefined orientation state.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh096",
    defect=(
        "OPEN_SHELL with 1 valid ADVANCED_FACE and 1 degenerate ADVANCED_FACE — IS the mechanism; "
        "degenerate face has all 4 VERTEX_POINTs collapsed to same point (1,1,0) — zero area; "
        "degenerate EDGE_LOOP has zero-length EDGE_CURVEs — all start==end VERTEX_POINT; "
        "zero-area face with undefined normal IS directly wired into shell ADVANCED_FACE list; "
        "CheckOrientedShells attempts normal-based classification on undefined-normal face; "
        "undefined normal IS the mechanism causing silent failure or undefined orientation; "
        "fix: detect zero-area faces before CheckOrientedShells classification; report error; "
        "emit E_DEGENERATE_FACE_IN_ORIENTED_SHELL_CHECK when normal undefined"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Valid face: 2x2 quad at z=0 — provides a well-defined reference face in the shell
pN = [cp(0,0,0), cp(2,0,0), cp(2,2,0), cp(0,2,0)]
vN = [f.vertex_point(p) for p in pN]
eN = [
    led(vN[0], vN[1], pN[0],  1, 0, 0),
    led(vN[1], vN[2], pN[1],  0, 1, 0),
    led(vN[2], vN[3], pN[2], -1, 0, 0),
    led(vN[3], vN[0], pN[3],  0,-1, 0),
]
loop_n = f.edge_loop([f.oriented_edge(e, True) for e in eN])
pl_n = f.plane(f.axis2_placement_3d(pN[0], dir3(0, 0, 1), dir3(1, 0, 0)))
face_n = f.advanced_face([f.face_outer_bound(loop_n, orientation=True)], pl_n, same_sense=True)

# Degenerate face: all 4 vertices collapsed to single point (1,1,0) — IS the mechanism
p_degen = cp(1, 1, 0)
v_degen = f.vertex_point(p_degen)
zero_dir = dir3(0, 0, 0)
zero_vec = f.vector(zero_dir, 0.0)
zero_line = f.line(p_degen, zero_vec)
# All four edges: same degenerate vertex, zero-length — IS directly in EDGE_LOOP
ed0 = f.edge_curve(v_degen, v_degen, zero_line)
ed1 = f.edge_curve(v_degen, v_degen, zero_line)
ed2 = f.edge_curve(v_degen, v_degen, zero_line)
ed3 = f.edge_curve(v_degen, v_degen, zero_line)
loop_d = f.edge_loop([
    f.oriented_edge(ed0, True), f.oriented_edge(ed1, True),
    f.oriented_edge(ed2, True), f.oriented_edge(ed3, True),
])
pl_d = f.plane(f.axis2_placement_3d(p_degen, dir3(0, 0, 1), dir3(1, 0, 0)))
# Zero-area degenerate ADVANCED_FACE IS the mechanism with undefined normal
face_d = f.advanced_face([f.face_outer_bound(loop_d, orientation=True)], pl_d, same_sense=True)

# OPEN_SHELL: valid face + degenerate face — degenerate IS wired into shell topology
shell = f.open_shell([face_n, face_d])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
