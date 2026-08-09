"""Ctl018 — Clean circular disc face: single closed-circle edge loop (§12-3c-faces control).

A planar disc whose outer bound is ONE closed circular edge with start
vertex == end vertex. This construct is completely legal STEP and appears
throughout real exports; single-member EDGE_LOOPs and same-vertex closed
edges must not be flagged by structural or slot-type checking (Tfa110
documents the orientation subtlety a kernel must handle here).

Expected: occt=shape(1)/shape(1)
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl018",
    defect="NEGATIVE CONTROL: valid disc face, single closed circle edge, no defect",
)

ctr = f.cartesian_point((0.0, 0.0, 0.0))
rim = f.cartesian_point((1.5, 0.0, 0.0))
plc = f.axis2_placement_3d(ctr, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
circ = f.circle(plc, 1.5)

v = f.vertex_point(rim)
e = f.edge_curve(v, v, circ)
loop = f.edge_loop([f.oriented_edge(e, True)])
face = f.advanced_face([f.face_outer_bound(loop)], f.plane(plc), True)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
