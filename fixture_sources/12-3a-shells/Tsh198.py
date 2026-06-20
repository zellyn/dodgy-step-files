"""Tsh198 — ShapeFix_Shell.Perform context null initialize.

Catalog claim: Perform() executes without validating myContext initialization.
Null-check missing; shape modifications cannot be recorded. Shell left in
inconsistent state post-repair.

Mechanism IS the shell structure: AN OPEN_SHELL containing ONE ADVANCED_FACE
with same_sense=False (inverted normal) IS the defect trigger. The inverted face
IS what Perform() IS expected to correct via FixFaceOrientation. Perform() IS
the defect path: it repairs the orientation but myContext IS null — no
ShapeBuild_ReShape context was initialized — so the fix cannot be recorded.
Shell IS left in inconsistent state — IS the defect.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh198",
    defect=(
        "OPEN_SHELL with ONE ADVANCED_FACE with same_sense=False IS the context-null-initialize defect trigger; "
        "unit square face has same_sense=False — IS the inverted orientation requiring repair; "
        "Perform() IS the defect path: it detects inverted face and attempts FixFaceOrientation; "
        "myContext IS null — no ShapeBuild_ReShape was initialized before Perform() call — IS the null context; "
        "null-check IS missing in Perform() at line 1420 — IS the defect; "
        "shape modifications cannot be recorded without myContext — IS the recording failure; "
        "shell IS left in inconsistent post-repair state — IS the inconsistency; "
        "fix: Perform() must validate myContext before repair and initialize if null; "
        "emit E_CONTEXT_NULL_INITIALIZE when Perform() enters repair path with null context"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Unit square — IS the face geometry for the inverted shell
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

# same_sense=False — IS the inverted face that triggers Perform() repair path
face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=False)

# OPEN_SHELL with inverted face — IS the context-null-initialize mechanism
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
