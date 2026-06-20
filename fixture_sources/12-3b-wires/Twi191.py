"""Twi191 — ShapeFix_Wire.FixIntersectingEdges parameter-monotonicity.

Catalog claim: Wire with edges whose parameters increase non-monotonically;
FixIntersectingEdges' parameter-sort step destroys the original wire ordering.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 5 edges on a
PLANE. Five line edges each carry a name encoding their position in the
non-monotonic parameter sequence: param_e0 (u=0.0..0.2), param_e1 (u=0.5..0.8),
param_e2 (u=0.1..0.4), param_e3 (u=0.7..1.0), param_e4 (u=0.3..0.6). The UV
pcurves are set so the 2D parameter starts increase in the order
[0.0, 0.5, 0.1, 0.7, 0.3] — non-monotonic. FixIntersectingEdges sorts by
parameter start: [0.0, 0.1, 0.3, 0.5, 0.7], reordering the edges and breaking
the original wire topology. The non-monotonic edge names make the parameter
ordering explicit in bytes.

Byte assertions:
  - contains(b'param_e0')
  - contains(b'param_e4')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi191",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 5 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "5 short line edges forming a closed pentagon with non-monotonic 2D params; "
        "param_e0: A(0,0)->B(2,0) pcurve u=0.0..0.2; "
        "param_e1: B(2,0)->C(3,2) pcurve u=0.5..0.8; "
        "param_e2: C(3,2)->D(1,3) pcurve u=0.1..0.4; "
        "param_e3: D(1,3)->E(-1,2) pcurve u=0.7..1.0; "
        "param_e4: E(-1,2)->A(0,0) pcurve u=0.3..0.6; "
        "non-monotonic parameter sequence [0.0,0.5,0.1,0.7,0.3] IS mechanism; "
        "FixIntersectingEdges IS mechanism — sorts by u-start, reorders to "
        "[param_e0,param_e2,param_e4,param_e1,param_e3], breaking wire topology; "
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

# Pentagon vertices
PA = (0.0,  0.0, 0.0)
PB = (2.0,  0.0, 0.0)
PC = (3.0,  2.0, 0.0)
PD = (1.0,  3.0, 0.0)
PE = (-1.0, 2.0, 0.0)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))
vD = f.vertex_point(f.cartesian_point(PD))
vE = f.vertex_point(f.cartesian_point(PE))


def _line_sc_with_param(v_s, v_e, ps, pe, u_start, u_end, name=""):
    """LINE-based SURFACE_CURVE with explicitly assigned non-monotonic pcurve param."""
    dx = pe[0]-ps[0]; dy = pe[1]-ps[1]; dz = pe[2]-ps[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    ln3 = f.line(f.cartesian_point(ps),
                 f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag))
    # 2D pcurve: starts at (u_start, 0), direction (1,0), length = u_end - u_start
    param_len = u_end - u_start
    uv_orig = f.cartesian_point((u_start, 0.0))
    uv_dir  = f.direction((1.0, 0.0))
    uv_vec  = f.vector(uv_dir, param_len)
    uv_ln   = f.line(uv_orig, uv_vec)
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln.eid}),#*)")
    pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")
    sc      = f._emit_raw(f"SURFACE_CURVE('',#{ln3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# Non-monotonic parameter sequence: [0.0, 0.5, 0.1, 0.7, 0.3]
# e0: A->B, param u=0.0..0.2
ec0 = _line_sc_with_param(vA, vB, PA, PB, 0.0, 0.2, name="param_e0")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: B->C, param u=0.5..0.8
ec1 = _line_sc_with_param(vB, vC, PB, PC, 0.5, 0.8, name="param_e1")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: C->D, param u=0.1..0.4
ec2 = _line_sc_with_param(vC, vD, PC, PD, 0.1, 0.4, name="param_e2")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: D->E, param u=0.7..1.0
ec3 = _line_sc_with_param(vD, vE, PD, PE, 0.7, 1.0, name="param_e3")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# e4: E->A, param u=0.3..0.6
ec4 = _line_sc_with_param(vE, vA, PE, PA, 0.3, 0.6, name="param_e4")
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi191.stp")
