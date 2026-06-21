"""Hea006 — Shape-contents inventory: subshape histogram.

Catalog claim: A compound shape whose constituents the kernel must enumerate
and tally (ShapeAnalysis_ShapeContents::Perform). Counts of faces, edges,
vertices, wires, surface kinds, curve kinds, etc. drive downstream
defect-detection thresholds.

Mechanism: OPEN_SHELL containing a 10×10 rectangular ADVANCED_FACE on a
PLANE. The shell has one face, one wire, 4 edges, 4 vertices.

Tier-3 assertions:
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea006",
    defect=(
        "OPEN_SHELL with single 10x10 rectangular ADVANCED_FACE on PLANE; "
        "ShapeAnalysis_ShapeContents::Perform must enumerate: 1 face, 4 edges, 4 vertices; "
        "informational shape-contents inventory for downstream defect-detection thresholds; "
        "defect: open boundary exposes the free-bound analysis path; "
        "subshape histogram: face=1, wire=1, edges=4, vertices=4, surface_kind=plane"
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
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── OPEN_SHELL ────────────────────────────────────────────────────────────────
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea006.stp")
