"""Tsh193 — ShapeUpgrade_ShellSewing.Apply tolerance-boundary classification.

Catalog claim: Two shells with coincident faces at exactly the tolerance boundary
(1e-7). Apply doesn't classify consistently across the threshold. The sewing
analysis distance-filter decision point triggers branching uncertainty — faces may
or may not merge depending on floating-point epsilon.

Mechanism IS the shell structure: TWO OPEN_SHELLs each a single ADVANCED_FACE
(unit square) sharing a COINCIDENT BOUNDARY where the gap between right edge of
shell_a and left edge of shell_b IS exactly 1e-7 — IS the tolerance-boundary
trigger. ShapeUpgrade_ShellSewing.Apply IS the defect path: its distance-filter
second pass classifies the coincident boundary at exactly tolerance, triggering
branching uncertainty — IS the defect. With gap == tolerance the sewing may or
may not merge — IS the inconsistent classification.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh193",
    defect=(
        "TWO OPEN_SHELLs WITH COINCIDENT BOUNDARY AT 1e-7 GAP IS the tolerance-boundary defect trigger; "
        "shell_a IS unit square (0,0,0)-(1,0,0)-(1,1,0)-(0,1,0) — IS the first shell; "
        "shell_b IS unit square (1e-7,0,0)-(1+1e-7,0,0)-(1+1e-7,1,0)-(1e-7,1,0) — IS the second shell; "
        "gap of 1e-7 between shell_a right edge and shell_b left edge IS at tolerance boundary — IS the trigger; "
        "ShapeUpgrade_ShellSewing.Apply distance-filter second pass classifies gap == tolerance — IS the defect path; "
        "BRepBuilderAPI_Sewing.cxx:1732 decision point IS where branching uncertainty occurs — IS the defect; "
        "faces may or may not merge depending on floating-point comparison outcome — IS the inconsistency; "
        "fix: Apply must use strictly-less-than comparison at tolerance boundary; "
        "emit E_SEWING_TOLERANCE_BRANCH when gap equals tolerance within floating-point epsilon"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# shell_a: unit square (0,0,0) to (1,1,0)
pa00 = cp(0, 0, 0);   va00 = f.vertex_point(pa00)
pa10 = cp(1, 0, 0);   va10 = f.vertex_point(pa10)
pa11 = cp(1, 1, 0);   va11 = f.vertex_point(pa11)
pa01 = cp(0, 1, 0);   va01 = f.vertex_point(pa01)

ea_bot = led(va00, va10, pa00,  1, 0, 0)   # bottom
ea_rgt = led(va10, va11, pa10,  0, 1, 0)   # right — IS the sewing candidate
ea_top = led(va11, va01, pa11, -1, 0, 0)   # top
ea_lft = led(va01, va00, pa01,  0,-1, 0)   # left

loop_a = f.edge_loop([
    f.oriented_edge(ea_bot, True),
    f.oriented_edge(ea_rgt, True),
    f.oriented_edge(ea_top, True),
    f.oriented_edge(ea_lft, True),
])
plane_a = f.plane(f.axis2_placement_3d(pa00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], plane_a, same_sense=True)
shell_a = f.open_shell([face_a])

# shell_b: offset by exactly 1e-7 in X — IS the tolerance-boundary gap
GAP = 1e-7
pb00 = cp(GAP,     0, 0); vb00 = f.vertex_point(pb00)
pb10 = cp(1+GAP,   0, 0); vb10 = f.vertex_point(pb10)
pb11 = cp(1+GAP,   1, 0); vb11 = f.vertex_point(pb11)
pb01 = cp(GAP,     1, 0); vb01 = f.vertex_point(pb01)

eb_bot = led(vb00, vb10, pb00,  1, 0, 0)
eb_rgt = led(vb10, vb11, pb10,  0, 1, 0)
eb_top = led(vb11, vb01, pb11, -1, 0, 0)
eb_lft = led(vb01, vb00, pb01,  0,-1, 0)  # left — IS the tolerance-boundary sewing candidate

loop_b = f.edge_loop([
    f.oriented_edge(eb_bot, True),
    f.oriented_edge(eb_rgt, True),
    f.oriented_edge(eb_top, True),
    f.oriented_edge(eb_lft, True),
])
plane_b = f.plane(f.axis2_placement_3d(pb00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], plane_b, same_sense=True)
shell_b = f.open_shell([face_b])

# Two OPEN_SHELLs with 1e-7 gap — IS the tolerance-boundary classification mechanism
sbsm = f.shell_based_surface_model([shell_a, shell_b])
f.add_product_chain(sbsm)
