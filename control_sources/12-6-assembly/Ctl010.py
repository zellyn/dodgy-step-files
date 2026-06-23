"""Ctl010 — Clean two-part assembly with NAUO chain (negative control for §12-6-assembly).

Two separate PRODUCT instances (assembly parent + sub-component) connected
by a NEXT_ASSEMBLY_USAGE_OCCURRENCE (NAUO).  Each part has its own
PRODUCT_DEFINITION and PRODUCT_DEFINITION_SHAPE.  The sub-component has
a unique placement (not shared).

The parent product chain is emitted by add_product_chain (IDs 9000+).
The sub-component product definition uses IDs emitted after the chain.
The NAUO correctly links parent PRODUCT_DEFINITION (#9054) to sub (#9068).

Expected: occt=shape(1)/shape(1), part21_strict=accept
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl010",
    defect="NEGATIVE CONTROL: clean two-part assembly with NAUO chain, no assembly defect",
)

# Sub-component geometry: a 1x1 planar face
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)

def ledge(va, vb, p, dvec, length):
    return f.edge_curve(va, vb, f.line(p, f.vector(f.direction(dvec), length)))

e0 = ledge(v00, v10, p00, (1.0, 0.0, 0.0), 1.0)
e1 = ledge(v10, v11, p10, (0.0, 1.0, 0.0), 1.0)
e2 = ledge(v11, v01, p11, (-1.0, 0.0, 0.0), 1.0)
e3 = ledge(v01, v00, p01, (0.0, -1.0, 0.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])

plc_sub = f.axis2_placement_3d(p00, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face_sub = f.advanced_face([f.face_outer_bound(loop)], f.plane(plc_sub))
shell_sub = f.open_shell([face_sub])
sbsm_sub = f.shell_based_surface_model([shell_sub])

# Parent product chain (entity IDs 9050..9062 after APPLICATION_CONTEXT at 9000)
# add_product_chain emits:
#   #9000  APPLICATION_CONTEXT
#   #9050  PRODUCT_CONTEXT
#   #9051  PRODUCT
#   #9052  PRODUCT_DEFINITION_FORMATION
#   #9053  PRODUCT_DEFINITION_CONTEXT
#   #9054  PRODUCT_DEFINITION  ← this is the assembly's PD
#   #9055  PRODUCT_DEFINITION_SHAPE
#   #9056  LENGTH_UNIT (complex)
#   #9057  PLANE_ANGLE_UNIT (complex)
#   #9058  SOLID_ANGLE_UNIT (complex)
#   #9059  UNCERTAINTY_MEASURE_WITH_UNIT
#   #9060  GEOMETRIC_REPRESENTATION_CONTEXT (complex)
#   #9061  MANIFOLD_SURFACE_SHAPE_REPRESENTATION
#   #9062  SHAPE_DEFINITION_REPRESENTATION
f.add_product_chain(sbsm_sub)

# Sub-component product definition (IDs 9063..9068 come after the chain above)
# We use _emit_raw to control entity types, referencing #9000 for context.
sub_prod_ctx = f._emit_raw("PRODUCT_CONTEXT('',#9000,'mechanical')")
sub_prod     = f._emit_raw(f"PRODUCT('Sub','Sub_Part','',(#{sub_prod_ctx.eid}))")
sub_pdf      = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdc      = f._emit_raw(f"PRODUCT_DEFINITION_CONTEXT('part definition',#9000,'design')")
sub_pd       = f._emit_raw(f"PRODUCT_DEFINITION('','',#{sub_pdf.eid},#{sub_pdc.eid})")

# NAUO: parent=#9054 (the assembly PRODUCT_DEFINITION), child=sub_pd
nauo = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','sub_instance','',#9054,#{sub_pd.eid},$)"
)

# Sub-component placement (unique, not shared) — not required for part21_strict
# but makes the file realistic
sub_orig = f._emit_raw("CARTESIAN_POINT('sub_origin',(2.0,0.0,0.0))")
sub_zdir = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
sub_xdir = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
sub_plc  = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('sub_placement',#{sub_orig.eid},#{sub_zdir.eid},#{sub_xdir.eid})"
)
