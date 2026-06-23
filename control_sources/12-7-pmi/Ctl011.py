"""Ctl011 — Clean fixture with valid PMI annotations (negative control for §12-7-pmi).

A 10x10 square planar face with a DIMENSIONAL_SIZE 'width' annotation
attached via a SHAPE_ASPECT and one GEOMETRIC_ITEM_SPECIFIC_USAGE.
Single face, single SHAPE_ASPECT, single GISU — no split-feature ambiguity.

Expected: occt=shape(1)/shape(1)
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl011",
    defect="NEGATIVE CONTROL: clean PMI DIMENSIONAL_SIZE annotation, no PMI defect",
)

# 10x10 square face
p00 = f.cartesian_point((0.0,  0.0,  0.0))
p10 = f.cartesian_point((10.0, 0.0,  0.0))
p11 = f.cartesian_point((10.0, 10.0, 0.0))
p01 = f.cartesian_point((0.0,  10.0, 0.0))

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)

def ledge(va, vb, p, dvec, length):
    return f.edge_curve(va, vb, f.line(p, f.vector(f.direction(dvec), length)))

e0 = ledge(v00, v10, p00, (1.0, 0.0, 0.0), 10.0)
e1 = ledge(v10, v11, p10, (0.0, 1.0, 0.0), 10.0)
e2 = ledge(v11, v01, p11, (-1.0, 0.0, 0.0), 10.0)
e3 = ledge(v01, v00, p01, (0.0, -1.0, 0.0), 10.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])

plc = f.axis2_placement_3d(p00, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face = f.advanced_face([f.face_outer_bound(loop)], f.plane(plc))
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# PMI: single SHAPE_ASPECT + single GISU + DIMENSIONAL_SIZE
# #9055 is PRODUCT_DEFINITION_SHAPE from add_product_chain
shape_asp = f._emit_raw(
    "SHAPE_ASPECT('width_feature','top face width',#9055,.T.)"
)
# GISU linking the SHAPE_ASPECT to the ADVANCED_FACE entity
gisu = f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('width_gisu',$,#{shape_asp.eid},#9061,#{face.eid})"
)
# Dimensional size annotation
dim_size = f._emit_raw(
    f"DIMENSIONAL_SIZE(#{shape_asp.eid},'width')"
)
# Nominal value
mri = f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('nominal',LENGTH_MEASURE(10.0),#9056)"
)
