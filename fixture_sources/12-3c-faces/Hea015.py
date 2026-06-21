"""Hea015 — Shape healing regression: shared EDGE_CURVE between two ADVANCED_FACEs
on same PLANE has duplicate PCURVE_S1_AND_S2 entries.

Catalog claim: Two ADVANCED_FACEs on the same PLANE share one EDGE_CURVE
whose SURFACE_CURVE has two PCURVE entries with
master_representation = .PCURVE_S1_AND_S2. but both pcurves are duplicates
(identical UV start point, identical direction) instead of representing the
two opposite sides. After glue-edges-with-pcurves, the defective heal leaves
only one pcurve attached.

Mechanism: Faces A and B side-by-side on the same PLANE (0,0) to (2,1).
The shared edge E at x=1.0 (from V_S0(1,0) to V_S1(1,1)) has a
SURFACE_CURVE with TWO PCURVE entries (.PCURVE_S1_AND_S2.) that are
duplicates of each other (both at uv_start=(1.0,0.0), direction (0,1)).

Tier-3 assertions:
  n_edges_total >= 8
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(15) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea015",
    defect=(
        "Two ADVANCED_FACEs (A: (0,0)-(1,1), B: (1,0)-(2,1)) on same PLANE "
        "share edge E (x=1.0, from V_S0 to V_S1); "
        "shared edge has SURFACE_CURVE with TWO identical PCURVE entries "
        "(.PCURVE_S1_AND_S2., both at uv_start=(1.0,0.0) direction (0,1)); "
        "glue-edges-with-pcurves drops one pcurve, leaving wrong face binding; "
        "heal regression: pcurve-to-face binding must be preserved"
    ),
)

# ── Shared PLANE for both faces ───────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir, name="shared_plane_repr")
plane = f.plane(plc, name="shared_plane")

# ── 6 perimeter vertices ──────────────────────────────────────────────────────
p_A0 = f.cartesian_point((0.0, 0.0, 0.0))
p_S0 = f.cartesian_point((1.0, 0.0, 0.0))
p_B0 = f.cartesian_point((2.0, 0.0, 0.0))
p_B1 = f.cartesian_point((2.0, 1.0, 0.0))
p_S1 = f.cartesian_point((1.0, 1.0, 0.0))
p_A1 = f.cartesian_point((0.0, 1.0, 0.0))
v_A0 = f.vertex_point(p_A0, name="V_A0")
v_S0 = f.vertex_point(p_S0, name="V_S0")
v_B0 = f.vertex_point(p_B0, name="V_B0")
v_B1 = f.vertex_point(p_B1, name="V_B1")
v_S1 = f.vertex_point(p_S1, name="V_S1")
v_A1 = f.vertex_point(p_A1, name="V_A1")

# ── Plain edges (no pcurve) ───────────────────────────────────────────────────
# Face A perimeter (non-shared edges)
ec_A_bot  = f.edge_curve(v_A0, v_S0, f.line(p_A0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)),
                          name="A_bottom")
ec_A_top  = f.edge_curve(v_S1, v_A1, f.line(p_S1, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)),
                          name="A_top")
ec_A_left = f.edge_curve(v_A1, v_A0, f.line(p_A1, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)),
                          name="A_left")
# Face B perimeter (non-shared edges)
ec_B_bot  = f.edge_curve(v_S0, v_B0, f.line(p_S0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)),
                          name="B_bottom")
ec_B_rgt  = f.edge_curve(v_B0, v_B1, f.line(p_B0, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)),
                          name="B_right")
ec_B_top  = f.edge_curve(v_B1, v_S1, f.line(p_B1, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)),
                          name="B_top")

# ── Shared edge E: SURFACE_CURVE with TWO duplicate PCURVEs ──────────────────
# 3D curve: LINE from V_S0(1,0,0) to V_S1(1,1,0) along +Y
d3_dir  = f.direction((0.0, 1.0, 0.0))
d3_ln   = f.line(p_S0, f.vector(d3_dir, 1.0), name="shared_3d")

# pcurve A: at uv_start=(1.0, 0.0) in face A's UV frame, direction (0,1)
uv_A = f._emit_raw("CARTESIAN_POINT('uv_pcA_start',(1.0,0.0))")
d_A  = f._emit_raw("DIRECTION('',(0.0,1.0))")
v_A  = f._emit_raw(f"VECTOR('',#{d_A.eid},1.0)")
ln_A = f._emit_raw(f"LINE('pcA_uv',#{uv_A.eid},#{v_A.eid})")
dr_A = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('A_repr',(#{ln_A.eid}),#{plc.eid})")
pc_A = f._emit_raw(f"PCURVE('pcurve_A_side',#{plane.eid},#{dr_A.eid})")

# pcurve B: IDENTICAL to pcurve A — same uv_start, same direction (the defect)
uv_B = f._emit_raw("CARTESIAN_POINT('uv_pcB_start',(1.0,0.0))")
d_B  = f._emit_raw("DIRECTION('',(0.0,1.0))")
v_B  = f._emit_raw(f"VECTOR('',#{d_B.eid},1.0)")
ln_B = f._emit_raw(f"LINE('pcB_uv',#{uv_B.eid},#{v_B.eid})")
dr_B = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('B_repr',(#{ln_B.eid}),#{plc.eid})")
pc_B = f._emit_raw(f"PCURVE('pcurve_B_side',#{plane.eid},#{dr_B.eid})")

# SURFACE_CURVE with both pcurves (PCURVE_S1_AND_S2)
sc_E  = f._emit_raw(
    f"SURFACE_CURVE('shared_edge_surface',#{d3_ln.eid},"
    f"(#{pc_A.eid},#{pc_B.eid}),.PCURVE_S1_AND_S2.)"
)
ec_E  = f.edge_curve(v_S0, v_S1, sc_E, name="shared_E_with_two_pcurves")

# ── Face A outer wire: A_bottom, shared_E, A_top, A_left ─────────────────────
loop_A = f.edge_loop([
    f.oriented_edge(ec_A_bot, True),
    f.oriented_edge(ec_E, True),
    f.oriented_edge(ec_A_top, True),
    f.oriented_edge(ec_A_left, True),
])
fob_A  = f.face_outer_bound(loop_A)
face_A = f.advanced_face([fob_A], plane, name="faceA_on_shared_plane")

# ── Face B outer wire: B_bottom, B_right, B_top, shared_E reversed ───────────
loop_B = f.edge_loop([
    f.oriented_edge(ec_B_bot, True),
    f.oriented_edge(ec_B_rgt, True),
    f.oriented_edge(ec_B_top, True),
    f.oriented_edge(ec_E, False),  # reversed: face B uses shared edge in reverse
])
fob_B  = f.face_outer_bound(loop_B)
face_B = f.advanced_face([fob_B], plane, name="faceB_on_shared_plane")

# ── OPEN_SHELL with both faces ────────────────────────────────────────────────
shell = f.open_shell([face_A, face_B], name="two_faces_share_edge_with_two_pcurves")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea015.stp")
