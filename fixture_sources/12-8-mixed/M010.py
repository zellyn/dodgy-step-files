"""M010 — Bound vs. unbound supplemental elements (planes, lines).

Catalog claim: NX-style preprocessors emit reference planes as unbounded plane
and centerlines as unbounded line. CATIA-style preprocessors emit bounded
face_surface/edge_curve. Round-tripping fails when a bounded reader receives
an unbounded element with no fallback, or when name-bearing elements lose
their name during the bound→unbound conversion.

Reproducer recipe: Author a constructive_geometry_representation with one named
unbounded plane and one named unbounded line. Reimport into a system that requires
bounded supplemental elements.

Byte assertions:
  contains(b'CONSTRUCTIVE_GEOMETRY_REPRESENTATION')
  contains(b'PLANE')
  contains(b'LINE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M010",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing CONSTRUCTIVE_GEOMETRY_REPRESENTATION "
        "with one named unbounded PLANE and one named unbounded LINE; "
        "NX-style writers emit unbounded PLANE/LINE supplemental elements; "
        "CATIA-style readers require bounded face_surface/edge_curve — round-trip fails; "
        "name-bearing supplemental elements lose their name on bound→unbound conversion; "
        "kernel must heal: auto-generate bounds from model extents on import; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: bound vs unbound supplemental geometry, datum plane unbounded vs bounded, "
        "centerline lost on round-trip, supplemental element type mismatch"
    ),
)

# ── Unbounded PLANE: placement at origin with Z-normal ───────────────────────
# PLANE in STEP is unbounded by definition; it has no boundary in the Part-21 entity.
plane_orig = f.cartesian_point((0.0, 0.0, 0.0))
plane_zdir = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plane_plc  = f.axis2_placement_3d(plane_orig, plane_zdir, plane_xdir)
# Named unbounded plane — the defect: name will be lost on bound→unbound conversion
datum_plane = f._emit_raw(f"PLANE('reference_datum_plane_unbounded',#{plane_plc.eid})")

# ── Unbounded LINE: origin + direction (no bounded edge_curve wrapper) ────────
line_orig = f.cartesian_point((0.0, 0.0, 0.0))
line_dir  = f.direction((1.0, 0.0, 0.0))
line_vec  = f.vector(line_dir, 1.0)
# Named unbounded line — the defect: CATIA readers expect bounded edge_curve
center_line = f._emit_raw(
    f"LINE('centerline_unbounded',#{line_orig.eid},#{line_vec.eid})"
)

# ── CONSTRUCTIVE_GEOMETRY_REPRESENTATION with both supplemental elements ──────
# Byte assertion: contains(b'CONSTRUCTIVE_GEOMETRY_REPRESENTATION')
# No geometric context yet — build the unit context entities first.
# The CGR holds the unbounded supplemental geometry items.

# Unit context for the CGR
length_unit = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
angle_unit  = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
solid_unit  = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc_ent     = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),"
    f"#{length_unit.eid},'distance_accuracy_value','')"
)
geom_ctx_cgr = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_ent.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{length_unit.eid},#{angle_unit.eid},#{solid_unit.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

cgr = f._emit_raw(
    f"CONSTRUCTIVE_GEOMETRY_REPRESENTATION('supplemental_geometry',"
    f"(#{datum_plane.eid},#{center_line.eid}),#{geom_ctx_cgr.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('bound-vs-unbound-supplemental',"
    f"(#{datum_plane.eid},#{center_line.eid},#{cgr.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M010.stp")
