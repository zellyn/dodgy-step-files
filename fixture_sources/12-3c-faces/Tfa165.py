"""Tfa165 — ShapeFix_Face.FixAddNaturalBound subsurface.

Catalog claim: Face defined on trimmed subset of larger PLANE surface; actual
wire bounds (0.5..1.5 in both u,v) are interior to surface's natural domain
(infinite plane). FixAddNaturalBound applies natural-bound logic using larger
surface's domain, not trimmed boundaries, producing inconsistent bounds.
Fixture: unit square at (0.5..1.5, 0.5..1.5) on infinite plane.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE: a 1.0×1.0 square (coordinates
from (0.5,0.5) to (1.5,1.5)) on a PLANE whose origin is at (0,0,0). The wire
bounds are interior to the infinite plane's natural domain. FixAddNaturalBound
uses the larger plane domain instead of the actual trimmed wire bounds,
producing inconsistent natural bounds.
Defect IS on live face traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa165",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on infinite PLANE; "
        "plane origin (0,0,0), normal +Z, ref +X — unbounded natural domain; "
        "outer wire: unit square at (0.5,0.5)→(1.5,1.5) — interior to plane domain; "
        "FixAddNaturalBound applies natural-bound logic using plane's infinite domain "
        "instead of actual wire bounds (0.5..1.5, 0.5..1.5); "
        "inconsistent bounds produced; "
        "defect IS on live OPEN_SHELL traversal path; "
        "no orphaned entities"
    ),
)

# ── PLANE surface: origin at (0,0,0), normal +Z — effectively infinite domain ──
# The plane is unbounded; the wire sits in a sub-region [0.5..1.5]×[0.5..1.5]
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
plane   = f.plane(f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir))

# ── Outer wire: unit square at (0.5,0.5)→(1.5,1.5) — interior to plane domain ─
p0 = f.cartesian_point((0.5, 0.5, 0.0))
p1 = f.cartesian_point((1.5, 0.5, 0.0))
p2 = f.cartesian_point((1.5, 1.5, 0.0))
p3 = f.cartesian_point((0.5, 1.5, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

ec_b = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
ec_r = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
ec_t = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
ec_l = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

outer_loop = f.edge_loop([
    f.oriented_edge(ec_b, True),
    f.oriented_edge(ec_r, True),
    f.oriented_edge(ec_t, True),
    f.oriented_edge(ec_l, True),
])

# ── ADVANCED_FACE: unit square on the plane, offset from origin ───────────────
face = f.advanced_face([f.face_outer_bound(outer_loop)], plane)

shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa165.stp")
