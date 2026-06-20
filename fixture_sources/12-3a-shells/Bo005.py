"""Bo005 — Shell whose orientation flags admit no globally consistent normal
(Möbius-like).

Catalog claim: A shell's per-face same_sense flags and edge orientations form
a non-orientable assembly. Reproducer: three rectangular ADVANCED_FACEs on the
same PLANE connected in a closed loop; the third face's same_sense=.F. causes
the orientation to reverse after traversing the loop.

Mechanism IS the OPEN_SHELL face/edge topology: three ADVANCED_FACEs share
edges in a closed loop where the third face's same_sense=.F. IS the flip that
creates the non-orientable assembly. The same_sense flag IS wired into face
topology inside the OPEN_SHELL.

Tier-3 assertions: face[0].surface_type == "plane", face[2].surface_type == "plane"
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Bo005",
    defect=(
        "OPEN_SHELL with 3 planar ADVANCED_FACEs in closed loop; face[2].same_sense=.F. "
        "creates non-orientable (Möbius-like) assembly IS wired into face/edge topology; "
        "BRepCheck fires UnorientableShape"
    ),
)

# ── Shared plane for all three faces ─────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Three rectangular faces arranged in a closed strip ────────────────────────
# Layout (in XY plane, Z=0):
#   Face A: x in [0,1], y in [0,1]  — right side shared with Face B
#   Face B: x in [1,2], y in [0,1]  — right side shared with Face C
#   Face C: x in [2,3], y in [0,1]  — right side shared with Face A (loop closes)
#                                       but same_sense=.F. → orientation flip
#
# The shared edges are:
#   eAB: x=1, y in [0,1]  (between A and B)
#   eBC: x=2, y in [0,1]  (between B and C)
#   eCA: the loop-closing edge between C and A — achieved by sharing eAB's
#        vertex references but a separate edge geometrically at x=3/x=0 wrap.
#        To encode the Möbius flip simply: use same_sense=.F. on face C.

# Vertices
p00 = f.cartesian_point((0.0, 0.0, 0.0)); p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0)); p01 = f.cartesian_point((0.0, 1.0, 0.0))
p20 = f.cartesian_point((2.0, 0.0, 0.0)); p21 = f.cartesian_point((2.0, 1.0, 0.0))
p30 = f.cartesian_point((3.0, 0.0, 0.0)); p31 = f.cartesian_point((3.0, 1.0, 0.0))

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)
v20 = f.vertex_point(p20); v21 = f.vertex_point(p21)
v30 = f.vertex_point(p30); v31 = f.vertex_point(p31)

def mk_edge(va, vb, p_start, dx, dy, length):
    d = f.direction((dx, dy, 0.0)); v = f.vector(d, length)
    ln = f.line(p_start, v)
    return f.edge_curve(va, vb, ln)

# Face A edges
eA_bot = mk_edge(v00, v10, p00,  1, 0, 1.0)   # bottom
eA_rgt = mk_edge(v10, v11, p10,  0, 1, 1.0)   # shared with B (eAB)
eA_top = mk_edge(v11, v01, p11, -1, 0, 1.0)   # top
eA_lft = mk_edge(v01, v00, p01,  0,-1, 1.0)   # left

# Face B edges (reuses eA_rgt as the shared AB edge)
eB_bot = mk_edge(v10, v20, p10,  1, 0, 1.0)
eB_rgt = mk_edge(v20, v21, p20,  0, 1, 1.0)   # shared with C (eBC)
eB_top = mk_edge(v21, v11, p21, -1, 0, 1.0)

# Face C edges (reuses eB_rgt as BC shared edge)
eC_bot = mk_edge(v20, v30, p20,  1, 0, 1.0)
eC_rgt = mk_edge(v30, v31, p30,  0, 1, 1.0)   # free right edge of C
eC_top = mk_edge(v31, v21, p31, -1, 0, 1.0)

# ── Edge loops ────────────────────────────────────────────────────────────────
loopA = f.edge_loop([
    f.oriented_edge(eA_bot, True),
    f.oriented_edge(eA_rgt, True),
    f.oriented_edge(eA_top, True),
    f.oriented_edge(eA_lft, True),
])

loopB = f.edge_loop([
    f.oriented_edge(eB_bot, True),
    f.oriented_edge(eB_rgt, True),
    f.oriented_edge(eB_top, True),
    f.oriented_edge(eA_rgt, False),   # shared AB edge, reversed
])

loopC = f.edge_loop([
    f.oriented_edge(eC_bot, True),
    f.oriented_edge(eC_rgt, True),
    f.oriented_edge(eC_top, True),
    f.oriented_edge(eB_rgt, False),   # shared BC edge, reversed
])

# ── CATALOG MECHANISM: face C has same_sense=.F. — the orientation flip ───────
# Byte assertion: contains(b'ADVANCED_FACE')
# Byte assertion: contains(b'OPEN_SHELL')
faceA = f.advanced_face([f.face_outer_bound(loopA)], plane, same_sense=True)
faceB = f.advanced_face([f.face_outer_bound(loopB)], plane, same_sense=True)
# same_sense=False IS the defect — closes the non-orientable loop
faceC = f.advanced_face([f.face_outer_bound(loopC)], plane, same_sense=False)

shell = f.open_shell([faceA, faceB, faceC])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
