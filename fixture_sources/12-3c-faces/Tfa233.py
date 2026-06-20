"""Tfa233 — FixPeriodicDegenerated context transformation

Periodic surface (SURFACE_OF_REVOLUTION) with B-spline profile curve and
degenerate seam closure. Tests context-aware transformation dispatch when
healing context is non-null; validates Context().IsNull() check and Apply()
invocation.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a SURFACE_OF_REVOLUTION
derived from a B-spline profile curve revolved around the Z-axis. The seam
closure is degenerate: the loop uses the profile edge forward then reversed,
creating a degenerate seam where the period boundary collapses. The
ShapeFix_Face::FixPeriodicDegenerated() context-aware transform path checks
Context().IsNull() before applying the context transformation via Apply();
when context is non-null the Apply() path is taken. The fixture exercises the
context-dispatch branch by providing a periodic surface with a degenerate
seam edge.

Byte assertions:
  - contains(b'SURFACE_OF_REVOLUTION')
  - contains(b'B_SPLINE_CURVE_WITH_KNOTS')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa233",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on SURFACE_OF_REVOLUTION; "
        "profile: B_SPLINE_CURVE_WITH_KNOTS degree=2, 3 control pts at x=1,2,1; "
        "axis: Z-axis through origin; full revolution; "
        "degenerate seam: EDGE_LOOP uses profile edge forward+reversed; "
        "ShapeFix_Face::FixPeriodicDegenerated() context dispatch: "
        "Context().IsNull() check gates Apply() invocation; "
        "non-null context → Apply() path taken; "
        "degenerate seam exercises periodic context-transform branch; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── B-spline profile curve: arc-like shape from (1,0,0) to (1,0,2) ────────────
# Degree 2, 3 control points — a gentle arc in the XZ plane
# Control points: start at (1,0,0), mid at (2,0,1), end at (1,0,2)
cp0 = f.cartesian_point((1.0, 0.0, 0.0))
cp1 = f.cartesian_point((2.0, 0.0, 1.0))
cp2 = f.cartesian_point((1.0, 0.0, 2.0))

# degree=2, n=3 → sum(mults)=3+2+1=6 → [3,3] at [0,1]
profile_curve = f.b_spline_curve_with_knots(
    2,
    [cp0, cp1, cp2],
    [3, 3],
    [0.0, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
)

# ── Axis of revolution: Z-axis through origin ─────────────────────────────────
axis_orig = f.cartesian_point((0.0, 0.0, 0.0))
axis_zdir = f.direction((0.0, 0.0, 1.0))
axis_xdir = f.direction((1.0, 0.0, 0.0))
axis_plc = f.axis2_placement_3d(axis_orig, axis_zdir, axis_xdir)

# ── SURFACE_OF_REVOLUTION: revolve profile around Z-axis ─────────────────────
# Using _emit so axis1 placement reference is correct
rev_surf = f._emit("SURFACE_OF_REVOLUTION", profile_curve, axis_plc)

# ── Vertices ──────────────────────────────────────────────────────────────────
v_bot = f.vertex_point(cp0)   # (1,0,0) — bottom of profile
v_top = f.vertex_point(cp2)   # (1,0,2) — top of profile

# ── Seam edge: the profile curve itself (from bot to top) ─────────────────────
seam_edge = f.edge_curve(v_bot, v_top, profile_curve)

# ── Bottom degenerate circle: z=0, radius=1 ───────────────────────────────────
bot_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
bot_circle = f.circle(bot_plc, 1.0)
bot_edge = f.edge_curve(v_bot, v_bot, bot_circle)

# ── Top degenerate circle: z=2, radius=1 ─────────────────────────────────────
top_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 2.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
top_circle = f.circle(top_plc, 1.0)
top_edge = f.edge_curve(v_top, v_top, top_circle)

# ── EDGE_LOOP: seam(T) + top(T) + seam(F) + bot(F) ──────────────────────────
# seam_edge used twice (forward and reversed) creates degenerate seam closure
rev_loop = f.edge_loop([
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(top_edge, True),
    f.oriented_edge(seam_edge, False),
    f.oriented_edge(bot_edge, False),
])
face = f.advanced_face([f.face_outer_bound(rev_loop)], rev_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa233.stp")
