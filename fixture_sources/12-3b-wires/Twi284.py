"""Twi284 — Consecutive wire edges share a corner LOCATION via two DISTINCT
VERTEX_POINT entities (coincident coordinates, not entity reuse).

Catalog claim: Two consecutive edges of one wire meet at a corner. Instead of
the normal pattern (edge A's end vertex and edge B's start vertex ARE the same
VERTEX_POINT entity), the sender emits TWO separate VERTEX_POINT entities that
happen to sit at identical coordinates. The wire is topologically "torn" at
that corner even though it looks geometrically closed. The general-purpose
vertex-unification utility (ShapeFix_WireVertex / ShapeFix_EdgeConnect::Build)
must recognize the coincident-but-distinct pair and merge them into one shared
vertex before the wire can be trusted as connected.

This is the OPPOSITE direction from Twi009/Twi050 (SplitCommonVertex): those
fixtures have ONE vertex entity over-shared across two wires that must be
SPLIT apart. Here there are TWO vertex entities at the SAME wire corner that
must be MERGED together.

Mechanism IS the pair of VERTEX_POINT entities at (10.0,0.0,0.0): #v1a (end of
the bottom edge) and #v1b (start of the right edge) — distinct entities,
identical CARTESIAN_POINT coordinates. Both ARE wired into EDGE_CURVEs inside
one EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE in an OPEN_SHELL; never
orphaned. The rest of the square uses ordinary single-entity-per-corner
vertices for contrast.

Byte assertions:
  - count_entity_def(b'VERTEX_POINT') >= 5
  - contains(b'(10.0,0.0,0.0)')

Tier-3 assertions:
  - n_edges_total >= 4
  - face[0].surface_type == "plane"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi284",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP for a 10x10 square wire; "
        "the bottom-right corner at (10,0,0) IS split across two DISTINCT "
        "VERTEX_POINT entities — #v1a (end of the bottom EDGE_CURVE) and "
        "#v1b (start of the right EDGE_CURVE) — both at identical coordinates "
        "but never unified into one entity; "
        "two coincident-but-distinct VERTEX_POINTs at one wire corner IS the "
        "mechanism; the general vertex-unification utility "
        "(ShapeFix_WireVertex/ShapeFix_EdgeConnect::Build) must detect the "
        "coincident pair and merge them into a single shared vertex; "
        "both VERTEX_POINTs ARE wired into EDGE_CURVE, EDGE_LOOP, "
        "FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL — never orphaned"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Vertices: 10x10 square; bottom-right corner split into #v1a/#v1b ─────────
v0  = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))    # bottom-left
# DEFECT: bottom-right corner encoded as TWO distinct VERTEX_POINT entities
# at the identical coordinate (10.0, 0.0, 0.0) instead of one shared entity.
v1a = f.vertex_point(f.cartesian_point((10.0, 0.0, 0.0)))   # end of bottom edge
v1b = f.vertex_point(f.cartesian_point((10.0, 0.0, 0.0)))   # start of right edge — DISTINCT entity
v2  = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))  # top-right
v3  = f.vertex_point(f.cartesian_point((0.0, 10.0, 0.0)))   # top-left

# ── Bottom edge: v0 → v1a ──────────────────────────────────────────────────
bot_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                   f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
e_bot  = f.edge_curve(v0, v1a, bot_line)
oe_bot = f.oriented_edge(e_bot, True)

# ── Right edge: v1b → v2 — starts at the DISTINCT-but-coincident vertex ──────
rgt_line = f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                   f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))
e_rgt  = f.edge_curve(v1b, v2, rgt_line)
oe_rgt = f.oriented_edge(e_rgt, True)

# ── Top edge: v2 → v3 ─────────────────────────────────────────────────────
top_line = f.line(f.cartesian_point((10.0, 10.0, 0.0)),
                   f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0))
e_top  = f.edge_curve(v2, v3, top_line)
oe_top = f.oriented_edge(e_top, True)

# ── Left edge: v3 → v0 ─────────────────────────────────────────────────────
lft_line = f.line(f.cartesian_point((0.0, 10.0, 0.0)),
                   f.vector(f.direction((0.0, -1.0, 0.0)), 10.0))
e_lft  = f.edge_curve(v3, v0, lft_line)
oe_lft = f.oriented_edge(e_lft, True)

loop = f.edge_loop([oe_bot, oe_rgt, oe_top, oe_lft])
fob   = f.face_outer_bound(loop)
face  = f.advanced_face([fob], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
