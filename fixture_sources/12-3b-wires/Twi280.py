"""Twi280 — AP242 Ed.3 `SUBPATH` (E11) dropped by Ed.2/AP214 readers.

Catalog claim: STEP AP242 Edition 3 file with a `PATH('interior_pocket_path',
(#oe1,#oe2,#oe3,#oe4,#oe5))` (5-segment ordered ORIENTED_EDGE list) plus a
`SUBPATH('interior_corner_segment',(#oe3,#oe4))` labelling edges 3-4 as a
named sub-region of the path. Also carries a co-present single planar face
(so the geometry loads and the fixture is not empty).

The file header declares the AP242 Ed.3 OID (`{1 0 10303 442 4 1 4}`)
with schema name `AUTOMOTIVE_DESIGN`.

Expected:
- Geometry loads under any reader (single planar face).
- Under AP242 Ed.3 readers, `SUBPATH` resolves and exposes the sub-region
  labelling so automated pocket-milling toolpath generation that keys off
  SUBPATH labels can recover the labelling.
- Under AP242 Ed.2 / AP214 readers, `SUBPATH` produces a `Void` transfer
  status: the `PATH` still loads but the sub-region labelling is lost.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242
Ed.3 21-new-entities list — `SUBPATH` §4.4). B4 wave-8 DEF-XX.
Confidence: MEDIUM — accept-live-oracle.

Byte assertions:
  contains(b'SUBPATH')
  contains(b'interior_corner_segment')
  contains(b'10303 442 4 1 4')
Tier-3: shape_null == False
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi280",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: single planar 5x5 mm carrier face plus an independent "
        "PATH('interior_pocket_path',(#oe1,#oe2,#oe3,#oe4,#oe5)) (5-segment "
        "ordered ORIENTED_EDGE list) and a "
        "SUBPATH('interior_corner_segment',(#oe3,#oe4)) labelling edges 3-4 as "
        "a named sub-region of the path (AP242 Ed.3 §4.4, one of 21 new Ed.3 "
        "entities); header OID = {1 0 10303 442 4 1 4}; Ed.3 readers expose the "
        "sub-path; Ed.2 / AP214 readers produce Void transfer status on the "
        "entity — the PATH still loads but the sub-region labelling is lost "
        "(automated pocket-milling toolpath generation that keys off SUBPATH "
        "labels cannot recover it); edition-boundary drop; steptools "
        "notes_ap242e3.html; MANIFOLD_SURFACE_SHAPE_REPRESENTATION with one "
        "face — OCC yields shape(1)"
    ),
)

# ── Override header to AP242 Ed.3 OID with AUTOMOTIVE_DESIGN schema name ─────
_HDR = (
    "HEADER;\n"
    f"FILE_DESCRIPTION(('{f.catalog_id}'),'2;1');\n"
    f"FILE_NAME('{f.catalog_id}.stp','{f.timestamp}',(''),(''),"
    f"'cad-research-suite','','');\n"
    "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 442 4 1 4 }'));\n"
    "ENDSEC;"
)
f._render_header = lambda: _HDR

# ── Planar carrier face (5x5 mm patch in the XY plane, z=0) ──────────────────
S = 5.0
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc, name="twi280_plane")

p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((S,   0.0, 0.0))
p11 = f.cartesian_point((S,   S,   0.0))
p01 = f.cartesian_point((0.0, S,   0.0))
loop = f.closed_polyline_loop([p00, p10, p11, p01])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="twi280_face")
shell = f.open_shell([face], name="twi280_shell")
sbsm  = f.shell_based_surface_model([shell], name="twi280_sbsm")
f.add_product_chain(sbsm)

# ── Independent 5-segment PATH representing a pocket-milling toolpath ─────────
# Points forming an inner pocket path (does NOT bound a face, so it is a
# standalone PATH — Ed.3 SUBPATH is defined on a PATH ordered list, not on
# an EDGE_LOOP).
path_pts_xyz = [
    (1.0, 1.0, 0.0),  # p0
    (2.0, 1.0, 0.0),  # p1
    (3.0, 1.5, 0.0),  # p2 — interior corner start
    (3.5, 2.0, 0.0),  # p3 — interior corner end
    (4.0, 3.0, 0.0),  # p4
    (4.0, 4.0, 0.0),  # p5
]
path_pts = [f.cartesian_point(xyz) for xyz in path_pts_xyz]
path_vps = [f.vertex_point(p) for p in path_pts]

path_edges = []
for k in range(5):
    a = path_pts_xyz[k]
    b = path_pts_xyz[k + 1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = (dx * dx + dy * dy) ** 0.5
    d = f.direction((dx / length, dy / length, 0.0))
    v = f.vector(d, length)
    ln = f.line(path_pts[k], v)
    ec = f._emit_raw(
        f"EDGE_CURVE('twi280_pe{k+1}',#{path_vps[k].eid},"
        f"#{path_vps[k+1].eid},#{ln.eid},.T.)"
    )
    path_edges.append(ec)

oriented_path = [f.oriented_edge(e, True) for e in path_edges]
path = f._emit_raw(
    f"PATH('interior_pocket_path',("
    f"{','.join(f'#{oe.eid}' for oe in oriented_path)}))"
)

# ── AP242 Ed.3 SUBPATH labelling edges 3, 4 as a named sub-region ────────────
# Per AP242 Ed.3 §4.4: SUBPATH declares a labelled sub-region of a PATH's
# ordered ORIENTED_EDGE list. Attributes per Ed.3: (name, edges).
# Byte assertion: contains(b'SUBPATH')
# Ed.2 / AP214 readers produce Void transfer status on this entity.
subpath = f._emit_raw(
    f"SUBPATH('interior_corner_segment',"
    f"(#{oriented_path[2].eid},#{oriented_path[3].eid}))"
)

# ── Tie the path + sub-path into a property representation ────────────────────
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('twi280_path',"
    f"'AP242 Ed.3 sub-path of pocket-milling toolpath',#9055)"
)
subpath_rep = f._emit_raw(
    f"REPRESENTATION('twi280_subpath_rep',(#{path.eid},#{subpath.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{subpath_rep.eid})"
)
