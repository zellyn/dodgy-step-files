"""Twi011 — Wire tail / hair (thin spike beyond max-angle/width threshold).

Catalog claim: A wire emits a thin spike — a collinear go-and-return — that is
sharper than a configured max-angle and narrower than a max-width threshold.
Produces zero-area extrusion artefacts. Some faces have two such notches per wire.

Mechanism IS the backtrack spike in the EDGE_LOOP: the wire for a 1×1 planar
face includes a go-and-return spike at one vertex. The spike is the sub-path
A→B→A (where B is 0.001 units off the nominal edge, well below any max-width
threshold) inserted mid-traversal so the wire nominally "closes" but has a
zero-area extrusion artefact. The spike IS wired into the EDGE_LOOP which IS
referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL;
never orphaned. Kernel must detect and remove the spike (drop the redundant
out-and-back edges, merge endpoints) or reject the wire as malformed.

Tier-3 assertions:
  - n_edges_total >= 5
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi011",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with 6 ORIENTED_EDGEs; "
        "the wire traces a 1×1 square but inserts a go-and-return spike "
        "A(0.5,0)→B(0.5,-0.001)→A at the bottom mid-edge; "
        "spike is 0.001 wide — well below any max-width threshold; "
        "sub-path A→B→A IS the hair/tail defect; "
        "kernel must detect and remove spike or reject as malformed"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Unit square corners ───────────────────────────────────────────────────────
# Bottom edge is interrupted by spike at (0.5, 0): (0,0)→(0.5,0)→(0.5,-0.001)→(0.5,0)→(1,0)
# Then right, top, left edges close the square normally.

def mk_line_edge(pa, pb, va, vb):
    dx = pb[0] - pa[0]; dy = pb[1] - pa[1]
    mag = math.hypot(dx, dy)
    d   = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, 1.0)
    ln  = f.line(f.cartesian_point(pa), vec)
    return f.edge_curve(va, vb, ln)

# Corner vertices
v_00a = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))  # start of bottom
v_mid = f.vertex_point(f.cartesian_point((0.5, 0.0, 0.0)))  # spike base (go)
v_tip = f.vertex_point(f.cartesian_point((0.5, -0.001, 0.0)))  # spike tip
v_mid2 = f.vertex_point(f.cartesian_point((0.5, 0.0, 0.0)))  # spike base (return) — distinct entity
v_10a  = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))  # end of bottom
v_10b  = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))  # start of right
v_11a  = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))
v_11b  = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))
v_01a  = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))
v_01b  = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))
v_00b  = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))  # end of left

# Bottom-left segment: (0,0)→(0.5,0)
e_bot_L  = mk_line_edge((0.0, 0.0, 0.0), (0.5, 0.0, 0.0), v_00a, v_mid)
# Spike out: (0.5,0)→(0.5,-0.001) — the "go" of the hair
e_spike_out  = mk_line_edge((0.5, 0.0, 0.0), (0.5, -0.001, 0.0), v_mid, v_tip)
# Spike back: (0.5,-0.001)→(0.5,0) — the "return" of the hair (IS the defect)
e_spike_back = mk_line_edge((0.5, -0.001, 0.0), (0.5, 0.0, 0.0), v_tip, v_mid2)
# Bottom-right segment: (0.5,0)→(1,0)
e_bot_R  = mk_line_edge((0.5, 0.0, 0.0), (1.0, 0.0, 0.0), v_mid2, v_10a)
# Right edge: (1,0)→(1,1)
e_right  = mk_line_edge((1.0, 0.0, 0.0), (1.0, 1.0, 0.0), v_10b, v_11a)
# Top edge: (1,1)→(0,1)
e_top    = mk_line_edge((1.0, 1.0, 0.0), (0.0, 1.0, 0.0), v_11b, v_01a)
# Left edge: (0,1)→(0,0)
e_left   = mk_line_edge((0.0, 1.0, 0.0), (0.0, 0.0, 0.0), v_01b, v_00b)

# ── EDGE_LOOP with embedded spike: IS the mechanism ───────────────────────────
loop = f.edge_loop([
    f.oriented_edge(e_bot_L,    True),   # (0,0)→(0.5,0)
    f.oriented_edge(e_spike_out, True),  # (0.5,0)→(0.5,-0.001)  ← spike go
    f.oriented_edge(e_spike_back, True), # (0.5,-0.001)→(0.5,0)  ← spike return (hair)
    f.oriented_edge(e_bot_R,    True),   # (0.5,0)→(1,0)
    f.oriented_edge(e_right,    True),   # (1,0)→(1,1)
    f.oriented_edge(e_top,      True),   # (1,1)→(0,1)
    f.oriented_edge(e_left,     True),   # (0,1)→(0,0)
])

# Wire defect loop into face/shell topology — never orphan.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
