"""Tsh197 — ShapeFix_Shell.FixFaceOrientation shells extraction loss.

Catalog claim: Compound with multiple shells; only first shell extracted for
FixFaceOrientation. Remaining shells skipped, losing structural information.
Shell-based model degrades.

Mechanism IS the shell structure: A SHELL_BASED_SURFACE_MODEL referencing TWO
OPEN_SHELLs (shell_a and shell_b) IS the defect trigger. shell_a IS a unit
square face — IS the first shell (processed by FixFaceOrientation). shell_b IS
an offset square face — IS the second shell that IS skipped/lost. FixFaceOrientation
IS the defect path: GetShells() extracts only shell_a; shell_b IS silently
discarded — IS the extraction loss. Reading yields two-face model but
FixFaceOrientation only processes one.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh197",
    defect=(
        "SHELL_BASED_SURFACE_MODEL with TWO OPEN_SHELLs IS the shells-extraction-loss defect trigger; "
        "shell_a IS OPEN_SHELL containing face_a (unit square at Z=0) — IS the first shell (processed); "
        "shell_b IS OPEN_SHELL containing face_b (unit square at Z=2) — IS the second shell (lost); "
        "FixFaceOrientation IS the defect path: GetShells() iterates compound and extracts only shell_a; "
        "shell_b IS skipped — IS the extraction loss; "
        "structural information from shell_b IS silently discarded — IS the degradation; "
        "reading compound with two shells yields only one orientation-fixed shell — IS the coverage failure; "
        "fix: FixFaceOrientation must iterate all shells in compound; "
        "emit E_SHELLS_EXTRACTION_INCOMPLETE when compound shell count exceeds processed shell count"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# shell_a: unit square at Z=0 — IS the first shell (processed by FixFaceOrientation)
pa00 = cp(0, 0, 0); va00 = f.vertex_point(pa00)
pa10 = cp(1, 0, 0); va10 = f.vertex_point(pa10)
pa11 = cp(1, 1, 0); va11 = f.vertex_point(pa11)
pa01 = cp(0, 1, 0); va01 = f.vertex_point(pa01)

ea_bot = led(va00, va10, pa00,  1, 0, 0)
ea_rgt = led(va10, va11, pa10,  0, 1, 0)
ea_top = led(va11, va01, pa11, -1, 0, 0)
ea_lft = led(va01, va00, pa01,  0,-1, 0)

loop_a = f.edge_loop([
    f.oriented_edge(ea_bot, True),
    f.oriented_edge(ea_rgt, True),
    f.oriented_edge(ea_top, True),
    f.oriented_edge(ea_lft, True),
])
plane_a = f.plane(f.axis2_placement_3d(pa00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], plane_a, same_sense=True)
shell_a = f.open_shell([face_a])

# shell_b: unit square at Z=2 — IS the second shell (lost/skipped by extraction)
pb00 = cp(0, 0, 2); vb00 = f.vertex_point(pb00)
pb10 = cp(1, 0, 2); vb10 = f.vertex_point(pb10)
pb11 = cp(1, 1, 2); vb11 = f.vertex_point(pb11)
pb01 = cp(0, 1, 2); vb01 = f.vertex_point(pb01)

eb_bot = led(vb00, vb10, pb00,  1, 0, 0)
eb_rgt = led(vb10, vb11, pb10,  0, 1, 0)
eb_top = led(vb11, vb01, pb11, -1, 0, 0)
eb_lft = led(vb01, vb00, pb01,  0,-1, 0)

loop_b = f.edge_loop([
    f.oriented_edge(eb_bot, True),
    f.oriented_edge(eb_rgt, True),
    f.oriented_edge(eb_top, True),
    f.oriented_edge(eb_lft, True),
])
plane_b = f.plane(f.axis2_placement_3d(pb00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], plane_b, same_sense=True)
shell_b = f.open_shell([face_b])

# TWO OPEN_SHELLs in one model — IS the shells-extraction-loss mechanism
sbsm = f.shell_based_surface_model([shell_a, shell_b])
f.add_product_chain(sbsm)
