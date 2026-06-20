"""Tfa221 — FixMissingSeam.null-surface-guard

Degenerated TOROIDAL_SURFACE (R=0.5, r=1.0) where the minor radius exceeds
the major radius, creating a self-intersecting torus. Tests the null-surface
guard at ShapeFix_Face.cxx:1724: if mySurf.IsNull() guard is omitted, a null
dereference at IsUClosed() crashes the kernel.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a TOROIDAL_SURFACE with
major_radius=0.5 and minor_radius=1.0. This degenerated configuration (r > R)
causes the surface representation to be geometrically invalid (the hole
collapses and self-intersects). The face outer boundary is a quad EDGE_LOOP
with 4 straight LINE edges forming a square near the origin.

The OCCT ShapeFix_Face.FixMissingSeam code path at line 1724 checks
`if (mySurf.IsNull()) return Standard_False` before calling `IsUClosed()`.
Without this guard, the surface handle would dereference null on the
degenerated torus, causing a crash. The canonical PRODUCT chain is used.
All DIRECTION ratios have unit magnitude.

Byte assertions:
  - contains(b'TOROIDAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa221",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on TOROIDAL_SURFACE; "
        "major_radius=0.5, minor_radius=1.0 (r > R: degenerated/self-intersecting torus); "
        "quad EDGE_LOOP: 4 straight LINE edges forming 1×1 square in XY at z=0; "
        "ShapeFix_Face.cxx line 1724: null-surface guard; "
        "degenerated torus: surface handle becomes null in some traversal paths; "
        "without guard: null dereference at IsUClosed() → crash; "
        "canonical PRODUCT chain; unit-magnitude DIRECTION ratios; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── TOROIDAL_SURFACE: degenerated (R=0.5, r=1.0: minor > major) ──────────────
torus_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
# Degenerated torus: r=1.0 > R=0.5 — self-intersecting, triggers null-surface guard
torus_surf = f.toroidal_surface(torus_plc, 0.5, 1.0)

# ── Quad EDGE_LOOP: 1×1 square in XY plane ───────────────────────────────────
p_ll = f.cartesian_point((0.0, 0.0, 0.0))
p_lr = f.cartesian_point((1.0, 0.0, 0.0))
p_ur = f.cartesian_point((1.0, 1.0, 0.0))
p_ul = f.cartesian_point((0.0, 1.0, 0.0))

v_ll = f.vertex_point(p_ll)
v_lr = f.vertex_point(p_lr)
v_ur = f.vertex_point(p_ur)
v_ul = f.vertex_point(p_ul)

e_bot = f.edge_curve(v_ll, v_lr, f.line(p_ll, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
e_rgt = f.edge_curve(v_lr, v_ur, f.line(p_lr, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
e_top = f.edge_curve(v_ur, v_ul, f.line(p_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_lft = f.edge_curve(v_ul, v_ll, f.line(p_ul, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

face_loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], torus_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa221.stp")
