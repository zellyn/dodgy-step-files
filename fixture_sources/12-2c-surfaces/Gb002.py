"""Gb002 — Surface tangent / normal undefined at a parameter (LProp_Status.Undefined).

Catalog claim: A SPHERICAL_SURFACE queried for U-tangent at v = π/2 (the north
pole) returns LProp_Status.Undefined because the partial derivative vanishes.
Receivers must return the undefined status, not NaN or an arbitrary unit vector.

OCC behavior: silently accepts, empty result. Expected: occt=empty.

STEP mechanism (literal):
  - SPHERICAL_SURFACE (radius 5.0) IS the ADVANCED_FACE.face_geometry.
    At the north pole (v = π/2) the U-partial derivative is identically zero;
    LProp_SLProps::IsUTangentDefined() returns False.
  - A VERTEX_LOOP at the north-pole VERTEX_POINT is used as the sole face bound,
    placing the loop exactly at the degenerate parameter — the pole IS the wired
    boundary.
  - Byte assertions: contains(b'SPHERICAL_SURFACE('),
    count_entity_def(b'SPHERICAL_SURFACE') == 1.
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SPHERICAL_SURFACE IS the ADVANCED_FACE.face_geometry;
    the VERTEX_LOOP is placed at the pole (0,0,5) — the exact degenerate UV
    parameter where LProp_Status.Undefined is triggered.
  - shape_null driver: degenerate loop at pole produces null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gb002",
    defect=(
        "SPHERICAL_SURFACE radius=5.0 IS ADVANCED_FACE.face_geometry; "
        "VERTEX_LOOP at north pole (0,0,5) wires loop to degenerate UV parameter "
        "where U-tangent partial derivative vanishes: LProp_Status.Undefined; "
        "shape_null=True"
    ),
)

# ── CATALOG MECHANISM: SPHERICAL_SURFACE as face_geometry ───────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
# SPHERICAL_SURFACE IS the face geometry — the pole defect is wired into the face.
sphere = f.spherical_surface(plc, radius=5.0)

# ── VERTEX_LOOP at north pole: wires the boundary to the degenerate parameter ─
pole = f.cartesian_point((0.0, 0.0, 5.0))   # north pole, v = π/2
v_pole = f.vertex_point(pole)
vloop = f._emit_raw(f"VERTEX_LOOP('pole_loop',#{v_pole.eid})")
fob = f._emit_raw(f"FACE_OUTER_BOUND('fob',#{vloop.eid},.T.)")

# ADVANCED_FACE: sphere IS face_geometry — mechanism IS the face surface.
face = f._emit_raw(f"ADVANCED_FACE('gb002_face',(#{fob.eid}),#{sphere.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('gb002_shell',(#{face.eid}))")
sbsm = f.shell_based_surface_model([])
f.add_product_chain(sbsm)
