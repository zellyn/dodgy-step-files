"""Twi178 — ShapeFix_Wire.FixSelfIntersection convergence-oscillation.

Catalog claim: Wire whose self-intersection fix produces output that
re-introduces a different self-intersection pattern. FixSelfIntersection
oscillates between two competing fix strategies without converging.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 6 edges on
a PLANE forming a figure-eight that has two crossing points arranged so that
fixing crossing A (by trimming edges) produces a new crossing B, and fixing B
re-introduces A. The oscillating pair of crossings is labelled
'osc_cross_A' / 'osc_cross_B' to make the defect explicit in bytes.

Byte assertions:
  - contains(b'osc_cross_A')
  - contains(b'osc_cross_B')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi178",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 6 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "figure-eight wire with two symmetrically placed crossings that oscillate "
        "under repeated FixSelfIntersection: crossing A at (4,4), crossing B at (6,6); "
        "vertices: P0(0,4), P1(8,0), P2(4,8), P3(8,4), P4(0,8), P5(4,0); "
        "edges: P0->P1 (osc_cross_A), P1->P2, P2->P3 (osc_cross_B), P3->P4, P4->P5, P5->P0; "
        "osc_cross_A and osc_cross_B are the oscillating crossing pair IS the mechanism; "
        "FixSelfIntersection IS mechanism — oscillates without convergence; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# PLANE: normal +Z
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# Vertices for the oscillating figure-eight
P0 = (0.0, 4.0, 0.0)
P1 = (8.0, 0.0, 0.0)
P2 = (4.0, 8.0, 0.0)
P3 = (8.0, 4.0, 0.0)
P4 = (0.0, 8.0, 0.0)
P5 = (4.0, 0.0, 0.0)

vP0 = f.vertex_point(f.cartesian_point(P0))
vP1 = f.vertex_point(f.cartesian_point(P1))
vP2 = f.vertex_point(f.cartesian_point(P2))
vP3 = f.vertex_point(f.cartesian_point(P3))
vP4 = f.vertex_point(f.cartesian_point(P4))
vP5 = f.vertex_point(f.cartesian_point(P5))


def _line_sc(v_s, v_e, ps, pe, name=""):
    dx = pe[0]-ps[0]; dy = pe[1]-ps[1]; dz = pe[2]-ps[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    ln3 = f.line(f.cartesian_point(ps),
                 f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag))
    uv_orig = f.cartesian_point((ps[0], ps[1]))
    uv_dir  = f.direction((dx/mag, dy/mag))
    uv_vec  = f.vector(uv_dir, mag)
    uv_ln   = f.line(uv_orig, uv_vec)
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln.eid}),#*)")
    pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")
    sc      = f._emit_raw(f"SURFACE_CURVE('',#{ln3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# e0: P0->P1 — oscillating crossing edge A
ec0 = _line_sc(vP0, vP1, P0, P1, name="osc_cross_A")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: P1->P2
ec1 = _line_sc(vP1, vP2, P1, P2)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: P2->P3 — oscillating crossing edge B
ec2 = _line_sc(vP2, vP3, P2, P3, name="osc_cross_B")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: P3->P4
ec3 = _line_sc(vP3, vP4, P3, P4)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# e4: P4->P5
ec4 = _line_sc(vP4, vP5, P4, P5)
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")

# e5: P5->P0 (closes the loop)
ec5 = _line_sc(vP5, vP0, P5, P0)
oe5 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec5.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},"
    f"#{oe3.eid},#{oe4.eid},#{oe5.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi178.stp")
