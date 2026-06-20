"""Tfa217 — curve_copy_trimming

PLANE face whose defect edge uses a nested TRIMMED_CURVE pcurve.
UnionPCurves line 1876 extracts the BasisCurve from the outer TRIMMED_CURVE
and discards the inner bounds, causing the effective trim range to collapse.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a PLANE. The face outer
boundary is a quad EDGE_LOOP where one edge (bottom, "defect edge") has its
curve given by a SURFACE_CURVE whose pcurve wraps a nested TRIMMED_CURVE:
an outer TRIMMED_CURVE [8,12] over an inner TRIMMED_CURVE [5,15] over a
base LINE of length 20. When UnionPCurves extracts the BasisCurve from the
outer TRIMMED_CURVE at line 1876, it finds another TRIMMED_CURVE and
unwraps to the inner basis (line) — discarding the inner bounds [5,15].
The effective range collapses to the outer [8,12] applied directly to the
unit-length line, producing an incorrect parametric range.

Three plain edges complete the quad loop. The face is fully connected.

Byte assertions:
  - contains(b'TRIMMED_CURVE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa217",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on PLANE; "
        "defect edge (bottom): SURFACE_CURVE with nested TRIMMED_CURVE pcurve; "
        "outer TRIMMED_CURVE [8,12] wraps inner TRIMMED_CURVE [5,15] wraps base LINE (len=20); "
        "UnionPCurves line 1876: BasisCurve extraction unwraps outer → finds inner TRIMMED_CURVE; "
        "second unwrap discards inner bounds [5,15]; effective range collapses; "
        "three plain edges complete the quad EDGE_LOOP; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ───────────────────────────────────────
plane_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
surf = f.plane(plane_plc)

# ── Vertices of the quad face: 10×5 rectangle ───────────────────────────────
p_ll = f.cartesian_point((0.0,  0.0, 0.0))
p_lr = f.cartesian_point((10.0, 0.0, 0.0))
p_ur = f.cartesian_point((10.0, 5.0, 0.0))
p_ul = f.cartesian_point((0.0,  5.0, 0.0))

v_ll = f.vertex_point(p_ll)
v_lr = f.vertex_point(p_lr)
v_ur = f.vertex_point(p_ur)
v_ul = f.vertex_point(p_ul)

# ── Bottom edge (v_ll→v_lr): the DEFECT edge with nested TRIMMED_CURVE ──────
# 3D LINE from (0,0,0) to (10,0,0) — correct 3D geometry
bot_3d = f.line(p_ll, f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))

# UV parametric space: base LINE length=20 (twice the edge length)
uv_base_pt  = f._emit_raw("CARTESIAN_POINT('',(0.,0.))")
uv_base_dir = f._emit_raw("DIRECTION('',(1.,0.))")
uv_base_vec = f._emit_raw(f"VECTOR('',#{uv_base_dir.eid},20.)")
uv_base_ln  = f._emit_raw(f"LINE('',#{uv_base_pt.eid},#{uv_base_vec.eid})")

# Inner TRIMMED_CURVE: restricts LINE to [5,15]
uv_tc_inner = f._emit_raw(
    f"TRIMMED_CURVE('',#{uv_base_ln.eid},"
    "(PARAMETER_VALUE(5.)),(PARAMETER_VALUE(15.)),.T.,.PARAMETER.)"
)

# Outer TRIMMED_CURVE: restricts inner TRIMMED_CURVE to [8,12]
# UnionPCurves line 1876 extracts BasisCurve from outer → finds inner TRIMMED_CURVE;
# second extraction loses inner [5,15] bounds — the defect
uv_tc_outer = f._emit_raw(
    f"TRIMMED_CURVE('',#{uv_tc_inner.eid},"
    "(PARAMETER_VALUE(8.)),(PARAMETER_VALUE(12.)),.T.,.PARAMETER.)"
)

# DEFINITIONAL_REPRESENTATION + PCURVE wrapping the nested TRIMMED_CURVE
geom_ctx_2d = f._emit_raw("GEOMETRIC_REPRESENTATION_CONTEXT(2)")
pc_defrep   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{uv_tc_outer.eid}),#{geom_ctx_2d.eid})"
)
bot_pcurve = f._emit_raw(f"PCURVE('',#{surf.eid},#{pc_defrep.eid})")

# SURFACE_CURVE: correct 3D LINE + nested-TRIMMED_CURVE pcurve
bot_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{bot_3d.eid},(#{bot_pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('nested_trim_defect',#{v_ll.eid},#{v_lr.eid},#{bot_sc.eid},.T.)"
)

# ── Right, top, left edges: plain LINE edges ──────────────────────────────────
e_rgt = f.edge_curve(v_lr, v_ur, f.line(p_lr, f.vector(f.direction(( 0.0, 1.0, 0.0)),  5.0)))
e_top = f.edge_curve(v_ur, v_ul, f.line(p_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
e_lft = f.edge_curve(v_ul, v_ll, f.line(p_ul, f.vector(f.direction(( 0.0,-1.0, 0.0)),  5.0)))

# ── EDGE_LOOP using _emit_raw for the defect edge, builder API for the rest ───
oe_bot = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e_bot.eid},.T.)")
oe_rgt = f.oriented_edge(e_rgt, True)
oe_top = f.oriented_edge(e_top, True)
oe_lft = f.oriented_edge(e_lft, True)

face_loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_rgt.eid},#{oe_top.eid},#{oe_lft.eid}))"
)
fob  = f._emit_raw(f"FACE_OUTER_BOUND('',#{face_loop.eid},.T.)")
face = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{surf.eid},.T.)")

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa217.stp")
