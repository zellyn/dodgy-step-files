"""M002 — AP242 Edition 1 disallows axis2_placement_3d in tessellated_shape_representation.

Catalog claim: AP242 Ed.1's tessellated_shape_representation accepts only
tessellated_representation_item in its items, so an axis2_placement_3d for assembly placement
cannot be inside it. Files written by tools that ignore this rule fail schema validation.

Reproducer recipe: AP242 Ed.1 file containing one tessellated_shape_representation whose items
list includes both a tessellated_solid and an axis2_placement_3d for component placement.

Byte assertions:
  contains(b'TESSELLATED_SHAPE_REPRESENTATION')
  contains(b'AXIS2_PLACEMENT_3D')
  matches(rb'TESSELLATED_SHAPE_REPRESENTATION\\([^)]*#133')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M002",
    defect=(
        "AP242 Ed.1 schema violation: TESSELLATED_SHAPE_REPRESENTATION contains "
        "AXIS2_PLACEMENT_3D in its items list; "
        "input: AP242 Edition 1 STEP file where tessellated_shape_representation.items "
        "contains both a tessellated_solid (valid tessellated_representation_item) "
        "and an AXIS2_PLACEMENT_3D for assembly placement (forbidden in Ed.1); "
        "AP242 Ed.1 §4.1 restricts tessellated_shape_representation.items to only "
        "tessellated_representation_item subtypes; "
        "kernel must reject for AP242 Ed.1 schema; "
        "workaround for writers: use plain shape_representation for the placement "
        "and keep tessellated items under a separate representation; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: axis2_placement in tessellated_shape, AP242 Ed.1 schema violation, "
        "placement inside tessellation rejected, AP242 ED1 disallows axis_placement in tess shape"
    ),
    schema="AP242",
)


def _render_m002() -> str:
    """Render AP242 Ed.1 file with TESSELLATED_SHAPE_REPRESENTATION containing AXIS2_PLACEMENT_3D.

    Entity layout:
      #1  CARTESIAN_POINT origin
      #2  CARTESIAN_POINT (1,0,0)
      #3  CARTESIAN_POINT (0,1,0)
      #4  CARTESIAN_POINT (1,1,0)
      #5  COORDINATES_LIST for tessellated face
      #6  TRIANGULATED_FACE referencing #5
      #7  TESSELLATED_SOLID referencing #6
      ... (unit context entities #10-#14)
      ... (pad entities #15-#130)
      #131 CARTESIAN_POINT for placement origin
      #132 DIRECTION z-axis
      #133 = AXIS2_PLACEMENT_3D — the forbidden item in TESSELLATED_SHAPE_REPRESENTATION
      #134 TESSELLATED_SHAPE_REPRESENTATION items=(#7, #133)  <- defect: #133 is A2P3D
      #200+ GEOMETRIC_CURVE_SET and product chain (for OCC empty result)
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M002: AP242 Ed.1 TESSELLATED_SHAPE_REPRESENTATION with AXIS2_PLACEMENT_3D in items */")
    lines.append("/* DEFECT: AP242 Ed.1 §4.1 forbids AXIS2_PLACEMENT_3D inside TESSELLATED_SHAPE_REPRESENTATION */")
    lines.append("/* Only tessellated_representation_item subtypes are allowed in Ed.1 items list */")
    lines.append("/* Correct writer: use plain SHAPE_REPRESENTATION for placement, separate rep for tess */")
    lines.append("/* Buggy writer: mixes AXIS2_PLACEMENT_3D directly into TESSELLATED_SHAPE_REPRESENTATION */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M002: AP242 Ed.1 TESSELLATED_SHAPE_REPRESENTATION with forbidden AXIS2_PLACEMENT_3D'),'2;1');")
    lines.append("FILE_NAME('M002.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 4 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("/* Tessellated geometry: a simple quad split into two triangles */")
    lines.append("#1=CARTESIAN_POINT('origin',(0.,0.,0.));")
    lines.append("#2=CARTESIAN_POINT('pt_a',(10.,0.,0.));")
    lines.append("#3=CARTESIAN_POINT('pt_b',(0.,10.,0.));")
    lines.append("#4=CARTESIAN_POINT('pt_c',(10.,10.,0.));")
    lines.append("/* COORDINATES_LIST: four quad vertices */")
    lines.append("#5=COORDINATES_LIST('quad_coords',3,((0.,0.,0.),(10.,0.,0.),(0.,10.,0.),(10.,10.,0.)));")
    lines.append("/* TRIANGULATED_FACE: two triangles from the quad (0-based indices) */")
    lines.append("#6=TRIANGULATED_FACE('quad_face',#5,$,((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,1,2),(1,3,2)));")
    lines.append("/* TESSELLATED_SOLID: wraps the triangulated face */")
    lines.append("#7=TESSELLATED_SOLID('tess_solid',(#6));")
    lines.append("/* Standard mm context */")
    lines.append("#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));")
    # Pad to reach #131 for CARTESIAN_POINT of placement (#131), #132=DIRECTION, #133=AXIS2_PLACEMENT_3D
    # Currently at #14 (next would be #15). Need to get to #131 = 131-14 = 117 more pad entities.
    for i in range(15, 131):
        lines.append(f"#{i}=CARTESIAN_POINT('pad_{i}',(0.,0.,0.));")
    lines.append("/* AXIS2_PLACEMENT_3D for component placement — forbidden in TESSELLATED_SHAPE_REPRESENTATION (Ed.1) */")
    lines.append("#131=CARTESIAN_POINT('comp_origin',(20.,0.,0.));")
    lines.append("#132=DIRECTION('comp_z',(0.,0.,1.));")
    lines.append("/* #133 = AXIS2_PLACEMENT_3D — the item that violates AP242 Ed.1 §4.1 */")
    lines.append("#133=AXIS2_PLACEMENT_3D('component_placement',#131,#132,$);")
    lines.append("/* TESSELLATED_SHAPE_REPRESENTATION: items=(#7, #133) — #133 is forbidden in Ed.1 */")
    lines.append("/* Byte assertion: matches(rb'TESSELLATED_SHAPE_REPRESENTATION\\([^)]*#133') */")
    lines.append("#134=TESSELLATED_SHAPE_REPRESENTATION('defect_tess_rep',(#7,#133),#14);")
    lines.append("/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */")
    lines.append("#200=GEOMETRIC_CURVE_SET('ap242-ed1-tess-rep-with-placement',(#1,#2,#3,#4));")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m002(path) -> None:
    Path(path).write_text(_render_m002())


f.render = _render_m002  # type: ignore[method-assign]
f.write = _write_m002    # type: ignore[method-assign]
