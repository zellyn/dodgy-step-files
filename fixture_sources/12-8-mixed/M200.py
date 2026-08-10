"""M200 — Polygon loop with an empty vertex-point list.

Catalog claim: a faceted face's boundary is written as
`POLY_LOOP('empty_polygon',())` — the polygon list empty where ISO
10303-42 requires at least three cartesian points. A polygon loop IS its
point list; with the list empty the face has a bound entity but zero
geometry, the degenerate limit of the mesh-as-B-rep encodings this
section catalogs.

Canonical claimant for the poly-loop row of the nonempty-aggregate table
(structural-linter v4).

Byte assertions:
  - contains(b"POLY_LOOP('empty_polygon',())")
  - count_entity_def(b'CARTESIAN_POINT') >= 1

Structural assertion: struct == EMPTY_AGGREGATE
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M200",
    defect=(
        "ADVANCED_FACE whose FACE_OUTER_BOUND wraps "
        "POLY_LOOP('empty_polygon',()) — the polygon list empty where the "
        "schema requires at least three points; a polygon loop is nothing "
        "but its point list, so the face has a bound and no geometry. "
        "Reachable through the shell and shape representation"
    ),
)

centre = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plane = f.plane(f.axis2_placement_3d(centre, zdir, xdir))

# THE DEFECT: empty polygon list.
ploop = f._emit_raw("POLY_LOOP('empty_polygon',())")
face = f.advanced_face([f.face_outer_bound(ploop)], plane, name="m200_facet")
sbsm = f.shell_based_surface_model([f.open_shell([face])])
f.add_product_chain(sbsm)
