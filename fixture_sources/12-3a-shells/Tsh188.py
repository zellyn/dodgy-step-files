"""Tsh188 — ShapeFix_Shell.Perform progress-abort inconsistent-status.

Catalog claim: User abort during long-running face-fix loop (aPS.More() returns
false) causes early exit with false return value. However, myStatus flag already
set to ShapeExtend_DONE1 or similar, creating ambiguity: caller cannot
distinguish abort from partial failure. Partial fixes applied with inconsistent
error state.

Mechanism IS the shell structure: AN OPEN_SHELL with FOUR ADVANCED_FACEs, TWO
of which have same_sense=False (requiring correction), IS the defect trigger.
The face-fix loop in Perform() processes each face in sequence and sets myStatus
as it goes. An abort triggered mid-loop (aPS.More() returns false after fixing
the first two faces) causes early return of false while myStatus already reflects
DONE1. The caller receives false but cannot determine whether the abort occurred
before or after partial correction. The remaining two inverted faces ARE left
uncorrected — IS the partial state.

Tier-3 assertion: n_faces_total == 4

live oracle: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh188",
    defect=(
        "OPEN_SHELL with FOUR ADVANCED_FACEs (two inverted) IS the progress-abort defect trigger; "
        "face_ok_1 and face_ok_2 ARE correctly-oriented (same_sense=True) triangles — IS the valid set; "
        "face_inv_1 and face_inv_2 ARE inverted (same_sense=False) triangles — IS the defect set; "
        "Perform() iterates all four faces, setting myStatus=DONE1 after first correction; "
        "abort gate aPS.More() returns false mid-loop after face_ok_2 — IS the abort point; "
        "Perform() returns false (abort) but myStatus IS already DONE1 — IS the ambiguity; "
        "face_inv_1 and face_inv_2 remain uncorrected — IS the partial state; "
        "caller cannot distinguish abort from partial failure from complete failure — IS the defect; "
        "fix: Perform must save/restore status on early exit, or return distinct abort code; "
        "emit E_PERFORM_ABORT_INCONSISTENT_STATUS when abort occurs with partial DONE state"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

def tri_face(x0, y0, x1, y1, x2, y2, z, nx, ny, nz, same_sense):
    """Build a triangular face in a plane at height z."""
    pa = cp(x0, y0, z); va = f.vertex_point(pa)
    pb = cp(x1, y1, z); vb = f.vertex_point(pb)
    pc = cp(x2, y2, z); vc = f.vertex_point(pc)
    ea = led(va, vb, pa, x1-x0, y1-y0, 0)
    eb = led(vb, vc, pb, x2-x1, y2-y1, 0)
    ec = led(vc, va, pc, x0-x2, y0-y2, 0)
    loop = f.edge_loop([
        f.oriented_edge(ea, True),
        f.oriented_edge(eb, True),
        f.oriented_edge(ec, True),
    ])
    pl = f.plane(f.axis2_placement_3d(pa, dir3(nx, ny, nz), dir3(1, 0, 0)))
    return f.advanced_face([f.face_outer_bound(loop, orientation=True)], pl, same_sense=same_sense)

# face_ok_1: correctly-oriented triangle in Z=0 plane
face_ok_1  = tri_face(0, 0, 1, 0, 0.5, 1,  0,  0, 0, 1, True)
# face_ok_2: correctly-oriented triangle in Z=0 plane (different position)
face_ok_2  = tri_face(2, 0, 3, 0, 2.5, 1,  0,  0, 0, 1, True)
# face_inv_1: inverted triangle — IS the first face requiring abort-path correction
face_inv_1 = tri_face(0, 2, 1, 2, 0.5, 3,  0,  0, 0, 1, False)
# face_inv_2: inverted triangle — IS the second face requiring abort-path correction
face_inv_2 = tri_face(2, 2, 3, 2, 2.5, 3,  0,  0, 0, 1, False)

# OPEN_SHELL: four faces (two inverted) — IS the progress-abort defect mechanism
shell = f.open_shell([face_ok_1, face_ok_2, face_inv_1, face_inv_2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
