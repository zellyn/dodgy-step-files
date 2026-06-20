"""Os012 — Loft produces an EDGE_CURVE with no 3D curve (pcurve-only edge).

Catalog claim: A loft completes but the longitudinal edges between profile vertices
have no 3D curve attached — the EDGE_CURVE's edge_geometry slot is null ('$').
Downstream consumers need explicit 3D curves.

Mechanism IS a GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a PLANE.  The
FACE_OUTER_BOUND references an EDGE_LOOP that includes an EDGE_CURVE where the
edge_geometry field is '$' (null), representing a pcurve-only edge with no 3D
curve.  OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'EDGE_CURVE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os012",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on a PLANE; "
        "FACE_OUTER_BOUND references EDGE_LOOP; "
        "one EDGE_CURVE has edge_geometry='$' (null) — pcurve-only, no 3D curve; "
        "loft Null3DCurve defect: BRepOffsetAPI_ThruSections omits 3D curve on "
        "longitudinal edge; GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Plane surface ─────────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Four corner vertices ──────────────────────────────────────────────────────
p0 = f.cartesian_point((0.0,  0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 8.0, 0.0))
p3 = f.cartesian_point(( 0.0, 8.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# ── Edge 0: bottom line v0→v1 (normal 3D curve) ──────────────────────────────
l0  = f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
ec0 = f.edge_curve(v0, v1, l0, True, name="e0_bottom")

# ── Edge 1: right line v1→v2 (normal 3D curve) ───────────────────────────────
l1  = f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 8.0))
ec1 = f.edge_curve(v1, v2, l1, True, name="e1_right")

# ── Edge 2: pcurve-only EDGE_CURVE v2→v3 — edge_geometry = '$' ───────────────
# This is the defect: null 3D curve slot.  Represents a loft longitudinal edge
# where the algorithm failed to synthesize a 3D curve.
ec2 = f._emit_raw(
    f"EDGE_CURVE('pcurve_only_edge',#{v2.eid},#{v3.eid},$,.T.)"
)  # EDGE_CURVE — byte assertion ✓

# ── Edge 3: left line v3→v0 (normal 3D curve) ────────────────────────────────
l3  = f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 8.0))
ec3 = f.edge_curve(v3, v0, l3, True, name="e3_left")

# ── EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE ─────────────────────────────
loop = f.edge_loop([
    f.oriented_edge(ec0, True),
    f.oriented_edge(ec1, True),
    f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)"),
    f.oriented_edge(ec3, True),
])
fob = f.face_outer_bound(loop)
af  = f.advanced_face([fob], plane)

# ── GEOMETRIC_CURVE_SET IS the model entity ───────────────────────────────────
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os012.stp")
