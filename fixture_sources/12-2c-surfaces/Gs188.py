"""Gs188 — Onshape SURFACE_OF_REVOLUTION micro-geometry (radius ≈ 0.002 mm) faulty self-import.

Catalog claim: a STEP file with a CLOSED_SHELL containing ADVANCED_FACE entities
on a SURFACE_OF_REVOLUTION whose profile curve is a circular arc of radius ≈ 0.002 mm
(2 microns) revolved 360° around the Z axis. The VERTEX_POINT coordinates are
near-coincident (distance < 1e-6 m = 1 micron). The resulting geometry is valid but
at the sub-tolerance boundary where OCCT's checkshape may flag degenerate edges or
near-coincident vertices, or the revolve may produce a near-degenerate torus.

Expected: fixture may load (small but non-zero geometry) or produce a faulty topology
error; checkshape should flag near-coincident vertices or degenerate edges; the shape
is at the micro-geometry boundary.

Source: https://forum.onshape.com/discussion/22945/step-file-export-import-bug
B4 wave-5 DEF-P. Confidence: MEDIUM — tolerance threshold is implementation-dependent;
fixture demonstrates the class; oracle needed to confirm OCCT behavior.

Byte assertions:
  contains(b'SURFACE_OF_REVOLUTION')
  contains(b'TRIMMED_CURVE')
Tier-3: verify with live oracle (may be shape_null or faulty topology)
Expected: verify with live oracle
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs188",
    defect=(
        "SURFACE_OF_REVOLUTION profile is TRIMMED_CURVE over circle of radius "
        "≈0.002 mm (2 microns) revolved 360° around Z axis; VERTEX_POINT "
        "coordinates near-coincident (distance < 1e-6 m); sub-tolerance "
        "micro-geometry causes faulty topology on Onshape self-import; "
        "checkshape should flag degenerate edges or near-coincident vertices; "
        "SURFACE_OF_REVOLUTION IS ADVANCED_FACE.face_geometry — "
        "OCC may yield shape(1) with healed tolerance or null"
    ),
)

# ── Parameters ────────────────────────────────────────────────────────────────
# Profile: circle of radius R = 0.002 mm centered on the Z axis offset
# to create a revolve body. We place the circle center at (offset, 0, 0)
# where offset = 0.002 mm so the profile circle touches the Z axis.
# This produces a torus-like surface, but the minor radius (0.002 mm) is
# at the micro-geometry boundary.
R_MINOR = 0.002     # mm — profile circle radius (micro-geometry defect)
R_MAJOR = 0.002     # mm — center offset from Z axis (near-coincident to axis)

# ── AXIS1_PLACEMENT for revolution axis (Z axis) ─────────────────────────────
axis_orig = f.cartesian_point((0.0, 0.0, 0.0))
axis_dir  = f.direction((0.0, 0.0, 1.0))
axis1     = f._emit_raw(
    f"AXIS1_PLACEMENT('gs188_axis',#{axis_orig.eid},#{axis_dir.eid})"
)

# ── Profile circle for the arc ────────────────────────────────────────────────
# Circle of radius R_MINOR centered at (R_MAJOR, 0, 0), in the XZ plane.
# The circle placement: center at (R_MAJOR, 0, 0), normal in Y direction.
prof_center  = f.cartesian_point((R_MAJOR, 0.0, 0.0))
prof_norm    = f.direction((0.0, 1.0, 0.0))   # normal to XZ plane
prof_xdir    = f.direction((1.0, 0.0, 0.0))
prof_plc     = f.axis2_placement_3d(prof_center, prof_norm, prof_xdir)
prof_circle  = f._emit_raw(f"CIRCLE('gs188_profile',#{prof_plc.eid},{R_MINOR})")

# ── TRIMMED_CURVE: full circle (trim from 0 to 2π) ───────────────────────────
# Byte assertion: contains(b'TRIMMED_CURVE')
# Trim parameters: 0 to 2*pi for a full revolution profile.
# The two trim points are at angle 0 and 2π (same 3D point — degenerate close).
PI2 = 2.0 * math.pi
# At angle 0: (R_MAJOR + R_MINOR, 0, 0) = (0.004, 0, 0)
# At angle π: (R_MAJOR - R_MINOR, 0, 0) = (0.0, 0, 0) — ON the Z axis!
# Near-coincident defect: the profile arc passes through/near the Z axis.
pt_start = f.cartesian_point((R_MAJOR + R_MINOR, 0.0, 0.0))   # (0.004, 0, 0)
pt_end   = f.cartesian_point((R_MAJOR + R_MINOR, 0.0, 0.0))   # same point (full circle)

tc = f._emit_raw(
    f"TRIMMED_CURVE('gs188_tc',#{prof_circle.eid},"
    f"(PARAMETER_VALUE(0.)),(PARAMETER_VALUE({PI2:.10f})),.T.,.PARAMETER.)"
)

# ── SURFACE_OF_REVOLUTION ─────────────────────────────────────────────────────
# Byte assertion: contains(b'SURFACE_OF_REVOLUTION')
sor = f._emit_raw(
    f"SURFACE_OF_REVOLUTION('gs188_sor',#{tc.eid},#{axis1.eid})"
)

# ── ADVANCED_FACE on the revolution surface ──────────────────────────────────
# Face boundary: use a degenerate seam loop at the start/end of the profile.
# The seam is the profile curve itself (the trim arc's full extent).
# Since the profile is a full circle revolved 360°, the face is topologically
# a torus. We use a minimal seam-edge EDGE_LOOP.
#
# 3D edge: from start point to itself (degenerate seam at u=0)
v_seam = f.vertex_point(pt_start)
e_seam = f._emit_raw(
    f"EDGE_CURVE('gs188_seam',#{v_seam.eid},#{v_seam.eid},#{tc.eid},.T.)"
)
seam_loop = f.edge_loop([f.oriented_edge(e_seam, True)])
fob       = f.face_outer_bound(seam_loop)
face      = f._emit_raw(
    f"ADVANCED_FACE('gs188_face',(#{fob.eid}),#{sor.eid},.T.)"
)

# ── CLOSED_SHELL ─────────────────────────────────────────────────────────────
shell = f._emit_raw(f"CLOSED_SHELL('gs188_shell',(#{face.eid}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('gs188_solid',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")
