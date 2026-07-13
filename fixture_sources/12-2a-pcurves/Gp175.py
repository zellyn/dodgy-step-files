"""Gp175 — Missing pcurve on one edge of an otherwise-healthy closed wire.

Work packet D1 (occt-coverage/WORK_PACKETS.md), item `bc-no-curve-on-surface`
(GAP, reclassified from §1a): "Single planar or cylindrical face, one boundary
edge with a real 3D curve but no pcurve entity and no other edges/faces
malformed enough to crash OCCT before BRepCheck runs (unlike Gp001/Gp042's
signal 11)."

Why Gp001/Gp042 crash (isolated empirically, not just by inspection): both
fixtures wrap their defective edge's 3D LINE in a SURFACE_CURVE whose
associated_geometry list is empty ('()') while master_representation is
still .PCURVE_S1. -- a self-contradictory pairing (the enum says "use
associated_geometry[0] as the representative curve" but that list has zero
elements). That combination reproduces signal(11) even when embedded in an
otherwise-healthy CLOSED 4-edge wire (verified directly: swapping master_
representation to .CURVE_3D. while keeping the empty-list SURFACE_CURVE
wrapper still crashes). The crash is therefore not about wire topology at
all -- it is specifically about using the SURFACE_CURVE wrapper (whose whole
purpose is to bundle a 3D curve with its pcurve(s)) when there are no
pcurves to bundle.

This fixture isolates the pcurve defect from that confounder: the host face
is a normal, valid, CLOSED 4-edge rectangular wire on a PLANE (the exact
topology used successfully by dozens of neighbor fixtures, e.g. Gp034/Gp045),
and the defective bottom edge's edge_geometry slot references the bare 3D
LINE directly -- no SURFACE_CURVE wrapper at all, which is the schema-clean
way to say "this edge has no parametric representation whatsoever" (rather
than a SURFACE_CURVE that promises pcurves and delivers none). The other
three edges are fully healthy (3D curve + pcurve via SURFACE_CURVE), so
nothing else in the file is malformed enough to crash the reader before
validity checking runs. Verified live: OCCT heals it (FixAddPCurve
reconstructs the missing pcurve by projection) and returns shape(1);
gmsh triangulates to shape(9).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp175",
    defect=(
        "Bottom edge of an otherwise-healthy closed 4-edge rectangular wire "
        "on a PLANE references a bare 3D LINE (no SURFACE_CURVE wrapper, no "
        "PCURVE) as its edge_geometry. Isolated from Gp001/Gp042's crash "
        "confounder: an empty-list SURFACE_CURVE(...,(),.PCURVE_S1.) wrapper "
        "segfaults OCCT regardless of wire topology; omitting the wrapper "
        "entirely lets FixAddPCurve reconstruct the pcurve by projection."
    ),
)

# Flat PLANE at Z=0 as the host surface.
p_orig = f.cartesian_point((0.0, 0.0, 0.0))
p_norm = f.direction((0.0, 0.0, 1.0))
p_ref = f.direction((1.0, 0.0, 0.0))
p_axis = f.axis2_placement_3d(p_orig, p_norm, p_ref)
plane = f.plane(p_axis)

# UV parametric context (the plane's own XY is UV).
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Rectangle corners (Z=0): A=(0,0,0) B=(10,0,0) C=(10,5,0) D=(0,5,0)
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((10.0, 0.0, 0.0))
p_c = f.cartesian_point((10.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

# ---- Bottom edge A->B: THE DEFECT. Real 3D LINE, but NO pcurve. ----
d_ab = f.direction((1.0, 0.0, 0.0))
v_ab = f.vector(d_ab, 10.0)
line_ab = f.line(p_a, v_ab)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('bottom_edge',#{v_a.eid},#{v_b.eid},#{line_ab.eid},.T.)"
)

# ---- Right edge B->C: healthy (3D curve + pcurve). ----
d_bc = f.direction((0.0, 1.0, 0.0))
v_bc = f.vector(d_bc, 5.0)
line_bc = f.line(p_b, v_bc)
pc_right_start = f.cartesian_point((10.0, 0.0))
pc_right_dir = f.direction((0.0, 1.0))
pc_right_vec = f.vector(pc_right_dir, 5.0)
pc_right_line = f.line(pc_right_start, pc_right_vec)
pc_right_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_right',(#{pc_right_line.eid}),#{prc.eid})"
)
pcurve_right = f._emit_raw(f"PCURVE('right_pc',#{plane.eid},#{pc_right_def.eid})")
sc_right = f._emit_raw(
    f"SURFACE_CURVE('right_edge',#{line_bc.eid},(#{pcurve_right.eid}),.PCURVE_S1.)"
)
edge_right = f._emit_raw(
    f"EDGE_CURVE('right_edge',#{v_b.eid},#{v_c.eid},#{sc_right.eid},.T.)"
)

# ---- Top edge D->C, traversed reversed C->D in the loop: healthy. ----
d_dc = f.direction((1.0, 0.0, 0.0))
v_dc = f.vector(d_dc, 10.0)
line_dc = f.line(p_d, v_dc)
pc_top_start = f.cartesian_point((0.0, 5.0))
pc_top_dir = f.direction((1.0, 0.0))
pc_top_vec = f.vector(pc_top_dir, 10.0)
pc_top_line = f.line(pc_top_start, pc_top_vec)
pc_top_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_pc',#{plane.eid},#{pc_top_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top_edge',#{line_dc.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
edge_top = f._emit_raw(
    f"EDGE_CURVE('top_edge',#{v_d.eid},#{v_c.eid},#{sc_top.eid},.T.)"
)

# ---- Left edge D->A: healthy. ----
d_da = f.direction((0.0, -1.0, 0.0))
v_da = f.vector(d_da, 5.0)
line_da = f.line(p_d, v_da)
pc_left_start = f.cartesian_point((0.0, 5.0))
pc_left_dir = f.direction((0.0, -1.0))
pc_left_vec = f.vector(pc_left_dir, 5.0)
pc_left_line = f.line(pc_left_start, pc_left_vec)
pc_left_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_left',(#{pc_left_line.eid}),#{prc.eid})"
)
pcurve_left = f._emit_raw(f"PCURVE('left_pc',#{plane.eid},#{pc_left_def.eid})")
sc_left = f._emit_raw(
    f"SURFACE_CURVE('left_edge',#{line_da.eid},(#{pcurve_left.eid}),.PCURVE_S1.)"
)
edge_left = f._emit_raw(
    f"EDGE_CURVE('left_edge',#{v_d.eid},#{v_a.eid},#{sc_left.eid},.T.)"
)

# Loop: bot(fwd A->B, DEFECT) -> right(fwd B->C) -> top(rev C->D) -> left(fwd D->A)
loop = f.edge_loop([
    f.oriented_edge(edge_bot, True),
    f.oriented_edge(edge_right, True),
    f.oriented_edge(edge_top, False),
    f.oriented_edge(edge_left, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
