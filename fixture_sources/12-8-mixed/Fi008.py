"""Fi008 — Fillet completes partially: HasResult but BadShape.

Catalog claim: The fillet builder finishes producing geometry but the resulting
solid fails downstream validation: self-intersecting fillet surfaces, missing
trimming patches, or non-watertight shell. Kernel returns result + "bad shape".

Fixture: A CLOSED_SHELL with two faces sharing a spine EDGE_CURVE, plus a third
"interfering" face positioned where the rolling ball would graze. The interfering
face forces the fillet geometry to self-intersect mid-spine, producing an invalid
(non-watertight) solid. OCC loads shape(1).

Tier-3: face[0].surface_type == "plane", face[2].surface_type == "plane"
Expected: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Fi008",
    defect=(
        "CLOSED_SHELL: spine EDGE_CURVE shared by two planar faces (face_a, face_b); "
        "third 'interfering' planar face at rolling-ball reach position; "
        "fillet rolling-ball intersects interfering face mid-spine; "
        "HasResult=True but BadShape: self-intersecting fillet patches; "
        "ChFi3d_Builder returns invalid BRep"
    ),
)

# Spine endpoints
p_start = f.cartesian_point((0.0, 0.0, 0.0), name="spine_start")
p_end   = f.cartesian_point((2.0, 0.0, 0.0), name="spine_end")
v_start = f._emit_raw(f"VERTEX_POINT('spine_start',#{p_start.eid})")
v_end   = f._emit_raw(f"VERTEX_POINT('spine_end',#{p_end.eid})")

d_spine   = f.direction((1.0, 0.0, 0.0))
vec_spine = f.vector(d_spine, 2.0)
line_spine = f.line(p_start, vec_spine)
spine_edge = f._emit_raw(
    f"EDGE_CURVE('spine_edge',#{v_start.eid},#{v_end.eid},#{line_spine.eid},.T.)"
)

# Face A: plane normal +Z
z_up   = f.direction((0.0, 0.0, 1.0))
x_ref  = f.direction((1.0, 0.0, 0.0))
plc_a  = f.axis2_placement_3d(p_start, z_up, x_ref)
surf_a = f.plane(plc_a, name="face_a_surface")

# Face B: plane normal +Y (perpendicular to A, sharing the spine)
y_up   = f.direction((0.0, 1.0, 0.0))
plc_b  = f.axis2_placement_3d(p_start, y_up, x_ref)
surf_b = f.plane(plc_b, name="face_b_surface")

# Additional vertices for the shared quad boundary
p2y = f.cartesian_point((2.0, 1.0, 0.0), name="p2y")
p0y = f.cartesian_point((0.0, 1.0, 0.0), name="p0y")
v2y = f.vertex_point(p2y)
v0y = f.vertex_point(p0y)

d_dy   = f.direction((0.0, 1.0, 0.0))
e_rgt  = f.edge_curve(v_end,  v2y, f.line(p_end,  f.vector(d_dy, 1.0)), name="e_rgt")
d_dxn  = f.direction((-1.0, 0.0, 0.0))
e_top  = f.edge_curve(v2y,   v0y, f.line(p2y,   f.vector(d_dxn, 2.0)), name="e_top")
d_dyn  = f.direction((0.0, -1.0, 0.0))
e_lft  = f.edge_curve(v0y,  v_start, f.line(p0y,   f.vector(d_dyn, 1.0)), name="e_lft")

loop_shared = f.edge_loop([
    f.oriented_edge(spine_edge, True),
    f.oriented_edge(e_rgt,     True),
    f.oriented_edge(e_top,     True),
    f.oriented_edge(e_lft,     True),
])
fob_shared = f.face_outer_bound(loop_shared)
face_a = f._emit_raw(f"ADVANCED_FACE('face_a',(#{fob_shared.eid}),#{surf_a.eid},.T.)")
face_b = f._emit_raw(f"ADVANCED_FACE('face_b',(#{fob_shared.eid}),#{surf_b.eid},.T.)")

# Third "interfering" face at (1, 0.5, 0.5) — where the rolling ball would graze
# A triangle: (0.5,0.5,0.5), (1.5,0.5,0.5), (1.0,0.5,1.0)
q0 = f.cartesian_point((0.5, 0.5, 0.5), name="q0")
q1 = f.cartesian_point((1.5, 0.5, 0.5), name="q1")
q2 = f.cartesian_point((1.0, 0.5, 1.0), name="q2")
vq0 = f.vertex_point(q0)
vq1 = f.vertex_point(q1)
vq2 = f.vertex_point(q2)

# Edge q0 → q1 (along +x)
eq01 = f.edge_curve(vq0, vq1, f.line(q0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)), name="eq01")

# Edge q1 → q2
dx12 = 1.0 - 1.5
dz12 = 1.0 - 0.5
m12  = math.sqrt(dx12**2 + dz12**2)
eq12 = f.edge_curve(vq1, vq2,
    f.line(q1, f.vector(f.direction((dx12/m12, 0.0, dz12/m12)), m12)),
    name="eq12")

# Edge q2 → q0
dx20 = 0.5 - 1.0
dz20 = 0.5 - 1.0
m20  = math.sqrt(dx20**2 + dz20**2)
eq20 = f.edge_curve(vq2, vq0,
    f.line(q2, f.vector(f.direction((dx20/m20, 0.0, dz20/m20)), m20)),
    name="eq20")

loop_tri = f.edge_loop([
    f.oriented_edge(eq01, True),
    f.oriented_edge(eq12, True),
    f.oriented_edge(eq20, True),
])
fob_tri = f.face_outer_bound(loop_tri)

# Interfering face plane: normal -Y (pointing toward the spine) at midpoint
interfere_orig = f.cartesian_point((1.0, 0.5, 0.5), name="interfere_origin")
yn  = f.direction((0.0, -1.0, 0.0))
plc_int = f.axis2_placement_3d(interfere_orig, yn, x_ref, name="interfere_axis")
surf_int = f.plane(plc_int, name="interfering_face_surface")
face_int = f._emit_raw(
    f"ADVANCED_FACE('interfering_face',(#{fob_tri.eid}),#{surf_int.eid},.T.)"
)

# CLOSED_SHELL containing all three faces
shell = f.closed_shell([face_a, face_b, face_int])
msb   = f.manifold_solid_brep(shell, name="solid")
f.add_product_chain(msb)
