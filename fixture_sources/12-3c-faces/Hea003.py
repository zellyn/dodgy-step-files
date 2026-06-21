"""Hea003 — Free-bound properties pipeline computes area/perimeter/notches together.

Catalog claim: A shell with one or more free bounds (open boundaries). The
kernel's free-bound analyzer (ShapeAnalysis_FreeBoundsProperties::Perform)
must compute, per bound, the area of the contour, perimeter, average
length-to-width ratio, average width, and notch list in a single unified pass.

Mechanism: OPEN_SHELL containing a single 10×10 rectangular ADVANCED_FACE on
a PLANE. The shell has one free boundary (the outer EDGE_LOOP), with:
  area = 100, perimeter = 40, width = 10, length = 10, no notches.

Tier-3 assertions:
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea003",
    defect=(
        "OPEN_SHELL with single 10x10 rectangular ADVANCED_FACE on PLANE; "
        "one free bound with area=100, perimeter=40, no notches; "
        "ShapeAnalysis_FreeBoundsProperties must compute all metrics in one pass; "
        "defect: open boundary (un-closed shell) triggers free-bound analysis pipeline"
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

# ── OPEN_SHELL (unclosed → free bound) ───────────────────────────────────────
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea003.stp")
