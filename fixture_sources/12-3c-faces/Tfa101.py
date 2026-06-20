"""Tfa101 — ShapeFix_Face.FixAddNaturalBound torus complete-surface.

Catalog claim: Full torus surface needing natural boundary insertion; the
boundary inserter must produce two boundary loops (interior+exterior) but only
constructs one, leaving the complete surface un-bounded.

Mechanism: MANIFOLD_SOLID_BREP with a TOROIDAL_SURFACE face (major radius 5,
minor radius 1). The face's outer wire forms a minimal closed loop encircling
the torus tube at one meridional cross-section. This wire is geometrically
insufficient to bound the full double-periodic torus surface, so
FixAddNaturalBound must insert both natural boundary loops (the outer ring at
u=0/2π and the inner ring at v=0/2π). The inserter's one-loop-only bug leaves
the surface un-bounded on one axis.

A flat rectangular companion face ensures OCC loads shape(1).

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(4) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa101",
    defect=(
        "CLOSED_SHELL: TOROIDAL_SURFACE face (major=5.0, minor=1.0) with single "
        "minimal closed outer wire at one meridional cross-section (v=0 circle); "
        "FixAddNaturalBound must insert two boundary loops for double-periodic torus "
        "but only constructs one, leaving surface un-bounded on one periodic direction; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# TOROIDAL_SURFACE: major radius 5.0, minor radius 1.0, centered at origin
tor_orig = f.cartesian_point((0.0, 0.0, 0.0))
tor_zdir = f.direction((0.0, 0.0, 1.0))
tor_xdir = f.direction((1.0, 0.0, 0.0))
tor_plc  = f.axis2_placement_3d(tor_orig, tor_zdir, tor_xdir)
torus    = f.toroidal_surface(tor_plc, 5.0, 1.0)

# Minimal wire: a circle in the XZ plane at the meridional cross-section
# (major radius 5, at x=5 cross-section where u=0)
# The tube circle center is at (5, 0, 0), radius=1, plane normal = Y axis.
# Points on the tube circle at u=0: (5+cos(θ), 0, sin(θ))
# Use 4 line segments approximating the tube circle
tube_cx = 5.0  # center x of the tube
tube_r  = 1.0

p0 = f.cartesian_point((tube_cx + tube_r, 0.0, 0.0))    # (6, 0, 0)
p1 = f.cartesian_point((tube_cx,          0.0, tube_r)) # (5, 0, 1)
p2 = f.cartesian_point((tube_cx - tube_r, 0.0, 0.0))    # (4, 0, 0)
p3 = f.cartesian_point((tube_cx,          0.0,-tube_r)) # (5, 0,-1)

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

e01 = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction((-1.0, 0.0,  1.0)), _math.sqrt(2.0))))
e12 = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction((-1.0, 0.0, -1.0)), _math.sqrt(2.0))))
e23 = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction(( 1.0, 0.0, -1.0)), _math.sqrt(2.0))))
e30 = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction(( 1.0, 0.0,  1.0)), _math.sqrt(2.0))))

torus_loop = f.edge_loop([
    f.oriented_edge(e01, True),
    f.oriented_edge(e12, True),
    f.oriented_edge(e23, True),
    f.oriented_edge(e30, True),
])
torus_face = f.advanced_face([f.face_outer_bound(torus_loop)], torus)

# ── Companion flat face to ensure shape(1) loads ────────────────────────────
# Rectangle at z=-2 (away from torus)
pc0 = f.cartesian_point((0.0, 0.0, -2.0))
pc1 = f.cartesian_point((1.0, 0.0, -2.0))
pc2 = f.cartesian_point((1.0, 1.0, -2.0))
pc3 = f.cartesian_point((0.0, 1.0, -2.0))

vc0 = f.vertex_point(pc0)
vc1 = f.vertex_point(pc1)
vc2 = f.vertex_point(pc2)
vc3 = f.vertex_point(pc3)

ec01 = f.edge_curve(vc0, vc1, f.line(pc0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
ec12 = f.edge_curve(vc1, vc2, f.line(pc1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
ec23 = f.edge_curve(vc2, vc3, f.line(pc2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
ec30 = f.edge_curve(vc3, vc0, f.line(pc3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

comp_loop = f.edge_loop([
    f.oriented_edge(ec01, True),
    f.oriented_edge(ec12, True),
    f.oriented_edge(ec23, True),
    f.oriented_edge(ec30, True),
])
comp_plc  = f.axis2_placement_3d(pc0, f.direction((0.0, 0.0, -1.0)),
                                   f.direction((1.0, 0.0, 0.0)))
comp_face = f.advanced_face([f.face_outer_bound(comp_loop)], f.plane(comp_plc))

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([torus_face, comp_face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa101.stp")
