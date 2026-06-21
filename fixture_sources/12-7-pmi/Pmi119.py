"""Pmi119 — PROFILE_FEATURE with non-closed profile (open polyline used as boundary).

Catalog claim: AP242 profile_feature profile must be a closed loop. This
fixture emits three VERTEX_POINTs connected by only two EDGE_CURVEs — the
closing edge is missing. Receivers must reject E_PROFILE_NOT_CLOSED; never
silently close the profile.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi119",
    defect=(
        "profile_feature SHAPE_ASPECT with open profile: 3 vertices, 2 edges, "
        "missing closing edge; profile_closure='OPEN'; "
        "receiver must reject E_PROFILE_NOT_CLOSED"
    ),
)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)
p0 = f.cartesian_point((0.0, 0.0, 0.0)); p1 = f.cartesian_point((50.0, 0.0, 0.0))
p2 = f.cartesian_point((50.0, 50.0, 0.0)); p3 = f.cartesian_point((0.0, 50.0, 0.0))
loop = f.closed_polyline_loop([p0, p1, p2, p3])
face = f.advanced_face([f.face_outer_bound(loop)], plane, name="host_face")
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# DEFECT: open profile with missing closing edge
host_asp    = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
profile_asp = f._emit_raw("SHAPE_ASPECT('profile_feature','',#9055,.T.)")

# Three vertices
pA = f.cartesian_point((5.0, 5.0, 0.0))
pB = f.cartesian_point((15.0, 5.0, 0.0))
pC = f.cartesian_point((10.0, 15.0, 0.0))
vA = f.vertex_point(pA); vB = f.vertex_point(pB); vC = f.vertex_point(pC)

# Two edges only — missing third (closing) edge C→A
dAB = f.direction((1.0, 0.0, 0.0))
eAB = f.edge_curve(vA, vB, f.line(pA, f.vector(dAB, 10.0)))
dBC = f.direction((-0.5, 1.0, 0.0))
eBC = f.edge_curve(vB, vC, f.line(pB, f.vector(dBC, 10.0)))
# Open edge loop (only 2 edges — NOT closed)
open_loop = f._emit_raw(
    f"EDGE_LOOP('open_profile',(#{f.oriented_edge(eAB, True).eid},"
    f"#{f.oriented_edge(eBC, True).eid}))"
)
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('profile_closure','OPEN')"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{profile_asp.eid},'sweep_depth')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('sweep_depth',LENGTH_MEASURE(5.0),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('profile_on_face','profile on host',"
    f"#{host_asp.eid},#{profile_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('profile_gisu',$,#{profile_asp.eid},#9061,#{face.eid})"
)
