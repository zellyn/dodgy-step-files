"""Hea002 — Solid-level healing on MANIFOLD_SOLID_BREP wrapping an OPEN_SHELL.

Catalog claim: A MANIFOLD_SOLID_BREP whose outer slot wraps an OPEN_SHELL
(not a CLOSED_SHELL). A manifold solid requires a closed outer shell.
The solid-level orchestrator (ShapeFix_Solid::Perform) must propagate fixes
inward to shells/faces and re-evaluate closure; if the post-fix shell still
doesn't bound a finite volume the shape must be rejected.

Mechanism: Single 10×10 square face on a PLANE wrapped in an OPEN_SHELL,
then wrapped in MANIFOLD_SOLID_BREP. The solid is defective: its outer
shell is not closed (only one face, no volume). OCC loads it as shape(1)
because the BRep entity is recognized but brepcheck catches the non-closure.

Tier-3 assertions:
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea002",
    defect=(
        "MANIFOLD_SOLID_BREP whose outer slot wraps an OPEN_SHELL (not CLOSED_SHELL); "
        "the single-face open shell is not watertight; "
        "ShapeFix_Solid orchestrator must detect non-closure and reject or cap; "
        "defect: MANIFOLD_SOLID_BREP outer = OPEN_SHELL, shell is a single plane face"
    ),
)

# ── Plane at origin ───────────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── 10×10 rectangular face ────────────────────────────────────────────────────
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

loop = f.edge_loop([
    f.oriented_edge(ec_b, True),
    f.oriented_edge(ec_r, True),
    f.oriented_edge(ec_t, True),
    f.oriented_edge(ec_l, True),
])
fob   = f.face_outer_bound(loop)
face  = f.advanced_face([fob], plane)

# ── DEFECT: MANIFOLD_SOLID_BREP wraps OPEN_SHELL ─────────────────────────────
shell = f.open_shell([face])
solid = f.manifold_solid_brep(shell)

f.add_product_chain(solid, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea002.stp")
