"""Gs185 — CONICAL_SURFACE EDGE_LOOP incorrectly trimmed — lateral face absent.

Catalog claim: STEP file with a CLOSED_SHELL containing two ADVANCED_FACEs:
(a) PLANE base circle and (b) CONICAL_SURFACE lateral surface, where the
EDGE_LOOP defining the CONICAL_SURFACE's boundary incorrectly clips the upper
extent to z ≈ 0.15 mm above the base (instead of the apex at z ≈ 76.2 mm),
making the lateral face extent effectively zero.

The CONICAL_SURFACE has semi_angle ≈ 0.165 rad and nominal height 76.2 mm.
The top edge of the lateral face references a vertex at z = 0.15 instead of
the apex — upper trim collapses the cone surface to near-zero height.

Source: https://discourse.mcneel.com/t/step-import-issue-conical-surface-interpreted-as-a-circle/219575
(Rhino RH-96071: cone imports as a flat disk; lateral face absent/degenerate)

OCCT behavior: may silently accept the near-degenerate shape with shape(1)
(OCCT's healing tolerates tiny-extent faces), or reject with shape(0)/error.

Byte assertions:
  contains(b'CONICAL_SURFACE')
  contains(b'EDGE_LOOP')
Tier-3: n_faces_total == 2
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs185",
    defect=(
        "CONICAL_SURFACE (semi_angle=0.165 rad, height 76.2 mm) IS ADVANCED_FACE.face_geometry; "
        "EDGE_LOOP upper trim vertex at z=0.15 instead of z=76.2 collapses lateral extent to ~0; "
        "cone lateral face absent/degenerate (Rhino RH-96071); "
        "CLOSED_SHELL IS model entity — OCC may yield shape(1) or shape(0)"
    ),
)

# ── Parameters from the Rhino bug report ─────────────────────────────────────
# Base radius: 12.7 mm (from cone geometry matching the report's unit scale)
# Semi-angle: 0.165 rad ≈ 9.45°
# Nominal apex height: base_radius / tan(semi_angle) ≈ 76.2 mm
# Defect: upper trim vertex placed at z = 0.15 instead of z = 76.2
SEMI_ANGLE = 0.165          # radians
BASE_RADIUS = 12.7          # mm
NOMINAL_HEIGHT = BASE_RADIUS / math.tan(SEMI_ANGLE)  # ≈ 76.2 mm
DEFECT_HEIGHT  = 0.15       # mm — the incorrectly-trimmed upper edge height

# Radius of cone at the defect trim height:
# r(z) = base_radius - z * tan(semi_angle) for a cone narrowing toward apex
DEFECT_RADIUS = BASE_RADIUS - DEFECT_HEIGHT * math.tan(SEMI_ANGLE)
# ≈ 12.7 - 0.15 * 0.166 ≈ 12.675 mm  (nearly equal to base — minimal lateral extent)

# ── CONICAL_SURFACE ──────────────────────────────────────────────────────────
# Apex at z = NOMINAL_HEIGHT; axis pointing -Z so cone opens downward toward base
apex_z = NOMINAL_HEIGHT
cone_orig = f.cartesian_point((0.0, 0.0, apex_z))
cone_zdir = f.direction((0.0, 0.0, -1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_plc  = f.axis2_placement_3d(cone_orig, cone_zdir, cone_xdir)
# radius=0 at apex, semi_angle opens out
cone_surf = f.conical_surface(cone_plc, radius=0.0, semi_angle=SEMI_ANGLE)

# ── PLANE base cap ───────────────────────────────────────────────────────────
base_orig = f.cartesian_point((0.0, 0.0, 0.0))
base_zdir = f.direction((0.0, 0.0, -1.0))
base_xdir = f.direction((1.0, 0.0, 0.0))
base_plc  = f.axis2_placement_3d(base_orig, base_zdir, base_xdir)
base_plane = f.plane(base_plc)

# ── Base circle edge (radius = BASE_RADIUS at z=0) ───────────────────────────
base_circle_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
base_circle = f._emit_raw(f"CIRCLE('gs185_base',#{base_circle_plc.eid},{BASE_RADIUS})")
v_base = f.vertex_point(f.cartesian_point((BASE_RADIUS, 0.0, 0.0)))
e_base = f._emit_raw(
    f"EDGE_CURVE('gs185_base_circle',#{v_base.eid},#{v_base.eid},#{base_circle.eid},.T.)"
)

# ── DEFECT: Upper trim circle at z = DEFECT_HEIGHT (0.15 mm above base) ──────
# This is the incorrectly-trimmed upper edge — should be at z ≈ 76.2 mm (apex)
# but is instead at z = 0.15, making the lateral face extent ~0.
defect_circle_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, DEFECT_HEIGHT)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
defect_circle = f._emit_raw(
    f"CIRCLE('gs185_defect_top',#{defect_circle_plc.eid},{DEFECT_RADIUS})"
)
v_top = f.vertex_point(f.cartesian_point((DEFECT_RADIUS, 0.0, DEFECT_HEIGHT)))
e_top = f._emit_raw(
    f"EDGE_CURVE('gs185_top_circle',#{v_top.eid},#{v_top.eid},#{defect_circle.eid},.T.)"
)

# ── Base face (disk) — valid ──────────────────────────────────────────────────
base_loop = f.edge_loop([f.oriented_edge(e_base, True)])
base_fob  = f.face_outer_bound(base_loop)
base_face = f.advanced_face([base_fob], base_plane)

# ── Cone lateral face — defect: upper bound at z=0.15 (nearly zero height) ───
# EDGE_LOOP references both the base circle (reversed, as inner bound) and the
# defect top circle; the cone face extends only 0.15 mm in height instead of 76.2
cone_top_loop  = f.edge_loop([f.oriented_edge(e_top, True)])
cone_base_loop = f.edge_loop([f.oriented_edge(e_base, False)])
cone_fob = f.face_outer_bound(cone_base_loop)
cone_fb  = f._emit_raw(f"FACE_BOUND('',#{cone_top_loop.eid},.T.)")
cone_face = f._emit_raw(
    f"ADVANCED_FACE('gs185_cone_lateral',(#{cone_fob.eid},#{cone_fb.eid}),#{cone_surf.eid},.T.)"
)

# ── CLOSED_SHELL and MANIFOLD_SOLID_BREP ─────────────────────────────────────
all_faces = [cone_face, base_face]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('gs185_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('gs185_solid',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")
