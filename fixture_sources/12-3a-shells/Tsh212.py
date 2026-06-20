"""Tsh212 — Mixed wire/edge orientation conflict.

Catalog claim: Face with inner hole wire (INTERNAL orientation) containing
edge with EXTERNAL orientation (conflicting). BreakWires must detect and flip
edge orientation, incrementing nbnew counter for segment finalization.

Mechanism IS the shell structure: AN OPEN_SHELL containing ONE ADVANCED_FACE
(4×4 square with a 2×2 hole) where the hole FACE_BOUND inner wire has
orientation=False (INTERNAL) but one of its ORIENTED_EDGEs has orientation=True
(EXTERNAL, conflicting) — IS the mixed-orientation defect trigger.
ShapeFix_ComposeShell.BreakWires IS the defect path: it must detect the
orientation mismatch between the hole wire (INTERNAL) and its contained edge
(EXTERNAL), flip the edge orientation, and increment nbnew for segment
finalization — IS the defect.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1) gmsh=shape(17) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh212",
    defect=(
        "OPEN_SHELL with ONE ADVANCED_FACE (4x4 square with 2x2 hole) IS the mixed-orientation defect trigger; "
        "outer FACE_OUTER_BOUND loop IS valid 4x4 square boundary at Z=0 — IS the outer boundary; "
        "inner FACE_BOUND hole wire IS orientation=False (INTERNAL) — IS the hole wire; "
        "hole wire IS 2x2 square centered in the outer face — IS the hole boundary; "
        "ORIENTED_EDGE for hole bottom edge IS orientation=True (EXTERNAL) — IS the conflicting edge; "
        "remaining three hole ORIENTED_EDGEs IS orientation=False — IS the consistent hole edges; "
        "inner wire orientation=False (INTERNAL) + bottom edge orientation=True (EXTERNAL) IS the mismatch — IS the defect; "
        "BreakWires IS the defect path: must detect wire-vs-edge orientation conflict; "
        "BreakWires must flip conflicting edge orientation and increment nbnew counter — IS the fix; "
        "failure to flip leaves mixed-orientation inner wire unresolved — IS the defect outcome; "
        "fix: BreakWires must detect INTERNAL wire with EXTERNAL edge and flip edge orientation; "
        "emit E_WIRE_EDGE_ORIENTATION_CONFLICT when mixed orientation survives BreakWires"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Outer square: (0,0,0)-(4,4,0) — IS the outer boundary
p00 = cp(0, 0, 0); v00 = f.vertex_point(p00)
p40 = cp(4, 0, 0); v40 = f.vertex_point(p40)
p44 = cp(4, 4, 0); v44 = f.vertex_point(p44)
p04 = cp(0, 4, 0); v04 = f.vertex_point(p04)

e_bot = led(v00, v40, p00,  1, 0, 0)
e_rgt = led(v40, v44, p40,  0, 1, 0)
e_top = led(v44, v04, p44, -1, 0, 0)
e_lft = led(v04, v00, p04,  0,-1, 0)

loop_outer = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])

# Hole square: (1,1,0)-(3,3,0) — IS the 2x2 hole boundary
ph11 = cp(1, 1, 0); vh11 = f.vertex_point(ph11)
ph31 = cp(3, 1, 0); vh31 = f.vertex_point(ph31)
ph33 = cp(3, 3, 0); vh33 = f.vertex_point(ph33)
ph13 = cp(1, 3, 0); vh13 = f.vertex_point(ph13)

eh_bot = led(vh11, vh31, ph11,  1, 0, 0)   # bottom hole edge — conflicting orientation
eh_rgt = led(vh31, vh33, ph31,  0, 1, 0)
eh_top = led(vh33, vh13, ph33, -1, 0, 0)
eh_lft = led(vh13, vh11, ph13,  0,-1, 0)

# Inner hole wire: orientation=False (INTERNAL), but bottom edge IS orientation=True (EXTERNAL conflict)
loop_hole = f.edge_loop([
    f.oriented_edge(eh_bot, True),    # IS the conflicting EXTERNAL edge in INTERNAL wire
    f.oriented_edge(eh_rgt, False),
    f.oriented_edge(eh_top, False),
    f.oriented_edge(eh_lft, False),
])

plane = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
# ADVANCED_FACE: outer bound + inner hole with mixed-orientation conflict — IS the defect face
face = f.advanced_face(
    [
        f.face_outer_bound(loop_outer, orientation=True),
        f.face_bound(loop_hole, orientation=False),   # INTERNAL hole wire — IS the defect
    ],
    plane,
    same_sense=True,
)

# OPEN_SHELL: one face with mixed wire/edge orientation — IS the mixed-orientation-conflict mechanism
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
