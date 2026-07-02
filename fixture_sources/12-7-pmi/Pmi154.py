"""Pmi154 — AP242 Ed.3 item-level topology-geometry association pair (E12) dropped by Ed.2/AP214 readers.

Catalog claim: STEP AP242 Edition 3 file with a single-face planar part
whose topological items (an EDGE / EDGE_CURVE and a face-associated
CARTESIAN_POINT) and geometric items (an ADVANCED_FACE and a CIRCLE
curve) are explicitly linked *at the item level* by
`TOPOLOGY_TO_GEOMETRY_ITEM_ASSOCIATION('t2g_item',#edge,#face)` and its
inverse `GEOMETRY_TO_TOPOLOGY_ITEM_ASSOCIATION('g2t_item',#face,#edge)`.

These are the item-level companions to `Pmi146`'s model-level
`TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION` pair. The file header declares
the AP242 Ed.3 OID (`{1 0 10303 442 4 1 4}`) with schema name
`AUTOMOTIVE_DESIGN`.

Distinct from `Pmi147` (`GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION`),
which is a locator entity — E12 is a bidirectional link between a
specific topological item and its geometric counterpart.

Expected:
- Geometry loads under any reader (single planar face).
- Under AP242 Ed.3 readers, both item-level association entities resolve;
  the topological EDGE_CURVE ↔ geometric ADVANCED_FACE binding is exposed.
- Under AP242 Ed.2 / AP214 readers, both association entities produce a
  `Void` transfer status: the face and edge still load but the explicit
  item-level bidirectional link is silently absent.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242
Ed.3 21-new-entities list — `TOPOLOGY_TO_GEOMETRY_ITEM_ASSOCIATION` /
inverse `GEOMETRY_TO_TOPOLOGY_ITEM_ASSOCIATION` §4.4). B4 wave-8 DEF-YY.
Confidence: MEDIUM — accept-live-oracle.

Byte assertions:
  contains(b'TOPOLOGY_TO_GEOMETRY_ITEM_ASSOCIATION')
  contains(b'GEOMETRY_TO_TOPOLOGY_ITEM_ASSOCIATION')
  contains(b'10303 442 4 1 4')
  contains(b'ANNOTATION_OCCURRENCE')
Tier-3: shape_null == False
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi154",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: single-face planar 10x10 mm part; the topological "
        "EDGE_CURVE of the face boundary and the geometric ADVANCED_FACE are "
        "explicitly linked at the ITEM level by "
        "TOPOLOGY_TO_GEOMETRY_ITEM_ASSOCIATION('t2g_item',#edge,#face) + "
        "inverse GEOMETRY_TO_TOPOLOGY_ITEM_ASSOCIATION('g2t_item',#face,#edge) "
        "(AP242 Ed.3 §4.4, two of 21 new Ed.3 entities; item-level companions "
        "to Pmi146's model-level TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION pair); "
        "header OID = {1 0 10303 442 4 1 4}; PMI ANNOTATION_OCCURRENCE "
        "references the face via a SHAPE_ASPECT anchor; Ed.3 readers resolve "
        "the item-level bidirectional link; Ed.2 / AP214 readers silently drop "
        "both association entities — the face + annotation still load but the "
        "explicit item-level topology<->geometry link is absent; edition-boundary "
        "drop; steptools notes_ap242e3.html; distinct from Pmi147's "
        "GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION locator entity; single-face "
        "shell — OCC yields shape(1)"
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

# ── Single planar ADVANCED_FACE (10×10 mm patch in the XY plane) ──────────────
S = 10.0

plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
plane = f.plane(plc, name="pmi154_plane")

# Four corner points and vertex points so we can also expose one EDGE_CURVE
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((S,   0.0, 0.0))
p11 = f.cartesian_point((S,   S,   0.0))
p01 = f.cartesian_point((0.0, S,   0.0))
v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)

# One explicit EDGE_CURVE (the bottom edge, +X direction, length S) — the
# topological ITEM that the association entities will bind to the face.
d_e = f.direction((1.0, 0.0, 0.0))
vec_e = f.vector(d_e, S)
line_e = f.line(p00, vec_e)
edge_curve = f._emit_raw(
    f"EDGE_CURVE('pmi154_bottom_edge',#{v00.eid},#{v10.eid},"
    f"#{line_e.eid},.T.)"
)

loop = f.closed_polyline_loop([p00, p10, p11, p01])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="pmi154_face")

shell = f.open_shell([face], name="pmi154_shell")
sbsm  = f.shell_based_surface_model([shell], name="pmi154_sbsm")
f.add_product_chain(sbsm)

# ── SHAPE_ASPECT anchor for the face (PMI annotation host) ────────────────────
shape_aspect = f._emit_raw(
    f"SHAPE_ASPECT('face_aspect','planar face host',#9055,.F.)"
)

# ── PMI annotation callout referencing the face ───────────────────────────────
# DESCRIPTIVE_REPRESENTATION_ITEM for the annotation content
dri = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('flatness_tol','FLATNESS 0.02')"
)
# ANNOTATION_OCCURRENCE on the face
# Byte assertion: contains(b'ANNOTATION_OCCURRENCE')
annot = f._emit_raw(
    f"ANNOTATION_OCCURRENCE('face_annot',$,#{dri.eid})"
)

# ── AP242 Ed.3 TOPOLOGY_TO_GEOMETRY_ITEM_ASSOCIATION ─────────────────────────
# Per AP242 Ed.3 §4.4: this entity links a specific topological ITEM (e.g.,
# an EDGE_CURVE) to its geometric-item counterpart (e.g., the ADVANCED_FACE
# it lies on) at the item level, not at the model level. Attributes per
# Ed.3: (name, description, topological_item, geometric_item).
# Byte assertion: contains(b'TOPOLOGY_TO_GEOMETRY_ITEM_ASSOCIATION')
# Ed.2 / AP214 readers produce Void transfer status on this entity.
topo_to_geom = f._emit_raw(
    f"TOPOLOGY_TO_GEOMETRY_ITEM_ASSOCIATION('t2g_item',"
    f"'edge to face item-level link',#{edge_curve.eid},#{face.eid})"
)

# ── AP242 Ed.3 GEOMETRY_TO_TOPOLOGY_ITEM_ASSOCIATION (inverse) ───────────────
# Per AP242 Ed.3 §4.4: the inverse-direction item-level entity.  Ed.3
# readers use the pair to validate consistency of the two item-level roots.
# Attributes per Ed.3: (name, description, geometric_item, topological_item).
# Byte assertion: contains(b'GEOMETRY_TO_TOPOLOGY_ITEM_ASSOCIATION')
# Ed.2 / AP214 readers drop both silently.
geom_to_topo = f._emit_raw(
    f"GEOMETRY_TO_TOPOLOGY_ITEM_ASSOCIATION('g2t_item',"
    f"'face to edge item-level link',#{face.eid},#{edge_curve.eid})"
)

# ── Anchor the annotation + item-level associations to the product ────────────
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('pmi_assoc_item',"
    f"'item-level topology-geometry link',#9055)"
)
assoc_rep = f._emit_raw(
    f"REPRESENTATION('assoc_item_rep',(#{annot.eid},#{topo_to_geom.eid},"
    f"#{geom_to_topo.eid},#{shape_aspect.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{assoc_rep.eid})"
)
