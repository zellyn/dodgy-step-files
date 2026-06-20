"""Tsh107 — ShapeFix_Shell.Perform double-orient oscillation.

Catalog claim: Perform's orientation pass runs FixFaceOrientation then re-checks;
the recheck flips orientation again when invariant is achieved (oscillation).
Three-face corner shell where each pair shares edges; subtle orientation
inconsistencies cause FixFaceOrientation to flip Face 3, then recheck flips it
back, creating oscillation loop.

Mechanism IS the shell structure: three ADVANCED_FACEs form an L-shaped corner.
Face1 (bottom, z=0) and Face2 (back, y=1) share one EDGE_CURVE. Face2 and
Face3 (right, x=1) share a second EDGE_CURVE. Face1 and Face3 share a third
EDGE_CURVE. Each shared edge IS referenced with opposite orientations by the two
faces that share it — this manifold wiring IS directly embedded in the three
EDGE_LOOPs. However Face3 has same_sense=False on its ADVANCED_FACE, creating
an orientation inconsistency that causes FixFaceOrientation to flip Face3 on
first pass, and the recheck to flip it back — oscillation IS the defect.

Tier-3 assertion: shape_null == True

live oracle: occt=empty/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh107",
    defect=(
        "OPEN_SHELL with 3 ADVANCED_FACEs forming corner — IS the shell mechanism; "
        "Face1 (bottom z=0) and Face2 (back y=1) share EDGE_CURVE e12 — wired into both EDGE_LOOPs; "
        "Face2 (back y=1) and Face3 (right x=1) share EDGE_CURVE e23 — wired into both EDGE_LOOPs; "
        "Face1 (bottom z=0) and Face3 (right x=1) share EDGE_CURVE e13 — wired into both EDGE_LOOPs; "
        "Face3 ADVANCED_FACE has same_sense=False — IS the orientation inconsistency mechanism; "
        "FixFaceOrientation propagates from Face1 via shared edges to Face2 then Face3; "
        "same_sense=False on Face3 triggers flip on first pass — invariant not achieved; "
        "recheck sees flipped Face3 as inconsistent and flips back — IS the oscillation; "
        "oscillation loop IS caused by same_sense mismatch wired into Face3 topology; "
        "fix: detect same_sense=False before propagation; stabilise flip decision; "
        "emit E_FACE_ORIENTATION_OSCILLATION when flip-then-recheck cycles detected"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Corners of a unit corner-shell: (0,0,0), (1,0,0), (1,1,0), (0,1,0), (1,0,1), (1,1,1)
p000 = cp(0,0,0); p100 = cp(1,0,0); p110 = cp(1,1,0); p010 = cp(0,1,0)
p101 = cp(1,0,1); p111 = cp(1,1,1)

v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v101 = f.vertex_point(p101); v111 = f.vertex_point(p111)

# Shared edges (each referenced by two faces)
# e12: (1,1,0)→(0,1,0) — shared between Face1 (bottom) and Face2 (back)
e12 = led(v110, v010, p110, -1, 0, 0)
# e23: (1,1,0)→(1,1,1) — shared between Face2 (back) and Face3 (right)
e23 = led(v110, v111, p110,  0, 0, 1)
# e13: (1,0,0)→(1,1,0) — shared between Face1 (bottom) and Face3 (right)
e13 = led(v100, v110, p100,  0, 1, 0)

# Face1: bottom z=0, normal (0,0,1), vertices: (0,0,0)(1,0,0)(1,1,0)(0,1,0)
e1_a = led(v000, v100, p000,  1, 0, 0)   # (0,0,0)→(1,0,0)
# e13 used True: (1,0,0)→(1,1,0)
e1_c = f.oriented_edge(e12, True)         # (1,1,0)→(0,1,0)
e1_d = led(v010, v000, p010,  0,-1, 0)   # (0,1,0)→(0,0,0)
loop1 = f.edge_loop([
    f.oriented_edge(e1_a, True),
    f.oriented_edge(e13,  True),          # shared (1,0,0)→(1,1,0) .T.
    e1_c,                                 # shared (1,1,0)→(0,1,0) .T.
    f.oriented_edge(e1_d, True),
])
pl1 = f.plane(f.axis2_placement_3d(p000, dir3(0, 0, 1), dir3(1, 0, 0)))
face1 = f.advanced_face([f.face_outer_bound(loop1, orientation=True)], pl1, same_sense=True)

# Face2: back y=1, normal (0,1,0), vertices: (0,1,0)(1,1,0)(1,1,1)(0,1,1) — no (0,1,1) in corner
# Simplify to triangle: (0,1,0)(1,1,0)(1,1,1)
# e12 reversed: (0,1,0)→(1,1,0) → use e12 .F.
# e23 used True: (1,1,0)→(1,1,1)
e2_c = led(v111, v010, p111,  -1, 0,-1)  # (1,1,1)→(0,1,0) closing edge
loop2 = f.edge_loop([
    f.oriented_edge(e12, False),          # (0,1,0)→(1,1,0) .F. — reversed shared edge
    f.oriented_edge(e23, True),           # (1,1,0)→(1,1,1) .T.
    f.oriented_edge(e2_c, True),          # (1,1,1)→(0,1,0)
])
pl2 = f.plane(f.axis2_placement_3d(p010, dir3(0, 1, 0), dir3(1, 0, 0)))
face2 = f.advanced_face([f.face_outer_bound(loop2, orientation=True)], pl2, same_sense=True)

# Face3: right x=1, normal (1,0,0), vertices: (1,0,0)(1,1,0)(1,1,1)(1,0,1) — triangle form
# e13 reversed: (1,1,0)→(1,0,0) → use e13 .F.
# e23 reversed: (1,1,1)→(1,1,0) → use e23 .F.
# same_sense=False on ADVANCED_FACE — IS the oscillation-trigger mechanism
e3_c = led(v101, v100, p101,  0,-1, 0)   # closing edge (1,0,1)→(1,0,0) — not used in triangle
# Use triangle: (1,0,0)(1,1,0)(1,1,1) traversal
e3_rise = led(v100, v101, p100,  0, 0, 1)  # (1,0,0)→(1,0,1)
e3_top  = led(v101, v111, p101,  0, 1, 0)  # (1,0,1)→(1,1,1)
loop3 = f.edge_loop([
    f.oriented_edge(e13,    False),       # (1,1,0)→(1,0,0) .F. — reversed shared edge
    f.oriented_edge(e3_rise, True),       # (1,0,0)→(1,0,1)
    f.oriented_edge(e3_top,  True),       # (1,0,1)→(1,1,1)
    f.oriented_edge(e23,    False),       # (1,1,1)→(1,1,0) .F. — reversed shared edge
])
pl3 = f.plane(f.axis2_placement_3d(p100, dir3(1, 0, 0), dir3(0, 1, 0)))
# same_sense=False IS the orientation-inconsistency that triggers oscillation
face3 = f.advanced_face([f.face_outer_bound(loop3, orientation=True)], pl3, same_sense=False)

# OPEN_SHELL: 3-face corner with same_sense=False on Face3 IS the oscillation mechanism
shell = f.open_shell([face1, face2, face3])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
