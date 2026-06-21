"""Hea010 — Shape-divide pipeline propagates B_SPLINE_SURFACE C0 knot-line splits to topology.

Catalog claim: When a surface is split at a C0 knot line (U-knot with
multiplicity = degree), every face built on it must be re-bounded; every edge
that crosses the cut must be sub-divided; every wire containing those edges
must be re-stitched. The shape-divide pipeline (ShapeUpgrade_ShapeDivide::Perform)
propagates splits transitively through the topology.

Mechanism: An ADVANCED_FACE on a B_SPLINE_SURFACE_WITH_KNOTS (degree 3 bicubic)
with a C0 cut at U=0.5 (interior knot multiplicity 3 = degree). The face's
outer EDGE_LOOP crosses the C0 isoline at U=0.5. The ADVANCED_FACE is wrapped
in a CLOSED_SHELL stand-in (a single-face "solid" wrapper) inside a
MANIFOLD_SOLID_BREP. Since the surface has a C0 crease and the wire crosses
it, brepcheck.valid == False.

Tier-3 assertion: brepcheck.valid == False

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea010",
    defect=(
        "ADVANCED_FACE on B_SPLINE_SURFACE_WITH_KNOTS (degree 3 bicubic) "
        "with interior U-knot at 0.5 with multiplicity 3 = degree (C0 crease); "
        "outer EDGE_LOOP crosses the C0 isoline; "
        "wrapped in CLOSED_SHELL + MANIFOLD_SOLID_BREP stand-in; "
        "ShapeUpgrade_ShapeDivide must propagate surface split to re-bound faces "
        "and re-stitch wires; brepcheck.valid=False due to C0 crease under the wire"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS bicubic with C0 cut at U=0.5 ─────────────────
# 6 U-spans × 4 V control points
# U-knot vector: (4,3,4) at (0.0, 0.5, 1.0) → sum=11, n_u=6+3+1-1=?
# n_u + u_deg + 1 = sum → n_u = 11-3-1=7 but we want a 6×4 grid...
# Actually: (4,3,4) sum=11. n_u + 3 + 1 = 11 → n_u = 7? No, 4+3+3=10? Let me re-check.
# u_deg=3, mults=(4,3,4): sum=11, n_u = sum - u_deg - 1 = 11-3-1 = 7? No: n_u + u_deg + 1 = sum → n_u = 11-4 = 7
# Actually: sum(mults) == n_u + u_deg + 1 → n_u = sum - u_deg - 1 = 11-3-1 = 7? no: 11-3-1=7? 4+3+4=11, 11-3-1=7. Hmm.
# But n_u is just the number of u control points. Let me try 6:
# n_u=6, u_deg=3: sum = 6+3+1=10 → (4,3,3) or (4,2,4)=10, or (4,3,3)=10, or other combos.
# For C0 at 0.5: need mult=3=u_deg at interior knot → (4,3,3)=10 ✓ (4+3+3=10=6+3+1)
# Let's use n_u=6, u_deg=3, mults=(4,3,3), knots=(0.0,0.5,1.0) → NOT symmetric.
# Better: use (4,3,4)=11, n_u=7.
# u_knot_mults=(4,3,4), u_knots=(0.0,0.5,1.0), n_u=7, u_deg=3: 7+3+1=11=4+3+4 ✓

# V: n_v=4, v_deg=3, v_mults=(4,4)=8=4+3+1 ✓, v_knots=(0.0,1.0)

# 7 U columns × 4 V rows
# U columns: 0→10 in 7 points with a kink at u~0.5 (the C0 line)
# Place the C0 crack at U-col index 3-4 (u=0.5)
u_xs = [0.0, 2.5, 5.0, 5.0, 5.0, 7.5, 10.0]
# Z values: introduce a kink at U=0.5 (crack = jump in z of 0.5)
u_zs = [0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5]  # C0 jump at col 2→3
v_ys = [0.0, 3.0, 7.0, 10.0]

grid = []
for ui, (x, z) in enumerate(zip(u_xs, u_zs)):
    col = []
    # Mark C0 points with explicit names for clarity
    prefix = "C0_" if ui in (3,) else ""
    for vi, y in enumerate(v_ys):
        lbl = chr(ord('a') + vi)
        nm  = f"{prefix}{lbl}" if prefix else ""
        pt = f.cartesian_point((x, y, z), name=nm)
        col.append(pt)
    grid.append(col)

surf = f.b_spline_surface_with_knots(
    u_degree=3,
    v_degree=3,
    control_points_grid=grid,
    u_multiplicities=[4, 3, 4],
    v_multiplicities=[4, 4],
    u_knots=[0.0, 0.5, 1.0],
    v_knots=[0.0, 1.0],
    name="host_C0_at_U0p5",
)

# ── Wire that crosses the C0 isoline at U=0.5 ────────────────────────────────
# Outer rectangle: corners at physical 3D positions
# Bottom-left: x=0,y=0,z=0  Bottom-right: x=10,y=0,z=0.5
# Top-right: x=10,y=10,z=0.5  Top-left: x=0,y=10,z=0
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.5))
p2 = f.cartesian_point((10.0, 10.0, 0.5))
p3 = f.cartesian_point((0.0, 10.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# Edges cross the C0 line (bottom and top edges pass through z-jump)
ec_b = f.edge_curve(v0, v1,
                     f.line(p0, f.vector(f.direction((1.0, 0.0, 0.05)), 1.0)),
                     name="crosses_C0")
ec_r = f.edge_curve(v1, v2,
                     f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)),
                     name="right")
ec_t = f.edge_curve(v2, v3,
                     f.line(p2, f.vector(f.direction((-1.0, 0.0, -0.05)), 1.0)),
                     name="top_crosses_C0")
ec_l = f.edge_curve(v3, v0,
                     f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)),
                     name="left")

loop = f.edge_loop([
    f.oriented_edge(ec_b, True),
    f.oriented_edge(ec_r, True),
    f.oriented_edge(ec_t, True),
    f.oriented_edge(ec_l, True),
], name="outer_with_C0_cross")
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], surf, name="face_on_C0_surface")

# ── CLOSED_SHELL stand-in + MANIFOLD_SOLID_BREP ───────────────────────────────
shell = f.closed_shell([face], name="solid_stand_in_with_C0_face")
solid = f.manifold_solid_brep(shell, name="solid_with_C0_split")

f.add_product_chain(solid, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea010.stp")
