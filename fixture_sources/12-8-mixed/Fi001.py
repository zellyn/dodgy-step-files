"""Fi001 — Fillet contour spans concavity flip.

Catalog claim: A solid whose spine edge has a vertex where the dihedral angle
transitions from <180° (convex) to >180° (concave). Request a fillet on the
entire spine. The fillet surface twists across the inflection; convex-side
fillet meets concave-side fillet in a self-intersecting way.

Fixture: A two-faced OPEN_SHELL sharing a spine EDGE_CURVE. Face A has a plane
tilted UP from the spine (convex side, dihedral ~120°). Face B has a plane
tilted DOWN (concave side, dihedral ~60°) with its origin at the inflection
vertex so the dihedral is discontinuous. OPEN_SHELL → SHELL_BASED_SURFACE_MODEL
→ PRODUCT chain. OCC loads shape(1).

Tier-3: n_edges_total >= 2, face[0].surface_type == "plane",
         face[1].surface_type == "plane"
Expected: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Fi001",
    defect=(
        "two-faced OPEN_SHELL sharing a spine EDGE_CURVE; "
        "face A has plane tilted up (convex side, ~120 deg dihedral); "
        "face B has plane tilted down at inflection vertex (concave side, ~60 deg dihedral); "
        "fillet surface twists across the concavity-flip inflection point; "
        "fillet must be rejected or split at inflection vertex"
    ),
)

# Spine endpoints and inflection vertex
p_start   = f.cartesian_point((0.0, 0.0, 0.0), name="v_start")
p_inflect = f.cartesian_point((5.0, 0.0, 0.0), name="v_inflect")
p_end     = f.cartesian_point((10.0, 0.0, 0.0))

v_start   = f.vertex_point(p_start)
v_inflect = f._emit_raw(f"VERTEX_POINT('inflection_vertex',#{p_inflect.eid})")
v_end     = f.vertex_point(p_end)

# Spine edge: single LINE from start to end
d_spine   = f.direction((1.0, 0.0, 0.0))
vec_spine = f.vector(d_spine, 1.0)
line_spine = f.line(p_start, vec_spine)
spine_edge = f._emit_raw(
    f"EDGE_CURVE('spine_edge',#{v_start.eid},#{v_end.eid},#{line_spine.eid},.T.)"
)

# Face A: plane tilted UP — normal = (0, -sin(30), cos(30))
# This gives dihedral ~120° on the convex side
sin30 = math.sin(math.radians(30))
cos30 = math.cos(math.radians(30))
na = f.direction((0.0, -sin30, cos30), name="na")
xa = f.direction((1.0, 0.0, 0.0))
plc_a = f.axis2_placement_3d(p_start, na, xa, name="plc_a")
surf_a = f.plane(plc_a, name="face_a_convex_surface")

# Face B: plane tilted DOWN — normal = (0, +sin(30), -cos(30))
# Origin at inflection vertex — creates discontinuity in dihedral (concavity flip)
nb = f.direction((0.0, sin30, -cos30), name="nb")
xb = f.direction((1.0, 0.0, 0.0))
plc_b = f.axis2_placement_3d(p_inflect, nb, xb, name="plc_b")
surf_b = f.plane(plc_b, name="face_b_concave_surface_flipped")

# Both faces share the spine edge as their only boundary
oe_spine_a = f.oriented_edge(spine_edge, True)
loop_a = f.edge_loop([oe_spine_a])
fob_a  = f.face_outer_bound(loop_a)
face_a = f._emit_raw(
    f"ADVANCED_FACE('face_a_convex',(#{fob_a.eid}),#{surf_a.eid},.T.)"
)

oe_spine_b = f.oriented_edge(spine_edge, True)
loop_b = f.edge_loop([oe_spine_b])
fob_b  = f.face_outer_bound(loop_b)
face_b = f._emit_raw(
    f"ADVANCED_FACE('face_b_concave',(#{fob_b.eid}),#{surf_b.eid},.F.)"
)

shell = f.open_shell([face_a, face_b])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
