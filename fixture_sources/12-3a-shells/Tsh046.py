"""Tsh046 — Adjacent same-domain faces fail to merge across linear-edge chain.

Catalog claim: A flat face has been split along a chain of small, near-collinear
edges. After a face-unification step, the chain remains: the merge skipped these
edges because the per-edge angle test passed but the chain's cumulative deviation
was not considered.

Mechanism IS the shell structure: an OPEN_SHELL contains two co-planar ADVANCED_FACEs
sharing a right-hand boundary composed of 8 short LINE edges, each turning 0.5° from
the previous (cumulative 4°). The kinked-chain shared boundary IS wired into the
shell/face topology — the two face boundaries both reference these 8 edge_curves
with opposite orientations. A face-unifier that only checks per-edge angle (<1°
threshold) marks each pair as non-collinear and skips the merge.

Byte assertions:
  - contains(b'OPEN_SHELL')
  - count_entity_def(b'ADVANCED_FACE') == 2

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh046",
    defect=(
        "OPEN_SHELL with 2 co-planar ADVANCED_FACEs; shared boundary is a chain of "
        "8 short near-collinear edges, each turning 0.5 deg (cumulative 4 deg); "
        "per-edge angle check (<1 deg) passes individually but chain fails overall; "
        "kinked-chain IS wired into shell/face/edge topology; "
        "face unifier must accumulate deviation across whole chain"
    ),
)

# Layout:
# Face A: left rectangle (0,0)→(1,1) in XY plane at z=0
# Face B: right strip sharing a slightly kinked vertical boundary from (1,0) to (1,1)
# The "shared" boundary is 8 short segments approximating x=1 but each segment
# deviates 0.5° from perfectly vertical.

# We build in the XY plane (z=0), normal (0,0,1).
# The kinked chain runs from (1.0, 0.0, 0) to approximately (1.0, 1.0, 0)
# with each segment turning 0.5° in XY.

N_SEGS = 8
SEG_LEN = 1.0 / N_SEGS         # each segment length in Y
TURN_DEG = 0.5                  # each segment turns this many degrees
TURN_RAD = math.radians(TURN_DEG)

# Generate chain points: start at (1.0, 0.0, 0), walk upward with small X wobble
chain_pts = []
x, y = 1.0, 0.0
angle = math.pi / 2  # start heading in +Y direction
chain_pts.append((x, y, 0.0))
for i in range(N_SEGS):
    angle += TURN_RAD  # turn 0.5° per segment
    x += SEG_LEN * math.cos(angle)
    y += SEG_LEN * math.sin(angle)
    chain_pts.append((x, y, 0.0))

# Chain vertices
chain_verts = [f.vertex_point(f.cartesian_point(p)) for p in chain_pts]

# Chain edges (going upward, from chain_verts[0] to chain_verts[N_SEGS])
chain_edges = []
for i in range(N_SEGS):
    p0 = chain_pts[i]; p1 = chain_pts[i+1]
    dx = p1[0] - p0[0]; dy = p1[1] - p0[1]
    pstart = f.cartesian_point(p0)
    d = f.direction((dx, dy, 0.0)); vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    chain_edges.append(f.edge_curve(chain_verts[i], chain_verts[i+1], ln))

# Fixed corner points for Face A (left rectangle x=0 to x=1)
pA_BL = f.cartesian_point((0.0, 0.0, 0.0))
pA_BR = f.cartesian_point(chain_pts[0])      # same as chain start (1.0,0.0,0)
pA_TR = f.cartesian_point(chain_pts[N_SEGS]) # same as chain end
pA_TL = f.cartesian_point((0.0, 1.0, 0.0))

vA_BL = f.vertex_point(pA_BL)
vA_BR = chain_verts[0]
vA_TR = chain_verts[N_SEGS]
vA_TL = f.vertex_point(pA_TL)

def straight_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0); ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

eA_bot = straight_edge(vA_BL, vA_BR, pA_BL,  1, 0, 0)
eA_top = straight_edge(vA_TR, vA_TL, chain_pts[N_SEGS], -1, 0, 0)
eA_lft = straight_edge(vA_TL, vA_BL, pA_TL,  0,-1, 0)

# Face A loop: bottom → chain (upward) → top → left side (downward)
chain_oriented_fwd = [f.oriented_edge(e, True) for e in chain_edges]
loopA = f.edge_loop(
    [f.oriented_edge(eA_bot, True)]
    + chain_oriented_fwd
    + [f.oriented_edge(eA_top, True), f.oriented_edge(eA_lft, True)]
)

ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0)); xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane = f.plane(plc)
faceA = f.advanced_face([f.face_outer_bound(loopA)], plane)

# Face B: right strip sharing the kinked chain as its left boundary.
# Right side at x = chain end x + 0.5
x_right = chain_pts[N_SEGS][0] + 0.5
pB_BL = f.cartesian_point(chain_pts[0])
pB_BR = f.cartesian_point((x_right, 0.0, 0.0))
pB_TR = f.cartesian_point((x_right, 1.0, 0.0))
pB_TL = f.cartesian_point(chain_pts[N_SEGS])

vB_BL = chain_verts[0]
vB_BR = f.vertex_point(pB_BR)
vB_TR = f.vertex_point(pB_TR)
vB_TL = chain_verts[N_SEGS]

eB_bot = straight_edge(vB_BL, vB_BR, chain_pts[0], 1, 0, 0)
eB_rgt = straight_edge(vB_BR, vB_TR, pB_BR,        0, 1, 0)
eB_top = straight_edge(vB_TR, vB_TL, pB_TR,       -1, 0, 0)

# Face B loop: bottom → right → top → chain reversed (downward)
chain_oriented_rev = [f.oriented_edge(e, False) for e in reversed(chain_edges)]
loopB = f.edge_loop(
    [f.oriented_edge(eB_bot, True),
     f.oriented_edge(eB_rgt, True),
     f.oriented_edge(eB_top, True)]
    + chain_oriented_rev
)
faceB = f.advanced_face([f.face_outer_bound(loopB)], plane)

# OPEN_SHELL: kinked chain IS the defect wired into shell/face topology
shell = f.open_shell([faceA, faceB])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
