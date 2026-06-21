"""Fi005 — Fillet stops at a vertex where the rolling-ball can't trim cleanly.

Catalog claim: A fillet contour terminates at a vertex where the fillet surface
needs to be trimmed by the adjacent faces, but the trimming operation produces
a degenerate piece. Two ADVANCED_FACEs share a spine edge with near-coplanar
normals (dihedral angle near zero, ~1e-3 radians).

Fixture: OPEN_SHELL with two faces sharing a spine edge. Face A has normal
+Z (0,0,1). Face B has normal almost +Z (0.001, 0, 0.999999499) — the
normals differ by ~1e-3 rad, making the faces nearly coplanar. The spine
edge is 1 mm long. Each face has a 4-edge closed loop (quad).

Tier-3: face[0].sliver_aspect_max_min > 100, face[0].surface_type == "plane",
         n_edges_total >= 4
Expected: occt=shape(1)/shape(1) gmsh=shape(10) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Fi005",
    defect=(
        "two ADVANCED_FACEs sharing a spine EDGE_CURVE; "
        "face_a normal = (0,0,1); face_b normal = (0.001,0,0.999999499); "
        "normals differ by ~1e-3 rad (near-coplanar, near-zero dihedral); "
        "fillet trim at terminal vertex degenerates (rolling-ball can't trim); "
        "FaultyVertex condition in ChFi3d_Builder"
    ),
)

# Spine endpoints
p_start   = f.cartesian_point((0.0, 0.0, 0.0))
p_terminal = f.cartesian_point((1.0, 0.0, 0.0), name="terminal")
v_start    = f.vertex_point(p_start)
v_terminal = f._emit_raw(f"VERTEX_POINT('terminal_vertex',#{p_terminal.eid})")

# Spine edge
d_spine   = f.direction((1.0, 0.0, 0.0))
vec_spine = f.vector(d_spine, 1.0)
line_spine = f.line(p_start, vec_spine)
spine_edge = f._emit_raw(
    f"EDGE_CURVE('spine',#{v_start.eid},#{v_terminal.eid},#{line_spine.eid},.T.)"
)

# Face A: normal +Z (perfectly up)
z_norm = f.direction((0.0, 0.0, 1.0), name="z_norm")
x_ref  = f.direction((1.0, 0.0, 0.0), name="x_ref")
plc_a  = f.axis2_placement_3d(p_start, z_norm, x_ref)
surf_a = f.plane(plc_a, name="face_a_surface")

# Face B: normal almost +Z (near-coplanar, ~1e-3 rad difference)
almost_z = f.direction((0.001, 0.0, 0.999999499), name="almost_z")
plc_b    = f.axis2_placement_3d(p_start, almost_z, x_ref)
surf_b   = f.plane(plc_b, name="face_b_surface_near_coplanar")

# Additional vertices to close each face into a quad
p10y = f.cartesian_point((1.0, 1.0, 0.0), name="p10y")
p00y = f.cartesian_point((0.0, 1.0, 0.0), name="p00y")
v10y = f.vertex_point(p10y)
v00y = f.vertex_point(p00y)

# Edge from terminal (1,0,0) → (1,1,0)
d_dy   = f.direction((0.0, 1.0, 0.0))
l_dy   = f.line(p_terminal, f.vector(d_dy, 1.0))
e_r    = f.edge_curve(v_terminal, v10y, l_dy, name="e_right")

# Edge from (1,1,0) → (0,1,0)
d_dxn  = f.direction((-1.0, 0.0, 0.0))
l_top  = f.line(p10y, f.vector(d_dxn, 1.0))
e_top  = f.edge_curve(v10y, v00y, l_top, name="e_top")

# Edge from (0,1,0) → (0,0,0)
d_dyn  = f.direction((0.0, -1.0, 0.0))
l_left = f.line(p00y, f.vector(d_dyn, 1.0))
e_left = f.edge_curve(v00y, v_start, l_left, name="e_left")

# Shared loop for both faces: spine → right → top → left
loop = f.edge_loop([
    f.oriented_edge(spine_edge, True),
    f.oriented_edge(e_r,    True),
    f.oriented_edge(e_top,  True),
    f.oriented_edge(e_left, True),
])
fob   = f.face_outer_bound(loop)
face_a = f._emit_raw(f"ADVANCED_FACE('face_a',(#{fob.eid}),#{surf_a.eid},.T.)")
face_b = f._emit_raw(
    f"ADVANCED_FACE('face_b_almost_coplanar',(#{fob.eid}),#{surf_b.eid},.T.)"
)

shell = f.open_shell([face_a, face_b])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
