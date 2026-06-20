"""Tsh064 — Same-surface face merge edge-removal history contract is undocumented.

Catalog claim: When adjacent same-surface faces are merged, interior edges are removed
from the result. Some downstream tools expect those removed edges to remain in the shape's
modification history map; others expect them removed entirely. The contract is not documented
and varies between versions.

Mechanism IS the shell structure: 2 ADVANCED_FACEs are wired into one OPEN_SHELL on a
shared PLANE, connected by a shared interior EDGE_CURVE (the shared boundary E). After
merge, E is removed from the result. The shared interior edge E IS directly wired into
both faces' EDGE_LOOPs via shared VERTEX_POINT/EDGE_CURVE entities. A merge step that
drops E without recording an explicit history entry (deleted / modified-into / split-into)
violates the contract — the modification history map is inconsistently populated across
OCCT versions.

Byte assertions:
  - contains(b'OPEN_SHELL')
  - count_entity_def(b'ADVANCED_FACE') == 2

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh064",
    defect=(
        "OPEN_SHELL with 2 coplanar ADVANCED_FACEs sharing interior EDGE_CURVE E; "
        "shared interior edge E IS wired into both EDGE_LOOP topologies; "
        "same-surface merge removes E from result without explicit history record; "
        "modification history map is silent about removed E; "
        "fix: every removed edge must appear in the modification history map as "
        "deleted / modified-into / split-into; never silently drop edges from history"
    ),
)

# Shared plane z=0, normal +Z
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Points for two side-by-side unit squares sharing edge E at x=1
# Left square: (0,0)-(1,0)-(1,1)-(0,1)
# Right square: (1,0)-(2,0)-(2,1)-(1,1)
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))
p20 = f.cartesian_point((2.0, 0.0, 0.0))
p21 = f.cartesian_point((2.0, 1.0, 0.0))

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)
v20 = f.vertex_point(p20)
v21 = f.vertex_point(p21)

def line_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# Shared interior edge E at x=1, y=0→1 — IS the mechanism
shared_E = line_edge(v10, v11, p10, 0, 1, 0)

# Left face: (0,0)→(1,0)→(1,1)→(0,1)
eL_bot = line_edge(v00, v10, p00,  1, 0, 0)
eL_top = line_edge(v11, v01, p11, -1, 0, 0)
eL_lft = line_edge(v01, v00, p01,  0,-1, 0)
loopL = f.edge_loop([
    f.oriented_edge(eL_bot,    True),
    f.oriented_edge(shared_E,  True),   # interior edge E: (1,0)→(1,1)
    f.oriented_edge(eL_top,    True),
    f.oriented_edge(eL_lft,    True),
])
face_L = f.advanced_face([f.face_outer_bound(loopL)], plane)

# Right face: (1,0)→(2,0)→(2,1)→(1,1)
eR_bot = line_edge(v10, v20, p10,  1, 0, 0)
eR_rgt = line_edge(v20, v21, p20,  0, 1, 0)
eR_top = line_edge(v21, v11, p21, -1, 0, 0)
loopR = f.edge_loop([
    f.oriented_edge(eR_bot,   True),
    f.oriented_edge(eR_rgt,   True),
    f.oriented_edge(eR_top,   True),
    f.oriented_edge(shared_E, False),   # interior edge E reversed: (1,1)→(1,0)
])
face_R = f.advanced_face([f.face_outer_bound(loopR)], plane)

# OPEN_SHELL: shared interior edge E IS wired into both faces
shell = f.open_shell([face_L, face_R])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
