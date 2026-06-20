"""Twi171 — ShapeFix_Wire.FixReorder reverse-then-forward.

Catalog claim: FixReorder on wire with mixed forward/reverse orientations.
Single-direction sweep misses mixed-mode case; incomplete reordering.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 5 edges on
a PLANE. Four edges are in forward orientation (.T.) and one edge is in
reverse orientation (.F.). The reverse edge is the last in the sequence —
a [forward, forward, forward, forward, reverse] arrangement. FixReorder's
single-direction sweep starts from the first forward edge and propagates; it
handles the reversal at position 4 but the seed-propagation leaves the
reordering incomplete for the mixed case, producing a partial result.

The reversed edge is labelled 'reverse_orientation_edge' to make the defect
explicit in bytes.

Byte assertions:
  - contains(b'reverse_orientation_edge')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi171",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 5 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "pentagon wire: A(0,0)→B(8,0)→C(10,6)→D(5,10)→E(-2,6)→back to A; "
        "edges e0..e3 have orientation .T. (forward); "
        "edge e4 (E→A) has orientation .F. (reverse) IS the defect — "
        "its EDGE_CURVE runs A→E but ORIENTED_EDGE uses reverse_orientation_edge .F.; "
        "FixReorder single-direction sweep from e0 fails to correctly handle "
        "mixed forward/reverse mode at position 4 IS mechanism; "
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

# ── Pentagon vertices ──────────────────────────────────────────────────────────
PA = (0.0,  0.0,  0.0)
PB = (8.0,  0.0,  0.0)
PC = (10.0, 6.0,  0.0)
PD = (5.0,  10.0, 0.0)
PE = (-2.0, 6.0,  0.0)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))
vD = f.vertex_point(f.cartesian_point(PD))
vE = f.vertex_point(f.cartesian_point(PE))


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
    return f._emit_raw(
        f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)"
    )


# e0: A→B forward (.T.)
ec0 = _line_sc(vA, vB, PA, PB)
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: B→C forward (.T.)
ec1 = _line_sc(vB, vC, PB, PC)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: C→D forward (.T.)
ec2 = _line_sc(vC, vD, PC, PD)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: D→E forward (.T.)
ec3 = _line_sc(vD, vE, PD, PE)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# e4: EDGE_CURVE stored as A→E (reversed direction), used with .F. orientation
# — ORIENTED_EDGE(.F.) means "traverse in reverse" so effective direction is E→A
ec4 = _line_sc(vA, vE, PA, PE, name="reverse_orientation_edge")
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.F.)")

# ── EDGE_LOOP: [T, T, T, T, F] — mixed orientation at position 4 ──────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi171.stp")
