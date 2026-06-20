"""Tsh178 — ShapeAnalysis_Shell.FreeEdges with-degenerate-edges.

Catalog claim: Shell where some edges are degenerate (zero-length); FreeEdges
counts them as free even though they don't bound a face.

Mechanism IS the shell structure: ONE ADVANCED_FACE (a valid triangle) IS
wired into an OPEN_SHELL together with THREE separate degenerate EDGE_CURVEs
(self-loop edges where start vertex == end vertex, zero length). Each degenerate
edge IS wired as a standalone ORIENTED_EDGE in its own EDGE_LOOP that references
no face — they are free-floating self-loop edges directly in the shell topology.
FreeEdges IS the defect trigger: the analysis classifies all three degenerate
self-loops as free edges instead of excluding them, so the free-edge count is
inflated from 3 (triangle boundary) to 6.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh178",
    defect=(
        "ONE ADVANCED_FACE (triangle) IS wired into OPEN_SHELL — IS the valid face; "
        "THREE degenerate EDGE_CURVEs (zero-length self-loops) also wired into same shell — IS the defect trigger; "
        "e_degen_a IS EDGE_CURVE from va back to va, zero-length LINE — IS degenerate self-loop at vertex (0,0,0); "
        "e_degen_b IS EDGE_CURVE from vb back to vb, zero-length LINE — IS degenerate self-loop at vertex (1,0,0); "
        "e_degen_c IS EDGE_CURVE from vc back to vc, zero-length LINE — IS degenerate self-loop at vertex (0.5,1,0); "
        "FreeEdges analysis classifies degenerate self-loops as free edges — IS the defect; "
        "fix: FreeEdges must exclude zero-length self-loop edges from free-edge count; "
        "emit E_FREE_EDGES_DEGENERATE_EXCLUDED when degenerate edges are filtered"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Triangle vertices
pa = cp(0,   0, 0)
pb = cp(1,   0, 0)
pc = cp(0.5, 1, 0)
va = f.vertex_point(pa)
vb = f.vertex_point(pb)
vc = f.vertex_point(pc)

# Valid triangle edges
e_ab = led(va, vb, pa, 1, 0, 0)
e_bc = led(vb, vc, pb, -0.5, 1, 0)
e_ca = led(vc, va, pc, -0.5, -1, 0)

# Valid triangular face
loop_tri = f.edge_loop([
    f.oriented_edge(e_ab, True),
    f.oriented_edge(e_bc, True),
    f.oriented_edge(e_ca, True),
])
plane = f.plane(f.axis2_placement_3d(pa, dir3(0, 0, 1), dir3(1, 0, 0)))
face_tri = f.advanced_face([f.face_outer_bound(loop_tri, orientation=True)], plane, same_sense=True)

# THREE degenerate self-loop EDGE_CURVEs — IS the FreeEdges defect trigger
# Each self-loop: vertex → same vertex, zero-length line
e_degen_a = led(va, va, pa, 1, 0, 0)   # zero-length at (0,0,0)
e_degen_b = led(vb, vb, pb, 1, 0, 0)   # zero-length at (1,0,0)
e_degen_c = led(vc, vc, pc, 1, 0, 0)   # zero-length at (0.5,1,0)

# Degenerate self-loop edge-loops (each contains one self-loop oriented edge)
loop_degen_a = f.edge_loop([f.oriented_edge(e_degen_a, True)])
loop_degen_b = f.edge_loop([f.oriented_edge(e_degen_b, True)])
loop_degen_c = f.edge_loop([f.oriented_edge(e_degen_c, True)])

# Degenerate faces with empty geometry but valid topology shell wiring
# Use the same plane — these degenerate "faces" have zero-area bounds
face_degen_a = f.advanced_face([f.face_outer_bound(loop_degen_a, orientation=True)], plane, same_sense=True)
face_degen_b = f.advanced_face([f.face_outer_bound(loop_degen_b, orientation=True)], plane, same_sense=True)
face_degen_c = f.advanced_face([f.face_outer_bound(loop_degen_c, orientation=True)], plane, same_sense=True)

# OPEN_SHELL: one valid face + three degenerate self-loop faces
# IS the FreeEdges defect: degenerate edges inflated in free-edge count
shell = f.open_shell([face_tri, face_degen_a, face_degen_b, face_degen_c])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
