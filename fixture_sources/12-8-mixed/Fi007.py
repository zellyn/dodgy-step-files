"""Fi007 — Fillet leaks off the boundary of its host face.

Catalog claim: The rolling-ball trace for a fillet leaves the parametric domain
of one of the adjacent faces before reaching the contour endpoint. The small
face's UV domain is too small to contain the rolling ball's trace.

Fixture: OPEN_SHELL with two faces sharing a spine EDGE_CURVE:
- big_face: large planar face (10x10) — normal +Z
- small_face: RECTANGULAR_TRIMMED_SURFACE clipped to [0, 0.5] × [0, 0.5]
  (area = 0.25 mm²) — normal -Z. Rolling ball exceeds this tiny domain.

Both faces reference the same spine EDGE_CURVE as their only boundary.
OCC loads shape(1).

Tier-3: face[0].area < 1e-3, n_edges_total >= 1, face[0].surface_type == "plane",
         n_vertices_total >= 2
Expected: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Fi007",
    defect=(
        "OPEN_SHELL: spine EDGE_CURVE shared by two faces; "
        "small face is RECTANGULAR_TRIMMED_SURFACE UV [0,0.5]x[0,0.5] "
        "(area 0.25 mm²) — too small for rolling-ball fillet trace; "
        "rolling-ball exits face parametric domain before spine ends; "
        "fillet-leaks: kernel must truncate at face boundary and emit diagnostic"
    ),
)

# Spine vertices (1 mm spine edge)
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((1.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

d_spine   = f.direction((1.0, 0.0, 0.0))
vec_spine = f.vector(d_spine, 1.0)
line_spine = f.line(p_start, vec_spine)
spine_edge = f._emit_raw(
    f"EDGE_CURVE('spine_edge',#{v_start.eid},#{v_end.eid},#{line_spine.eid},.T.)"
)

# Big face: normal +Z, large domain
z_up    = f.direction((0.0, 0.0, 1.0))
x_ref   = f.direction((1.0, 0.0, 0.0))
plc_big = f.axis2_placement_3d(p_start, z_up, x_ref)
surf_big = f.plane(plc_big, name="big_face_surface")

# Small face base plane: normal -Z (face on opposite side of spine)
z_dn      = f.direction((0.0, 0.0, -1.0))
plc_small_base = f.axis2_placement_3d(p_start, z_dn, x_ref)
surf_small_base = f.plane(plc_small_base)

# RECTANGULAR_TRIMMED_SURFACE: clip to [0, 0.5] × [0, 0.5]
# This makes the face domain tiny — rolling ball leaks out
surf_small = f.rectangular_trimmed_surface(
    surf_small_base, 0.0, 0.5, 0.0, 0.5,
    usense=True, vsense=True,
    name="small_face"
)

# Shared EDGE_LOOP: just the spine edge (open wire — minimal topology)
oe_big = f.oriented_edge(spine_edge, True)
loop_shared = f.edge_loop([oe_big])
fob_big = f.face_outer_bound(loop_shared)

big_face   = f._emit_raw(
    f"ADVANCED_FACE('big_face',(#{fob_big.eid}),#{surf_big.eid},.T.)"
)
small_face = f._emit_raw(
    f"ADVANCED_FACE('small_face_adjacent',(#{fob_big.eid}),#{surf_small.eid},.T.)"
)

shell = f.open_shell([big_face, small_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
