"""Tsh215 — ShapeFix_Shell.Perform.context_null_initialize.

Catalog claim: Multiple Perform() calls reuse stale context; SetContext state
accumulation applies reshape operations twice.

Mechanism IS the shell structure: AN OPEN_SHELL containing ONE ADVANCED_FACE
(unit square) IS the defect trigger. The shell IS the entity on which
ShapeFix_Shell.Perform() IS called twice in sequence without re-initializing
the BRep_Builder context (SetContext). The stale context accumulates reshape
operations from the first Perform() call; the second Perform() call reapplies
those accumulated operations to the already-fixed shape — IS the double-fix
defect.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh215",
    defect=(
        "OPEN_SHELL with ONE ADVANCED_FACE IS the context-null-initialize defect trigger; "
        "unit square face IS at (0,0,0)-(1,1,0) with normal +Z — IS the face geometry; "
        "face has same_sense=False to trigger orientation repair — IS the repair-triggering condition; "
        "ShapeFix_Shell.Perform() IS the defect path: first Perform() call fixes face orientation; "
        "SetContext context IS NOT re-initialized between calls — IS the stale-context condition; "
        "stale BRep_Builder context accumulates reshape operations from first Perform() — IS the accumulation; "
        "second Perform() call reuses stale context — IS the double-apply path; "
        "second Perform() reapplies reshape operations to already-fixed shape — IS the double-fix defect; "
        "result: face orientation IS flipped twice, returning to wrong orientation — IS the defect outcome; "
        "fix: Perform() must null-initialize context (SetContext(nullptr)) before each call; "
        "emit E_CONTEXT_STALE_DOUBLE_FIX when reshape operations applied twice due to stale context"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Unit square — IS the face geometry
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
# same_sense=False — IS the repair-triggering condition that causes Perform() to reshape
face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=False)

# OPEN_SHELL: one face needing orientation repair — IS the context-null-initialize mechanism
# Perform() called twice without SetContext reset IS the double-fix trigger
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
