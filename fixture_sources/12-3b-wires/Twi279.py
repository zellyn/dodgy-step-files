"""Twi279 — AP242 Ed.3 `CONNECTED_EDGE_SUB_SET` (E08) dropped by Ed.2/AP214 readers.

Catalog claim: STEP AP242 Edition 3 file with a single planar face whose
`EDGE_LOOP` has 8 oriented edges (an 8-sided plate), plus a
`CONNECTED_EDGE_SUB_SET('c1_fillet_chain',(#e3,#e4,#e5))` that groups
edges 3-5 as a semantic sub-region — the "chamfer/fillet chain" of
the boundary.

The file header declares the AP242 Ed.3 OID (`{1 0 10303 442 4 1 4}`)
with schema name `AUTOMOTIVE_DESIGN`.

Expected:
- Geometry loads under any reader (single octagonal planar face).
- Under AP242 Ed.3 readers, `CONNECTED_EDGE_SUB_SET` resolves and exposes
  the sub-grouping so CAM/inspection tools can query the semantic sub-region.
- Under AP242 Ed.2 / AP214 readers, `CONNECTED_EDGE_SUB_SET` produces a
  `Void` transfer status: the `EDGE_LOOP` still loads with all 8 edges but
  the semantic sub-region grouping is silently gone.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242
Ed.3 21-new-entities list — `CONNECTED_EDGE_SUB_SET` §4.4). B4 wave-8
DEF-WW. Confidence: MEDIUM — accept-live-oracle.

Byte assertions:
  contains(b'CONNECTED_EDGE_SUB_SET')
  contains(b'c1_fillet_chain')
  contains(b'10303 442 4 1 4')
Tier-3: shape_null == False
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi279",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: single planar octagonal face (8 oriented edges in the "
        "EDGE_LOOP) plus a CONNECTED_EDGE_SUB_SET('c1_fillet_chain',(#e3,#e4,#e5)) "
        "grouping edges 3-5 as a semantic sub-region (labelled c1_fillet_chain — "
        "the fillet/chamfer chain); AP242 Ed.3 §4.4 (one of 21 new Ed.3 entities); "
        "header OID = {1 0 10303 442 4 1 4}; Ed.3 readers resolve the sub-grouping; "
        "Ed.2 / AP214 readers produce Void transfer status on the entity — the "
        "EDGE_LOOP still loads with all 8 edges but the semantic sub-region "
        "grouping is silently gone (CAM/inspection tools that key off the "
        "sub-region label cannot recover it); edition-boundary drop; steptools "
        "notes_ap242e3.html; MANIFOLD_SURFACE_SHAPE_REPRESENTATION with one face — "
        "OCC yields shape(1)"
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

# ── Planar carrier face at z=0 with octagonal boundary ────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc, name="twi279_plane")

# Eight vertices of an octagon of circumradius 5.0 at (0,0)
R = 5.0
verts_xyz = [
    (R * math.cos(2 * math.pi * k / 8),
     R * math.sin(2 * math.pi * k / 8),
     0.0)
    for k in range(8)
]
pts = [f.cartesian_point(xyz) for xyz in verts_xyz]
vps = [f.vertex_point(p) for p in pts]

# Build 8 straight EDGE_CURVEs, each on a LINE from p[k] toward p[k+1]
edges = []
for k in range(8):
    p_a = verts_xyz[k]
    p_b = verts_xyz[(k + 1) % 8]
    dx = p_b[0] - p_a[0]
    dy = p_b[1] - p_a[1]
    length = math.hypot(dx, dy)
    d = f.direction((dx / length, dy / length, 0.0))
    v = f.vector(d, length)
    ln = f.line(pts[k], v)
    ec = f._emit_raw(
        f"EDGE_CURVE('twi279_e{k+1}',#{vps[k].eid},"
        f"#{vps[(k+1) % 8].eid},#{ln.eid},.T.)"
    )
    edges.append(ec)

oriented = [f.oriented_edge(e, True) for e in edges]
loop = f.edge_loop(oriented, name="twi279_loop")
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="twi279_face")
shell = f.open_shell([face], name="twi279_shell")
sbsm  = f.shell_based_surface_model([shell], name="twi279_sbsm")
f.add_product_chain(sbsm)

# ── AP242 Ed.3 CONNECTED_EDGE_SUB_SET grouping edges 3, 4, 5 ─────────────────
# Per AP242 Ed.3 §4.4: this entity declares a labelled, connected subset of
# edges within a topological representation, so downstream tools can query
# the semantic sub-region (e.g., the "fillet chain" on the boundary).
# Attributes per Ed.3: (name, edges).
# Byte assertion: contains(b'CONNECTED_EDGE_SUB_SET')
# Ed.2 / AP214 readers produce Void transfer status on this entity.
sub_set = f._emit_raw(
    f"CONNECTED_EDGE_SUB_SET('c1_fillet_chain',"
    f"(#{edges[2].eid},#{edges[3].eid},#{edges[4].eid}))"
)

# ── Tie the sub-set into a property representation ────────────────────────────
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('twi279_sub_set',"
    f"'AP242 Ed.3 connected-edge sub-set',#9055)"
)
sub_rep = f._emit_raw(
    f"REPRESENTATION('twi279_sub_rep',(#{sub_set.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{sub_rep.eid})"
)
