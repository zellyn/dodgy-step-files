"""M011 — Supplemental geometry inadvertently included in part-level GVP.

Catalog claim: Supplemental elements (datum planes, centerlines) may be reported by a
writer as if they were part of the manufactured shape, inflating volume/area/centroid.

Reproducer recipe: Build a part with a CONSTRUCTIVE_GEOMETRY_REPRESENTATION containing
an unbounded plane and a centerline. Compute and emit the volume/area/centroid GVP at
part level by accidentally summing the supplemental elements.

Tier-3 assertions:
  face[0].surface_type == "plane"
  face[5].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(27) ifc=schema_n/a
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M011",
    schema="AP242",
    defect=(
        "Supplemental geometry inadvertently included in part-level GVP; "
        "input: AP242 STEP file with MANIFOLD_SOLID_BREP (1 mm cube) plus "
        "CONSTRUCTIVE_GEOMETRY_REPRESENTATION containing an unbounded plane and "
        "a centerline; the writer summed supplemental elements into part-level "
        "volume/centroid GVP, inflating the values; "
        "kernel must exclude any element referenced solely by "
        "CONSTRUCTIVE_GEOMETRY_REPRESENTATION from part-level GVPs; "
        "synonyms: supplemental geometry inflates GVP, datum plane in part-level volume, "
        "validation property fails check, centerline counted in shape area, "
        "unbounded supplemental geometry yields infinite volume"
    ),
)


# Shared 1 mm cube body (entity IDs #5700-#5855, shell #510, solid #500)
_CUBE_BODY = """\
#5700=CARTESIAN_POINT('p000',(0.0,0.0,0.0));
#5701=CARTESIAN_POINT('p100',(1.0,0.0,0.0));
#5702=CARTESIAN_POINT('p110',(1.0,1.0,0.0));
#5703=CARTESIAN_POINT('p010',(0.0,1.0,0.0));
#5704=CARTESIAN_POINT('p001',(0.0,0.0,1.0));
#5705=CARTESIAN_POINT('p101',(1.0,0.0,1.0));
#5706=CARTESIAN_POINT('p111',(1.0,1.0,1.0));
#5707=CARTESIAN_POINT('p011',(0.0,1.0,1.0));
#5710=VERTEX_POINT('',#5700);
#5711=VERTEX_POINT('',#5701);
#5712=VERTEX_POINT('',#5702);
#5713=VERTEX_POINT('',#5703);
#5714=VERTEX_POINT('',#5704);
#5715=VERTEX_POINT('',#5705);
#5716=VERTEX_POINT('',#5706);
#5717=VERTEX_POINT('',#5707);
#5720=DIRECTION('dx',(1.0,0.0,0.0));
#5721=DIRECTION('dy',(0.0,1.0,0.0));
#5722=DIRECTION('dz',(0.0,0.0,1.0));
#5723=DIRECTION('dxn',(-1.0,0.0,0.0));
#5724=DIRECTION('dyn',(0.0,-1.0,0.0));
#5725=DIRECTION('dzn',(0.0,0.0,-1.0));
#5730=VECTOR('vx',#5720,1.0);
#5731=VECTOR('vy',#5721,1.0);
#5732=VECTOR('vz',#5722,1.0);
#5740=LINE('',#5700,#5730);
#5741=LINE('',#5701,#5731);
#5742=LINE('',#5703,#5730);
#5743=LINE('',#5700,#5731);
#5744=LINE('',#5704,#5730);
#5745=LINE('',#5705,#5731);
#5746=LINE('',#5707,#5730);
#5747=LINE('',#5704,#5731);
#5748=LINE('',#5700,#5732);
#5749=LINE('',#5701,#5732);
#5750=LINE('',#5702,#5732);
#5751=LINE('',#5703,#5732);
#5760=EDGE_CURVE('',#5710,#5711,#5740,.T.);
#5761=EDGE_CURVE('',#5711,#5712,#5741,.T.);
#5762=EDGE_CURVE('',#5713,#5712,#5742,.T.);
#5763=EDGE_CURVE('',#5710,#5713,#5743,.T.);
#5764=EDGE_CURVE('',#5714,#5715,#5744,.T.);
#5765=EDGE_CURVE('',#5715,#5716,#5745,.T.);
#5766=EDGE_CURVE('',#5717,#5716,#5746,.T.);
#5767=EDGE_CURVE('',#5714,#5717,#5747,.T.);
#5768=EDGE_CURVE('',#5710,#5714,#5748,.T.);
#5769=EDGE_CURVE('',#5711,#5715,#5749,.T.);
#5770=EDGE_CURVE('',#5712,#5716,#5750,.T.);
#5771=EDGE_CURVE('',#5713,#5717,#5751,.T.);
#5780=AXIS2_PLACEMENT_3D('',#5700,#5725,#5720);
#5781=AXIS2_PLACEMENT_3D('',#5704,#5722,#5720);
#5782=AXIS2_PLACEMENT_3D('',#5700,#5724,#5720);
#5783=AXIS2_PLACEMENT_3D('',#5703,#5721,#5720);
#5784=AXIS2_PLACEMENT_3D('',#5700,#5723,#5721);
#5785=AXIS2_PLACEMENT_3D('',#5701,#5720,#5721);
#5790=PLANE('',#5780);
#5791=PLANE('',#5781);
#5792=PLANE('',#5782);
#5793=PLANE('',#5783);
#5794=PLANE('',#5784);
#5795=PLANE('',#5785);
#5800=ORIENTED_EDGE('',*,*,#5763,.T.);
#5801=ORIENTED_EDGE('',*,*,#5762,.T.);
#5802=ORIENTED_EDGE('',*,*,#5761,.F.);
#5803=ORIENTED_EDGE('',*,*,#5760,.F.);
#5804=ORIENTED_EDGE('',*,*,#5764,.T.);
#5805=ORIENTED_EDGE('',*,*,#5765,.T.);
#5806=ORIENTED_EDGE('',*,*,#5766,.F.);
#5807=ORIENTED_EDGE('',*,*,#5767,.F.);
#5808=ORIENTED_EDGE('',*,*,#5760,.T.);
#5809=ORIENTED_EDGE('',*,*,#5769,.T.);
#5810=ORIENTED_EDGE('',*,*,#5764,.F.);
#5811=ORIENTED_EDGE('',*,*,#5768,.F.);
#5812=ORIENTED_EDGE('',*,*,#5771,.T.);
#5813=ORIENTED_EDGE('',*,*,#5766,.T.);
#5814=ORIENTED_EDGE('',*,*,#5770,.F.);
#5815=ORIENTED_EDGE('',*,*,#5762,.F.);
#5816=ORIENTED_EDGE('',*,*,#5768,.T.);
#5817=ORIENTED_EDGE('',*,*,#5767,.T.);
#5818=ORIENTED_EDGE('',*,*,#5771,.F.);
#5819=ORIENTED_EDGE('',*,*,#5763,.F.);
#5820=ORIENTED_EDGE('',*,*,#5761,.T.);
#5821=ORIENTED_EDGE('',*,*,#5770,.T.);
#5822=ORIENTED_EDGE('',*,*,#5765,.F.);
#5823=ORIENTED_EDGE('',*,*,#5769,.F.);
#5830=EDGE_LOOP('',(#5800,#5801,#5802,#5803));
#5831=EDGE_LOOP('',(#5804,#5805,#5806,#5807));
#5832=EDGE_LOOP('',(#5808,#5809,#5810,#5811));
#5833=EDGE_LOOP('',(#5812,#5813,#5814,#5815));
#5834=EDGE_LOOP('',(#5816,#5817,#5818,#5819));
#5835=EDGE_LOOP('',(#5820,#5821,#5822,#5823));
#5840=FACE_OUTER_BOUND('',#5830,.T.);
#5841=FACE_OUTER_BOUND('',#5831,.T.);
#5842=FACE_OUTER_BOUND('',#5832,.T.);
#5843=FACE_OUTER_BOUND('',#5833,.T.);
#5844=FACE_OUTER_BOUND('',#5834,.T.);
#5845=FACE_OUTER_BOUND('',#5835,.T.);
#5850=ADVANCED_FACE('bottom',(#5840),#5790,.F.);
#5851=ADVANCED_FACE('top',(#5841),#5791,.T.);
#5852=ADVANCED_FACE('front',(#5842),#5792,.F.);
#5853=ADVANCED_FACE('back',(#5843),#5793,.T.);
#5854=ADVANCED_FACE('left',(#5844),#5794,.F.);
#5855=ADVANCED_FACE('right',(#5845),#5795,.T.);"""


