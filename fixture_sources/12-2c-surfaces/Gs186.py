"""Gs186 — SPHERICAL_SURFACE PCURVE V-range [0, π] instead of [-π/2, +π/2].

Catalog claim: STEP file with a SPHERICAL_SURFACE ADVANCED_FACE containing a
PCURVE whose parameter-space representation uses a V-range of [0, π] instead
of the STEP-defined [-π/2, +π/2] (ISO 10303-42 §4.4.32 sphere parametrization).
The V-origin is offset by +π/2, causing UV curves to be mapped to the wrong
half of the sphere in receivers that enforce the standard parametrization.

Source: https://docs.techsoft3d.com/exchange/2023_SP2_U1/fixed_bugs.html
(SDHE-12051: incorrect UV curves on spherical face from STEP)

The defect is in the PCURVE's DEFINITIONAL_REPRESENTATION (the 2D curve) —
the V-parameter origin is at 0 instead of -π/2, offsetting the parametric
strip by π/2. On a sphere of radius 5, standard V ∈ [-π/2, +π/2] maps the
equatorial strip; V ∈ [0, π] maps a strip from equator to south pole to north
pole, which is geometrically incorrect for the intended seam edge.

OCCT behavior: healing may recompute the pcurve, yielding shape(1)/shape(1).
Pre-fix HOOPS Exchange produced incorrect UV curves (tessellation artifacts).

Byte assertions:
  contains(b'SPHERICAL_SURFACE')
  contains(b'PCURVE')
Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs186",
    defect=(
        "SPHERICAL_SURFACE (radius 5) IS ADVANCED_FACE.face_geometry; "
        "PCURVE on seam edge uses V-range [0, pi] instead of ISO-10303-42 §4.4.32 "
        "standard [-pi/2, +pi/2] — V-origin offset by +pi/2; "
        "wrong V-parametrization maps UV strip to wrong hemisphere (SDHE-12051); "
        "shape_null or shape(1) depending on healing"
    ),
)

PI = math.pi

# ── SPHERICAL_SURFACE (radius 5, centered at origin) ─────────────────────────
# Byte assertion: contains(b'SPHERICAL_SURFACE')
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_ax   = f.axis2_placement_3d(sph_orig, sph_zdir, sph_xdir)
sphere   = f.spherical_surface(sph_ax, 5.0)

# ── Parametric representation context (2D) ───────────────────────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Sphere face boundary ──────────────────────────────────────────────────────
# Use a rectangular equatorial patch: U ∈ [0, 2π], V ∈ [0, π] (defect range).
# Standard ISO 10303-42 §4.4.32 sphere parametrization:
#   X = R * cos(V) * cos(U)
#   Y = R * cos(V) * sin(U)
#   Z = R * sin(V)
# with V ∈ [-π/2, +π/2].
#
# DEFECT: This fixture's PCURVE uses V ∈ [0, π] — the V-origin is shifted +π/2
# from the standard. The 2D line starts at (U=0, V=0) and spans to (U=0, V=π).
# Under the standard, V=0 → equator (Z=0), V=π/2 → north pole (Z=R),
# V=π → equator again (sin(π)=0). This produces a seam that doubles back,
# violating the standard's injection requirement for the seam.
#
# Seam edge: a line from south pole (0,0,-5) to north pole (0,0,5) at U=0.

south_pole = f.cartesian_point((0.0, 0.0, -5.0))
north_pole = f.cartesian_point((0.0, 0.0,  5.0))
v_south = f.vertex_point(south_pole)
v_north = f.vertex_point(north_pole)

# 3D seam edge: line from (0,0,-5) to (0,0,+5) along Z
seam_dir3  = f.direction((0.0, 0.0, 1.0))
seam_vec3  = f.vector(seam_dir3, 10.0)    # length = 2R = 10
seam_line3 = f.line(south_pole, seam_vec3)

# ── DEFECT: 2D PCURVE on sphere surface ──────────────────────────────────────
# Standard: seam at U=0, V from -π/2 (south) to +π/2 (north)
# DEFECT:   seam at U=0, V from 0 to π  (offset by +π/2 from standard)
#           V=0 maps to equator, V=π/2 maps to north pole, V=π maps back to equator
# Byte assertion: contains(b'PCURVE')
seam_p2d_start = f.cartesian_point((0.0, 0.0))          # (U=0, V=0) — defect origin
seam_dir2d     = f.direction((0.0, 1.0))                  # V direction
seam_vec2d     = f.vector(seam_dir2d, PI)                 # V range [0, π] — defect
seam_line2d    = f.line(seam_p2d_start, seam_vec2d)

pcd_seam = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gs186_seam_pcdef',(#{seam_line2d.eid}),#{prc.eid})"
)
# PCURVE on SPHERICAL_SURFACE with the wrong V-range parametrization
pc_seam = f._emit_raw(f"PCURVE('gs186_seam_pc',#{sphere.eid},#{pcd_seam.eid})")
sc_seam = f._emit_raw(
    f"SURFACE_CURVE('gs186_seam_sc',#{seam_line3.eid},(#{pc_seam.eid}),.PCURVE_S1.)"
)
e_seam  = f._emit_raw(
    f"EDGE_CURVE('gs186_seam',#{v_south.eid},#{v_north.eid},#{sc_seam.eid},.T.)"
)

# ── Equatorial arc: from south pole approach to north pole approach ───────────
# Half-circle arc at U=0 sweeping from south pole to north pole through (5,0,0)
# 3D: circle of radius 5 in the XZ plane, centered at origin
equator_plc_o = f.cartesian_point((0.0, 0.0, 0.0))
equator_plc_z = f.direction((0.0, 1.0, 0.0))   # normal to XZ plane
equator_plc_x = f.direction((1.0, 0.0, 0.0))
equator_ax    = f.axis2_placement_3d(equator_plc_o, equator_plc_z, equator_plc_x)
equator_circ3 = f._emit_raw(f"CIRCLE('gs186_eq_arc',#{equator_ax.eid},5.0)")

# 2D pcurve: straight line from (π, 0) to (π, π) on the sphere in defect V-coords
# (U=π meridian, V from 0 to π)
eq_p2d_start = f.cartesian_point((PI, 0.0))
eq_dir2d     = f.direction((0.0, 1.0))
eq_vec2d     = f.vector(eq_dir2d, PI)
eq_line2d    = f.line(eq_p2d_start, eq_vec2d)
pcd_eq = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gs186_eq_pcdef',(#{eq_line2d.eid}),#{prc.eid})"
)
pc_eq  = f._emit_raw(f"PCURVE('gs186_eq_pc',#{sphere.eid},#{pcd_eq.eid})")
sc_eq  = f._emit_raw(
    f"SURFACE_CURVE('gs186_eq_sc',#{equator_circ3.eid},(#{pc_eq.eid}),.PCURVE_S1.)"
)
e_eq   = f._emit_raw(
    f"EDGE_CURVE('gs186_eq',#{v_south.eid},#{v_north.eid},#{sc_eq.eid},.T.)"
)

# ── EDGE_LOOP: two oriented edges forming a closed loop ───────────────────────
# Seam forward (south→north), then back-arc reversed (north→south)
oe_seam_fwd = f.oriented_edge(e_seam, True)
oe_eq_rev   = f.oriented_edge(e_eq,   False)
loop = f.edge_loop([oe_seam_fwd, oe_eq_rev])

# ── SPHERICAL_SURFACE IS the face_geometry — defect pcurve IS wired into face ─
face  = f.advanced_face([f.face_outer_bound(loop)], sphere)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
