"""Ctl005 — Clean closed cube (negative control for §12-3a-shells).

A unit cube MANIFOLD_SOLID_BREP with CLOSED_SHELL containing exactly 6
ADVANCED_FACE instances.  All faces share edges correctly; no duplicate
faces, no open boundaries, no flipped normals.

Expected: occt=shape(1)/shape(1)
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl005",
    defect="NEGATIVE CONTROL: clean unit-cube closed shell, no shell defect",
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

# 12 edges of the unit cube
e_b0 = ledge(v000, v100, p000, (1,0,0), 1.0)   # bottom front
e_b1 = ledge(v100, v110, p100, (0,1,0), 1.0)   # bottom right
e_b2 = ledge(v110, v010, p110, (-1,0,0), 1.0)  # bottom back
e_b3 = ledge(v010, v000, p010, (0,-1,0), 1.0)  # bottom left
e_t0 = ledge(v001, v101, p001, (1,0,0), 1.0)   # top front
e_t1 = ledge(v101, v111, p101, (0,1,0), 1.0)   # top right
e_t2 = ledge(v111, v011, p111, (-1,0,0), 1.0)  # top back
e_t3 = ledge(v011, v001, p011, (0,-1,0), 1.0)  # top left
e_v0 = ledge(v000, v001, p000, (0,0,1), 1.0)   # vertical: 000-001
e_v1 = ledge(v100, v101, p100, (0,0,1), 1.0)   # vertical: 100-101
e_v2 = ledge(v110, v111, p110, (0,0,1), 1.0)   # vertical: 110-111
e_v3 = ledge(v010, v011, p010, (0,0,1), 1.0)   # vertical: 010-011

oe = f.oriented_edge

def make_face(normal, orig, xdir, bound_edges):
    plc = f.axis2_placement_3d(
        f.cartesian_point(orig),
        f.direction(normal),
        f.direction(xdir),
    )
    loop = f.edge_loop(bound_edges)
    return f.advanced_face([f.face_outer_bound(loop)], f.plane(plc))

# Bottom z=0, normal (0,0,-1)
face_bot = make_face(
    (0,0,-1), (0,0,0), (1,0,0),
    [oe(e_b0, True), oe(e_b1, True), oe(e_b2, True), oe(e_b3, True)],
)
# Top z=1, normal (0,0,1)
face_top = make_face(
    (0,0,1), (0,0,1), (1,0,0),
    [oe(e_t0, True), oe(e_t1, True), oe(e_t2, True), oe(e_t3, True)],
)
# Front y=0, normal (0,-1,0)
face_frt = make_face(
    (0,-1,0), (0,0,0), (1,0,0),
    [oe(e_b0, True), oe(e_v1, True), oe(e_t0, False), oe(e_v0, False)],
)
# Back y=1, normal (0,1,0)
face_bk = make_face(
    (0,1,0), (0,1,0), (-1,0,0),
    [oe(e_b2, False), oe(e_v3, True), oe(e_t2, False), oe(e_v2, False)],
)
# Left x=0, normal (-1,0,0)
face_lft = make_face(
    (-1,0,0), (0,0,0), (0,1,0),
    [oe(e_b3, False), oe(e_v0, True), oe(e_t3, False), oe(e_v3, False)],
)
# Right x=1, normal (1,0,0)
face_rgt = make_face(
    (1,0,0), (1,0,0), (0,1,0),
    [oe(e_b1, True), oe(e_v2, True), oe(e_t1, False), oe(e_v1, False)],
)

closed_sh = f.closed_shell([face_bot, face_top, face_frt, face_bk, face_lft, face_rgt])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
