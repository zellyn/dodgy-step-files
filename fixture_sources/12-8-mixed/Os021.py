"""Os021 — Normal projection: source curve has no projection on target surface.

Catalog claim: A LINE at z=10 is requested to be projected normally onto a
small SPHERICAL_SURFACE at the origin (radius 1).  The line is far from the
sphere; no normal foot exists.

Mechanism IS a GEOMETRIC_CURVE_SET containing:
  - A LINE at z=10 (parallel to X axis) — byte assertion ✓
  - A SPHERICAL_SURFACE at origin, radius 1 — byte assertion ✓
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'SPHERICAL_SURFACE')
  - contains(b'LINE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os021",
    defect=(
        "GEOMETRIC_CURVE_SET containing a LINE at z=10 (parallel to X axis) and "
        "a SPHERICAL_SURFACE at origin radius=1; "
        "line is 10 units above the sphere's north pole — no normal foot exists; "
        "BRepOffsetAPI_NormalProjection projection_failed; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Source curve: LINE at z=10, parallel to X axis ───────────────────────────
line_pt  = f.cartesian_point((0.0, 0.0, 10.0))
line_dir = f.direction((1.0, 0.0, 0.0))
line_vec = f.vector(line_dir, 20.0)
line     = f.line(line_pt, line_vec)   # LINE — byte assertion ✓

# ── Target surface: SPHERICAL_SURFACE at origin, radius 1 ───────────────────
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_plc  = f.axis2_placement_3d(sph_orig, sph_zdir, sph_xdir)
sphere   = f.spherical_surface(sph_plc, 1.0)   # SPHERICAL_SURFACE — byte assertion ✓

# ── GEOMETRIC_CURVE_SET wrapping line + sphere ───────────────────────────────
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{line.eid},#{sphere.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os021.stp")