def _render_m011() -> str:
    lines = []
    lines.append("ISO-10303-21;")
    lines.append(f"/* M011: {f.defect} */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M011'),'2;1');")
    lines.append("FILE_NAME('M011.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 4 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('managed model based 3d engineering');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'ap242_managed_model_based_3d_engineering',2014,#1);")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-6),#10,'distance_accuracy_value','');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("     GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("     GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("     REPRESENTATION_CONTEXT('part','3D'));")
    lines.append("#300=PRODUCT('cube','cube','',(#310));")
    lines.append("#310=MECHANICAL_CONTEXT('',#1,'mechanical');")
    lines.append("#320=PRODUCT_DEFINITION_FORMATION('','',#300);")
    lines.append("#330=PRODUCT_DEFINITION('design','',#320,#340);")
    lines.append("#340=PRODUCT_DEFINITION_CONTEXT('part definition',#1,'design');")
    lines.append("#350=PRODUCT_DEFINITION_SHAPE('','',#330);")
    lines.append("#500=MANIFOLD_SOLID_BREP('cube_body',#510);")
    lines.append(_CUBE_BODY)
    lines.append("#510=CLOSED_SHELL('',(#5850,#5851,#5852,#5853,#5854,#5855));")
    lines.append("#520=ADVANCED_BREP_SHAPE_REPRESENTATION('cube_brep',(#500),#14);")
    lines.append("#530=SHAPE_DEFINITION_REPRESENTATION(#350,#520);")
    lines.append("/* Supplemental geometry: unbounded reference plane + centerline axis */")
    lines.append("#600=CARTESIAN_POINT('',(0.5,0.5,0.5));")
    lines.append("#601=DIRECTION('',(0.0,0.0,1.0));")
    lines.append("#602=DIRECTION('',(1.0,0.0,0.0));")
    lines.append("#603=AXIS2_PLACEMENT_3D('',#600,#601,#602);")
    lines.append("/* Unbounded datum plane — has no finite area/volume */")
    lines.append("#604=PLANE('datum_plane',#603);")
    lines.append("/* Centerline axis — has no volume */")
    lines.append("#610=CARTESIAN_POINT('',(0.5,0.5,0.0));")
    lines.append("#611=DIRECTION('',(0.0,0.0,1.0));")
    lines.append("#612=VECTOR('',#611,1.0);")
    lines.append("#613=LINE('centerline',#610,#612);")
    lines.append("/* CONSTRUCTIVE_GEOMETRY_REPRESENTATION: supplemental elements not part of BRep */")
    lines.append("#620=CONSTRUCTIVE_GEOMETRY_REPRESENTATION('supplemental',(#604,#613),#14);")
    lines.append("/* Defect: part-level GVP inflated by summing supplemental geometry.")
    lines.append("   True volume of 1mm cube = 1.0 mm^3; writer emits 1.5 (50% over). */")
    lines.append("#700=PROPERTY_DEFINITION('geometric validation property','volume',#350);")
    lines.append("#710=MEASURE_REPRESENTATION_ITEM('volume',VOLUME_MEASURE(1.5),#10);")
    lines.append("#720=REPRESENTATION('',(#710),#14);")
    lines.append("#730=PROPERTY_DEFINITION_REPRESENTATION(#700,#720);")
    lines.append("/* Wrong centroid: pulled toward the supplemental plane location */")
    lines.append("#740=PROPERTY_DEFINITION('geometric validation property','centroid',#350);")
    lines.append("#750=CARTESIAN_POINT('centroid',(0.5,0.5,0.75));")
    lines.append("#760=REPRESENTATION('',(#750),#14);")
    lines.append("#770=PROPERTY_DEFINITION_REPRESENTATION(#740,#760);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m011(path) -> None:
    _Path(path).write_text(_render_m011())


f.render = _render_m011   # type: ignore[method-assign]
f.write  = _write_m011    # type: ignore[method-assign]
