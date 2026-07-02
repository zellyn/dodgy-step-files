"""Pmi146 — AP242 Ed.3 `TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION` bidirectional link dropped by Ed.2 readers.

Catalog claim: STEP AP242 Edition 3 file with a single-face planar part whose
topological model and geometric model are explicitly linked by a
`TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION` entity and its inverse
`GEOMETRY_TO_TOPOLOGY_MODEL_ASSOCIATION`. The file header declares the AP242
Ed.3 OID (`{1 0 10303 442 4 1 4}`) with schema name `AUTOMOTIVE_DESIGN`. A PMI
`ANNOTATION_OCCURRENCE` references the face via a `SHAPE_ASPECT` anchor.

Expected:
- Geometry loads under any reader (single planar face).
- Under AP242 Ed.3 readers, the topology↔geometry association is resolvable.
- Under AP242 Ed.2 / AP214 readers, both association entities produce a Void
  transfer status: the face + annotation still load but the explicit bidirectional
  link between topological and geometric models is silently absent.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242 Ed.3
21-new-entities list — `TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION` / inverse
`GEOMETRY_TO_TOPOLOGY_MODEL_ASSOCIATION` §4.4). B4 wave-7 DEF-KK. Confidence:
MEDIUM — accept-live-oracle. The bidirectional link's exact semantic is defined
in Ed.3 only; OCCT drops the Ed.3 entity and loads the geometry as if AP214.
That IS the defect.

Byte assertions:
  contains(b'TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION')
  contains(b'GEOMETRY_TO_TOPOLOGY_MODEL_ASSOCIATION')
  contains(b'10303 442 4 1 4')
  contains(b'ANNOTATION_OCCURRENCE')
Tier-3: shape_null == False
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi146",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: single-face planar part with the topological model "
        "and geometric model explicitly linked by "
        "TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION + inverse "
        "GEOMETRY_TO_TOPOLOGY_MODEL_ASSOCIATION (AP242 Ed.3 §4.4, two of the "
        "21 new Ed.3 entities); header OID = {1 0 10303 442 4 1 4}; PMI "
        "ANNOTATION_OCCURRENCE references the face via a SHAPE_ASPECT anchor; "
        "Ed.3 readers resolve the bidirectional link; Ed.2 / AP214 readers "
        "silently drop both association entities — the face + annotation still "
        "load but the explicit topology↔geometry link is absent; "
        "edition-boundary drop; steptools notes_ap242e3.html; single-face "
        "shell — OCC yields shape(1)"
    ),
)

# ── Override header to AP242 Ed.3 OID with AUTOMOTIVE_DESIGN schema name ─────
# Task requires the exact FILE_SCHEMA string:
#   AUTOMOTIVE_DESIGN { 1 0 10303 442 4 1 4 }
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
# The face is the sole face of an OPEN_SHELL / SHELL_BASED_SURFACE_MODEL — a
# minimal but complete geometric model.  The topological model that the
# association entity links to is this face's EDGE_LOOP.
S = 10.0

# Plane surface at z=0
plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
plane = f.plane(plc, name="pmi146_plane")

# Four corner points → four vertices
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((S,   0.0, 0.0))
p11 = f.cartesian_point((S,   S,   0.0))
p01 = f.cartesian_point((0.0, S,   0.0))
loop = f.closed_polyline_loop([p00, p10, p11, p01])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="pmi146_face")

shell = f.open_shell([face], name="pmi146_shell")
sbsm  = f.shell_based_surface_model([shell], name="pmi146_sbsm")
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

# ── AP242 Ed.3 TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION ────────────────────────
# Per AP242 Ed.3 §4.4: this entity links the topological representation of a
# shape (via its topological model root — e.g. an EDGE_LOOP or SHELL entity)
# to the geometric representation (via its geometric model root — e.g. the
# SHELL_BASED_SURFACE_MODEL). Attributes: (name, description, topological_model,
# geometric_model).
# Byte assertion: contains(b'TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION')
# This entity does NOT exist in AP242 Ed.2 or earlier schemas — Ed.2 / AP214
# readers produce a Void transfer status on this entity.
topo_to_geom = f._emit_raw(
    f"TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION('t2g_assoc',"
    f"'topology to geometry link',#{loop.eid},#{sbsm.eid})"
)

# ── AP242 Ed.3 GEOMETRY_TO_TOPOLOGY_MODEL_ASSOCIATION (inverse) ──────────────
# Per AP242 Ed.3 §4.4: the inverse-direction entity for the topology↔geometry
# link.  Ed.3 readers use the pair to validate consistency of the two model
# roots.  Ed.2 / AP214 readers drop both silently.
# Byte assertion: contains(b'GEOMETRY_TO_TOPOLOGY_MODEL_ASSOCIATION')
geom_to_topo = f._emit_raw(
    f"GEOMETRY_TO_TOPOLOGY_MODEL_ASSOCIATION('g2t_assoc',"
    f"'geometry to topology link',#{sbsm.eid},#{loop.eid})"
)

# ── Anchor the annotation + associations to the product-definition shape ──────
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('pmi_assoc','topology-geometry link',#9055)"
)
assoc_rep = f._emit_raw(
    f"REPRESENTATION('assoc_rep',(#{annot.eid},#{topo_to_geom.eid},"
    f"#{geom_to_topo.eid},#{shape_aspect.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{assoc_rep.eid})"
)
