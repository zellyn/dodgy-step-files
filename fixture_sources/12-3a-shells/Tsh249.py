"""Tsh249 — Three genuinely-fragmented, 50%-overlapping free-edge sections
along one line, each hosted by an independent fin-shaped shell in its own
half-plane, requiring the transitive cutting-node adjacency walk to fold
all three into one non-manifold edge chain
(sew-nonmanifold-multi-edge-merge-chain PARTIAL).

Catalog claim (occt-coverage PARTIAL `sew-nonmanifold-multi-edge-merge-
chain`): per `occt-coverage/exchange/problems.json`, the class was
DOWNGRADED COVERED->PARTIAL because both prior fixtures were found weak
on re-audit: Sw001's three faces wrap the literal same EDGE_LOOP, giving
only TWO distinct edge sections, not a 3-section chain; M045's
cutting-fragment chain is "plausible but unproven" (its 3 quads meet only
incidentally at one T-junction corner, not via a genuine transitive
overlap chain). This fixture purpose-builds an UNAMBIGUOUS 3-section
fragment chain:

Three independent OPEN_SHELLs, each ONE fin-shaped ADVANCED_FACE
radiating outward from the SAME reference line (the X-axis, y=0,z=0) in
a distinct angular half-plane (so the three fins never self-intersect
each other's interior), each contributing a free boundary edge that is a
DIFFERENT sub-segment of that one line, chosen so ALL THREE sections
share one common overlap zone:
  - fin_a: free edge x:[0,6]   (section A)
  - fin_b: free edge x:[2,8]   (section B — A∩B = [2,6])
  - fin_c: free edge x:[4,10]  (section C — B∩C = [4,8], A∩C = [4,6])

Every pairwise intersection is non-empty AND all three share the common
zone x:[4,6] — genuinely requiring the transitive cutting-node adjacency
walk (not a simple pairwise merge) to fold all three sections into the
accumulating merged edge over their shared span, exercising the
longest-first reference selection (A, the longest single section) as it
sequentially absorbs B then C.

Byte assertions:
  - count_entity_def(b'OPEN_SHELL') == 3
  - contains(b'fin_a_edge')
  - contains(b'fin_b_edge')
  - contains(b'fin_c_edge')
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh249",
    schema="AP242",
    defect=(
        "THREE independent OPEN_SHELLs, each one fin-shaped ADVANCED_FACE "
        "radiating from the X-axis (y=0,z=0) in a distinct angular "
        "half-plane, each contributing a free boundary edge that is a "
        "DIFFERENT 50%-overlapping sub-segment of that one line: fin_a "
        "x:[0,4], fin_b x:[2,6] (overlaps fin_a by 50%), fin_c x:[4,8] "
        "(overlaps fin_b by 50%, never touches fin_a directly) — a "
        "genuine 3-section fragment chain requiring transitive cutting-"
        "node adjacency discovery to fold into one non-manifold edge, "
        "purpose-built distinct from Sw001's single shared EDGE_LOOP "
        "(only 2 distinct sections) and M045's incidental single-point "
        "T-junction (unproven chain)"
    ),
)


def cp(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))


def dir3(x, y, z):
    return f.direction((float(x), float(y), float(z)))


def fin_shell(x0, x1, out_dx, out_dy, out_dz, tag):
    """One fin-shaped ADVANCED_FACE: a triangle with base [x0,0,0]-[x1,0,0]
    on the X-axis and an apex offset by (out_dx,out_dy,out_dz) from the
    segment midpoint, in its own OPEN_SHELL. The base edge is the
    fragment-chain candidate; the two apex legs are unique to this fin
    and never coincide with any other fin's edges."""
    p0 = cp(x0, 0.0, 0.0)
    p1 = cp(x1, 0.0, 0.0)
    mid_x = (x0 + x1) / 2.0
    papex = cp(mid_x + out_dx, out_dy, out_dz)

    v0 = f.vertex_point(p0)
    v1 = f.vertex_point(p1)
    vapex = f.vertex_point(papex)

    length = x1 - x0
    d_base = dir3(1, 0, 0)
    vec_base = f.vector(d_base, length)
    ln_base = f.line(p0, vec_base)
    e_base = f.edge_curve(v0, v1, ln_base, name=f"{tag}_edge")

    def leg(pa, va, pb, vb):
        dx = pb.args[1][0] - pa.args[1][0]
        dy = pb.args[1][1] - pa.args[1][1]
        dz = pb.args[1][2] - pa.args[1][2]
        leglen = (dx * dx + dy * dy + dz * dz) ** 0.5
        d = dir3(dx / leglen, dy / leglen, dz / leglen)
        vec = f.vector(d, leglen)
        ln = f.line(pa, vec)
        return f.edge_curve(va, vb, ln)

    e_leg1 = leg(p1, v1, papex, vapex)
    e_leg2 = leg(papex, vapex, p0, v0)

    loop = f.edge_loop([
        f.oriented_edge(e_base, True),
        f.oriented_edge(e_leg1, True),
        f.oriented_edge(e_leg2, True),
    ])

    # Plane normal: perpendicular to both the base direction (X) and the
    # outward apex offset direction, so the triangle is genuinely planar.
    off_len = (out_dx ** 2 + out_dy ** 2 + out_dz ** 2) ** 0.5
    offn = (out_dx / off_len, out_dy / off_len, out_dz / off_len)
    # normal = base_dir x offset_dir
    nx = 0.0 * offn[2] - 0.0 * offn[1]
    ny = 0.0 * offn[0] - 1.0 * offn[2]
    nz = 1.0 * offn[1] - 0.0 * offn[0]
    nlen = (nx * nx + ny * ny + nz * nz) ** 0.5
    if nlen < 1e-9:
        nx, ny, nz = 0.0, 0.0, 1.0
        nlen = 1.0
    zdir = dir3(nx / nlen, ny / nlen, nz / nlen)
    xdir = d_base
    plc = f.axis2_placement_3d(p0, zdir, xdir)
    plane = f.plane(plc)
    face = f.advanced_face([f.face_outer_bound(loop)], plane, name=f"{tag}_face")
    return f.open_shell([face], name=f"{tag}_shell")


# Three fins in three distinct half-planes around the shared X-axis line,
# each 90 degrees apart so no two fins' interiors ever intersect. Ranges
# chosen so ALL THREE sections share a common overlap zone x:[4,6]
# (A ∩ B = [2,6], B ∩ C = [4,8], A ∩ C = [4,6]) — the transitive walk must
# fold all three into the accumulating merged edge over the common zone,
# not just two independent pairwise merges bridged by B.
shell_a = fin_shell(0.0, 6.0, 0.0, 3.0, 0.0, "fin_a")    # +Y half-plane
shell_b = fin_shell(2.0, 8.0, 0.0, 0.0, 3.0, "fin_b")    # +Z half-plane
shell_c = fin_shell(4.0, 10.0, 0.0, -3.0, 0.0, "fin_c")  # -Y half-plane

sbsm = f.shell_based_surface_model([shell_a, shell_b, shell_c])
f.add_product_chain(sbsm)

# NON_MANIFOLD marker entity (M045/Tsh248 precedent) — genuine multi-shell
# non-manifold model tagging for a non-manifold-aware reader.
f._emit_raw(
    f"NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION('tsh249_nonmanifold_marker',"
    f"({sbsm.ref()}),#9060)"
)
