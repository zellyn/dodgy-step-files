"""Twi192 — ShapeFix_Wire.FixGaps2d 2D-only-bridge.

Catalog claim: ShapeFix_Wire.FixGaps2d creates a 2D-only edge whose 3D
coordinates are nonsense when bridging a 2D pcurve gap that doesn't exist in 3D.

Mechanism: Wire on a PLANE has two edges connected at a shared vertex in 3D but
with a discontinuous jump in the 2D pcurve parameter space (0.5 unit gap).
FixGaps2d creates a bridge edge to close the 2D gap. The bridge edge's 3D
geometry is derived from invalid parametrization, resulting in nonsense 3D
coordinates that don't lie on the surface.

The PLANE parameter space maps (u, v) directly to 3D via the axis2 placement.
We set up:
  E0: LINE from P0=(0,0,0) to P1=(5,0,0); pcurve (u:0→5, v=0)    [correct]
  E1: LINE from P1=(5,0,0) to P2=(5,10,0); pcurve (u=5.5, v:0→10) [defect: u jumps 0.5]
  E2: LINE from P2=(5,10,0) to P3=(0,10,0); pcurve (u:5.5→0, v=10) [follows from E1]
  E3: LINE from P3=(0,10,0) to P0=(0,0,0); pcurve (u=0, v:10→0)   [correct]

In 3D all edges are connected correctly (shared vertices). But the pcurve for E1
starts at u=5.5 instead of u=5.0 — there is a 0.5-unit 2D gap in the
u-parameter at the E0/E1 junction. FixGaps2d detects this and inserts a bridge
pcurve segment, but since the plane is parametrized 1:1 with 3D, the bridge
generates a 3D coordinate that is off the expected path (the 0.5 unit step in u
maps to 0.5 unit in x → 3D bridge goes from (5,0) to (5.5,0) in XY, which is
outside the actual 3D geometry of the polygon).

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi192",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; "
        "outer EDGE_LOOP has 4 LINE edges forming a 5x10 rectangle; "
        "all 3D curves and vertices are correct and connected; "
        "E1 pcurve starts at u=5.5 instead of u=5.0 — 0.5-unit 2D gap at "
        "E0/E1 junction in parameter space IS the defect; "
        "E2 pcurve continues from u=5.5 (following E1's defective start); "
        "FixGaps2d bridges the 2D gap but the bridge edge's 3D coordinates "
        "are derived from invalid parametrization — nonsense 3D point at "
        "x=5.5 (outside the rectangle) IS the mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE in "
        "CLOSED_SHELL — never orphaned"
    ),
)

# ── PLANE: normal +Z, origin at (0,0,0) ──────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── 3D Vertices: 5×10 rectangle ─────────────────────────────────────────────
P0 = (0.0,  0.0,  0.0)
P1 = (5.0,  0.0,  0.0)
P2 = (5.0,  10.0, 0.0)
P3 = (0.0,  10.0, 0.0)

v0 = f.vertex_point(f.cartesian_point(P0))
v1 = f.vertex_point(f.cartesian_point(P1))
v2 = f.vertex_point(f.cartesian_point(P2))
v3 = f.vertex_point(f.cartesian_point(P3))


def _pcurve_line(surf, u_start, v_start, du, dv, length):
    """2D line pcurve in plane parameter space (u, v) → (x, y, z)."""
    pc_orig  = f.cartesian_point((u_start, v_start))
    mag = _math.sqrt(du * du + dv * dv)
    pc_dir   = f.direction((du / mag, dv / mag))
    pc_line  = f.line(pc_orig, f.vector(pc_dir, length))
    pc_def   = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{pc_line.eid}),#*)"
    )
    return f._emit_raw(f"PCURVE('',#{surf.eid},#{pc_def.eid})")


# ── E0: P0→P1 (bottom edge), 3D correct, pcurve u:0→5, v=0 ─────────────────
e0_3d = f.line(f.cartesian_point(P0), f.vector(f.direction((1.0, 0.0, 0.0)), 5.0))
pc0   = _pcurve_line(plane, 0.0, 0.0, 1.0, 0.0, 5.0)   # u:0→5, v=0
e0_sc = f._emit_raw(f"SURFACE_CURVE('',#{e0_3d.eid},(#{pc0.eid}),.PCURVE_S1.)")
e0    = f._emit_raw(f"EDGE_CURVE('',#{v0.eid},#{v1.eid},#{e0_sc.eid},.T.)")
oe0   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e0.eid},.T.)")

# ── E1: P1→P2 (right edge), 3D correct, pcurve DEFECT: u=5.5 (not 5.0) ──────
# 3D: correct vertical line at x=5
e1_3d = f.line(f.cartesian_point(P1), f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))
# pcurve DEFECT: starts at u=5.5 instead of u=5.0 → 0.5-unit gap at E0/E1 junction
pc1   = _pcurve_line(plane, 5.5, 0.0, 0.0, 1.0, 10.0)  # u=5.5 IS the defect
e1_sc = f._emit_raw(f"SURFACE_CURVE('',#{e1_3d.eid},(#{pc1.eid}),.PCURVE_S1.)")
e1    = f._emit_raw(f"EDGE_CURVE('',#{v1.eid},#{v2.eid},#{e1_sc.eid},.T.)")
oe1   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e1.eid},.T.)")

# ── E2: P2→P3 (top edge), 3D correct, pcurve continues from u=5.5 ─────────────
e2_3d = f.line(f.cartesian_point(P2), f.vector(f.direction((-1.0, 0.0, 0.0)), 5.0))
pc2   = _pcurve_line(plane, 5.5, 10.0, -1.0, 0.0, 5.5)  # u:5.5→0, v=10
e2_sc = f._emit_raw(f"SURFACE_CURVE('',#{e2_3d.eid},(#{pc2.eid}),.PCURVE_S1.)")
e2    = f._emit_raw(f"EDGE_CURVE('',#{v2.eid},#{v3.eid},#{e2_sc.eid},.T.)")
oe2   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e2.eid},.T.)")

# ── E3: P3→P0 (left edge), 3D and pcurve correct ─────────────────────────────
e3_3d = f.line(f.cartesian_point(P3), f.vector(f.direction((0.0, -1.0, 0.0)), 10.0))
pc3   = _pcurve_line(plane, 0.0, 10.0, 0.0, -1.0, 10.0)  # u=0, v:10→0
e3_sc = f._emit_raw(f"SURFACE_CURVE('',#{e3_3d.eid},(#{pc3.eid}),.PCURVE_S1.)")
e3    = f._emit_raw(f"EDGE_CURVE('',#{v3.eid},#{v0.eid},#{e3_sc.eid},.T.)")
oe3   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e3.eid},.T.)")

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi192.stp")
