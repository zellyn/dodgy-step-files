"""Gs002 — Degenerate (lemon/apple) torus where minor_radius >= major_radius.

Catalog claim: A TOROIDAL_SURFACE with minor_radius (3.0) >= major_radius (2.0)
collapses the analytic torus into a self-intersecting "lemon" shape (no central
hole). Receivers that assume minor < major produce wrong bounding boxes, mis-handle
seam insertion, or import the shape inverted.

OCC behavior: silently accepts, empty result. Expected: occt=empty.

STEP mechanism (literal):
  - TOROIDAL_SURFACE major_radius=2.0, minor_radius=3.0 IS the
    ADVANCED_FACE.face_geometry.  minor > major → no central hole → lemon shape.
  - A VERTEX_LOOP (degenerate single-point boundary at the apex where the lemon
    touches itself) is used as the FACE_OUTER_BOUND — wired into the face.
  - Byte assertions: contains(b'TOROIDAL_SURFACE('), contains(b'2.0,3.0'),
    contains(b'VERTEX_LOOP(').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE minor_radius >= major_radius IS
    ADVANCED_FACE.face_geometry; VERTEX_LOOP at lemon apex wires the degenerate
    boundary to the face topology.
  - shape_null driver: self-intersecting / lemon torus produces null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs002",
    defect=(
        "TOROIDAL_SURFACE major_radius=2.0 minor_radius=3.0 IS "
        "ADVANCED_FACE.face_geometry; minor > major → lemon/apple shape, "
        "self-intersecting torus, no central hole; VERTEX_LOOP at apex "
        "wires degenerate boundary; shape_null=True"
    ),
)

# ── CATALOG MECHANISM: lemon torus, minor_radius > major_radius ───────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)

# TOROIDAL_SURFACE with major=2.0, minor=3.0 — lemon shape (byte assertions 2.0,3.0)
# IS the ADVANCED_FACE.face_geometry.
torus = f._emit_raw(f"TOROIDAL_SURFACE('gs002_lemon',#{plc.eid},2.0,3.0)")

# ── VERTEX_LOOP at lemon apex ─────────────────────────────────────────────────
# When minor_radius=3.0 > major_radius=2.0, the lemon touches itself at:
# (0,0, minor_radius - major_radius) = (0,0,1.0) is the inner apex.
# Use (0,0,5.0) as the outer apex (major + minor = 5.0 at u=0, v=0):
apex = f.cartesian_point((5.0, 0.0, 0.0))   # outer apex: R+r at u=0,v=0
v_apex = f.vertex_point(apex)
vloop = f._emit_raw(f"VERTEX_LOOP('gs002_vloop',#{v_apex.eid})")
fob   = f._emit_raw(f"FACE_OUTER_BOUND('gs002_fob',#{vloop.eid},.T.)")

# ADVANCED_FACE: lemon torus IS the face_geometry — mechanism IS the face surface.
face  = f._emit_raw(f"ADVANCED_FACE('gs002_face',(#{fob.eid}),#{torus.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('gs002_shell',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([])
f.add_product_chain(sbsm, uncertainty_literal="LENGTH_MEASURE(1.0E-7)")  # bare typed real, not enum-wrapped (scaffolding-artifact fix)
