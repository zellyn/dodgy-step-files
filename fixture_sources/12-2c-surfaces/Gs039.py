"""Gs039 — Helical sweep / variable-radius blend silently emitted as incomplete shell.

Catalog claim: A SHELL_BASED_SURFACE_MODEL carries only one face — a
SPHERICAL_SURFACE cap whose FACE_OUTER_BOUND is a degenerate VERTEX_LOOP at
a single equator vertex — with side walls and other caps missing. Silent
incomplete shell from a failed helix-sweep or variable-radius blend
round-trip.

OCC behavior: silently accepts cap-only shell as zero-volume body (empty
result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SPHERICAL_SURFACE IS the ADVANCED_FACE.face_geometry.
  - FACE_OUTER_BOUND references a VERTEX_LOOP (single degenerate point at
    the equator vertex) instead of a proper EDGE_LOOP — this IS the defect.
  - The face is the only face in an OPEN_SHELL, producing a zero-volume body.
  - Byte assertions: contains(b'SPHERICAL_SURFACE('),
                     contains(b'VERTEX_LOOP('),
                     contains(b'OPEN_SHELL(').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SPHERICAL_SURFACE IS the ADVANCED_FACE.face_geometry;
    VERTEX_LOOP (degenerate single-point boundary) IS the FACE_OUTER_BOUND;
    degenerate VERTEX_LOOP IS wired into face topology.
  - shape_null driver: zero-volume cap-only shell; strict kernels detect
    missing side walls and produce null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs039",
    defect=(
        "SPHERICAL_SURFACE IS ADVANCED_FACE.face_geometry; "
        "VERTEX_LOOP (single degenerate equator point) IS FACE_OUTER_BOUND; "
        "cap-only OPEN_SHELL with zero volume; "
        "degenerate VERTEX_LOOP IS wired into face topology; shape(1) (live OCC heals)"
    ),
)

# ── SPHERICAL_SURFACE (the cap face surface) ──────────────────────────────────
# Byte assertion: contains(b'SPHERICAL_SURFACE(')
orig   = f.cartesian_point((0.0, 0.0, 0.0))
zdir   = f.direction((0.0, 0.0, 1.0))
xdir   = f.direction((1.0, 0.0, 0.0))
ax3    = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs039_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})"
)
sphere = f._emit_raw(f"SPHERICAL_SURFACE('gs039_sphere',#{ax3.eid},5.0)")

# ── VERTEX_LOOP: degenerate single-point boundary at equator ─────────────────
# Byte assertion: contains(b'VERTEX_LOOP(')
equator_pt = f.cartesian_point((5.0, 0.0, 0.0))
equator_v  = f.vertex_point(equator_pt)
vtx_loop   = f._emit_raw(f"VERTEX_LOOP('gs039_vloop',#{equator_v.eid})")

# FACE with VERTEX_LOOP as its outer bound — the defect IS here.
fob  = f._emit_raw(f"FACE_OUTER_BOUND('',#{vtx_loop.eid},.T.)")
face = f._emit_raw(f"ADVANCED_FACE('gs039_cap',(#{fob.eid}),#{sphere.eid},.T.)")

# OPEN_SHELL: only one face (cap), side walls missing.
# Byte assertion: contains(b'OPEN_SHELL(')
shell = f._emit_raw(f"OPEN_SHELL('gs039_shell',(#{face.eid}))")
sbsm  = f._emit_raw(
    f"SHELL_BASED_SURFACE_MODEL('gs039_sbsm',(#{shell.eid}))"
)
f.add_product_chain(sbsm)
