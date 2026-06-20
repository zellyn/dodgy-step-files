"""Twi132 — ShapeFix_Wire.FixDummySeam non-periodic-surface.

Catalog claim: Wire on PLANE (non-periodic) with edge orientation pattern that
triggers seam-like heuristic. FixDummySeam logic should be a no-op for
non-periodic surfaces but incorrectly evaluates the heuristic trigger conditions.

Fixture: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with 4 edges on a PLANE.
Two of the edges are arranged so their 2D pcurve vectors are anti-parallel,
mimicking a seam edge pattern on a non-periodic surface. FixDummySeam's heuristic
fires because it detects anti-parallel adjacent pcurves but cannot correctly
identify a seam since PLANE has no periodicity.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi132",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "e1: (0,0,0)→(10,0,0) pcurve u:[0→10] v=0; "
        "e2: (10,0,0)→(10,5,0) pcurve v:[0→5] u=10; "
        "e3: (10,5,0)→(0,5,0) pcurve u:[10→0] v=5 — anti-parallel to e1 IS seam-trigger; "
        "e4: (0,5,0)→(0,0,0) pcurve v:[5→0] u=0 — anti-parallel to e2 IS seam-trigger; "
        "FixDummySeam heuristic fires on anti-parallel adjacent pcurves on non-periodic PLANE IS defect; "
        "PLANE has no seam — FixDummySeam should be no-op but incorrectly triggers; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── PLANE: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)


def _pcurve_line(u0, v0, du, dv, length):
    """2D line pcurve on the plane."""
    pc_orig = f.cartesian_point((u0, v0))
    mag = _math.sqrt(du*du + dv*dv)
    pc_dir  = f.direction((du/mag, dv/mag))
    pc_line = f.line(pc_orig, f.vector(pc_dir, length))
    pc_def  = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{pc_line.eid}),#*)")
    return f._emit_raw(f"PCURVE('',#{plane.eid},#{pc_def.eid})")


def _sc_edge(v_s, p_s, v_e, p_e, pc):
    """Build SURFACE_CURVE + EDGE_CURVE for a line segment."""
    dx, dy, dz = p_e[0]-p_s[0], p_e[1]-p_s[1], p_e[2]-p_s[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    line3d = f.line(
        f.cartesian_point(p_s),
        f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag),
    )
    sc = f._emit_raw(f"SURFACE_CURVE('',#{line3d.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# ── Vertices ──────────────────────────────────────────────────────────────────
PA = (0.0,  0.0, 0.0)
PB = (10.0, 0.0, 0.0)
PC = (10.0, 5.0, 0.0)
PD = (0.0,  5.0, 0.0)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))
vD = f.vertex_point(f.cartesian_point(PD))

# e1: A→B, pcurve u:[0→10] v=0 (forward)
pc1 = _pcurve_line(0.0, 0.0, 1.0, 0.0, 10.0)
ec1 = _sc_edge(vA, PA, vB, PB, pc1)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: B→C, pcurve v:[0→5] u=10 (upward)
pc2 = _pcurve_line(10.0, 0.0, 0.0, 1.0, 5.0)
ec2 = _sc_edge(vB, PB, vC, PC, pc2)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: C→D, pcurve u:[10→0] v=5 — ANTI-PARALLEL to e1 (IS seam-trigger)
pc3 = _pcurve_line(10.0, 5.0, -1.0, 0.0, 10.0)
ec3 = _sc_edge(vC, PC, vD, PD, pc3)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# e4: D→A, pcurve v:[5→0] u=0 — ANTI-PARALLEL to e2 (IS seam-trigger)
pc4 = _pcurve_line(0.0, 5.0, 0.0, -1.0, 5.0)
ec4 = _sc_edge(vD, PD, vA, PA, pc4)
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")

# ── EDGE_LOOP: 4 edges ────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi132.stp")
