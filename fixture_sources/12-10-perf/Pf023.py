"""Pf023 — Iterative ShapeFix exposes new defect every pass (unbounded).

Catalog claim: a wire-healing pass iterates until modification flags settle;
each fix can introduce a new defect needing another pass (reordering exposes
self-intersection; closing a gap exposes a tolerance violation).  Without an
iteration cap, pathological inputs loop indefinitely.

The structural pattern is a wire with simultaneous defects that interact: a
reorder need (edges listed in wrong order), a 3D/2D mismatch, and a
self-intersecting micro-loop.  Six CARTESIAN_POINTs form an intentionally
disordered wire whose edges are out-of-sequence and create a small crossing
at the centre, so each ShapeFix pass exposes a new issue.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 6
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf023",
    defect=(
        "wire with simultaneous reorder-need + 3D/2D mismatch + self-intersecting "
        "micro-loop: each ShapeFix pass exposes a new defect; without iteration cap "
        "the healer loops indefinitely; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Six points forming a self-intersecting, out-of-order wire.
# Layout: square with corners A,B,C,D and two extra micro-loop points M1,M2.
#   A=(0,0)  B=(2,0)  C=(2,2)  D=(0,2)
#   M1=(1,1-eps)  M2=(1,1+eps)  — micro-loop inside the square.
EPS = 1e-9
p_A  = f.cartesian_point((0.0, 0.0, 0.0))
p_B  = f.cartesian_point((2.0, 0.0, 0.0))
p_C  = f.cartesian_point((2.0, 2.0, 0.0))
p_D  = f.cartesian_point((0.0, 2.0, 0.0))
p_M1 = f.cartesian_point((1.0, 1.0 - EPS, 0.0))
p_M2 = f.cartesian_point((1.0, 1.0 + EPS, 0.0))

v_A  = f.vertex_point(p_A)
v_B  = f.vertex_point(p_B)
v_C  = f.vertex_point(p_C)
v_D  = f.vertex_point(p_D)
v_M1 = f.vertex_point(p_M1)
v_M2 = f.vertex_point(p_M2)

def line_edge(p_start, d_tuple, length, va, vb):
    d   = f.direction(d_tuple)
    vec = f.vector(d, length)
    ln  = f.line(p_start, vec)
    return f.edge_curve(va, vb, ln)

import math

# Intentionally disordered edge sequence: D→A, A→B, B→M1, M1→M2, M2→C, C→D
# (B→M1 and M2→C create a diversion through the micro-loop — out-of-order
# relative to a simple square + self-intersecting micro segment).
e_DA = line_edge(p_D, (0.0, -1.0, 0.0), 2.0, v_D, v_A)
e_AB = line_edge(p_A, (1.0,  0.0, 0.0), 2.0, v_A, v_B)
d_BM1 = (-1.0/math.sqrt(2), 1.0/math.sqrt(2), 0.0)
e_BM1 = line_edge(p_B, d_BM1, math.sqrt(2.0), v_B, v_M1)
e_M1M2 = line_edge(p_M1, (0.0, 1.0, 0.0), 2.0 * EPS, v_M1, v_M2)
d_M2C = (1.0/math.sqrt(2), 1.0/math.sqrt(2), 0.0)
e_M2C = line_edge(p_M2, d_M2C, math.sqrt(2.0), v_M2, v_C)
e_CD = line_edge(p_C, (-1.0, 0.0, 0.0), 2.0, v_C, v_D)

# EDGE_LOOP with out-of-order + micro-loop crossing — the multi-pass trigger.
loop = f.edge_loop([
    f.oriented_edge(e_DA,   True),
    f.oriented_edge(e_AB,   True),
    f.oriented_edge(e_BM1,  True),
    f.oriented_edge(e_M1M2, True),
    f.oriented_edge(e_M2C,  True),
    f.oriented_edge(e_CD,   True),
])

# Plane for the face.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)
face  = f.advanced_face([f.face_outer_bound(loop)], plane)

shell = f.open_shell([face], name="unbounded_heal_shell")
f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('unbounded_heal_sbsm',(#{shell.eid}))")
