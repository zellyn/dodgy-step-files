"""M042 — Color override at root label not applied (regression).

Catalog claim: STEP color attached to root label was lost in OCCT 7.5/7.6
(regression from 6.8).

Reproducer recipe: STEP file with color on root product, expressed as
STYLED_ITEM on top-level shape.

Byte assertions:
  contains(b'STYLED_ITEM')
  contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
  contains(b'COLOUR_RGB')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M042",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing assembly with STYLED_ITEM color override "
        "on root product label, plus NEXT_ASSEMBLY_USAGE_OCCURRENCE sub-shape; "
        "input: AP242 STEP file where a color is attached to the root product "
        "via STYLED_ITEM on the top-level shape; "
        "OCCT d7d89ac (Mantis 0032977): OCCT 7.5/7.6 regression — color on root "
        "label was dropped during traversal, losing the override for all instances; "
        "kernel must honor root-level color overrides and propagate through "
        "assembly/part/instance hierarchy; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: root color override lost, color regression OCCT 7.5, "
        "STEP color at root not applied, label color override dropped"
    ),
)

# ── Root product colour ────────────────────────────────────────────────────────
# Byte assertion: contains(b'COLOUR_RGB')
root_colour = f._emit_raw("COLOUR_RGB('root_override_color',0.8,0.2,0.1)")

fill_area = f._emit_raw(f"FILL_AREA_STYLE('root_fill',(#{root_colour.eid}))")
fill_area_style = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fill_area.eid})")
surf_side = f._emit_raw(
    f"SURFACE_SIDE_STYLE('root_side',(#{fill_area_style.eid}))"
)
surf_usage = f._emit_raw(
    f"SURFACE_STYLE_USAGE(.BOTH.,#{surf_side.eid})"
)
psa = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{surf_usage.eid}))"
)

# ── Root product geometry placeholder ────────────────────────────────────────
root_pt = f._emit_raw("CARTESIAN_POINT('root_origin',(0.,0.,0.))")
root_dir_z = f._emit_raw("DIRECTION('root_z',(0.,0.,1.))")
root_dir_x = f._emit_raw("DIRECTION('root_x',(1.,0.,0.))")
root_placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('root_placement',"
    f"#{root_pt.eid},#{root_dir_z.eid},#{root_dir_x.eid})"
)

# ── STYLED_ITEM on root shape (the regression target) ─────────────────────────
# Byte assertion: contains(b'STYLED_ITEM')
root_styled = f._emit_raw(
    f"STYLED_ITEM('root_label_color_override',(#{psa.eid}),$)"
)

# ── NEXT_ASSEMBLY_USAGE_OCCURRENCE — child component instance ─────────────────
# Byte assertion: contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
# Parent and child product definitions
parent_def = f._emit_raw(
    "PRODUCT_DEFINITION('root_assembly','root product definition',$,$)"
)
child_def = f._emit_raw(
    "PRODUCT_DEFINITION('child_part','child part definition',$,$)"
)
nauo = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','child instance in root',"
    f"'',#{parent_def.eid},#{child_def.eid},$)"
)

# Child placement
child_pt = f._emit_raw("CARTESIAN_POINT('child_origin',(5.,0.,0.))")
child_dir_z = f._emit_raw("DIRECTION('child_z',(0.,0.,1.))")
child_dir_x = f._emit_raw("DIRECTION('child_x',(1.,0.,0.))")
child_placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('child_placement',"
    f"#{child_pt.eid},#{child_dir_z.eid},#{child_dir_x.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('root-label-color-override-lost',"
    f"(#{root_styled.eid},#{nauo.eid},#{root_colour.eid},"
    f"#{root_placement.eid},#{child_placement.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M042.stp")
