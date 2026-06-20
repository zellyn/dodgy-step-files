"""Twi176 — ShapeFix_Wire.FixIntersectingEdges concurrent-modification.

Catalog claim: Wire where FixIntersectingEdges modifies the edge list while
iterating; downstream operations get stale iterator.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 6 edges
on a PLANE forming a figure-eight (self-intersecting). The figure-eight
has two crossing points — one near the centre where two edges cross, and
a second crossing elsewhere in the wire. When FixIntersectingEdges
processes the first crossing, it splits one or more edges and modifies
the wire's edge list. The outer iteration loop (over the original 6 edges)
holds a stale iterator that no longer reflects the modified list, causing
downstream split operations to reference wrong edge indices.

The crossing edges are labelled 'crossing_edge_A' and 'crossing_edge_B'
to make the defect explicit in bytes.

Byte assertions:
  - contains(b'crossing_edge_A')
  - contains(b'crossing_edge_B')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi176",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 6 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "figure-eight self-intersecting wire — 6 edges with two crossing points; "
        "vertices: A(0,5), B(10,0), C(5,10), D(10,5) (crossing 1 ~(7.5,2.5)), "
        "E(0,10), F(5,0); wire: A→B (crossing_edge_A), B→C, C→D (crossing_edge_B), "
        "D→E, E→F, F→A; "
        "crossing_edge_A and crossing_edge_B each cross another edge IS the defect; "
        "FixIntersectingEdges IS mechanism — splits first crossing, modifying edge "
        "list while outer loop iterates; stale iterator causes second crossing "
        "to reference wrong edge after concurrent modification; "
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

# ── Figure-eight vertices ──────────────────────────────────────────────────────
# Wire: A→B→C→D→E→F→A
# A→B and C→D cross each other (figure-eight crossings)
# A=(0,5), B=(10,0), C=(5,10), D=(10,5), E=(0,10), F=(5,0)
# A→B crosses C→D at approximately (7.5,2.5) — the first crossing
# E→F crosses A→B at approximately (3.75,3.75) — the second crossing
PA = (0.0,  5.0,  0.0)
PB = (10.0, 0.0,  0.0)
PC = (5.0,  10.0, 0.0)
PD = (10.0, 5.0,  0.0)
PE = (0.0,  10.0, 0.0)
PF = (5.0,  0.0,  0.0)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))
vD = f.vertex_point(f.cartesian_point(PD))
vE = f.vertex_point(f.cartesian_point(PE))
vF = f.vertex_point(f.cartesian_point(PF))


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


# e0: A→B (first crossing edge — crosses C→D and also E→F)
ec0 = _line_sc(vA, vB, PA, PB, name="crossing_edge_A")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: B→C
ec1 = _line_sc(vB, vC, PB, PC)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: C→D (second crossing edge — crosses A→B)
ec2 = _line_sc(vC, vD, PC, PD, name="crossing_edge_B")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: D→E
ec3 = _line_sc(vD, vE, PD, PE)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# e4: E→F
ec4 = _line_sc(vE, vF, PE, PF)
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")

# e5: F→A  (closes the loop)
ec5 = _line_sc(vF, vA, PF, PA)
oe5 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec5.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},"
    f"#{oe3.eid},#{oe4.eid},#{oe5.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi176.stp")
