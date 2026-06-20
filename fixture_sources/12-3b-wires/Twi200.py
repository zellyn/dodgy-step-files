"""Twi200 — ShapeAnalysis_Wire.CheckOrder cycle-vs-acyclic.

Catalog claim: Wire that's actually a graph (with branches) but presented as
wire; CheckOrder fails to detect non-linear topology.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 3 edges on a
PLANE. Vertex H at (1,0,0) is shared by two edges as their start point
('branch_e1' and 'branch_e2') while only one edge arrives there ('main_e0').
This creates a branching structure — degree-3 vertex — which is not a valid
wire. CheckOrder sees 3 edges in a loop but misses the branching topology
since vertex H has in-degree=1 and out-degree=2. The branching vertex IS
the mechanism.

Byte assertions:
  - contains(b'branch_e1')
  - contains(b'branch_e2')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi200",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "main_e0: A(0,0,0)->H(1,0,0) — single incoming edge to hub vertex H; "
        "branch_e1: H(1,0,0)->B(2,1,0) — first outgoing branch from H; "
        "branch_e2: H(1,0,0)->C(2,-1,0) — second outgoing branch from H; "
        "vertex H has in-degree=1, out-degree=2 — branching topology; "
        "branching degree-3 vertex IS defect — not a valid closed wire; "
        "CheckOrder IS mechanism — sees 3 edges but misses branching; "
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

# Vertices
PA = (0.0, 0.0,  0.0)   # start of incoming edge
PH = (1.0, 0.0,  0.0)   # hub vertex — degree-3 branching point
PB = (2.0, 1.0,  0.0)   # branch 1 endpoint
PC = (2.0, -1.0, 0.0)   # branch 2 endpoint

vA = f.vertex_point(f.cartesian_point(PA))
vH = f.vertex_point(f.cartesian_point(PH))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))


def _line_sc(v_s, v_e, ps, pe, name=""):
    dx = pe[0] - ps[0]; dy = pe[1] - ps[1]; dz = pe[2] - ps[2]
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


# main_e0: A->H (single incoming edge to hub)
ec0 = _line_sc(vA, vH, PA, PH, name="main_e0")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# branch_e1: H->B (first outgoing branch)
ec1 = _line_sc(vH, vB, PH, PB, name="branch_e1")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# branch_e2: H->C (second outgoing branch — branching IS the defect)
ec2 = _line_sc(vH, vC, PH, PC, name="branch_e2")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi200.stp")
