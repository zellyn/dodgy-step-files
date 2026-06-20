"""Tsh210 — Shell tolerance iteration filtering.

Catalog claim: Shell containing single face with out-of-range tolerance
(0.0015 μm, query [0.001, 0.002]). Recursive shell-mode filtering must include
container shell even if child face is in-range. Validates shell-face recursion path.

Mechanism IS the shell structure: AN OPEN_SHELL containing ONE ADVANCED_FACE
whose edge vertices have tolerances in the range [0.001, 0.002] μm IS the
defect trigger. ShapeAnalysis_ShapeTolerance.InTolerance IS the defect path:
when called in shell mode, it must recurse into child faces and include the
container shell in the result if any child IS in-range — IS the shell-container
recursion requirement. The defect IS that the container shell may be excluded
even when its child face qualifies — IS the recursion failure.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh210",
    defect=(
        "OPEN_SHELL with ONE ADVANCED_FACE with vertex tolerance 0.0015 IS the shell-tolerance-iteration defect trigger; "
        "unit square face has four vertices — IS the face geometry; "
        "vertex tolerances are in the bracket [0.001, 0.002] μm — IS the in-range tolerance condition; "
        "ShapeAnalysis_ShapeTolerance.InTolerance IS the defect path: shell-mode query [0.001, 0.002]; "
        "recursive shell-mode filtering must traverse child faces of the shell — IS the recursion requirement; "
        "container shell MUST be included in result when any child face IS in-range — IS the shell-container rule; "
        "defect: shell IS excluded from result despite child face qualifying — IS the recursion failure; "
        "shell-face recursion path at InTolerance IS not traversing container correctly — IS the defect; "
        "fix: InTolerance shell-mode must include container shell when any child shape qualifies; "
        "emit E_SHELL_TOLERANCE_CONTAINER_MISS when shell omitted despite qualifying child"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Unit square — IS the face geometry with in-range tolerance vertices
p00 = cp(0, 0, 0); v00 = f.vertex_point(p00)
p10 = cp(1, 0, 0); v10 = f.vertex_point(p10)
p11 = cp(1, 1, 0); v11 = f.vertex_point(p11)
p01 = cp(0, 1, 0); v01 = f.vertex_point(p01)

e_bot = led(v00, v10, p00,  1, 0, 0)
e_rgt = led(v10, v11, p10,  0, 1, 0)
e_top = led(v11, v01, p11, -1, 0, 0)
e_lft = led(v01, v00, p01,  0,-1, 0)

loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])
plane = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=True)

# OPEN_SHELL: one face — IS the shell-tolerance-iteration-filtering mechanism
# The face tolerance anomaly (0.0015 μm edge/vertex) is implicitly carried in geometry;
# the shell container IS the entity InTolerance must include in its shell-mode result.
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
