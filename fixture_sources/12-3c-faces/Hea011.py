"""Hea011 — Shape-healing driver runs a runtime-configured operator sequence
over a GEOMETRIC_SET with sub-tolerance EDGE_CURVE, OPEN_SHELL, and same-parameter violation.

Catalog claim: A top-level driver (ShapeProcess::Perform) runs a sequence of
named healing operators ("fix-shape, same-parameter, remove-small-edges").
The fixture establishes the input precondition: a GEOMETRIC_SET compound mixing:
  (a) a sub-tolerance EDGE_CURVE (~1e-7 long) — target of remove-small-edges;
  (b) an OPEN_SHELL with one rectangular face — target of fix-shape;
  (c) an EDGE_CURVE whose 3D length (1.0) disagrees with pcurve length (5.0)
      — target of same-parameter operator.

The operator-list invocation is API-level; the defect is in the input geometry.

Tier-3 assertions:
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea011",
    defect=(
        "GEOMETRIC_SET compound mixing three defect classes: "
        "(a) sub-tolerance EDGE_CURVE 1e-7 long between near-coincident VERTEX_POINTs; "
        "(b) OPEN_SHELL with one 1x1 rectangular ADVANCED_FACE on PLANE; "
        "(c) EDGE_CURVE with 3D LINE length=1.0 but pcurve LINE length=5.0 (same-param violation); "
        "ShapeProcess driver must chain fix-shape + same-parameter + remove-small-edges"
    ),
)

# ── Plane for (b) and (c) ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── (a) Sub-tolerance EDGE_CURVE: 1e-7 between Va(0,0,0) and Vb(1e-7,0,0) ──
p_Va    = f.cartesian_point((0.0, 0.0, 0.0))
p_Vb    = f.cartesian_point((1.0e-7, 0.0, 0.0), name="subtol")
v_Va    = f.vertex_point(p_Va, name="Va")
v_Vb    = f.vertex_point(p_Vb, name="Vb_subtol")
subtol_ln  = f.line(p_Va, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0))
subtol_ec  = f.edge_curve(v_Va, v_Vb, subtol_ln, name="part_a_subtol_edge")

# ── (b) OPEN_SHELL: 1×1 rectangular face at (2,0,0)-(3,1,0) ─────────────────
p_c1 = f.cartesian_point((2.0, 0.0, 0.0))
p_c2 = f.cartesian_point((3.0, 0.0, 0.0))
p_c3 = f.cartesian_point((3.0, 1.0, 0.0))
p_c4 = f.cartesian_point((2.0, 1.0, 0.0))
v_c1 = f.vertex_point(p_c1, name="Vc1")
v_c2 = f.vertex_point(p_c2, name="Vc2")
v_c3 = f.vertex_point(p_c3, name="Vc3")
v_c4 = f.vertex_point(p_c4, name="Vc4")

ec_b = f.edge_curve(v_c1, v_c2, f.line(p_c1, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
ec_r = f.edge_curve(v_c2, v_c3, f.line(p_c2, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
ec_t = f.edge_curve(v_c3, v_c4, f.line(p_c3, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
ec_l = f.edge_curve(v_c4, v_c1, f.line(p_c4, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

loop_b = f.edge_loop([
    f.oriented_edge(ec_b, True),
    f.oriented_edge(ec_r, True),
    f.oriented_edge(ec_t, True),
    f.oriented_edge(ec_l, True),
], name="part_b_face_loop")
fob_b  = f.face_outer_bound(loop_b)
face_b = f.advanced_face([fob_b], plane, name="part_b_face")
shell_b = f.open_shell([face_b], name="part_b_open_shell")

# ── (c) Same-parameter violation: 3D length=1.0, pcurve length=5.0 ───────────
p_d1 = f.cartesian_point((5.0, 0.0, 0.0))
p_d2 = f.cartesian_point((6.0, 0.0, 0.0))
v_d1 = f.vertex_point(p_d1, name="Vd1")
v_d2 = f.vertex_point(p_d2, name="Vd2")
d3_line = f.line(p_d1, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0), name="part_c_3d_len1")
# Pcurve length=5.0 (mismatch with 3D length=1.0)
pc_pt  = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0))")
pc_dir = f._emit_raw("DIRECTION('',(1.0,0.0))")
pc_vec = f._emit_raw(f"VECTOR('',#{pc_dir.eid},5.0)")
pc_ln  = f._emit_raw(f"LINE('part_c_pcurve_len5',#{pc_pt.eid},#{pc_vec.eid})")
def_r  = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',( #{pc_ln.eid}),#{plc.eid})")
pcurve = f._emit_raw(f"PCURVE('',#{plane.eid},#{def_r.eid})")
sc_c   = f._emit_raw(
    f"SURFACE_CURVE('',#{d3_line.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
ec_c = f.edge_curve(v_d1, v_d2, sc_c, name="part_c_sameparam_violation")

# ── GEOMETRIC_SET compound ────────────────────────────────────────────────────
gset = f._emit_raw(
    f"GEOMETRIC_SET('multi_defect_compound',(#{subtol_ec.eid},#{shell_b.eid},#{ec_c.eid}))"
)
# Product chain uses the shell as the model entity
f.add_product_chain(shell_b)

f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea011.stp")
