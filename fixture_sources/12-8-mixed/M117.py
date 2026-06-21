"""M117 — AP209 anisotropic material with missing tensor components.

Catalog claim: An ANISOTROPIC_LINEAR_ELASTICITY card declares 9 of the 21
independent components of the elasticity tensor, leaving the rest as $.
The downstream solver either substitutes zeros (yielding a non-positive
definite matrix) or treats as orthotropic (different physics).

Reproducer recipe: An ANISOTROPIC_LINEAR_ELASTICITY (or analogous
multi-attribute material entity) with several mandatory tensor components
set to $.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'ANISOTROPIC_LINEAR_ELASTICITY')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M117",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 ANISOTROPIC_LINEAR_ELASTICITY material card "
        "with only 9 of 21 independent elasticity tensor components declared, the rest as $; "
        "input: AP209 STEP file where an ANISOTROPIC_LINEAR_ELASTICITY entity carries the "
        "full 21-component upper-triangle of the Voigt-notation elasticity matrix but only "
        "9 components are given explicit values; the remaining 12 components are set to $ "
        "(undefined/missing); "
        "per ISO 10303-209 §8 anisotropic_linear_elasticity tensor symmetry-class invariants, "
        "all 21 independent stiffness components are mandatory for a fully anisotropic material; "
        "a downstream solver that substitutes zero for $ components receives a stiffness matrix "
        "that is not positive-definite, causing the LU or Cholesky factorization to fail; "
        "a solver that infers orthotropy from the declared components applies different physics "
        "than the exporter intended; "
        "kernel must reject as malformed, or zero-fill and warn with explicit symmetry-class "
        "downgrade diagnostic; "
        "synonyms: AP209 incomplete material card, elasticity tensor missing values, "
        "anisotropic stiffness components missing, AP209 material tensor sparse, "
        "AP209 material tensor incomplete, FEM elasticity matrix not positive-definite, "
        "anisotropic card missing components"
    ),
    schema="AP242",
)


def _render_m117() -> str:
    """Render AP209 file with ANISOTROPIC_LINEAR_ELASTICITY with 12 of 21 components as $.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100      CARTESIAN_POINT for a representative node
      #110      NODE entity
      #300      NODE_GROUP
      #310      FEA_MODEL referencing the node group
      #400      ANISOTROPIC_LINEAR_ELASTICITY — 9 values given, 12 as $ — DEFECT
      #410      MATERIAL_PROPERTY_REPRESENTATION linking material to model
      #500      GEOMETRIC_CURVE_SET model entity
      #600+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M117: AP209 anisotropic material with missing tensor components */")
    lines.append("/* DEFECT: ANISOTROPIC_LINEAR_ELASTICITY — only 9 of 21 components given */")
    lines.append("/* Remaining 12 components are $ (undefined); solver gets non-PD matrix */")
    lines.append("/* Per AP209 §8 all 21 independent tensor components are mandatory */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'ANISOTROPIC_LINEAR_ELASTICITY') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M117: AP209 anisotropic material elasticity tensor incomplete'),'2;1');")
    lines.append("FILE_NAME('M117.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("FILE_SCHEMA(('STRUCTURAL_ANALYSIS_DESIGN { 1 0 10303 209 1 0 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('structural_analysis_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'structural_analysis_design',2001,#1);")
    lines.append("/* Standard unit context */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('fea','3D'));")
    lines.append("/* Single representative node for the material model */")
    lines.append("#100=CARTESIAN_POINT('origin',(0.0,0.0,0.0));")
    lines.append("#110=NODE('mat_node',(#100),$);")
    lines.append("#300=NODE_GROUP('mat_nodes',(#110),$);")
    lines.append("#310=FEA_MODEL('aniso_model',$,'',(#300),(),());")
    lines.append("/* Byte assertion: contains(b'ANISOTROPIC_LINEAR_ELASTICITY') */")
    lines.append("/* DEFECT: 21-component Voigt upper triangle; only 9 given, 12 are $ (undefined) */")
    lines.append("/* Row 1 (C11,C12,C13,C14,C15,C16): C11=210000 given; C12-C16 all $ */")
    lines.append("/* Row 2 (C22,C23,C24,C25,C26): C22=210000 given; C23-C26 all $ */")
    lines.append("/* Row 3 (C33,C34,C35,C36): C33=210000 given; C34-C36 all $ */")
    lines.append("/* Row 4 (C44,C45,C46): C44=80769 given; C45,C46 are $ */")
    lines.append("/* Row 5 (C55,C56): C55=80769 given; C56 is $ */")
    lines.append("/* Row 6 (C66): C66=80769 given */")
    lines.append("/* 9 values given (diagonal + partial), 12 off-diagonal couplings are $ */")
    lines.append("/* A fully anisotropic material requires all 21 components explicitly */")
    lines.append("#400=ANISOTROPIC_LINEAR_ELASTICITY('aniso_carbon_fibre',")
    lines.append("  210000.0,$,$,$,$,$,")
    lines.append("  210000.0,$,$,$,$,")
    lines.append("  210000.0,$,$,$,")
    lines.append("  80769.0,$,$,")
    lines.append("  80769.0,$,")
    lines.append("  80769.0);")
    lines.append("/* Material property linking anisotropic stiffness to FEA model */")
    lines.append("#410=MATERIAL_PROPERTY_REPRESENTATION('aniso_mat_prop',#400,#310,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-anisotropic-material-missing-tensor-components',")
    lines.append("  (#110,#310,#400,#410));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M117','M117','M117',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m117(path) -> None:
    Path(path).write_text(_render_m117())


f.render = _render_m117  # type: ignore[method-assign]
f.write = _write_m117    # type: ignore[method-assign]
