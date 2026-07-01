"""Gs189 — SPHERICAL_SURFACE hemispherical cap with zero-radius CIRCLE EDGE at pole.

Catalog claim: STEP file with a MANIFOLD_SOLID_BREP containing a hemispherical
cap face: a SPHERICAL_SURFACE ADVANCED_FACE with a single FACE_OUTER_BOUND
EDGE_LOOP containing one ORIENTED_EDGE whose basis is a CIRCLE with radius=0.0
and centre at the sphere's north pole; edge_start and edge_end are the same
VERTEX_POINT entity (self-referential degenerate loop).

The solid also includes a planar equatorial ADVANCED_FACE (PLANE cap at z=0).

Source: Fusion 360 community — hemisphere STEP export (B4 wave-6 DEF-U).

Mechanism: CIRCLE with radius=0.0 IS the basis curve of the EDGE_CURVE on the
polar ADVANCED_FACE; degenerate zero-radius circle at pole IS wired into
face topology via EDGE_LOOP. Readers should either reject the zero-radius
CIRCLE as degenerate, or treat the apex as a VERTEX_LOOP.

Byte assertions:
  contains(b'SPHERICAL_SURFACE')
  contains(b'CIRCLE')
  count_entity_def(b'ADVANCED_FACE') == 2

Tier-3 assertion: n_faces_total == 2
Expected: occt=shape(1)/shape(1) or shape(0) depending on healing
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs189",
    defect=(
        "SPHERICAL_SURFACE (radius=5) IS hemispherical-cap ADVANCED_FACE.face_geometry; "
        "EDGE_LOOP on polar face contains one ORIENTED_EDGE whose basis IS a CIRCLE "
        "with radius=0.0 centred at north pole (0,0,5); edge_start==edge_end (same VERTEX_POINT); "
        "degenerate zero-radius pole circle (Fusion 360 DEF-U); "
        "OCCT may accept with null triangulation on polar cap or reject as degenerate"
    ),
)

R = 5.0  # sphere radius

# ── SPHERICAL_SURFACE (radius 5, centered at origin) ─────────────────────────
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_ax   = f.axis2_placement_3d(sph_orig, sph_zdir, sph_xdir)
sphere   = f.spherical_surface(sph_ax, R, name="gs189_sphere")

# ── Equatorial circle (radius=R at z=0) — shared edge ────────────────────────
eq_orig = f.cartesian_point((0.0, 0.0, 0.0))
eq_zdir = f.direction((0.0, 0.0, 1.0))
eq_xdir = f.direction((1.0, 0.0, 0.0))
eq_ax   = f.axis2_placement_3d(eq_orig, eq_zdir, eq_xdir)
eq_circ = f.circle(eq_ax, R, name="gs189_eq")

# Equatorial vertex (full circle: same vertex for start and end)
v_eq = f.vertex_point(f.cartesian_point((R, 0.0, 0.0)))
e_eq = f._emit_raw(
    f"EDGE_CURVE('gs189_equator',#{v_eq.eid},#{v_eq.eid},#{eq_circ.eid},.T.)"
)

# ── DEFECT: zero-radius CIRCLE at north pole ──────────────────────────────────
# A CIRCLE with radius=0.0 centred at the north pole (0, 0, R).
# Both edge_start and edge_end reference the same VERTEX_POINT.
north_pt = f.cartesian_point((0.0, 0.0, R))
v_north  = f.vertex_point(north_pt)

pole_ax_orig = f.cartesian_point((0.0, 0.0, R))
pole_ax_zdir = f.direction((0.0, 0.0, 1.0))
pole_ax_xdir = f.direction((1.0, 0.0, 0.0))
pole_ax      = f.axis2_placement_3d(pole_ax_orig, pole_ax_zdir, pole_ax_xdir)

# DEFECT: radius=0.0 — degenerate zero-radius circle at pole
pole_circle = f._emit_raw(
    f"CIRCLE('gs189_pole_circle',#{pole_ax.eid},0.0)"
)
# Self-referential: edge_start == edge_end == v_north
e_pole = f._emit_raw(
    f"EDGE_CURVE('gs189_pole_edge',#{v_north.eid},#{v_north.eid},#{pole_circle.eid},.T.)"
)

# ── Hemispherical cap face (SPHERICAL_SURFACE) ────────────────────────────────
# Boundary: equatorial circle (as inner bound going CW = reversed, since sphere
# outward normal points away from center).
# The cap face spans from equator up to the north pole.
# Outer bound: the equatorial edge loop (traversed to match face normal)
# plus a degenerate pole loop.
# For simplicity, use one FACE_OUTER_BOUND with the equatorial edge,
# and a FACE_BOUND for the pole (degenerate).
eq_loop  = f.edge_loop([f.oriented_edge(e_eq, True)])
eq_fob   = f.face_outer_bound(eq_loop)

# Pole degenerate loop (zero-radius circle, self-loop)
pole_loop = f.edge_loop([f.oriented_edge(e_pole, True)])
pole_fb   = f._emit_raw(f"FACE_BOUND('gs189_pole_bound',#{pole_loop.eid},.T.)")

# SPHERICAL_SURFACE IS the face_geometry — defect zero-radius edge IS wired in
cap_face = f._emit_raw(
    f"ADVANCED_FACE('gs189_cap',(#{eq_fob.eid},#{pole_fb.eid}),#{sphere.eid},.T.)"
)

# ── Planar equatorial disk (base cap at z=0) ──────────────────────────────────
base_orig = f.cartesian_point((0.0, 0.0, 0.0))
base_zdir = f.direction((0.0, 0.0, -1.0))
base_xdir = f.direction((1.0, 0.0, 0.0))
base_plc  = f.axis2_placement_3d(base_orig, base_zdir, base_xdir)
base_plane = f.plane(base_plc)

# Base uses the equatorial circle edge reversed (for correct outward normal)
base_loop = f.edge_loop([f.oriented_edge(e_eq, False)])
base_fob  = f.face_outer_bound(base_loop)
base_face = f.advanced_face([base_fob], base_plane)

# ── CLOSED_SHELL and MANIFOLD_SOLID_BREP ─────────────────────────────────────
all_faces = [cap_face, base_face]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('gs189_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('gs189_solid',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")
