"""Tsh073 — Perform Context State Reuse Vulnerability.

Catalog claim: CLOSED_SHELL with 5 faces (base quad + 4 apex triangles).
Face 2 has intentionally reversed orientation requiring a fix.
ShapeFix_Shell.Perform at line 102 checks if Context() is null and creates
a new context only on first call. If Perform() is called twice without
context reset, the second call reuses the stale ShapeBuild_ReShape, causing
accumulated reshape operations to apply twice — resulting in double-fixed
faces and inconsistent orientation state.

Mechanism IS the shell structure: CLOSED_SHELL contains 5 ADVANCED_FACEs
forming a pyramid (square base + 4 triangular sides). Face 2 (first
triangular side) IS wired with same_sense=False, making its normal point
inward instead of outward — this reversed-orientation face IS the target of
ShapeFix_Shell.Perform's context accumulation. The CLOSED_SHELL topology
with Face 2's same_sense=False IS the mechanism: a second Perform() call
reapplies the fix, double-inverting Face 2 back to wrong orientation.

Tier-3 assertion: n_faces_total == 5

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh073",
    defect=(
        "CLOSED_SHELL with 5 ADVANCED_FACEs (square base + 4 triangular sides forming pyramid); "
        "Face 2 (first triangular side) IS wired with same_sense=False (inward normal); "
        "reversed-orientation Face 2 IS the context-accumulation target; "
        "ShapeFix_Shell.Perform at line 102 creates context only when null; "
        "second Perform() call reuses stale ShapeBuild_ReShape; "
        "double-fix silently re-reverses Face 2 back to inward orientation; "
        "fix: reset Context() to null before each Perform() call; "
        "or raise E_STALE_CONTEXT when called twice without reset"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Square base vertices at z=0
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0)
p11 = cp(1, 1, 0); p01 = cp(0, 1, 0)
# Apex at center, z=1
pap = cp(0.5, 0.5, 1)

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)
vap = f.vertex_point(pap)

# ── Base face: square z=0 (outward normal −Z) ─────────────────────────────
pl_base = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, -1), dir3(1, 0, 0)))
eB0 = led(v00, v10, p00,  1, 0, 0)
eB1 = led(v10, v11, p10,  0, 1, 0)
eB2 = led(v11, v01, p11, -1, 0, 0)
eB3 = led(v01, v00, p01,  0,-1, 0)
loop_base = f.edge_loop([
    f.oriented_edge(eB0, True), f.oriented_edge(eB1, True),
    f.oriented_edge(eB2, True), f.oriented_edge(eB3, True),
])
face_base = f.advanced_face([f.face_outer_bound(loop_base)], pl_base, same_sense=True)

# ── Shared lateral edges (apex spokes) ────────────────────────────────────
spoke0 = led(v00, vap, p00, 0.5, 0.5, 1)
spoke1 = led(v10, vap, p10,-0.5, 0.5, 1)
spoke2 = led(v11, vap, p11,-0.5,-0.5, 1)
spoke3 = led(v01, vap, p01, 0.5,-0.5, 1)

def tri_face(va, vb, base_edge, sp_a, sp_b, nx, ny, nz, ox, oy, oz, sense):
    """Triangular side face: base_edge traversed reversed, spokes out and back."""
    pl = f.plane(f.axis2_placement_3d(cp(ox,oy,oz), dir3(nx,ny,nz), dir3(1,0,0)))
    # Return base edge (vb→va) then spoke_b (vb→apex) then spoke_a (apex→va)
    loop = f.edge_loop([
        f.oriented_edge(base_edge, False),   # base traversed va←vb (reversed)
        f.oriented_edge(sp_b,      True),    # vb→apex
        f.oriented_edge(sp_a,      False),   # apex→va (reversed)
    ])
    return f.advanced_face([f.face_outer_bound(loop)], pl, same_sense=sense)

# Face 2: front side (v00→v10 base) — same_sense=False IS the reversed defect
face2 = tri_face(v00, v10, eB0, spoke0, spoke1,  0,-1, 0,  0,0,0, False)

# Faces 3,4,5: correct outward orientation (same_sense=True)
face3 = tri_face(v10, v11, eB1, spoke1, spoke2,  1, 0, 0,  1,0,0, True)
face4 = tri_face(v11, v01, eB2, spoke2, spoke3,  0, 1, 0,  1,1,0, True)
face5 = tri_face(v01, v00, eB3, spoke3, spoke0, -1, 0, 0,  0,1,0, True)

# CLOSED_SHELL: Face 2 with same_sense=False IS the mechanism wired in
shell = f.closed_shell([face_base, face2, face3, face4, face5])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
