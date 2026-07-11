"""P013 — AP203-claimed file uses AP214/AP242-only entities.

Catalog claim: AP203 output emits entities SEAM_CURVE, SURFACE_CURVE, PCURVE
not in AP203's defined entity set. Strict AP203 readers reject. Implementor
detail of OCCT's "merged AP" approach.

The defect: FILE_SCHEMA declares CONFIG_CONTROL_DESIGN but the DATA section
contains SEAM_CURVE and PCURVE entities — which are AP214/AP242-only. A strict
AP203 reader must reject with a schema-conformance diagnostic; silent
empty result is the bug.

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  contains(b'SEAM_CURVE')
  contains(b'PCURVE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P013",
    defect=(
        "FILE_SCHEMA=CONFIG_CONTROL_DESIGN (AP203) but DATA section contains "
        "SEAM_CURVE and PCURVE — AP214/AP242-only entities not in AP203 entity set; "
        "strict AP203 readers must reject with schema-conformance diagnostic; "
        "OCCT silently accepts with empty result — must reject or diagnose; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# Minimal geometry: a single point so that readers that somehow accept
# the schema still yield no solid.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# ── SEAM_CURVE + PCURVE defect entities ───────────────────────────────────────
# These are AP214/AP242-only; their presence in an AP203-claimed file is the
# schema-conformance violation.

# A simple line as the 3D curve for SURFACE_CURVE.
seam_dir = f._emit_raw("DIRECTION('seam_dir',(1.0,0.0,0.0))")
seam_vec = f._emit_raw(f"VECTOR('',#{seam_dir.eid},1.0)")
seam_start = f._emit_raw("CARTESIAN_POINT('seam_start',(0.0,0.0,0.0))")
seam_line = f._emit_raw(f"LINE('',#{seam_start.eid},#{seam_vec.eid})")

# A 2D point and direction for the PCURVE definition.
pcurve_origin = f._emit_raw("CARTESIAN_POINT('pcurve_origin',(0.0,0.0))")
pcurve_dir = f._emit_raw("DIRECTION('pcurve_dir',(1.0,0.0))")
pcurve_vec = f._emit_raw(f"VECTOR('',#{pcurve_dir.eid},1.0)")
pcurve_line = f._emit_raw(
    f"LINE('',#{pcurve_origin.eid},#{pcurve_vec.eid})"
)

# A minimal surface for the PCURVE definitional placement.
surf_origin = f._emit_raw("CARTESIAN_POINT('surf_origin',(0.0,0.0,0.0))")
surf_z = f._emit_raw("DIRECTION('surf_z',(0.0,0.0,1.0))")
surf_x = f._emit_raw("DIRECTION('surf_x',(1.0,0.0,0.0))")
surf_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('surf_plc',#{surf_origin.eid},#{surf_z.eid},#{surf_x.eid})"
)
surf = f._emit_raw(f"PLANE('seam_plane',#{surf_plc.eid})")

# PCURVE: AP214/AP242-only entity — the key defect entity.
# definitional_representation is a minimal DEFINITIONAL_REPRESENTATION.
def_rep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{pcurve_line.eid}),#9060)"
)
pcurve = f._emit_raw(f"PCURVE('',#{surf.eid},#{def_rep.eid})")

# SEAM_CURVE: AP214/AP242-only entity — the other key defect entity.
# SEAM_CURVE('', 3d_curve, (pcurve_geom,...), .PARAMETER.)
seam_curve = f._emit_raw(
    f"SEAM_CURVE('',#{seam_line.eid},(#{pcurve.eid}),.PARAMETER.)"
)

# ── NAUO scaffolding for §12.6 assembly-presence lint ─────────────────────────
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('SeamCurveComp','SeamCurveComp','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','seam_curve_instance','',#9054,#{sub_pdef.eid},$)"
)

# ── Override FILE_SCHEMA to emit CONFIG_CONTROL_DESIGN (AP203) ────────────────
_original_render = f.render


def _render_with_ap203_schema():
    text = _original_render()
    text = text.replace(
        "AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 4 }",
        "CONFIG_CONTROL_DESIGN",
    )
    return text


f.render = _render_with_ap203_schema  # type: ignore[method-assign]
