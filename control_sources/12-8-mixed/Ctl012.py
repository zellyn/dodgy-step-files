"""Ctl012 — Clean mixed fixture (negative control for §12-8-mixed).

A simple solid box using AP214 schema with no mixed-schema entity types.
All entity types belong to AUTOMOTIVE_DESIGN; no AP242-only tessellation
or PMI entities.  Serves as the §12-8-mixed negative control.

Expected: occt=shape(1)/shape(1), schema_oracle: 0 violations
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl012",
    defect="NEGATIVE CONTROL: clean AP214 STEP, no mixed-schema entity types",
    schema="AP214",
)

def pt(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))

def ledge(va, vb, p, dvec, length):
    return f.edge_curve(va, vb, f.line(p, f.vector(f.direction(dvec), length)))

p000 = pt(0,0,0); p100 = pt(1,0,0); p110 = pt(1,1,0); p010 = pt(0,1,0)
p001 = pt(0,0,1); p101 = pt(1,0,1); p111 = pt(1,1,1); p011 = pt(0,1,1)

v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

e_b0 = ledge(v000, v100, p000, (1,0,0), 1.0)
e_b1 = ledge(v100, v110, p100, (0,1,0), 1.0)
e_b2 = ledge(v110, v010, p110, (-1,0,0), 1.0)
e_b3 = ledge(v010, v000, p010, (0,-1,0), 1.0)
e_t0 = ledge(v001, v101, p001, (1,0,0), 1.0)
e_t1 = ledge(v101, v111, p101, (0,1,0), 1.0)
e_t2 = ledge(v111, v011, p111, (-1,0,0), 1.0)
e_t3 = ledge(v011, v001, p011, (0,-1,0), 1.0)
e_v0 = ledge(v000, v001, p000, (0,0,1), 1.0)
e_v1 = ledge(v100, v101, p100, (0,0,1), 1.0)
e_v2 = ledge(v110, v111, p110, (0,0,1), 1.0)
e_v3 = ledge(v010, v011, p010, (0,0,1), 1.0)

oe = f.oriented_edge

def mface(normal, orig, xdir, bounds):
    plc = f.axis2_placement_3d(
        f.cartesian_point(orig), f.direction(normal), f.direction(xdir)
    )
    loop = f.edge_loop(bounds)
    return f.advanced_face([f.face_outer_bound(loop)], f.plane(plc))

face_bot = mface((0,0,-1), (0,0,0), (1,0,0),
    [oe(e_b0,True), oe(e_b1,True), oe(e_b2,True), oe(e_b3,True)])
face_top = mface((0,0,1), (0,0,1), (1,0,0),
    [oe(e_t0,True), oe(e_t1,True), oe(e_t2,True), oe(e_t3,True)])
face_frt = mface((0,-1,0), (0,0,0), (1,0,0),
    [oe(e_b0,True), oe(e_v1,True), oe(e_t0,False), oe(e_v0,False)])
face_bk  = mface((0,1,0), (0,1,0), (-1,0,0),
    [oe(e_b2,False), oe(e_v3,True), oe(e_t2,False), oe(e_v2,False)])
face_lft = mface((-1,0,0), (0,0,0), (0,1,0),
    [oe(e_b3,False), oe(e_v0,True), oe(e_t3,False), oe(e_v3,False)])
face_rgt = mface((1,0,0), (1,0,0), (0,1,0),
    [oe(e_b1,True), oe(e_v2,True), oe(e_t1,False), oe(e_v1,False)])

closed_sh = f.closed_shell([face_bot, face_top, face_frt, face_bk, face_lft, face_rgt])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
