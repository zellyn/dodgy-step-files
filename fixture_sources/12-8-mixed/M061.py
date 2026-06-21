"""M061 — Scaling-factor encoded as non-unit DIRECTION ratios in AXIS2_PLACEMENT_3D.

Catalog claim: A child component's placement transformation includes a non-unit
scale factor encoded as DIRECTION ratios with magnitude != 1.0 (e.g. (2.0,0.0,0.0))
inside an AXIS2_PLACEMENT_3D. The writer drops the scale silently because STEP
placements canonically have no scale and DIRECTION should be normalized.

Reproducer recipe: An assembly where a child's AXIS2_PLACEMENT_3D references
DIRECTION entities with non-unit ratios (e.g. (2.0,0.0,0.0) and (0.0,2.0,0.0))
implicitly encoding scale 2.0.

Byte assertions:
  contains(b'AXIS2_PLACEMENT_3D')
  matches(rb'DIRECTION\(\\'not_unit_length\\',\\(2\\.0,0\\.0,0\\.0\\)\\)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M061",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET in file with AXIS2_PLACEMENT_3D referencing DIRECTION "
        "entities with non-unit magnitude (2.0,0.0,0.0) — hidden scale factor that "
        "STEP writers silently strip on write; "
        "input: AP242 STEP assembly file where a child component's AXIS2_PLACEMENT_3D "
        "uses DIRECTION('not_unit_length',(2.0,0.0,0.0)) and "
        "DIRECTION('not_unit_length',(0.0,2.0,0.0)) implicitly encoding scale 2.0; "
        "STEP placements have no canonical scale attribute; the DIRECTION magnitude "
        "is not a standardised scale encoding but some tools exploit it; "
        "AP242 ISO 10303-42 §4.4 states DIRECTION values should be normalised; "
        "on write, the writer normalises the DIRECTION to unit length and the scale "
        "is silently lost — the exported child appears at the wrong size; "
        "kernel must reject non-unit DIRECTION in AXIS2_PLACEMENT_3D; or bake the "
        "scale factor into child geometry before write; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: scale dropped, AXIS2_PLACEMENT scale lost, "
        "non-unit DIRECTION scale stripped, ITEM_DEFINED_TRANSFORMATION ignored scale"
    ),
)

# ── Child component origin ────────────────────────────────────────────────────
child_origin = f._emit_raw("CARTESIAN_POINT('child_origin',(0.,0.,0.))")

# ── Non-unit DIRECTION ratios encoding a hidden scale of 2.0 ─────────────────
# Byte assertion: matches(rb'DIRECTION\(\'not_unit_length\',\(2\.0,0\.0,0\.0\)\)')
# Magnitude = sqrt(2.0^2 + 0^2 + 0^2) = 2.0; a conformant DIRECTION must be unit.
dir_z_scaled = f._emit_raw(
    "DIRECTION('not_unit_length',(2.0,0.0,0.0))"
)
dir_x_scaled = f._emit_raw(
    "DIRECTION('not_unit_length',(0.0,2.0,0.0))"
)

# ── AXIS2_PLACEMENT_3D with non-unit DIRECTION — the defect ──────────────────
# Byte assertion: contains(b'AXIS2_PLACEMENT_3D')
scaled_placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('scaled_child_placement',"
    f"#{child_origin.eid},#{dir_z_scaled.eid},#{dir_x_scaled.eid})"
)

# ── ITEM_DEFINED_TRANSFORMATION encoding the same implicit scale ───────────────
parent_origin = f._emit_raw("CARTESIAN_POINT('parent_origin',(0.,0.,0.))")
unit_dir_z = f._emit_raw("DIRECTION('z_axis',(0.,0.,1.))")
unit_dir_x = f._emit_raw("DIRECTION('x_axis',(1.,0.,0.))")
parent_placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('parent_placement',"
    f"#{parent_origin.eid},#{unit_dir_z.eid},#{unit_dir_x.eid})"
)
idt = f._emit_raw(
    f"ITEM_DEFINED_TRANSFORMATION('scale2x','implicit scale by 2',"
    f"#{parent_placement.eid},#{scaled_placement.eid})"
)

# ── Simple geometry for the child component ──────────────────────────────────
box_pt1 = f._emit_raw("CARTESIAN_POINT('box_a',(0.,0.,0.))")
box_pt2 = f._emit_raw("CARTESIAN_POINT('box_b',(1.,0.,0.))")
box_pt3 = f._emit_raw("CARTESIAN_POINT('box_c',(0.,1.,0.))")

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('non-unit-direction-encodes-hidden-scale-in-placement',"
    f"(#{scaled_placement.eid},#{dir_z_scaled.eid},#{dir_x_scaled.eid},"
    f"#{idt.eid},#{box_pt1.eid},#{box_pt2.eid},#{box_pt3.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M061.stp")
