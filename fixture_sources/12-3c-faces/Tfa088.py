"""Tfa088 — ShapeFix_Face.FixAddNaturalBound: sphere natural boundary.

Catalog claim: Full-sphere face (complete spherical surface) requesting natural
boundary correction. The code attempts to construct a single-edge bound when a
"no-boundary" representation should be used. Sphere radius 5.0 centered at origin.

Mechanism: CLOSED_SHELL containing a single ADVANCED_FACE on a SPHERICAL_SURFACE
of radius 5.0, with a minimal outer bound (a degenerate point-circle at the
north pole). FixAddNaturalBound for a full sphere should produce a proper
two-parameter boundary but instead constructs a single-edge loop, triggering the
defect. Companion flat cap closes the shell to produce a valid CLOSED_SHELL.

Byte assertions:
  - contains(b'SPHERICAL_SURFACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(6) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa088",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on SPHERICAL_SURFACE radius=5.0 at origin; "
        "outer FACE_OUTER_BOUND is a single-edge circle at equator (latitude 0); "
        "FixAddNaturalBound for full sphere: attempts single-edge bound construction "
        "instead of 'no-boundary' representation for complete sphere; "
        "natural boundary for full sphere should span entire parameter domain; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

R = 5.0

# ── SPHERICAL_SURFACE at origin, radius 5.0 ──────────────────────────────────
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_ax   = f.direction((0.0, 0.0, 1.0))
sph_ref  = f.direction((1.0, 0.0, 0.0))
sph_plc  = f.axis2_placement_3d(sph_orig, sph_ax, sph_ref)
sphere   = f.spherical_surface(sph_plc, R)

# ── Equatorial circle as outer bound (single closed edge) ────────────────────
# Equator: z=0 plane, radius 5.0; seam point at (5,0,0)
eq_seam_pt  = f.cartesian_point((R, 0.0, 0.0))
v_eq_seam   = f.vertex_point(eq_seam_pt)

eq_ctr  = f.cartesian_point((0.0, 0.0, 0.0))
eq_ax   = f.direction((0.0, 0.0, 1.0))
eq_ref  = f.direction((1.0, 0.0, 0.0))
eq_plc  = f.axis2_placement_3d(eq_ctr, eq_ax, eq_ref)
eq_circ = f.circle(eq_plc, R)

# Closed circle: start == end
eq_edge = f.edge_curve(v_eq_seam, v_eq_seam, eq_circ)
eq_loop = f.edge_loop([f.oriented_edge(eq_edge, True)])
eq_fob  = f.face_outer_bound(eq_loop)

# ADVANCED_FACE on sphere with equatorial outer bound
face_sphere = f.advanced_face([eq_fob], sphere)

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face_sphere])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa088.stp")
