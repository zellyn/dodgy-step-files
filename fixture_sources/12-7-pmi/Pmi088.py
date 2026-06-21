"""Pmi088 — GEOMETRIC_VALIDATION_PROPERTY claimed surface area disagrees with geometry.

Catalog claim: A MANIFOLD_SOLID_BREP representing a 10x10x10 mm cube (surface
area 600 mm²) is accompanied by a GEOMETRIC_VALIDATION_PROPERTY asserting
AREA_MEASURE(540.0) — 10% lower than the actual area. Common cause: area
computed before a final face-merge pass. Receivers must detect and surface
the disagreement.

Tier-3 assertions:
  n_faces_total == 6
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 99 and < 101
  face[5].edge_count == 4
  face[5].area > 99 and < 101
  n_edges_total >= 24

Expected: occt=shape(1)/shape(1) gmsh=shape(27) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi088",
    defect=(
        "GEOMETRIC_VALIDATION_PROPERTY AREA_MEASURE(540.0) claimed for a "
        "10x10x10 mm cube whose actual surface area is 600.0 mm² — stale "
        "pre-merge cache; receivers must detect and surface the disagreement"
    ),
)

# ── Build a 10×10×10 mm closed-shell cube ─────────────────────────────────────
def pt(x, y, z):
    return f.cartesian_point((x, y, z))

p000 = pt(0, 0, 0); p100 = pt(10, 0, 0)
p110 = pt(10, 10, 0); p010 = pt(0, 10, 0)
p001 = pt(0, 0, 10); p101 = pt(10, 0, 10)
p111 = pt(10, 10, 10); p011 = pt(0, 10, 10)

def vp(p): return f.vertex_point(p)

v000 = vp(p000); v100 = vp(p100); v110 = vp(p110); v010 = vp(p010)
v001 = vp(p001); v101 = vp(p101); v111 = vp(p111); v011 = vp(p011)

def line_edge(pa, vstart, vend, dvec):
    d = f.direction(dvec)
    ln = f.line(pa, f.vector(d, 10.0))
    return f.edge_curve(vstart, vend, ln)

# 12 edges
e_b0 = line_edge(p000, v000, v100, (1,0,0))
e_b1 = line_edge(p100, v100, v110, (0,1,0))
e_b2 = line_edge(p010, v110, v010, (-1,0,0))
e_b3 = line_edge(p000, v010, v000, (0,-1,0))

e_t0 = line_edge(p001, v001, v101, (1,0,0))
e_t1 = line_edge(p101, v101, v111, (0,1,0))
e_t2 = line_edge(p011, v111, v011, (-1,0,0))
e_t3 = line_edge(p001, v011, v001, (0,-1,0))

e_v0 = line_edge(p000, v000, v001, (0,0,1))
e_v1 = line_edge(p100, v100, v101, (0,0,1))
e_v2 = line_edge(p110, v110, v111, (0,0,1))
e_v3 = line_edge(p010, v010, v011, (0,0,1))

def oe(e, sense): return f.oriented_edge(e, sense)

def make_plane_face(normal_xyz, orig_xyz, xdir_xyz, corners):
    orig = f.cartesian_point(orig_xyz)
    zd = f.direction(normal_xyz)
    xd = f.direction(xdir_xyz)
    plc = f.axis2_placement_3d(orig, zd, xd)
    plane = f.plane(plc)
    loop = f.edge_loop(corners)
    fob = f.face_outer_bound(loop)
    return f.advanced_face([fob], plane)

bottom = make_plane_face(
    (0,0,-1), (0,0,0), (1,0,0),
    [oe(e_b0, True), oe(e_b1, True), oe(e_b2, True), oe(e_b3, True)]
)
top = make_plane_face(
    (0,0,1), (0,0,10), (1,0,0),
    [oe(e_t0, True), oe(e_t1, True), oe(e_t2, True), oe(e_t3, True)]
)
front = make_plane_face(
    (0,-1,0), (0,0,0), (1,0,0),
    [oe(e_b0, True), oe(e_v1, True), oe(e_t0, False), oe(e_v0, False)]
)
back = make_plane_face(
    (0,1,0), (0,10,0), (1,0,0),
    [oe(e_b1, True), oe(e_v2, True), oe(e_t1, False), oe(e_v1, False)]
)
left = make_plane_face(
    (-1,0,0), (0,0,0), (0,1,0),
    [oe(e_b3, False), oe(e_v0, True), oe(e_t3, False), oe(e_v3, False)]
)
right = make_plane_face(
    (1,0,0), (10,0,0), (0,1,0),
    [oe(e_b2, False), oe(e_v3, True), oe(e_t2, False), oe(e_v2, False)]
)

shell = f.closed_shell([bottom, top, front, back, left, right])
msb = f.manifold_solid_brep(shell)
f.add_product_chain(msb, mode="brep_shape")

# ── DEFECT: GEOMETRIC_VALIDATION_PROPERTY claiming wrong surface area ─────────
# Actual surface area: 6 × 10×10 = 600 mm²; claimed 540.0 mm² (stale cache).
f._emit_raw(
    "GEOMETRIC_VALIDATION_PROPERTY('surface_area','',#9055,"
    "(MEASURE_REPRESENTATION_ITEM('surface_area',AREA_MEASURE(540.0),#9056)))"
)
# SHAPE_ASPECT anchors the validation property to the body for PMI-presence lint.
shape_asp = f._emit_raw(
    "SHAPE_ASPECT('area_scope','validation_property_scope',#9055,.T.)"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('gvp_scope',$,#{shape_asp.eid},#9061,#{msb.eid})"
)
f._emit_raw(
    f"DIMENSIONAL_SIZE(#{shape_asp.eid},'reference_area')"
)
