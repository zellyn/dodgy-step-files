"""Tfa058 — Plane-typed face whose vertices are non-coplanar.

Catalog claim: An ADVANCED_FACE declares its surface as a PLANE, but the bounding
wire visits 3D vertices that don't lie on that plane (the largest deviation exceeds
any plausible tolerance). Bug-reporter language: "face not planar", "vertices not
on plane", "non-flat plane face".

Mechanism: OPEN_SHELL with TWO faces:
  face[0] (defective): ADVANCED_FACE on PLANE at z=0 (z_normal=(0,0,1)).
    The bounding wire visits 4 vertices: (0,0,0), (100,0,0), (100,100,0),
    (0,100,50.0) — the fourth vertex is 50mm above the declared plane.
    This is the non-coplanar defect: vertex 3 deviates from z=0 by 50mm,
    far beyond any tolerance.
  face[1] (reference): valid 100×100 plane at z=100 to give OCC a valid face.
    Satisfies n_vertices_total >= 8 and n_edges_total >= 4.

OCC heals by adjusting the face; brepcheck reports valid == True on the healed
shape.

Tier-3 assertions:
  face[0].surface_type == "plane"
  n_edges_total >= 4
  n_vertices_total >= 8
  brepcheck.valid == True

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math

f = StepFile(
    catalog_id="Tfa058",
    defect=(
        "OPEN_SHELL: face[0] on PLANE at z=0; "
        "vertex[3] at (0,100,50) — 50mm above the declared z=0 plane; "
        "non-coplanar defect: largest vertex deviation = 50mm >> tolerance; "
        "BRepLib_MakeFace::NotPlanar condition; "
        "face[1] is valid 100×100 plane at z=100 (adds n_vertices >= 4 more); "
        "n_vertices_total >= 8, n_edges_total >= 4; "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)


def make_edge(v1, cp1, dx, dy, dz, mag, v2):
    """Make an edge_curve from v1 to v2 using a line through cp1 in direction (dx,dy,dz)/mag."""
    d   = f.direction((dx/mag, dy/mag, dz/mag))
    vec = f.vector(d, mag)
    return f.edge_curve(v1, v2, f.line(cp1, vec))


# ── DEFECTIVE face[0]: non-coplanar quad on z=0 PLANE ────────────────────────
# Vertices: three at z=0, one at z=50
p0 = f.cartesian_point((  0.0,   0.0, 0.0))   # BL — on plane
p1 = f.cartesian_point((100.0,   0.0, 0.0))   # BR — on plane
p2 = f.cartesian_point((100.0, 100.0, 0.0))   # TR — on plane
p3 = f.cartesian_point((  0.0, 100.0, 50.0))  # TL — OFF plane by 50mm (DEFECT)

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# Edge lengths
L01 = 100.0
L12 = 100.0
L23 = math.sqrt(100.0**2 + 50.0**2)  # diagonal in 3D
L30 = math.sqrt(100.0**2 + 50.0**2)  # diagonal in 3D

ec01 = make_edge(v0, p0,  100.0,   0.0, 0.0, L01, v1)
ec12 = make_edge(v1, p1,    0.0, 100.0, 0.0, L12, v2)
ec23 = make_edge(v2, p2, -100.0,   0.0, 50.0, L23, v3)
ec30 = make_edge(v3, p3,    0.0,-100.0,-50.0, L30, v0)

defect_loop = f.edge_loop([
    f.oriented_edge(ec01, True),
    f.oriented_edge(ec12, True),
    f.oriented_edge(ec23, True),
    f.oriented_edge(ec30, True),
])

# PLANE declared at z=0 (the defect: vertices don't all lie on this plane)
pl0_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl0_zdir = f.direction((0.0, 0.0, 1.0))
pl0_xdir = f.direction((1.0, 0.0, 0.0))
plane0   = f.plane(f.axis2_placement_3d(pl0_orig, pl0_zdir, pl0_xdir))

face0 = f.advanced_face([f.face_outer_bound(defect_loop)], plane0)

# ── VALID reference face[1]: 100×100 plane at z=100 ──────────────────────────
r0 = f.cartesian_point((  0.0,   0.0, 100.0))
r1 = f.cartesian_point((100.0,   0.0, 100.0))
r2 = f.cartesian_point((100.0, 100.0, 100.0))
r3 = f.cartesian_point((  0.0, 100.0, 100.0))

rv0 = f.vertex_point(r0)
rv1 = f.vertex_point(r1)
rv2 = f.vertex_point(r2)
rv3 = f.vertex_point(r3)

re0 = f.edge_curve(rv0, rv1, f.line(r0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 100.0)))
re1 = f.edge_curve(rv1, rv2, f.line(r1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 100.0)))
re2 = f.edge_curve(rv2, rv3, f.line(r2, f.vector(f.direction((-1.0, 0.0, 0.0)), 100.0)))
re3 = f.edge_curve(rv3, rv0, f.line(r3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 100.0)))

ref_loop  = f.edge_loop([
    f.oriented_edge(re0, True),
    f.oriented_edge(re1, True),
    f.oriented_edge(re2, True),
    f.oriented_edge(re3, True),
])
pl1_orig  = f.cartesian_point((0.0, 0.0, 100.0))
pl1_zdir  = f.direction((0.0, 0.0, 1.0))
pl1_xdir  = f.direction((1.0, 0.0, 0.0))
plane1    = f.plane(f.axis2_placement_3d(pl1_orig, pl1_zdir, pl1_xdir))
face1     = f.advanced_face([f.face_outer_bound(ref_loop)], plane1)

# ── OPEN_SHELL ────────────────────────────────────────────────────────────────
shell = f.open_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa058.stp")
