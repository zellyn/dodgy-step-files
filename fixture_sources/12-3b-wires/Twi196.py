"""Twi196 — FixDegenerated zero-length-after-trim.

Catalog claim: ShapeFix_Wire.FixDegenerated fails to detect edges that are
non-degenerate as 3D LINE but become zero-length after applying pcurve trim
ranges.

Mechanism: Edge E1 has valid 3D geometry (LINE from (5,0,0) to (15,0,0), 10
units long) but its pcurve trim range is [5.0, 5.0] (zero-width interval — a
single point in parameter space). The 3D curve is geometrically non-degenerate,
so BRep_Tool::Degenerated returns false. However, the effective parametric range
is zero. FixDegenerated only checks pre-marked degeneracy, missing
trim-induced zero-length.

Wire layout on PLANE (normal +Z):
  E0: (0,0,0) → (5,0,0)   — bottom-left, fine
  E1: (5,0,0) → (5,0,0)   — zero-length in pcurve space [5.0,5.0], IS defect
  E2: (5,0,0) → (5,10,0)  — right edge, fine
  E3: (5,10,0)→ (0,10,0)  — top edge, fine
  E4: (0,10,0)→ (0,0,0)   — left edge, fine

The face is a 5×10 rectangle (E1 is degenerate in 2D but non-degenerate in 3D).

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi196",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; outer EDGE_LOOP has 5 "
        "LINE edges; E1 has 3D LINE from (5,0,0) to (15,0,0) — geometrically "
        "non-degenerate — but its pcurve trim range is [5.0,5.0] (zero-width); "
        "BRep_Tool::Degenerated returns false (misses it); FixDegenerated fails "
        "to detect trim-induced zero-length — zero-length-after-trim IS the "
        "mechanism; EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE "
        "in CLOSED_SHELL — never orphaned"
    ),
)

# ── PLANE: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices ─────────────────────────────────────────────────────────────────
P0 = (0.0,  0.0,  0.0)
P1 = (5.0,  0.0,  0.0)
# P2 = same as P1 — E1 is zero-length in pcurve space
P2 = (5.0,  0.0,  0.0)
P3 = (5.0,  10.0, 0.0)
P4 = (0.0,  10.0, 0.0)

v0 = f.vertex_point(f.cartesian_point(P0))
v1 = f.vertex_point(f.cartesian_point(P1))
v2 = f.vertex_point(f.cartesian_point(P2))
v3 = f.vertex_point(f.cartesian_point(P3))
v4 = f.vertex_point(f.cartesian_point(P4))


def _pcurve_line(surf, u_start, v_start, du, dv, length):
    """2D line pcurve in plane parameter space."""
    pc_orig = f.cartesian_point((u_start, v_start))
    mag = _math.sqrt(du * du + dv * dv)
    pc_dir  = f.direction((du / mag, dv / mag))
    pc_line = f.line(pc_orig, f.vector(pc_dir, length))
    pc_def  = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{pc_line.eid}),#*)"
    )
    return f._emit_raw(f"PCURVE('',#{surf.eid},#{pc_def.eid})")


# ── E0: P0→P1, bottom segment, pcurve u:0→5, v=0 ────────────────────────────
e0_3d = f.line(f.cartesian_point(P0), f.vector(f.direction((1.0, 0.0, 0.0)), 5.0))
pc0   = _pcurve_line(plane, 0.0, 0.0, 1.0, 0.0, 5.0)
e0_sc = f._emit_raw(f"SURFACE_CURVE('',#{e0_3d.eid},(#{pc0.eid}),.PCURVE_S1.)")
e0    = f._emit_raw(f"EDGE_CURVE('',#{v0.eid},#{v1.eid},#{e0_sc.eid},.T.)")
oe0   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e0.eid},.T.)")

# ── E1: P1→P2 (zero-length in 2D — IS THE DEFECT) ───────────────────────────
# 3D: valid LINE from (5,0,0) to (15,0,0), 10 units long — non-degenerate
# pcurve: trim range [5.0, 5.0] — zero-width interval; a point in param space
e1_3d = f.line(f.cartesian_point(P1), f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
# pcurve: starts at u=5.0, length=0 IS the defect (zero-width trim)
# We use a non-zero direction but zero trim will be encoded via TRIMMED_CURVE
# Encode as a TRIMMED_CURVE with degenerate [5.0,5.0] trim on top of valid LINE
e1_3d_trimmed = f._emit_raw(
    f"TRIMMED_CURVE('',#{e1_3d.eid},"
    f"(PARAMETER_VALUE(5.0)),(PARAMETER_VALUE(5.0)),.T.,.PARAMETER.)"
)
pc1   = _pcurve_line(plane, 5.0, 0.0, 1.0, 0.0, 1.0)   # pcurve exists but is zero-range
e1_sc = f._emit_raw(f"SURFACE_CURVE('',#{e1_3d_trimmed.eid},(#{pc1.eid}),.PCURVE_S1.)")
e1    = f._emit_raw(f"EDGE_CURVE('',#{v1.eid},#{v2.eid},#{e1_sc.eid},.F.)")
oe1   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e1.eid},.T.)")

# ── E2: P2→P3, right edge, pcurve u=5, v:0→10 ───────────────────────────────
e2_3d = f.line(f.cartesian_point(P2), f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))
pc2   = _pcurve_line(plane, 5.0, 0.0, 0.0, 1.0, 10.0)
e2_sc = f._emit_raw(f"SURFACE_CURVE('',#{e2_3d.eid},(#{pc2.eid}),.PCURVE_S1.)")
e2    = f._emit_raw(f"EDGE_CURVE('',#{v2.eid},#{v3.eid},#{e2_sc.eid},.T.)")
oe2   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e2.eid},.T.)")

# ── E3: P3→P4, top edge, pcurve u:5→0, v=10 ─────────────────────────────────
e3_3d = f.line(f.cartesian_point(P3), f.vector(f.direction((-1.0, 0.0, 0.0)), 5.0))
pc3   = _pcurve_line(plane, 5.0, 10.0, -1.0, 0.0, 5.0)
e3_sc = f._emit_raw(f"SURFACE_CURVE('',#{e3_3d.eid},(#{pc3.eid}),.PCURVE_S1.)")
e3    = f._emit_raw(f"EDGE_CURVE('',#{v3.eid},#{v4.eid},#{e3_sc.eid},.T.)")
oe3   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e3.eid},.T.)")

# ── E4: P4→P0, left edge, pcurve u=0, v:10→0 ────────────────────────────────
e4_3d = f.line(f.cartesian_point(P4), f.vector(f.direction((0.0, -1.0, 0.0)), 10.0))
pc4   = _pcurve_line(plane, 0.0, 10.0, 0.0, -1.0, 10.0)
e4_sc = f._emit_raw(f"SURFACE_CURVE('',#{e4_3d.eid},(#{pc4.eid}),.PCURVE_S1.)")
e4    = f._emit_raw(f"EDGE_CURVE('',#{v4.eid},#{v0.eid},#{e4_sc.eid},.T.)")
oe4   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e4.eid},.T.)")

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))"
)
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi196.stp")
