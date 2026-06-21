"""Hea014 — Compound rebuild misses location chain when child SHAPE_REPRESENTATION
via REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION at non-identity placement.

Catalog claim: A document processed through a generic shape-rebuild pass
(ShapeCustom-class operation) rebuilds the compound from modified children
but loses the source compound's location attribute and any cached context state.

Mechanism: A compound containing one solid at a NON-IDENTITY location,
attached via a MAPPED_ITEM / REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION
that places the solid at (50, 0, 0). After ShapeCustom rebuild, the compound's
location should still be honored; the defect is that the location is silently
dropped.

Tier-3 assertions:
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea014",
    defect=(
        "Compound containing one 1x1 ADVANCED_FACE solid at NON-IDENTITY placement "
        "(50,0,0) via REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION; "
        "ShapeCustom rebuild must preserve the compound's TopLoc location chain; "
        "defect: rebuild loses location attribute + cached context state; "
        "REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION encodes the non-identity transform"
    ),
)

# ── Identity placement and host plane ────────────────────────────────────────
orig_id = f.cartesian_point((0.0, 0.0, 0.0))
zdir    = f.direction((0.0, 0.0, 1.0))
xdir    = f.direction((1.0, 0.0, 0.0))
plc_id  = f.axis2_placement_3d(orig_id, zdir, xdir, name="identity")
plane   = f.plane(plc_id, name="host")

# ── 1×1 square face ──────────────────────────────────────────────────────────
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

ec_b = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
ec_r = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
ec_t = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
ec_l = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

loop  = f.edge_loop([
    f.oriented_edge(ec_b, True),
    f.oriented_edge(ec_r, True),
    f.oriented_edge(ec_t, True),
    f.oriented_edge(ec_l, True),
])
fob   = f.face_outer_bound(loop)
face  = f.advanced_face([fob], plane, name="quad")
shell = f.closed_shell([face], name="child_shell")
solid = f.manifold_solid_brep(shell, name="child_solid")

# ── Non-identity placement at (50, 0, 0) ─────────────────────────────────────
p_offset  = f.cartesian_point((50.0, 0.0, 0.0))
zdir2     = f.direction((0.0, 0.0, 1.0))
xdir2     = f.direction((1.0, 0.0, 0.0))
plc_ni    = f.axis2_placement_3d(p_offset, zdir2, xdir2, name="non_identity")

# REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION to encode the placement
item_def_xform = f._emit_raw(
    f"ITEM_DEFINED_TRANSFORMATION('move_50',$,#{plc_id.eid},#{plc_ni.eid})"
)
local_ctx = f._emit_raw(
    f"GEOMETRIC_REPRESENTATION_CONTEXT('local_ctx',(#{plc_id.eid}),3)"
)
child_repr  = f._emit_raw(
    f"SHAPE_REPRESENTATION('child_repr',(#{face.eid}),#{local_ctx.eid})"
)
parent_repr = f._emit_raw(
    f"SHAPE_REPRESENTATION('parent_compound',(#{plc_ni.eid}),#{local_ctx.eid})"
)
rr = f._emit_raw(
    f"(REPRESENTATION_RELATIONSHIP('move','solid located at non-identity',"
    f"#{child_repr.eid},#{parent_repr.eid})"
    f"REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION(#{item_def_xform.eid})"
    f"SHAPE_REPRESENTATION_RELATIONSHIP())"
)

f.add_product_chain(solid, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea014.stp")
