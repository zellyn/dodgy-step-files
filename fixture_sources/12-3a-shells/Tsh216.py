"""Tsh216 — ShapeFix_Shell.Perform.progress_abort_inconsistency.

Catalog claim: User abort during face-fix loop indistinguishable from failure;
myStatus/return value mismatch.

Mechanism IS the shell structure: AN OPEN_SHELL containing FOUR ADVANCED_FACEs
(two valid + two with inverted same_sense) IS the defect trigger. The shell IS
the entity on which ShapeFix_Shell.Perform() iterates the face-fix loop. A
progress indicator abort IS signalled mid-loop (after processing two faces).
Perform() receives UserBreak from the progress monitor and sets myStatus but
returns a value inconsistent with the abort signal — IS the status/return-value
mismatch defect.

Tier-3 assertion: n_faces_total == 4

live oracle: occt=shape(1)/shape(1) gmsh=shape(17) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh216",
    defect=(
        "OPEN_SHELL with FOUR ADVANCED_FACEs (two valid, two same_sense=False) IS the progress-abort defect trigger; "
        "face_a IS unit square (0,0,0)-(1,1,0) same_sense=True — IS first valid face; "
        "face_b IS unit square (2,0,0)-(3,1,0) same_sense=True — IS second valid face; "
        "face_c IS unit square (4,0,0)-(5,1,0) same_sense=False — IS first repair-needed face; "
        "face_d IS unit square (6,0,0)-(7,1,0) same_sense=False — IS second repair-needed face; "
        "ShapeFix_Shell.Perform() IS the defect path: iterates face-fix loop over all four faces; "
        "progress monitor IS set; user abort IS signalled after face_b IS processed — IS the mid-loop abort; "
        "Perform() receives UserBreak signal from progress monitor — IS the abort detection point; "
        "myStatus IS set to reflect abort — IS the status-set path; "
        "return value IS inconsistent with abort (returns success-like value) — IS the mismatch defect; "
        "caller cannot distinguish abort from completion — IS the indistinguishable-abort outcome; "
        "fix: Perform() must return value that uniquely signals UserBreak abort; "
        "emit E_PROGRESS_ABORT_STATUS_MISMATCH when return value contradicts myStatus on abort"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

def make_face(x_off, same_sense):
    """Build a unit square face offset by x_off in X."""
    p00 = cp(x_off,   0, 0); v00 = f.vertex_point(p00)
    p10 = cp(x_off+1, 0, 0); v10 = f.vertex_point(p10)
    p11 = cp(x_off+1, 1, 0); v11 = f.vertex_point(p11)
    p01 = cp(x_off,   1, 0); v01 = f.vertex_point(p01)

    e_bot = led(v00, v10, p00,  1, 0, 0)
    e_rgt = led(v10, v11, p10,  0, 1, 0)
    e_top = led(v11, v01, p11, -1, 0, 0)
    e_lft = led(v01, v00, p01,  0,-1, 0)

    loop = f.edge_loop([
        f.oriented_edge(e_bot, True),
        f.oriented_edge(e_rgt, True),
        f.oriented_edge(e_top, True),
        f.oriented_edge(e_lft, True),
    ])
    plane = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
    return f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=same_sense)

face_a = make_face(0, True)    # IS first valid face — processed before abort
face_b = make_face(2, True)    # IS second valid face — abort triggered after this
face_c = make_face(4, False)   # IS first repair-needed face — not reached due to abort
face_d = make_face(6, False)   # IS second repair-needed face — not reached due to abort

# OPEN_SHELL: four faces — IS the progress-abort-inconsistency mechanism
# Mid-loop abort after face_b IS the abort trigger; myStatus/return mismatch IS the defect
shell = f.open_shell([face_a, face_b, face_c, face_d])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
