"""Tfa038 — Face on closed surface lacks outer boundary.

Catalog claim: An ADVANCED_FACE on a SPHERICAL_SURFACE (geometrically closed in
both U and V) carries only inner FACE_BOUND wires (holes) and no
FACE_OUTER_BOUND. The face is "the surface minus the holes". Without a
synthesized natural boundary, area, sampling, and sewing are undefined.

Mechanism: An ADVANCED_FACE on a sphere of radius 5 with:
  - No FACE_OUTER_BOUND at all (the defect)
  - One inner FACE_BOUND: a small circle at the equator (a "hole" punched
    through the sphere surface near the north pole)

The circle is a closed CIRCLE EDGE_CURVE with start==end vertex at a point on
the sphere. The FACE_BOUND has orientation=False (inner boundary convention).

Tier-3 assertions:
  face[0].surface_type == "sphere"
  n_edges_total >= 1
  n_vertices_total >= 2
  brepcheck.valid == False

Expected: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa038",
    defect=(
        "OPEN_SHELL: ADVANCED_FACE on SPHERICAL_SURFACE (radius=5) has NO "
        "FACE_OUTER_BOUND — only one inner FACE_BOUND (a circular hole near equator); "
        "face is 'whole sphere minus the hole'; FixAddNaturalBound must synthesize "
        "a natural outer boundary spanning the full parameter domain; "
        "brepcheck.valid=False because missing outer bound; "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

R = 5.0

# ── SPHERICAL_SURFACE: center (0,0,0), radius 5 ───────────────────────────────
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_ax   = f.direction((0.0, 0.0, 1.0))
sph_ref  = f.direction((1.0, 0.0, 0.0))
sph_plc  = f.axis2_placement_3d(sph_orig, sph_ax, sph_ref)
sphere   = f.spherical_surface(sph_plc, R)

# ── Inner hole: small circle near north pole at (0,0,R)==(0,0,5) ─────────────
# The hole is a small circle at latitude 80° (elevation=80°): z = R*sin(80°)
# and radius_at_lat = R*cos(80°).
lat_rad    = math.radians(80.0)
hole_z     = R * math.sin(lat_rad)    # ≈ 4.924
hole_r     = R * math.cos(lat_rad)    # ≈ 0.868

# A circle in a plane z=hole_z, center (0,0,hole_z), radius=hole_r.
# The seam point is at (hole_r, 0, hole_z).
seam_pt = f.cartesian_point((hole_r, 0.0, hole_z))
v_seam  = f.vertex_point(seam_pt)

# Circle placement: center at (0,0,hole_z), axis up (+Z), ref along +X
hole_ctr = f.cartesian_point((0.0, 0.0, hole_z))
hole_ax  = f.direction((0.0, 0.0, 1.0))
hole_ref = f.direction((1.0, 0.0, 0.0))
hole_plc = f.axis2_placement_3d(hole_ctr, hole_ax, hole_ref)
hole_circle = f.circle(hole_plc, hole_r)

# Closed circle edge: start == end == v_seam
hole_edge = f.edge_curve(v_seam, v_seam, hole_circle)

# EDGE_LOOP for the inner hole
hole_loop = f.edge_loop([f.oriented_edge(hole_edge, True)])

# FACE_BOUND (inner boundary) with orientation=False (inner convention)
# NO FACE_OUTER_BOUND — that is the defect
inner_bound = f.face_bound(hole_loop, orientation=False)
face_sphere = f.advanced_face([inner_bound], sphere)

# ── OPEN_SHELL ────────────────────────────────────────────────────────────────
shell = f.open_shell([face_sphere])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa038.stp")
