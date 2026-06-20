"""Tsh185 — ShapeFix_Solid.Perform context-stale-state cumulative fixes.

Catalog claim: Multiple Perform() calls without context reset cause accumulated
reshape operations. First fix creates new context via SetContext(new
ShapeBuild_ReShape); second call reuses same context, applying queued
operations twice to same shell faces. Orientation inconsistency results.

Mechanism IS the shell structure: A CLOSED_SHELL with SIX ADVANCED_FACEs IS
the defect trigger. The shell IS a cube (six unit-square faces). Half the faces
use same_sense=True and half use same_sense=False — creating a mixed-orientation
shell. On the first Perform() call, ShapeFix_Solid creates a new context and
queues orientation flips for the inverted faces. On the second call, the stale
context re-applies those queued flips to already-corrected faces, producing
doubly-flipped (back to wrong) orientation. The over-correction IS the defect.

Tier-3 assertion: n_faces_total == 6

live oracle: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh185",
    defect=(
        "CLOSED_SHELL with SIX ADVANCED_FACEs (cube) IS the stale-context defect trigger; "
        "faces bottom/top/front/back use same_sense=True — IS the correctly-oriented set; "
        "faces left/right use same_sense=False — IS the inverted faces requiring correction; "
        "first Perform() call creates new context, queues orientation flips — IS expected behavior; "
        "second Perform() call reuses stale context, re-applies queued flips — IS the defect path; "
        "over-correction re-inverts previously-fixed faces — IS the cumulative-fix defect; "
        "caller cannot distinguish partial failure from double-flip state — IS the model impact; "
        "fix: Perform() must reset context on each call or guard against re-application; "
        "emit E_PERFORM_CONTEXT_STALE when second call detects non-empty queued context"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

def quad(x0, y0, z0, x1, y1, z1, x2, y2, z2, x3, y3, z3, nx, ny, nz, same_sense):
    """Build a quadrilateral face given 4 corners, normal dir, and same_sense."""
    pa = cp(x0, y0, z0); va = f.vertex_point(pa)
    pb = cp(x1, y1, z1); vb = f.vertex_point(pb)
    pc = cp(x2, y2, z2); vc = f.vertex_point(pc)
    pd = cp(x3, y3, z3); vd = f.vertex_point(pd)
    # Determine ref axis: if normal is Z, ref is X; if normal is X, ref is Y; if Y, ref is X
    if abs(nz) > 0.5:
        ax, ay, az = 1.0, 0.0, 0.0
    elif abs(nx) > 0.5:
        ax, ay, az = 0.0, 1.0, 0.0
    else:
        ax, ay, az = 1.0, 0.0, 0.0
    ea = led(va, vb, pa, x1-x0, y1-y0, z1-z0)
    eb = led(vb, vc, pb, x2-x1, y2-y1, z2-z1)
    ec = led(vc, vd, pc, x3-x2, y3-y2, z3-z2)
    ed = led(vd, va, pd, x0-x3, y0-y3, z0-z3)
    loop = f.edge_loop([
        f.oriented_edge(ea, True),
        f.oriented_edge(eb, True),
        f.oriented_edge(ec, True),
        f.oriented_edge(ed, True),
    ])
    pl = f.plane(f.axis2_placement_3d(pa, dir3(nx, ny, nz), dir3(ax, ay, az)))
    return f.advanced_face([f.face_outer_bound(loop, orientation=True)], pl, same_sense=same_sense)

# Cube faces: 6 faces, half inverted (same_sense=False) to trigger stale-context re-fix
face_bottom = quad(0,0,0, 1,0,0, 1,1,0, 0,1,0,  0, 0,-1, True)   # bottom: -Z normal, correct
face_top    = quad(0,0,1, 1,0,1, 1,1,1, 0,1,1,  0, 0, 1, True)   # top: +Z normal, correct
face_front  = quad(0,0,0, 1,0,0, 1,0,1, 0,0,1,  0,-1, 0, True)   # front: -Y normal, correct
face_back   = quad(0,1,0, 1,1,0, 1,1,1, 0,1,1,  0, 1, 0, True)   # back: +Y normal, correct
face_left   = quad(0,0,0, 0,1,0, 0,1,1, 0,0,1, -1, 0, 0, False)  # left: inverted — IS defect face
face_right  = quad(1,0,0, 1,1,0, 1,1,1, 1,0,1,  1, 0, 0, False)  # right: inverted — IS defect face

# CLOSED_SHELL: six faces (cube), mixed orientation — IS the stale-context mechanism
shell = f.closed_shell([face_bottom, face_top, face_front, face_back, face_left, face_right])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
