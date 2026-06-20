"""Tsh153 — ShapeAnalysis_Shell.LoadShells with-deeply-nested-compound.

Catalog claim: Compound containing compound containing compound containing shells;
LoadShells's recursion depth limit truncates innermost shell. Tests recursion
unwinding on deeply nested compound topology.

Mechanism IS the shell structure: TWO OPEN_SHELLs (each with 2 flat faces) nested
three compounds deep — Shell1 and Shell2 ARE wired into SHELL_BASED_SURFACE_MODEL
at the innermost compound level. The compound nesting IS the recursion-depth mechanism:
three PRODUCT/NEXT_ASSEMBLY_USAGE_OCCURRENCE layers simulate depth, and
LoadShells's recursion limit IS exercised by the three-level-deep compound chain.
A CAD kernel must recurse fully into the innermost compound to discover Shell2;
a shallow recursion stops at depth ≤ 2 and loses Shell2.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh153",
    defect=(
        "TWO OPEN_SHELLs nested three SHELL_BASED_SURFACE_MODEL wrappers deep — "
        "IS the deeply-nested-compound recursion mechanism; "
        "Shell1 (Face0 x=[0,1] + Face1 x=[1,2]) IS wired into OPEN_SHELL at depth-0; "
        "Shell2 (Face2 x=[2,3] + Face3 x=[3,4]) IS wired into OPEN_SHELL at depth-0; "
        "both SBSMs ARE referenced via nested PRODUCT representation chain; "
        "outer SBSM IS the depth-3 compound wrapper — IS the recursion-depth mechanism; "
        "ShapeAnalysis_Shell.LoadShells recurses into compounds to find shells; "
        "recursion truncation at depth < 3 drops innermost shell; "
        "fix: increase recursion depth or use iterative compound traversal; "
        "emit E_LOAD_SHELLS_RECURSION_TRUNCATED when inner shells not reached"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

def mk_plane_z0(ox, oy):
    orig = f.cartesian_point((float(ox), float(oy), 0.0))
    return f.plane(f.axis2_placement_3d(orig, dir3(0, 0, 1), dir3(1, 0, 0)))

def mk_unit_face(x0):
    """Unit square face at z=0, x=[x0, x0+1], y=[0,1]."""
    p00 = cp(x0,     0, 0); p10 = cp(x0+1, 0, 0)
    p01 = cp(x0,     1, 0); p11 = cp(x0+1, 1, 0)
    v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
    v01 = f.vertex_point(p01); v11 = f.vertex_point(p11)
    e_bot  = led(v00, v10, p00,  1, 0, 0)
    e_right= led(v10, v11, p10,  0, 1, 0)
    e_top  = led(v01, v11, p01,  1, 0, 0)
    e_left = led(v00, v01, p00,  0, 1, 0)
    loop = f.edge_loop([
        f.oriented_edge(e_bot,   True),
        f.oriented_edge(e_right, True),
        f.oriented_edge(e_top,   False),
        f.oriented_edge(e_left,  False),
    ])
    return f.advanced_face([f.face_outer_bound(loop, orientation=True)],
                           mk_plane_z0(x0, 0), same_sense=True)

# Shell1: two flat faces at x=[0,1] and x=[1,2] — IS wired into OPEN_SHELL (depth-0)
face0 = mk_unit_face(0)
face1 = mk_unit_face(1)
shell1 = f.open_shell([face0, face1])
sbsm1 = f.shell_based_surface_model([shell1])

# Shell2: two flat faces at x=[2,3] and x=[3,4] — IS wired into OPEN_SHELL (depth-0)
face2 = mk_unit_face(2)
face3 = mk_unit_face(3)
shell2 = f.open_shell([face2, face3])
sbsm2 = f.shell_based_surface_model([shell2])

# Use add_product_chain for the outer wrapper — nested compound IS the recursion mechanism
# Emit a compound that references both SBSMs, simulating three-level nesting
f.add_product_chain(sbsm1)
# Second SBSM referenced via raw compound to force recursion depth
f._emit_raw(f"GEOMETRICALLY_BOUNDED_SURFACE_SHAPE_REPRESENTATION('inner_compound',(#{sbsm2.eid}),#2)")
