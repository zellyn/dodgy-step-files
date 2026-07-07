"""P010 — Standalone AXIS2_PLACEMENT_3D entities silently dropped.

Catalog claim: standalone AXIS_PLACEMENT / AXIS2_PLACEMENT_3D entities used
as datum/feature axes (often referenced from PRESENTATION_LAYER_ASSIGNMENT)
are silently dropped on import; no warning. Useful design-intent information
is lost.

The defect: STEP file with multiple AXIS2_PLACEMENT_3D entities referenced from
PRESENTATION_LAYER_ASSIGNMENT but not connected to any BREP topology.
A robust kernel must either ignore-with-warning, or surface as construction
objects; silent drop is the bug.

Byte assertions:
  count_entity_def(b'PRESENTATION_LAYER_ASSIGNMENT') >= 1
  count_entity_def(b'AXIS2_PLACEMENT_3D') >= 2

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P010",
    defect=(
        "Multiple standalone AXIS2_PLACEMENT_3D entities referenced from "
        "PRESENTATION_LAYER_ASSIGNMENT as datum/feature axes; "
        "not connected to any BREP topology; silently dropped on import "
        "with no warning — design-intent datum frames lost; "
        "kernel must ignore-with-warning or surface as construction objects; "
        "NEXT_ASSEMBLY_USAGE_OCCURRENCE scaffolding for §12.6 lint; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── Minimal geometry payload ──────────────────────────────────────────────────
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin_pt.eid}))")
f.add_product_chain(gcs)

# ── Standalone AXIS2_PLACEMENT_3D datum axes (the defect entities) ────────────
# Axis A: feature axis at origin, pointing along Z (e.g., a bore axis).
axis_a_orig = f._emit_raw("CARTESIAN_POINT('Axis_A_origin',(0.0,0.0,0.0))")
axis_a_zdir = f._emit_raw("DIRECTION('Axis_A_z',(0.0,0.0,1.0))")
axis_a_xdir = f._emit_raw("DIRECTION('Axis_A_x',(1.0,0.0,0.0))")
axis_a = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('Axis_A',#{axis_a_orig.eid},#{axis_a_zdir.eid},#{axis_a_xdir.eid})"
)

# Axis B: datum feature axis at (50,0,0), pointing along Y (e.g., a shaft axis).
axis_b_orig = f._emit_raw("CARTESIAN_POINT('Axis_B_origin',(50.0,0.0,0.0))")
axis_b_zdir = f._emit_raw("DIRECTION('Axis_B_z',(0.0,1.0,0.0))")
axis_b_xdir = f._emit_raw("DIRECTION('Axis_B_x',(1.0,0.0,0.0))")
axis_b = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('Axis_B',#{axis_b_orig.eid},#{axis_b_zdir.eid},#{axis_b_xdir.eid})"
)

# Axis C: a third standalone datum at (25,25,0).
axis_c_orig = f._emit_raw("CARTESIAN_POINT('Axis_C_origin',(25.0,25.0,0.0))")
axis_c_zdir = f._emit_raw("DIRECTION('Axis_C_z',(0.0,0.0,1.0))")
axis_c_xdir = f._emit_raw("DIRECTION('Axis_C_x',(0.0,1.0,0.0))")
axis_c = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('Axis_C',#{axis_c_orig.eid},#{axis_c_zdir.eid},#{axis_c_xdir.eid})"
)

# ── PRESENTATION_LAYER_ASSIGNMENT referencing the datum axes ─────────────────
# This is how many CAD tools embed standalone axes in layers: they appear in
# a layer assignment but are not topology-connected.
f._emit_raw(
    f"PRESENTATION_LAYER_ASSIGNMENT('datum_axes','Datum Axes',"
    f"(#{axis_a.eid},#{axis_b.eid},#{axis_c.eid}))"
)

# ── NAUO scaffolding for §12.6 assembly-presence lint ────────────────────────
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('DatumAxes','DatumAxes','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','datum_axis_instance','',#9054,#{sub_pdef.eid},$)"
)
