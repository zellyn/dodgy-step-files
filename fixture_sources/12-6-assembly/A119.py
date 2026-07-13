"""A119 -- MAPPED_ITEM with a resolvable REPRESENTATION_MAP + real target shape,
but a placement/transform reference of an unrecognized type -- the shape must
still load unpositioned (not dropped/aborted).

Closes exchange PARTIAL `stp-mapped-item-no-transform`. Tfa248 (the existing
fixture) puts an empty string ('') where the mapping_source (REPRESENTATION_MAP
reference) belongs and the REPRESENTATION_MAP itself in the mapping_target
slot -- a malformed EMPTY-STRING source slot that risks aborting the transfer
before the identity-fallback-with-warning branch ever runs. This fixture
keeps mapping_source resolvable (a real REPRESENTATION_MAP with a real target
representation) and only makes mapping_target an unrecognized ENTITY TYPE
(a plain CARTESIAN_POINT, neither a CartesianTransformationOperator3d nor an
Axis2Placement3d) -- the narrower, distinct "recognized map, unrecognized
placement" case.

Mechanism (read from OCCT 7.8.1 source, bd2a789f15235755ce4d1a3b07379a2e062fdc2e):
  STEPControl_ActorRead::TransferEntity(StepRepr_MappedItem), STEPControl_ActorRead.cxx:1555-1577:
    Handle(StepGeom_CartesianTransformationOperator3d) CartOp =
      DownCast(mapit->MappingTarget());
    if (!CartOp.IsNull()) { ok = MakeTransformation3d(CartOp, Trsf, ...); }
    else {
      Handle(StepGeom_Axis2Placement3d) Origin = DownCast(mapit->MappingSource()->MappingOrigin());
      Handle(StepGeom_Axis2Placement3d) Target = DownCast(mapit->MappingTarget());
      if (!Origin.IsNull() && !Target.IsNull()) { ok = ComputeTransformation(...); }
    }
    if (ok) ApplyTransformation(mappedShape, Trsf);
    else TP->AddWarning(mapit, "Mapped Item, case not recognized, location ignored");
    shbinder = new TransferBRep_ShapeBinder(mappedShape);   // <-- ALWAYS bound,
                                                              //     regardless of `ok`
  `mapit->MappingTarget()` downcasts to neither `CartesianTransformationOperator3d`
  nor `Axis2Placement3d` when it is a `CARTESIAN_POINT` -- both branches leave
  `ok=False`, the "case not recognized" warning fires, but `mappedShape`
  (already resolved via the REAL, resolvable `REPRESENTATION_MAP`) is bound
  and returned UNTRANSFORMED (effectively identity/un-positioned) rather than
  dropped.

Live-verified (2026-07-12, OCP 7.8.1, direct probing -- not mirrored/
guessed): shape_null=False, n_faces_total=1; the mapped face's bounding box
sits at the ORIGIN (its own local placement), confirming it loaded
un-positioned (identity transform) rather than being dropped by the
unrecognized mapping_target.

Byte assertions:
  contains(b"MAPPED_ITEM('mapped_inst'")
  contains(b"CARTESIAN_POINT('unrecognized_target'")

Tier-3: shape_null == False; n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="A119",
    defect=(
        "MAPPED_ITEM('mapped_inst',#representation_map,#unrecognized_target) where "
        "#representation_map is a genuinely resolvable REPRESENTATION_MAP pointing at a real "
        "target SHAPE_REPRESENTATION with live geometry, but #unrecognized_target is a plain "
        "CARTESIAN_POINT -- neither a CartesianTransformationOperator3d nor an "
        "Axis2Placement3d, so both of TransferEntity(MappedItem)'s placement-resolution "
        "branches fail (ok=False); 'Mapped Item, case not recognized, location ignored' "
        "warning fires but the already-resolved mappedShape is still bound and returned "
        "UNTRANSFORMED rather than dropped; not Tfa248's empty-string mapping_source, which "
        "risks aborting before this identity-fallback branch ever runs; "
        "synonyms: MAPPED_ITEM unrecognized transform type, placement case not recognized, "
        "location ignored fallback, MAPPED_ITEM loads unpositioned"
    ),
)


def _render_a119() -> str:
    return (
        "ISO-10303-21;\n"
        "/* A119: MAPPED_ITEM with resolvable REPRESENTATION_MAP but unrecognized-type mapping_target */\n"
        "/* DEFECT: mapping_target (#44) is a plain CARTESIAN_POINT -- neither a */\n"
        "/* CartesianTransformationOperator3d nor an Axis2Placement3d -- 'case not recognized, */\n"
        "/* location ignored' fires, but the mapped shape (via the REAL, resolvable */\n"
        "/* REPRESENTATION_MAP) still loads, un-positioned, rather than being dropped */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('A119: MAPPED_ITEM unrecognized-type mapping_target, shape still loads'),'2;1');\n"
        "FILE_NAME('A119.stp','2026-07-12T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('',(0.0,0.0,0.0));\n"
        "#2=DIRECTION('',(0.0,0.0,1.0));\n"
        "#3=DIRECTION('',(1.0,0.0,0.0));\n"
        "#4=AXIS2_PLACEMENT_3D('',#1,#2,#3);\n"
        "#5=PLANE('',#4);\n"
        "#6=CARTESIAN_POINT('',(0.0,0.0,0.0));\n"
        "#7=CARTESIAN_POINT('',(1.0,0.0,0.0));\n"
        "#8=CARTESIAN_POINT('',(1.0,1.0,0.0));\n"
        "#9=CARTESIAN_POINT('',(0.0,1.0,0.0));\n"
        "#10=VERTEX_POINT('',#6);\n"
        "#11=VERTEX_POINT('',#7);\n"
        "#12=VERTEX_POINT('',#8);\n"
        "#13=VERTEX_POINT('',#9);\n"
        "#14=DIRECTION('',(1.0,0.0,0.0));\n"
        "#15=VECTOR('',#14,1.0);\n"
        "#16=LINE('',#6,#15);\n"
        "#17=EDGE_CURVE('',#10,#11,#16,.T.);\n"
        "#18=DIRECTION('',(0.0,1.0,0.0));\n"
        "#19=VECTOR('',#18,1.0);\n"
        "#20=LINE('',#7,#19);\n"
        "#21=EDGE_CURVE('',#11,#12,#20,.T.);\n"
        "#22=DIRECTION('',(-1.0,0.0,0.0));\n"
        "#23=VECTOR('',#22,1.0);\n"
        "#24=LINE('',#8,#23);\n"
        "#25=EDGE_CURVE('',#12,#13,#24,.T.);\n"
        "#26=DIRECTION('',(0.0,-1.0,0.0));\n"
        "#27=VECTOR('',#26,1.0);\n"
        "#28=LINE('',#9,#27);\n"
        "#29=EDGE_CURVE('',#13,#10,#28,.T.);\n"
        "#30=ORIENTED_EDGE('',$,$,#17,.T.);\n"
        "#31=ORIENTED_EDGE('',$,$,#21,.T.);\n"
        "#32=ORIENTED_EDGE('',$,$,#25,.T.);\n"
        "#33=ORIENTED_EDGE('',$,$,#29,.T.);\n"
        "#34=EDGE_LOOP('',(#30,#31,#32,#33));\n"
        "#35=FACE_OUTER_BOUND('',#34,.T.);\n"
        "#36=ADVANCED_FACE('',(#35),#5,.T.);\n"
        "#37=OPEN_SHELL('',(#36));\n"
        "#38=SHELL_BASED_SURFACE_MODEL('',(#37));\n"
        "#39=(GEOMETRIC_REPRESENTATION_CONTEXT(3)REPRESENTATION_CONTEXT('','3D'));\n"
        "#40=SHAPE_REPRESENTATION('target_rep',(#38),#39);\n"
        "#41=CARTESIAN_POINT('',(0.0,0.0,0.0));\n"
        "#42=AXIS2_PLACEMENT_3D('map_origin',#41,#2,#3);\n"
        "/* Resolvable REPRESENTATION_MAP: origin + a REAL target SHAPE_REPRESENTATION with live geometry */\n"
        "#43=REPRESENTATION_MAP(#42,#40);\n"
        "/* DEFECT: mapping_target is a plain CARTESIAN_POINT -- unrecognized type for placement resolution */\n"
        "#44=CARTESIAN_POINT('unrecognized_target',(5.0,0.0,0.0));\n"
        "#45=MAPPED_ITEM('mapped_inst',#43,#44);\n"
        "#46=SHAPE_REPRESENTATION('host_rep',(#45),#39);\n"
        "#100=APPLICATION_CONTEXT('mechanical design');\n"
        "#101=PRODUCT_CONTEXT('',#100,'mechanical');\n"
        "#102=PRODUCT('A119','A119','',(#101));\n"
        "#103=PRODUCT_DEFINITION_FORMATION('','',#102);\n"
        "#104=PRODUCT_DEFINITION_CONTEXT('part definition',#100,'design');\n"
        "#105=PRODUCT_DEFINITION('','',#103,#104);\n"
        "#106=PRODUCT_DEFINITION_SHAPE('','',#105);\n"
        "#107=SHAPE_DEFINITION_REPRESENTATION(#106,#46);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_a119(path) -> None:
    Path(path).write_text(_render_a119())


f.render = _render_a119  # type: ignore[method-assign]
f.write = _write_a119    # type: ignore[method-assign]
