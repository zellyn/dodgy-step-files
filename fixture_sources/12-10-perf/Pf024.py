"""Pf024 — Self-intersection-healing tool enters infinite loop on EDGE_LOOP with crossed diagonals (out-of-range split index).

Catalog claim: intersection-healing algorithm could infinite-loop on certain
edges because a split-index range check was missing.  Common trigger: an
EDGE_LOOP with self-intersecting diagonals; for example four edges A→C, B→D,
A→B, C→D in cross order forming an X-shape — exercises the missing bound on
the split index.

The fixture encodes exactly that X-shaped EDGE_LOOP: five CARTESIAN_POINTs
(four corners + one intersection centre), and four edges in the order that
maximises out-of-range split indices: A→C (diagonal), B→D (anti-diagonal),
A→B (bottom), C→D (top).  The two diagonals cross at the centre, creating
the split-index overflow condition.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 5
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf024",
    defect=(
        "EDGE_LOOP with crossed diagonals forming X-shape: A→C, B→D, A→B, C→D; "
        "intersection-healing split-index range check missing; healer infinite-loops "
        "on out-of-range split index; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Five points: four corners A,B,C,D + centre X.
# A=(0,0)  B=(2,0)  C=(2,2)  D=(0,2)  X=(1,1) (intersection of diagonals)
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((2.0, 0.0, 0.0))
p_C = f.cartesian_point((2.0, 2.0, 0.0))
p_D = f.cartesian_point((0.0, 2.0, 0.0))
p_X = f.cartesian_point((1.0, 1.0, 0.0))  # crossing point

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

import math

def line_edge(p_start, d_tuple, length, va, vb):
    d   = f.direction(d_tuple)
    vec = f.vector(d, length)
    ln  = f.line(p_start, vec)
    return f.edge_curve(va, vb, ln)

# X-pattern edges in the documented order: A→C, B→D, A→B, C→D.
# Diagonal A→C and anti-diagonal B→D cross at X — the X-shape.
DIAG = math.sqrt(8.0)  # length of diagonal in 2×2 square
e_AC = line_edge(p_A, ( 1.0/math.sqrt(2),  1.0/math.sqrt(2), 0.0), DIAG, v_A, v_C)
e_BD = line_edge(p_B, (-1.0/math.sqrt(2),  1.0/math.sqrt(2), 0.0), DIAG, v_B, v_D)
e_AB = line_edge(p_A, ( 1.0,               0.0,              0.0),  2.0,  v_A, v_B)
e_CD = line_edge(p_C, (-1.0,               0.0,              0.0),  2.0,  v_C, v_D)

# EDGE_LOOP with crossed diagonals — split-index overflow trigger.
# The loop is intentionally non-manifold: it closes D→A to form a wire.
d_DA = (0.0, -1.0, 0.0)
e_DA = line_edge(p_D, d_DA, 2.0, v_D, v_A)

loop = f.edge_loop([
    f.oriented_edge(e_AC, True),
    f.oriented_edge(e_BD, True),
    f.oriented_edge(e_AB, True),
    f.oriented_edge(e_CD, True),
    f.oriented_edge(e_DA, True),
])

# Plane and face.
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)
face  = f.advanced_face([f.face_outer_bound(loop)], plane)

shell = f.open_shell([face], name="crossed_diag_shell")
f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('crossed_diag_sbsm',(#{shell.eid}))")
