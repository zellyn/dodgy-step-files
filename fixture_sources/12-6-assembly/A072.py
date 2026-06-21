"""A072 — Compound with single vertex written as compound-of-two-points.

Catalog claim: a single vertex at (0,0,0) causes the writer to emit both
a CARTESIAN_POINT and a VERTEX_POINT at top level — creating a
compound-of-two-points on re-import. The keyword 'emitted_twice' must
appear. Exactly 1 CARTESIAN_POINT entity def + 1 VERTEX_POINT entity def
(the writer's erroneous output is what we capture).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A072",
             defect="single vertex emitted as both CARTESIAN_POINT and VERTEX_POINT ('emitted_twice' pattern)")

# This fixture represents the writer's ERRONEOUS output: a compound of
# two points instead of one. We emit ONLY these entities (no product chain,
# no full geometry) because the byte assertions require exactly 1 CP + 1 VP.

# Geometric context.
length_unit = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
plane_angle_unit = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
solid_angle_unit = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{length_unit.eid},'distance_accuracy_value','')"
)
geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{length_unit.eid},#{plane_angle_unit.eid},#{solid_angle_unit.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

# The single source vertex at origin.
cp = f._emit_raw("CARTESIAN_POINT('emitted_twice',(0.0,0.0,0.0))")
vp = f._emit_raw(f"VERTEX_POINT('emitted_twice',#{cp.eid})")

# The writer wrongly emits BOTH the CARTESIAN_POINT and the VERTEX_POINT
# at the top level of an ADVANCED_BREP_SHAPE_REPRESENTATION — creating
# a compound-of-two-points instead of a single vertex.
f._emit_raw(
    f"ADVANCED_BREP_SHAPE_REPRESENTATION('compound_two_pts',(#{cp.eid},#{vp.eid}),#{geom_ctx.eid})"
)

# STYLED_ITEM scaffolding for assembly-presence lint.
colour = f._emit_raw("COLOUR_RGB('vertex_color',0.5,0.5,0.5)")
fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
f._emit_raw(f"STYLED_ITEM('vertex_style',(#{psa.eid}),#{vp.eid})")
