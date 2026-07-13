"""Gp177 — Edge's interior 3D curve passes directly over a sphere pole
(must force a SPLIT into two sub-edges, not just an apex-adjacent pcurve).

Work packet D1, item `tkshh-edge-crossing-surface-singularity` (PARTIAL,
missing 2 of 2), subvariant (a): "An edge whose interior 3D curve passes
directly over a cone apex/sphere pole -- must trigger a SPLIT into two
sub-edges, not just an apex-adjacent pcurve." Mirrors: Xp013, Gp048 -- both
of which touch a singularity only at an edge ENDPOINT (a vertex sits exactly
at the apex). This fixture is the distinct, uncovered case: the singularity
is strictly INTERIOR to a single edge's parameter range, with no vertex
there at all.

Geometry: a SPHERICAL_SURFACE, radius 1, standard placement (axis Z). Vertex
A = (1,0,0) is on the equator at (u=0,v=0); vertex B = (-1,0,0) is on the
equator at (u=pi,v=0) -- diametrically opposite through the sphere. The
DEFECT edge's 3D curve is the great-circle CIRCLE lying in the XZ-plane,
oriented so its natural parameter runs A -> north pole (0,0,1) -> B: the
pole is strictly the MIDPOINT of the edge's parameter range, not an
endpoint. A second, healthy edge closes the loop via the *other* equatorial
semicircle (through the back, negative-Y side), which touches neither pole,
giving a real, non-degenerate 2-edge lune face.

THE DEFECT: the polar edge's pcurve is a single straight UV LINE from
(u=0,v=0) to (u=pi,v=0) -- i.e. it naively treats the edge as if it stayed
on the equator (v=0) the whole way, exactly the kind of "apex-adjacent"
patch-job pcurve the work packet calls out as insufficient. It does not
reflect that the true 3D path climbs to v=pi/2 (the pole) at its midpoint,
where u is undefined (every u maps to the same 3D point) -- a single pcurve
cannot represent that correctly; the geometrically correct fix is to split
this edge into two sub-edges at the pole (each with its own clean pcurve
and a shared degenerate vertex there), not patch one pcurve near the apex.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp177",
    defect=(
        "SPHERICAL_SURFACE edge whose 3D curve (a great-circle CIRCLE) "
        "climbs from equator vertex A=(1,0,0) through the NORTH POLE "
        "(0,0,1) -- strictly interior to the edge's parameter range, not "
        "an endpoint -- down to equator vertex B=(-1,0,0). Its pcurve is a "
        "single straight UV line v=0 constant (u:0->pi), naively treating "
        "the edge as if it stayed on the equator; the true path needs u to "
        "jump 0->pi exactly at v=pi/2 (the pole), which one pcurve cannot "
        "represent -- correct healing requires splitting into two "
        "sub-edges at the pole, not patching one apex-adjacent pcurve."
    ),
)

# SPHERICAL_SURFACE, radius 1, standard placement (axis Z, ref X).
s_orig = f.cartesian_point((0.0, 0.0, 0.0))
s_axis = f.direction((0.0, 0.0, 1.0))
s_ref = f.direction((1.0, 0.0, 0.0))
s_plc = f.axis2_placement_3d(s_orig, s_axis, s_ref)
sphere = f.spherical_surface(s_plc, 1.0)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertices: A=(1,0,0) at (u=0,v=0); B=(-1,0,0) at (u=pi,v=0).
p_a = f.cartesian_point((1.0, 0.0, 0.0))
p_b = f.cartesian_point((-1.0, 0.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)

# ---- Polar edge (THE DEFECT): great circle in the XZ-plane. ----
# Placement chosen so t=0 -> A, t=pi/2 -> north pole (0,0,1), t=pi -> B.
polar_loc = f.cartesian_point((0.0, 0.0, 0.0))
polar_axis = f.direction((0.0, -1.0, 0.0))  # circle-plane normal
polar_ref = f.direction((1.0, 0.0, 0.0))    # points at A (t=0)
polar_plc = f.axis2_placement_3d(polar_loc, polar_axis, polar_ref)
polar_circle = f._emit_raw(f"CIRCLE('polar_great_circle',#{polar_plc.eid},1.0)")

# WRONG single pcurve: straight UV line v=0 constant, u:0->pi (equator-style).
pc_polar_start = f.cartesian_point((0.0, 0.0))
pc_polar_dir = f.direction((1.0, 0.0))
pc_polar_vec = f.vector(pc_polar_dir, math.pi)
pc_polar_line = f.line(pc_polar_start, pc_polar_vec)
pc_polar_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_polar_def',(#{pc_polar_line.eid}),#{prc.eid})"
)
pcurve_polar = f._emit_raw(f"PCURVE('pc_polar_wrong',#{sphere.eid},#{pc_polar_def.eid})")
sc_polar = f._emit_raw(
    f"SURFACE_CURVE('polar_edge_sc',#{polar_circle.eid},(#{pcurve_polar.eid}),.PCURVE_S1.)"
)
edge_polar = f._emit_raw(
    f"EDGE_CURVE('polar_edge',#{v_a.eid},#{v_b.eid},#{sc_polar.eid},.T.)"
)

# ---- Equator-back edge (healthy): closes the loop via the back
# (negative-Y) semicircle, touching neither pole. ----
eq_loc = f.cartesian_point((0.0, 0.0, 0.0))
eq_axis = f.direction((0.0, 0.0, 1.0))
eq_ref = f.direction((-1.0, 0.0, 0.0))  # points at B (t=0)
eq_plc = f.axis2_placement_3d(eq_loc, eq_axis, eq_ref)
eq_circle = f._emit_raw(f"CIRCLE('equator_back_circle',#{eq_plc.eid},1.0)")

# Correct pcurve: straight UV line v=0 constant, u: pi -> 2*pi.
pc_eq_start = f.cartesian_point((math.pi, 0.0))
pc_eq_dir = f.direction((1.0, 0.0))
pc_eq_vec = f.vector(pc_eq_dir, math.pi)
pc_eq_line = f.line(pc_eq_start, pc_eq_vec)
pc_eq_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_eq_def',(#{pc_eq_line.eid}),#{prc.eid})"
)
pcurve_eq = f._emit_raw(f"PCURVE('pc_eq_back',#{sphere.eid},#{pc_eq_def.eid})")
sc_eq = f._emit_raw(
    f"SURFACE_CURVE('equator_back_sc',#{eq_circle.eid},(#{pcurve_eq.eid}),.PCURVE_S1.)"
)
edge_eq = f._emit_raw(
    f"EDGE_CURVE('equator_back_edge',#{v_b.eid},#{v_a.eid},#{sc_eq.eid},.T.)"
)

# Loop: polar (A->B via north pole, DEFECT) -> equator_back (B->A via back).
loop = f.edge_loop([
    f.oriented_edge(edge_polar, True),
    f.oriented_edge(edge_eq, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], sphere)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
