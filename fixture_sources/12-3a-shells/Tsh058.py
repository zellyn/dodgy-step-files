"""Tsh058 — Adjacent same-surface face merge ignores edge-preservation request.

Catalog claim: When same-surface face merging is invoked with a flag instructing
it to preserve a specified set of edges, the algorithm processes surrounding
topology but still merges across the protected edges — because the flag is
consulted at the top-level call site but not propagated into the inner
edge-walker. Resulting shape no longer contains the kept edge.

Mechanism IS the shell structure: an OPEN_SHELL contains two coplanar
ADVANCED_FACEs on the same PLANE (z=0) sharing one EDGE_CURVE at x=1. A
PRODUCT_DEFINITION_CONTEXT name-encoded attribute 'keep_edge' is embedded in the
StepFile defect string and as a NAME token on the shared EDGE_CURVE to mark it
for preservation. The shared EDGE_CURVE IS directly wired into both faces'
EDGE_LOOPs. A merge that does not propagate the keep-edge flag into the inner
edge-walker will dissolve this shared edge.

Byte assertions:
  - contains(b'OPEN_SHELL')
  - count_entity_def(b'ADVANCED_FACE') == 2

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh058",
    defect=(
        "OPEN_SHELL with 2 coplanar ADVANCED_FACEs on same PLANE (z=0); "
        "both faces share one EDGE_CURVE at x=1 (y=0→1) marked 'keep_edge'; "
        "keep_edge mark IS wired into shared EDGE_CURVE name token in topology; "
        "merge flag to preserve named edges consulted at top-level only; "
        "inner edge-walker dissolves the shared edge ignoring the keep flag; "
        "fix requires propagating keep-edge set into every traversal step"
    ),
)

# ── Shared plane z=0, normal +Z ───────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Points and vertices ───────────────────────────────────────────────────────
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

# ── Shared protected edge at x=1, y=0→1 — IS the keep_edge mechanism ─────────
# Named 'keep_edge' in entity label so merge-edge-walker can look it up.
d_shared = f.direction((0.0, 1.0, 0.0))
vec_shared = f.vector(d_shared, 1.0)
ln_shared = f.line(p10, vec_shared)
# Emit with 'keep_edge' name so the byte-level assertion and kernel flag can find it
shared_edge = f._emit_raw(
    f"EDGE_CURVE('keep_edge',#{v10.eid},#{v11.eid},#{ln_shared.eid},.T.)"
)

# ── Face A: unit square [0,0]→[1,1] ──────────────────────────────────────────
eA_bot = line_edge(v00, v10, p00,  1, 0, 0)
eA_top = line_edge(v11, v01, p11, -1, 0, 0)
eA_lft = line_edge(v01, v00, p01,  0,-1, 0)

loopA = f.edge_loop([
    f.oriented_edge(eA_bot,     True),
    f.oriented_edge(shared_edge, True),   # (1,0)→(1,1) forward — keep_edge IS here
    f.oriented_edge(eA_top,     True),
    f.oriented_edge(eA_lft,     True),
])
faceA = f.advanced_face([f.face_outer_bound(loopA)], plane)

# ── Face B: unit square [1,0]→[2,1] ──────────────────────────────────────────
eB_bot = line_edge(v10, v20, p10,  1, 0, 0)
eB_rgt = line_edge(v20, v21, p20,  0, 1, 0)
eB_top = line_edge(v21, v11, p21, -1, 0, 0)

loopB = f.edge_loop([
    f.oriented_edge(eB_bot,      True),
    f.oriented_edge(eB_rgt,      True),
    f.oriented_edge(eB_top,      True),
    f.oriented_edge(shared_edge, False),  # (1,1)→(1,0) reversed — same keep_edge
])
faceB = f.advanced_face([f.face_outer_bound(loopB)], plane)

# ── OPEN_SHELL: keep_edge IS wired into both faces' EDGE_LOOP topology ────────
shell = f.open_shell([faceA, faceB])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
