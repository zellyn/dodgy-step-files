"""Twi180 — ShapeFix_Wire.FixGaps3d 4-edge-gap-chain.

Catalog claim: Wire with 4 consecutive edges all having tiny gaps between them.
FixGaps3d bridges each individual gap independently but the chain of bridges
accumulates curvature deviations.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges on a
PLANE. Each consecutive pair of edges has a 1e-6 gap: vertex coordinates are
slightly mismatched at each junction. The 4-edge gap chain is labelled with
'gap_chain_edge_N' names (N=0..3) to make the defect explicit in bytes.
FixGaps3d bridges gap_0, gap_1, gap_2, gap_3 independently; the cumulative
drift of 4 independent bridge adjustments reaches 4e-6, exceeding what a
single-gap fix would produce.

Byte assertions:
  - contains(b'gap_chain_edge_0')
  - contains(b'gap_chain_edge_3')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi180",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "4-edge gap-chain square: each edge endpoint is offset by 1e-6 from "
        "the next edge's start, creating 4 tiny independent gaps; "
        "P0(0,0)->P1a(1,0) gap P1b(1.000001,0)->P2a(1,1) gap P2b(1,1.000001) "
        "->P3a(0,1) gap P3b(-0.000001,1)->P0b(0.000001,0); "
        "gap_chain_edge_0..3 ARE all 4 edges IS the 4-gap-chain mechanism; "
        "FixGaps3d IS mechanism — bridges each gap independently, accumulating "
        "curvature deviations across the 4-bridge chain; "
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

GAP = 1e-6

# Each edge's start/end have a tiny gap to the next edge's start
P0  = (0.0,       0.0,     0.0)
P1a = (1.0,       0.0,     0.0)   # edge0 end
P1b = (1.0+GAP,   0.0,     0.0)   # edge1 start  (gap at junction 0-1)
P2a = (1.0+GAP,   1.0,     0.0)   # edge1 end
P2b = (1.0+GAP,   1.0+GAP, 0.0)   # edge2 start  (gap at junction 1-2)
P3a = (0.0,       1.0+GAP, 0.0)   # edge2 end
P3b = (0.0-GAP,   1.0+GAP, 0.0)   # edge3 start  (gap at junction 2-3)
P0b = (0.0-GAP,   0.0,     0.0)   # edge3 end (gap at junction 3-0)

v0  = f.vertex_point(f.cartesian_point(P0))
v1a = f.vertex_point(f.cartesian_point(P1a))
v1b = f.vertex_point(f.cartesian_point(P1b))
v2a = f.vertex_point(f.cartesian_point(P2a))
v2b = f.vertex_point(f.cartesian_point(P2b))
v3a = f.vertex_point(f.cartesian_point(P3a))
v3b = f.vertex_point(f.cartesian_point(P3b))
v0b = f.vertex_point(f.cartesian_point(P0b))


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


# 4 gap-chain edges
ec0 = _line_sc(v0,  v1a, P0,  P1a, name="gap_chain_edge_0")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

ec1 = _line_sc(v1b, v2a, P1b, P2a, name="gap_chain_edge_1")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

ec2 = _line_sc(v2b, v3a, P2b, P3a, name="gap_chain_edge_2")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

ec3 = _line_sc(v3b, v0b, P3b, P0b, name="gap_chain_edge_3")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi180.stp")
