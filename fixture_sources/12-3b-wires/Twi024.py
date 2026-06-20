"""Twi024 — Wires forming inner loops outside outer loop (mis-classified hole).

Catalog claim: An inner ("hole") wire is oriented as if it were the outer wire
(wrong winding direction), or actually lies geometrically outside the outer wire
it is meant to be cut from. CW winding where CCW is expected (or vice-versa)
for the face's outward normal.

Mechanism IS the FACE_BOUND inner wire whose 2D winding is CCW (same as the outer
FACE_OUTER_BOUND), when it should be CW for a hole. The inner EDGE_LOOP IS wired
directly into a FACE_BOUND in the ADVANCED_FACE, and FACE_BOUND IS wired into the
ADVANCED_FACE in the OPEN_SHELL; never orphaned. The defect is present in the
topological wire orientation flag of the inner bound.

Reproducer: ADVANCED_FACE on a PLANE with one FACE_OUTER_BOUND (outer rect CCW)
and one FACE_BOUND (inner rect also CCW — same winding direction as outer).

Byte assertions:
  - count_entity_def(b'FACE_OUTER_BOUND') == 1
  - count_entity_def(b'FACE_BOUND') == 1

Tier-3 assertions:
  - n_edges_total >= 8
  - face[0].surface_type == "plane"
  - n_vertices_total >= 16

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi024",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP for outer rectangle traversed CCW; "
        "FACE_BOUND references an EDGE_LOOP for inner rectangle also traversed CCW — "
        "same winding direction as outer, i.e. not reversed as required for a hole; "
        "wrong CCW winding on inner FACE_BOUND IS the mechanism (mis-classified hole); "
        "both EDGE_LOOPs ARE wired into face bounds in ADVANCED_FACE in OPEN_SHELL; "
        "kernel must flip inner wire orientation or reject as malformed"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Helper: build a rectangular EDGE_LOOP in z=0 from four corners ───────────
def rect_loop(corners):
    """corners: list of (x,y) tuples traversed in order (CCW for outer)."""
    n = len(corners)
    verts = [f.vertex_point(f.cartesian_point((x, y, 0.0))) for x, y in corners]
    oes = []
    for i in range(n):
        v_s = verts[i]
        v_e = verts[(i + 1) % n]
        xs, ys = corners[i]
        xe, ye = corners[(i + 1) % n]
        ln_dir = f.direction((xe - xs, ye - ys, 0.0))
        length = ((xe - xs)**2 + (ye - ys)**2) ** 0.5
        ln_vec = f.vector(ln_dir, length)
        ln     = f.line(f.cartesian_point((xs, ys, 0.0)), ln_vec)
        ec     = f.edge_curve(v_s, v_e, ln)
        oe     = f.oriented_edge(ec, True)
        oes.append(oe)
    loop = f._emit_raw(
        "EDGE_LOOP('',({}))".format(",".join(f"#{oe.eid}" for oe in oes))
    )
    return loop

# ── Outer rectangle: CCW (correct) ─────────────────────────────────────────
outer_corners = [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)]
outer_loop = rect_loop(outer_corners)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{outer_loop.eid},.T.)")

# ── Inner rectangle: also CCW — IS the defect (should be CW for a hole) ─────
# Geometrically inside the outer rect but same winding — mis-classified hole.
inner_corners = [(1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0)]
inner_loop = rect_loop(inner_corners)
# FACE_BOUND (not FACE_OUTER_BOUND); inner wire bound flag .T. = same-sense
# The defect: inner bound traversed CCW like the outer (not reversed to CW).
fb = f._emit_raw(f"FACE_BOUND('',#{inner_loop.eid},.T.)")

# Wire both bounds into ADVANCED_FACE in OPEN_SHELL — never orphan.
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid},#{fb.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
