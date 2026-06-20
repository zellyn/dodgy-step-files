"""Ps002 — FACE_OUTER_BOUND traversed CW; inner loop traversed CCW.

Catalog claim: A planar face with a rectangular hole where the FACE_OUTER_BOUND
loop is traversed clockwise (when viewed from the surface's positive side) and
the inner FACE_BOUND is traversed counter-clockwise.  The inside/outside
semantics of the face are swapped: the kernel "sees" material where the producer
intended a hole.

Mechanism IS the OPEN_SHELL / SHELL_BASED_SURFACE_MODEL face topology: a single
ADVANCED_FACE on z=0 has a 10×10 outer loop wound CW (as seen from +Z) and a
4×4 inner loop wound CCW.  The reversed winding IS wired into the FACE_OUTER_BOUND
and FACE_BOUND of the ADVANCED_FACE, which IS in the OPEN_SHELL of the
SHELL_BASED_SURFACE_MODEL.

Tier-3 assertions:
  - n_edges_total >= 8
  - face[0].surface_type == "plane"
  - n_vertices_total >= 16
OCC behavior: loads a shape (no diagnostic) — healing; strict kernels must reject.
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ps002",
    defect=(
        "Planar face at z=0: FACE_OUTER_BOUND (10x10 square) traversed CW from +Z; "
        "inner FACE_BOUND (4x4 hole) traversed CCW from +Z; inside/outside semantics "
        "swapped; reversed windings ARE wired into FACE_OUTER_BOUND + FACE_BOUND of "
        "ADVANCED_FACE in OPEN_SHELL of SHELL_BASED_SURFACE_MODEL"
    ),
)

# ── Plane at z=0, normal +Z ───────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plane = f.plane(f.axis2_placement_3d(orig, zdir, xdir))

# ── Helper: make a rectangular loop from (x,y) corner tuples ─────────────────
def make_rect_loop(corners):
    """Build EDGE_LOOP from a list of (x,y) corner tuples (z=0); returns loop entity."""
    pts2d = list(corners)
    n     = len(pts2d)
    cps   = [f.cartesian_point((x, y, 0.0)) for x, y in pts2d]
    vts   = [f.vertex_point(p) for p in cps]
    edges = []
    for i in range(n):
        j    = (i + 1) % n
        x0, y0 = pts2d[i]
        x1, y1 = pts2d[j]
        ddx  = x1 - x0
        ddy  = y1 - y0
        length = (ddx*ddx + ddy*ddy) ** 0.5
        d_e  = f.direction((ddx / length, ddy / length, 0.0))
        vec_e = f.vector(d_e, length)
        edges.append(f.edge_curve(vts[i], vts[j], f.line(cps[i], vec_e)))
    oes  = [f.oriented_edge(e, True) for e in edges]
    return f.edge_loop(oes)

# ── CATALOG MECHANISM: outer loop CW, inner loop CCW (from +Z view) ──────────
# Correct CCW outer from +Z: (0,0)→(10,0)→(10,10)→(0,10)
# DEFECT CW outer from +Z:   (0,0)→(0,10)→(10,10)→(10,0)   ← reversed winding
outer_loop = make_rect_loop([(0.0,0.0),(0.0,10.0),(10.0,10.0),(10.0,0.0)])
outer_bound = f.face_outer_bound(outer_loop, orientation=True)

# Correct CW inner (hole) from +Z: (3,3)→(3,7)→(7,7)→(7,3)
# DEFECT CCW inner from +Z:        (3,3)→(7,3)→(7,7)→(3,7)  ← reversed winding
inner_loop  = make_rect_loop([(3.0,3.0),(7.0,3.0),(7.0,7.0),(3.0,7.0)])
inner_bound = f.face_bound(inner_loop, orientation=True)

# ADVANCED_FACE with swapped loop windings IS the defect wired into face topology
face  = f.advanced_face([outer_bound, inner_bound], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])

f.add_product_chain(sbsm, mode="surface_shape")
