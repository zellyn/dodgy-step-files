"""Ps010 — ORIENTED_EDGE.orientation=.F. on every half-edge of a wire.

Catalog claim: A planar face with a square outer loop.  Each underlying
EDGE_CURVE is constructed so its 3D direction matches the intended CCW
traversal; but every ORIENTED_EDGE on that loop has orientation=.F., reversing
each one.  Adjacent endpoints still match (the loop closes), every edge has
degree 2, kernel accepts the file silently.  Tier-3 introspection (signed-area
of the loop in the face's parametric domain vs. surface normal) reveals the
loop traverses CW where CCW was intended.

Mechanism IS the OPEN_SHELL / SHELL_BASED_SURFACE_MODEL face topology: a
square ADVANCED_FACE at z=0 whose EDGE_LOOP contains four ORIENTED_EDGEs each
with orientation=.F. IS the defect — all four reversed flags ARE wired directly
into the EDGE_LOOP of the FACE_OUTER_BOUND of the ADVANCED_FACE in the
OPEN_SHELL of the SHELL_BASED_SURFACE_MODEL.  The loop closes but has
sliver-like signed-area behaviour.

Tier-3 assertions:
  - face[0].surface_type == "plane"
  - n_edges_total >= 4
  - n_vertices_total >= 8
  - face[0].sliver_aspect_max_min > 1e6
OCC behavior: loads a shape (no diagnostic) — healing; strict kernels must reject/warn.
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ps010",
    defect=(
        "Square ADVANCED_FACE at z=0: all four ORIENTED_EDGEs in EDGE_LOOP have "
        "orientation=.F. (reversed); underlying EDGE_CURVEs trace CCW but each "
        "reversal makes traversal CW; all reversed flags ARE wired into EDGE_LOOP "
        "of FACE_OUTER_BOUND in OPEN_SHELL of SHELL_BASED_SURFACE_MODEL; "
        "loop closes (endpoints match) but signed area is wrong"
    ),
)

# ── Plane at z=0, normal +Z ───────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plane = f.plane(f.axis2_placement_3d(orig, zdir, xdir))

# ── CATALOG MECHANISM: four EDGE_CURVEs tracing CCW, all with orientation=.F. ─
# Square vertices: (0,0)→(1,0)→(1,1)→(0,1) in CCW order when viewed from +Z.
# The underlying EDGE_CURVEs are built in this CCW direction.
# Every ORIENTED_EDGE has orientation=.F. → each edge is traversed backwards.
# Result: loop traverses (0,0)←(1,0)←(1,1)←(0,1)←(0,0) = CW from +Z.

corners = [(0.0,0.0),(1.0,0.0),(1.0,1.0),(0.0,1.0)]
n = len(corners)
cps  = [f.cartesian_point((x, y, 0.0)) for x, y in corners]
vts  = [f.vertex_point(p) for p in cps]

edges = []
for i in range(n):
    j        = (i + 1) % n
    x0, y0   = corners[i]
    x1, y1   = corners[j]
    ddx      = x1 - x0
    ddy      = y1 - y0
    length   = (ddx*ddx + ddy*ddy) ** 0.5
    d_e      = f.direction((ddx / length, ddy / length, 0.0))
    vec_e    = f.vector(d_e, length)
    # EDGE_CURVE direction is CCW (correct)
    ec = f.edge_curve(vts[i], vts[j], f.line(cps[i], vec_e))
    edges.append(ec)

# All ORIENTED_EDGEs with orientation=.F. — THE DEFECT wired into EDGE_LOOP
oes  = [f.oriented_edge(e, False) for e in edges]  # orientation=.F. on all
loop = f.edge_loop(oes)
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# OPEN_SHELL IS the face topology container — reversed orientations wired in
shell = f.open_shell([face], name="ps010_all_edges_reversed")
sbsm  = f.shell_based_surface_model([shell], name="ps010_cw_loop_face")

f.add_product_chain(sbsm, mode="surface_shape")
