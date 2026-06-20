"""Twi002 — Single-edge EDGE_LOOP with non-coincident start/end vertex.

Catalog claim: A loop containing exactly one ORIENTED_EDGE requires the
underlying EDGE_CURVE start and end vertices to coincide (closed curve such as
full circle/ellipse). Some files emit a single open edge as a "loop",
violating the closure invariant.

Mechanism IS the single-edge EDGE_LOOP with open EDGE_CURVE: the one
ORIENTED_EDGE's underlying EDGE_CURVE has distinct start and end
VERTEX_POINTs separated by 1 unit — clearly not a closed curve. The defect
loop IS referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE in an
OPEN_SHELL; never orphaned. Kernel must reject loop or heal by inserting a
closing edge, and warn.

Tier-3 assertions:
  - n_edges_total >= 1
  - face[0].surface_type == "plane"
  - n_vertices_total >= 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi002",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with a single ORIENTED_EDGE "
        "whose EDGE_CURVE has distinct start (0,0,0) and end (1,0,0) VERTEX_POINTs; "
        "single-edge loop invariant requires a closed (coincident-endpoint) curve; "
        "kernel must reject or heal with closing edge and warn"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Two distinct vertices: this IS the defect (no coincident endpoints) ───────
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((1.0, 0.0, 0.0))   # distinct — not coincident with start

v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

# ── Single open EDGE_CURVE: line from (0,0,0) to (1,0,0) ─────────────────────
d   = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1.0)
ln  = f.line(p_start, vec)
ec  = f.edge_curve(v_start, v_end, ln)

# ── Single-edge EDGE_LOOP: IS the mechanism ───────────────────────────────────
loop = f.edge_loop([f.oriented_edge(ec, True)])

# Wire the defect loop into face/shell topology — never orphan.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
