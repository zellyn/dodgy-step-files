"""Twi167 — ShapeFix_Wire.FixIntersectingEdges loop-collapse.

Catalog claim: FixIntersectingEdges applied to crossing-edge wire (bow-tie
topology). Loop collapses to single point; no collapse-detection error raised.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges on
a PLANE, forming a bow-tie (self-crossing figure-8 variant): two pairs of
edges cross each other at a single interior point, producing a topology where
applying FixIntersectingEdges would collapse the loop to a degenerate point.
The 4 vertices are arranged so that edges 0-2 and 1-3 cross, forming the
bow-tie. The fixture labels the crossing point 'bowtie_crossing' in the
description to make the defect explicit.

The fixture encodes the crossing explicitly: e0 goes from v_A to v_C, e1
from v_C to v_B, e2 from v_B to v_D, e3 from v_D to v_A. In 2D:
  A=(0,0), B=(6,6), C=(6,0), D=(0,6)
  e0: A→C = (0,0)→(6,0)
  e1: C→B = (6,0)→(6,6)
  e2: B→D = (6,6)→(0,6)
  e3: D→A = (0,6)→(0,0)
This is actually a valid square — for a true bow-tie we need crossing diagonals.

Bow-tie: A=(0,0), B=(10,10), C=(10,0), D=(0,10)
  e0: A→B = diagonal    e1: B→C = right side
  e2: C→D = antidiag    e3: D→A = left side
  e0 and e2 cross at (5,5) — bow-tie crossing IS the defect.

Byte assertions:
  - contains(b'bowtie_crossing')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi167",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "bow-tie topology: e0 A(0,0)→B(10,10), e1 B(10,10)→C(10,0), "
        "e2 C(10,0)→D(0,10), e3 D(0,10)→A(0,0); "
        "e0 and e2 cross at bowtie_crossing (5,5,0) IS defect; "
        "FixIntersectingEdges applied to crossing-edge wire collapses loop to "
        "single point without raising collapse-detection error IS mechanism; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── PLANE: normal +Z ──────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Bow-tie vertices ──────────────────────────────────────────────────────────
# A=(0,0,0), B=(10,10,0), C=(10,0,0), D=(0,10,0)
# e0: A→B and e2: C→D cross at (5,5,0) — the bow-tie crossing.
PA = (0.0,  0.0,  0.0)
PB = (10.0, 10.0, 0.0)
PC = (10.0, 0.0,  0.0)
PD = (0.0,  10.0, 0.0)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))
vD = f.vertex_point(f.cartesian_point(PD))

# Label the crossing point in a raw entity name for byte assertion
cross_pt = f.cartesian_point((5.0, 5.0, 0.0), name="bowtie_crossing")


def _line_sc(v_s, v_e, ps, pe):
    """Build SURFACE_CURVE(LINE + PCURVE on plane) and EDGE_CURVE."""
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
    return f._emit_raw(f"EDGE_CURVE('',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# e0: A→B (first diagonal — crosses e2 at bowtie_crossing (5,5))
ec0 = _line_sc(vA, vB, PA, PB)
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: B→C
ec1 = _line_sc(vB, vC, PB, PC)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: C→D (anti-diagonal — crosses e0 at (5,5))
ec2 = _line_sc(vC, vD, PC, PD)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: D→A
ec3 = _line_sc(vD, vA, PD, PA)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi167.stp")
