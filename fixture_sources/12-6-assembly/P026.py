"""P026 — LENGTH_UNIT(.MILLI.,.METRE.) context but CARTESIAN_POINT coordinates
pre-scaled x1000 (global OCCT unit setting contaminated across in-process
clients).

Catalog claim: After gmsh's OCCT instance sets Geometry.OCCTargetUnit=M,
subsequent FreeCAD STEP exports emit coordinates scaled x1000 because the
OCCT global unit setting was mutated. Common file signature:
GEOMETRIC_REPRESENTATION_CONTEXT declares LENGTH_UNIT(SI MILLI METRE) but
CARTESIAN_POINT coordinates carry values like 10000.0 where 10 mm was
intended.

The defect: coordinates are pre-scaled x1000 relative to the declared unit
context. A kernel must coerce the per-call unit context without inheriting
global state; silent empty result is the bug.

Byte assertions:
  contains(b'LENGTH_UNIT') and contains(b'MILLI')
  matches(rb'CARTESIAN_POINT[^;]*1000[0-9]')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P026",
    defect=(
        "GEOMETRIC_REPRESENTATION_CONTEXT declares LENGTH_UNIT(SI MILLI METRE) "
        "but CARTESIAN_POINT coordinates are pre-scaled x1000 (e.g. 10000.0 for 10 mm); "
        "process-state contamination: gmsh Geometry.OCCTargetUnit=M mutated global OCCT unit; "
        "subsequent FreeCAD STEP export inherited that global and scaled all coords x1000; "
        "kernel must coerce per-call context without inheriting global state; "
        "the defect entity is emitted but sits unreachable from the shape-rep root (product chain roots a GEOMETRIC_CURVE_SET stub), so OCC loads only a 1-vertex stub (shape(1)); byte-present but oracle-invisible to the load-time shape-count oracles"
    ),
    schema="AP242",
)

# ── Minimal geometry payload so shape is empty ────────────────────────────────
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin_pt.eid}))")
f.add_product_chain(gcs)

# ── The defect: CARTESIAN_POINTs with x1000 pre-scaled coordinates ─────────────
# A 10mm cube would have coordinates at (10.0, 10.0, 10.0) in MILLI METRE context.
# After process-state contamination the export writes (10000.0, 10000.0, 10000.0).
# Byte assertion: matches(rb'CARTESIAN_POINT[^;]*1000[0-9]')
# We use 10000.0 (should have been 10.0) to trigger this pattern.
scaled_p0 = f._emit_raw("CARTESIAN_POINT('scaled_p0',(0.0,0.0,0.0))")
scaled_p1 = f._emit_raw("CARTESIAN_POINT('scaled_p1',(10000.0,0.0,0.0))")
scaled_p2 = f._emit_raw("CARTESIAN_POINT('scaled_p2',(10000.0,10000.0,0.0))")
scaled_p3 = f._emit_raw("CARTESIAN_POINT('scaled_p3',(0.0,10000.0,0.0))")

# Vertex points for the defect geometry.
sv0 = f._emit_raw(f"VERTEX_POINT('sv0',#{scaled_p0.eid})")
sv1 = f._emit_raw(f"VERTEX_POINT('sv1',#{scaled_p1.eid})")
sv2 = f._emit_raw(f"VERTEX_POINT('sv2',#{scaled_p2.eid})")
sv3 = f._emit_raw(f"VERTEX_POINT('sv3',#{scaled_p3.eid})")

# Edges using the over-scaled coordinates.
d0 = f._emit_raw("DIRECTION('sd0',(1.0,0.0,0.0))")
vec0 = f._emit_raw(f"VECTOR('',#{d0.eid},10000.0)")
line0 = f._emit_raw(f"LINE('sl0',#{scaled_p0.eid},#{vec0.eid})")
se0 = f._emit_raw(f"EDGE_CURVE('se0',#{sv0.eid},#{sv1.eid},#{line0.eid},.T.)")

d1 = f._emit_raw("DIRECTION('sd1',(0.0,1.0,0.0))")
vec1 = f._emit_raw(f"VECTOR('',#{d1.eid},10000.0)")
line1 = f._emit_raw(f"LINE('sl1',#{scaled_p1.eid},#{vec1.eid})")
se1 = f._emit_raw(f"EDGE_CURVE('se1',#{sv1.eid},#{sv2.eid},#{line1.eid},.T.)")

# Place the defect geometry in a GEOMETRIC_CURVE_SET for reference.
defect_gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('scaled_coords_defect',(#{se0.eid},#{se1.eid}))"
)

# ── Unit context: declares MILLI METRE — satisfies contains(b'LENGTH_UNIT')
# and contains(b'MILLI'). This is a separate representation context from
# add_product_chain's internal context; we use _emit_raw for the explicit
# MILLI annotation to guarantee the byte assertion. ─────────────────────────
# (The standard product chain from add_product_chain already includes
# SI_UNIT(.MILLI.,.METRE.) via the builder's internal header; these raw
# entities make the byte assertion unambiguous in the DATA section too.)
length_unit_milli = f._emit_raw(
    "(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))"
)
pa_unit = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sa_unit = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),"
    f"#{length_unit_milli.eid},'distance_accuracy_value','')"
)
# GEOMETRIC_REPRESENTATION_CONTEXT with GLOBAL_UNIT_ASSIGNED_CONTEXT.
# This represents what the file claims (MILLI METRE), contradicting
# the 10000.0-scale coordinates above.
geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{length_unit_milli.eid},#{pa_unit.eid},#{sa_unit.eid}))"
    f"REPRESENTATION_CONTEXT('P026_unit_ctx','3D Millimetre context'))"
)

# ── NAUO scaffolding for §12.6 assembly-presence lint ─────────────────────────
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('ScaledCoordComp','ScaledCoordComp','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','scaled_coord_instance','',#9054,#{sub_pdef.eid},$)"
)
