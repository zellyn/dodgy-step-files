"""Hea012 — Shape-process operator contract: pluggable healing step over
face with scrambled inner FACE_BOUND triangle.

Catalog claim: A single registered operator must (a) accept a context,
(b) perform its healing step, (c) record changes back to the context for
subsequent operators to observe. The contract is stateless w.r.t. the
operator's own data; all transient state lives in the context.

Mechanism: An ADVANCED_FACE with a rectangular 10×10 outer EDGE_LOOP and
an inner FACE_BOUND triangle whose three VERTEX_POINTs are near-coincident
(sub-mm: 5.0, 5.001) and whose ORIENTED_EDGEs are listed in scrambled
(non-head-to-tail) order. The operator processes the face via the
Perform(context) interface.

Tier-3 assertions:
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea012",
    defect=(
        "ADVANCED_FACE on PLANE with 10x10 outer wire + inner FACE_BOUND triangle "
        "whose VERTEX_POINTs are near-coincident (5.0, 5.001) and ORIENTED_EDGEs "
        "are in scrambled order (third edge first); "
        "ShapeProcess_Operator::Perform must process via Perform(context) interface; "
        "operator records modified flag in context; "
        "defect: scrambled inner wire + near-coincident vertices"
    ),
)

# ── Plane at origin ───────────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Outer 10×10 rectangular wire ─────────────────────────────────────────────
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 10.0, 0.0))
p3 = f.cartesian_point((0.0, 10.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

ec_b = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
ec_r = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
ec_t = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
ec_l = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

outer_loop = f.edge_loop([
    f.oriented_edge(ec_b, True),
    f.oriented_edge(ec_r, True),
    f.oriented_edge(ec_t, True),
    f.oriented_edge(ec_l, True),
])
fob = f.face_outer_bound(outer_loop)
face = f.advanced_face([fob], plane)

# ── Inner triangle: near-coincident vertices (5.0, 5.001), scrambled order ───
# Triangle: p_i1(5,5), p_i2(5.001,5), p_i3(5,5.001)
pi1 = f.cartesian_point((5.0, 5.0, 0.0))
pi2 = f.cartesian_point((5.001, 5.0, 0.0))
pi3 = f.cartesian_point((5.0, 5.001, 0.0))
vi1 = f.vertex_point(pi1)
vi2 = f.vertex_point(pi2)
vi3 = f.vertex_point(pi3)

# Edge 1: pi1 -> pi2 (along +X, sub-tolerance)
ie1 = f.edge_curve(vi1, vi2, f.line(pi1, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
# Edge 2: pi2 -> pi3 (diagonal)
ie2 = f.edge_curve(vi2, vi3, f.line(pi2, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
# Edge 3: pi3 -> pi1 (diagonal)
_sq2 = 1.0 / _math.sqrt(2.0)
ie3 = f.edge_curve(vi3, vi1,
                   f.line(pi3, f.vector(f.direction((-_sq2, _sq2, 0.0)), 1.4142)))

# SCRAMBLED: edge3 first, then edge1, then edge2
inner_loop = f.edge_loop([
    f.oriented_edge(ie3, True),
    f.oriented_edge(ie1, True),
    f.oriented_edge(ie2, True),
])
# FACE_BOUND with .T. (wrong orientation for inner hole — keeps defect live)
fb = f._emit_raw(f"FACE_BOUND('',#{inner_loop.eid},.T.)")

# ── OPEN_SHELL wrapper ────────────────────────────────────────────────────────
shell = f.open_shell([face], name="wrap_shell")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea012.stp")
