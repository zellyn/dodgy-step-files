"""Ps005 — Two MANIFOLD_SOLID_BREPs at identical coordinates in one SHAPE_REPRESENTATION.

Catalog claim: a single SHAPE_REPRESENTATION lists two MANIFOLD_SOLID_BREPs that
occupy the same coordinate space. They share no entities; vertices, edges, faces,
and shells are all distinct instances but with bit-identical coordinates.
Tier-3: pairwise spatial-overlap check among solids.

Tier-3: n_edges_total >= 48, face[0].surface_type == "plane", face[5].surface_type == "plane"
Expected: occt=shape(1)/shape(1) gmsh=shape(54) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ps005",
    defect=(
        "Two MANIFOLD_SOLID_BREPs at identical coordinates in one SHAPE_REPRESENTATION; "
        "distinct instances with bit-identical coordinates form duplicate solids; "
        "kernel sees two bodies; producer intent was one; "
        "detect spatially-coincident solids and either deduplicate, warn, or expose metrics; "
        "two MANIFOLD_SOLID_BREPs IS model entities — OCC yields shape(1)"
    ),
)


def build_cube(pts, label):
    """Build a unit-cube MANIFOLD_SOLID_BREP from 8 (x,y,z) tuples."""
    ps = [f.cartesian_point(p) for p in pts]
    vts = [f.vertex_point(p) for p in ps]

    def le(ia, ib, dx, dy, dz, length):
        d  = f.direction((dx, dy, dz))
        v  = f.vector(d, length)
        ln = f.line(ps[ia], v)
        return f.edge_curve(vts[ia], vts[ib], ln)

    e_bot_f = le(0, 1,  1, 0, 0, 10.0)
    e_bot_r = le(1, 2,  0, 1, 0, 10.0)
    e_bot_b = le(3, 2,  1, 0, 0, 10.0)
    e_bot_l = le(0, 3,  0, 1, 0, 10.0)
    e_top_f = le(4, 5,  1, 0, 0, 10.0)
    e_top_r = le(5, 6,  0, 1, 0, 10.0)
    e_top_b = le(7, 6,  1, 0, 0, 10.0)
    e_top_l = le(4, 7,  0, 1, 0, 10.0)
    e_v0    = le(0, 4,  0, 0, 1, 10.0)
    e_v1    = le(1, 5,  0, 0, 1, 10.0)
    e_v2    = le(2, 6,  0, 0, 1, 10.0)
    e_v3    = le(3, 7,  0, 0, 1, 10.0)

    def mk_plane(px, py, pz, zx, zy, zz, xx, xy, xz):
        orig = f.cartesian_point((px, py, pz))
        zd   = f.direction((zx, zy, zz))
        xd   = f.direction((xx, xy, xz))
        return f.plane(f.axis2_placement_3d(orig, zd, xd))

    def face4(edges_with_ori, plane):
        loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
        fob  = f.face_outer_bound(loop)
        return f.advanced_face([fob], plane)

    B = pts[0][0]  # base x
    pl_bot = mk_plane(B+5, 5, 0,   0, 0,-1,  1, 0, 0)
    pl_top = mk_plane(B+5, 5, 10,  0, 0, 1,  1, 0, 0)
    pl_frt = mk_plane(B+5, 0, 5,   0,-1, 0,  1, 0, 0)
    pl_bck = mk_plane(B+5,10, 5,   0, 1, 0,  1, 0, 0)
    pl_lft = mk_plane(B,   5, 5,  -1, 0, 0,  0, 1, 0)
    pl_rgt = mk_plane(B+10,5, 5,   1, 0, 0,  0, 1, 0)

    f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)
    f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)], pl_top)
    f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)],       pl_frt)
    f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)],       pl_bck)
    f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)],       pl_lft)
    f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)],       pl_rgt)

    all_faces = [f_bot, f_top, f_frt, f_bck, f_lft, f_rgt]
    face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
    shell = f._emit_raw(f"CLOSED_SHELL('{label}_shell',({face_refs}))")
    msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('{label}_solid',#{shell.eid})")
    return msb


# First cube: 0..10 in all axes
cube_pts_a = [
    (0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0), (0.0, 10.0, 0.0),
    (0.0, 0.0, 10.0), (10.0, 0.0, 10.0), (10.0, 10.0, 10.0), (0.0, 10.0, 10.0),
]
# Second cube: bit-identical coordinates — SAME geometry, distinct entities
cube_pts_b = list(cube_pts_a)  # identical coordinates

msb_a = build_cube(cube_pts_a, "solidA")
msb_b = build_cube(cube_pts_b, "solidB")

# Both MANIFOLD_SOLID_BREPs go into the same product chain
# use mode="brep_shape" for the first, then add the second msb reference manually
f.add_product_chain(msb_a, mode="brep_shape")
# The second msb is emitted already; add a second PRODUCT_DEFINITION chain for it
f.add_product_chain(msb_b, mode="brep_shape")
