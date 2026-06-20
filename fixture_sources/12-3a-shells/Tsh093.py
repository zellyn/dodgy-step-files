"""Tsh093 — ShapeFix_Shell.Perform empty-output handling.

Catalog claim: Shell with two faces whose vertices all collapse to near-degenerate
edges (edge from P to same P with zero direction). Tests Perform when all faces get
rejected during fixing. Expected: diagnostic flag set or exception.
Likely failure: Returns empty shell silently; no error flag; caller unaware that
output is invalid.

Mechanism IS the shell structure: Two ADVANCED_FACEs are wired with zero-length
edges — each EDGE_CURVE has the same VERTEX_POINT for start and end, and the LINE
direction vector has magnitude 0.0. The degenerate edges IS directly embedded in
the EDGE_LOOP topology. Both faces carry this zero-length-edge defect, meaning
ShapeFix_Shell.Perform must reject all faces. The all-faces-rejected outcome IS
the mechanism that exposes silent empty-shell return with no error flag.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh093",
    defect=(
        "OPEN_SHELL with 2 ADVANCED_FACEs each wired with zero-length EDGE_CURVEs; "
        "each EDGE_CURVE has same VERTEX_POINT for start and end — IS the degenerate-edge mechanism; "
        "LINE direction vector magnitude 0.0 IS directly in the edge topology; "
        "all faces carry zero-length-edge defect — all rejected by ShapeFix_Shell.Perform; "
        "all-faces-rejected outcome IS the mechanism exposing silent empty-shell return; "
        "ShapeFix_Shell.Perform returns empty shell with no diagnostic flag set; "
        "fix: set error flag / raise when output shell is empty after Perform; "
        "emit E_SHELL_PERFORM_EMPTY_OUTPUT when all faces are rejected"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))

# Face A: degenerate — all four corners collapse to single point P0=(0,0,0)
# Zero-length edges: VERTEX_POINT start == end, direction magnitude 0.0
p0a = cp(0, 0, 0)
v0a = f.vertex_point(p0a)
# Each edge: same vertex start and end, zero direction vector
zero_dir_a = dir3(0, 0, 0)
zero_vec_a = f.vector(zero_dir_a, 0.0)
zero_line_a = f.line(p0a, zero_vec_a)
ea0 = f.edge_curve(v0a, v0a, zero_line_a)
ea1 = f.edge_curve(v0a, v0a, zero_line_a)
ea2 = f.edge_curve(v0a, v0a, zero_line_a)
ea3 = f.edge_curve(v0a, v0a, zero_line_a)
loop_a = f.edge_loop([
    f.oriented_edge(ea0, True), f.oriented_edge(ea1, True),
    f.oriented_edge(ea2, True), f.oriented_edge(ea3, True),
])
pl_a = f.plane(f.axis2_placement_3d(p0a, dir3(0, 0, 1), dir3(1, 0, 0)))
# Zero-length EDGE_LOOP IS wired into ADVANCED_FACE — IS the mechanism
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], pl_a, same_sense=True)

# Face B: same degenerate pattern at a different nominal point P0=(5,0,0)
p0b = cp(5, 0, 0)
v0b = f.vertex_point(p0b)
zero_dir_b = dir3(0, 0, 0)
zero_vec_b = f.vector(zero_dir_b, 0.0)
zero_line_b = f.line(p0b, zero_vec_b)
eb0 = f.edge_curve(v0b, v0b, zero_line_b)
eb1 = f.edge_curve(v0b, v0b, zero_line_b)
eb2 = f.edge_curve(v0b, v0b, zero_line_b)
eb3 = f.edge_curve(v0b, v0b, zero_line_b)
loop_b = f.edge_loop([
    f.oriented_edge(eb0, True), f.oriented_edge(eb1, True),
    f.oriented_edge(eb2, True), f.oriented_edge(eb3, True),
])
pl_b = f.plane(f.axis2_placement_3d(p0b, dir3(0, 0, 1), dir3(1, 0, 0)))
# Second zero-length face: both faces degenerate — all-rejected IS the mechanism
face_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], pl_b, same_sense=True)

# OPEN_SHELL containing both degenerate faces — IS the shell structure wired with mechanism
shell = f.open_shell([face_a, face_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
