"""N150 — IsMergedClosed.v_overlap_negativity_test.

V-parameter gap detection missing: curves separated by 1.0 in V (gap beyond
overlap tolerance) proceed to distInner/distOuter logic. dist<0 check omitted;
non-overlapping geometries incorrectly merged on U-closed surfaces.

Mechanism IS wired into 2 real ADVANCED_FACEs on a genuinely U-closed
(periodic) CYLINDRICAL_SURFACE (not a faceless GEOMETRIC_CURVE_SET):
Face1 is a full-revolution cylindrical band (radius 5) spanning z=[0,1]
(seam edge eA_v0_to_v1 referenced .T./.F., matching the corpus's
established full-revolution-face idiom -- see Tfa066); Face2 is a second
full-revolution band on the SAME cylindrical surface spanning z=[2,3]
(seam edge eB_v2_to_v3). The 1.0mm Z(V) gap between the two bands is a
real gap between two live faces on a genuinely U-closed surface -- the
exact non-overlapping-candidate input IsMergedClosed's missing dist<0
guard would incorrectly merge.

Fixture kind: scaffold (kernel-test-pair) -- the STEP file provides the
genuine V-gap-on-U-closed-surface setup; the merge bug fires when
IsMergedClosed is invoked at runtime.

Tier-3: n_faces_total == 2
Expected: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a  [NEEDS-ORACLE-REFRESH]
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N150",
    defect=(
        "IsMergedClosed v_overlap_negativity_test: two full-revolution "
        "cylindrical band ADVANCED_FACEs on the same U-closed "
        "CYLINDRICAL_SURFACE, separated 1.0mm in V (Z); dist<0 guard "
        "absent; non-overlapping bands would be incorrectly merged"
    ),
)

R = 5.0


def cyl_band(z0, z1, seam_name):
    """Build one full-revolution cylindrical band face spanning z=[z0,z1]
    on radius-R cylinder, following the corpus's established
    full-revolution-face idiom (seam edge .T./.F. + closed top/bottom
    circles), matching Tfa066.
    """
    pt_seam_bot = f.cartesian_point((R, 0.0, z0))
    pt_seam_top = f.cartesian_point((R, 0.0, z1))
    v_seam_bot = f.vertex_point(pt_seam_bot)
    v_seam_top = f.vertex_point(pt_seam_top)

    seam_line = f.line(pt_seam_bot, f.vector(f.direction((0.0, 0.0, 1.0)), z1 - z0))
    seam_ec = f.edge_curve(v_seam_bot, v_seam_top, seam_line, name=seam_name)

    bot_ctr = f.cartesian_point((0.0, 0.0, z0))
    bot_circ_ec = f.edge_curve(
        v_seam_bot, v_seam_bot,
        f.circle(f.axis2_placement_3d(
            bot_ctr, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0))
        ), R)
    )

    top_ctr = f.cartesian_point((0.0, 0.0, z1))
    top_circ_ec = f.edge_curve(
        v_seam_top, v_seam_top,
        f.circle(f.axis2_placement_3d(
            top_ctr, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))
        ), R)
    )

    cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
    cyl_surf = f.cylindrical_surface(
        f.axis2_placement_3d(cyl_orig, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))),
        R
    )

    cyl_loop = f.edge_loop([
        f.oriented_edge(seam_ec, True),
        f.oriented_edge(top_circ_ec, True),
        f.oriented_edge(seam_ec, False),
        f.oriented_edge(bot_circ_ec, False),
    ])
    return f.advanced_face([f.face_outer_bound(cyl_loop)], cyl_surf), seam_ec


# Face1: z=[0,1] -- seam eA_v0_to_v1.
face1, eA_v0_to_v1 = cyl_band(0.0, 1.0, "eA_v0_to_v1")

# Face2: z=[2,3] -- seam eB_v2_to_v3. Gap in Z(V) = 1.0 between the bands.
face2, eB_v2_to_v3 = cyl_band(2.0, 3.0, "eB_v2_to_v3")

# OPEN_SHELL with two full-revolution bands on the same U-closed cylinder,
# separated 1.0mm in V, IS the non-overlapping-candidate merge mechanism.
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
