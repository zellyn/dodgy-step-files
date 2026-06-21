"""Hea013 — User-defined shape-process operator (UOperator) on face with
scrambled inner FACE_BOUND triangle.

Catalog claim: A kernel API for registering ad-hoc user operators in the
shape-healing pipeline (ShapeProcess_UOperator::Perform); same contract as
Hea012 but injected by a caller rather than being part of the kernel's
built-in operator set. Lets host applications splice domain-specific healing
into the standard pipeline.

Mechanism: Identical input to Hea012 — an ADVANCED_FACE with a 10×10 outer
wire and a near-coincident scrambled inner FACE_BOUND triangle. The operator
is user-registered; the kernel must accept it in the pipeline.

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
    catalog_id="Hea013",
    defect=(
        "ADVANCED_FACE on PLANE with 10x10 outer wire + inner FACE_BOUND triangle "
        "whose VERTEX_POINTs are near-coincident (5.0, 5.001) and ORIENTED_EDGEs "
        "are in scrambled order (third edge first); "
        "ShapeProcess_UOperator::Perform; user-registered operator injected by caller; "
        "kernel must accept user operator via same Perform(context) interface; "
        "structurally identical to Hea012"
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

# ── Inner triangle: near-coincident, scrambled order ─────────────────────────
pi1 = f.cartesian_point((5.0, 5.0, 0.0))
pi2 = f.cartesian_point((5.001, 5.0, 0.0))
pi3 = f.cartesian_point((5.0, 5.001, 0.0))
vi1 = f.vertex_point(pi1)
vi2 = f.vertex_point(pi2)
vi3 = f.vertex_point(pi3)

ie1 = f.edge_curve(vi1, vi2, f.line(pi1, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
ie2 = f.edge_curve(vi2, vi3, f.line(pi2, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
_sq2 = 1.0 / _math.sqrt(2.0)
ie3 = f.edge_curve(vi3, vi1,
                   f.line(pi3, f.vector(f.direction((-_sq2, _sq2, 0.0)), 1.4142)))

inner_loop = f.edge_loop([
    f.oriented_edge(ie3, True),
    f.oriented_edge(ie1, True),
    f.oriented_edge(ie2, True),
])
fb = f._emit_raw(f"FACE_BOUND('',#{inner_loop.eid},.T.)")

# ── OPEN_SHELL wrapper ────────────────────────────────────────────────────────
shell = f.open_shell([face], name="wrap_shell")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea013.stp")
