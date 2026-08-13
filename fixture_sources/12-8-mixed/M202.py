"""M202 — Auxiliary GEOMETRICALLY_BOUNDED_SURFACE_SHAPE_REPRESENTATION alongside the main solid B-rep.

Catalog claim (input pattern): a STEP part carries TWO representations of the
same shape, tied by a SHAPE_REPRESENTATION_RELATIONSHIP: the primary
ADVANCED_BREP_SHAPE_REPRESENTATION (a real MANIFOLD_SOLID_BREP) plus an
*auxiliary* GEOMETRICALLY_BOUNDED_SURFACE_SHAPE_REPRESENTATION whose items are a
GEOMETRIC_CURVE_SET of construction/wireframe geometry (a line and a circle off
to the side). This is a common real-world CAD export shape — the exporter emits
construction geometry as a secondary geometrically-bounded representation next to
the solid.

A robust reader must select the ADVANCED_BREP representation to build the solid
and treat the geometrically-bounded auxiliary representation as free-form
non-solid geometry (or skip it) — never try to build a solid *from* the
auxiliary set and fail resolving the "root" representation. Pattern-mined from
Formlabs/foxtrot issue #24 (a pure-Rust, non-OCCT STEP reader): its
representation-matching "falls through the root representation match" and panics
("Could not get shape from GeometricallyBoundedSurfaceShapeRepresentation")
instead of skipping the auxiliary rep and triangulating the real B-rep. OCCT
selects the B-rep and loads the solid. MIT-licensed source; pattern only, no
bytes copied.

Byte assertions:
  - contains(b'GEOMETRICALLY_BOUNDED_SURFACE_SHAPE_REPRESENTATION')
  - contains(b'SHAPE_REPRESENTATION_RELATIONSHIP')
  - contains(b'GEOMETRIC_CURVE_SET')

Tier-3 assertion: shape_null == False (OCCT selects the B-rep and loads it)

Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
(gmsh loads the B-rep plus the auxiliary line+circle as separate entities → 7;
this count is CI-Linux-authoritative if it diverges from the local macOS oracle.)
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M202",
    defect=(
        "one product carries two representations of its shape tied by a "
        "SHAPE_REPRESENTATION_RELATIONSHIP: a primary "
        "ADVANCED_BREP_SHAPE_REPRESENTATION (a real MANIFOLD_SOLID_BREP, one "
        "clean truncated-cone face) and an auxiliary "
        "GEOMETRICALLY_BOUNDED_SURFACE_SHAPE_REPRESENTATION whose items are a "
        "GEOMETRIC_CURVE_SET of construction geometry (a LINE and a CIRCLE off "
        "to the side); a reader must select the advanced-brep representation to "
        "build the solid and treat the geometrically-bounded auxiliary "
        "representation as free-form non-solid geometry, never try to build a "
        "solid from the auxiliary set and fail resolving the root "
        "representation; synonyms: auxiliary geometrically-bounded surface "
        "representation, construction geometry alongside solid, multiple "
        "shape representations related, GEOMETRIC_CURVE_SET wireframe next to "
        "brep, representation-selection robustness; the auxiliary GBSSR and its "
        "GEOMETRIC_CURVE_SET are the defect carriers"
    ),
)

# ── Main solid: one clean (non-degenerate) truncated-cone face as a CLOSED_SHELL ──
semi_angle = 0.4          # ~23°, clean cone
base_r = 1.0
h_face = 1.0
apex_r = base_r - h_face * _math.tan(semi_angle)   # ≈ 0.577, clean

cone_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
cone_surf = f.conical_surface(cone_plc, base_r, semi_angle)

pt_base_seam = f.cartesian_point((base_r, 0.0, 0.0))
pt_apex_seam = f.cartesian_point((apex_r, 0.0, h_face))
v_base = f.vertex_point(pt_base_seam)
v_apex = f.vertex_point(pt_apex_seam)

base_circle = f.circle(
    f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)),
                         f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0))),
    base_r,
)
base_edge = f.edge_curve(v_base, v_base, base_circle)
apex_circle = f.circle(
    f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, h_face)),
                         f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))),
    apex_r,
)
apex_edge = f.edge_curve(v_apex, v_apex, apex_circle)

dx, dz = apex_r - base_r, h_face
seam_len = _math.sqrt(dx * dx + dz * dz)
seam_edge = f.edge_curve(
    v_base, v_apex,
    f.line(pt_base_seam, f.vector(f.direction((dx / seam_len, 0.0, dz / seam_len)), seam_len)),
)
face_loop = f.edge_loop([
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(apex_edge, True),
    f.oriented_edge(seam_edge, False),
    f.oriented_edge(base_edge, False),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], cone_surf)
msb = f.manifold_solid_brep(f.closed_shell([face]))

sdr = f.add_product_chain(msb, mode="brep_shape")
main_rep = sdr.args[1]          # ADVANCED_BREP_SHAPE_REPRESENTATION
geom_ctx = main_rep.args[2]     # shared (GEOMETRIC_REPRESENTATION_CONTEXT ...) complex

# ── Auxiliary construction geometry: a GEOMETRIC_CURVE_SET placed off to the side ──
aux_line = f.line(
    f.cartesian_point((10.0, 0.0, 0.0)),
    f.vector(f.direction((0.0, 1.0, 0.0)), 5.0),
)
aux_circle = f.circle(
    f.axis2_placement_3d(f.cartesian_point((10.0, 0.0, 0.0)),
                         f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))),
    2.0,
)
geom_set = f._emit("GEOMETRIC_CURVE_SET", [aux_line, aux_circle], name="construction")

# Auxiliary representation sharing the primary representation's geometric context.
aux_rep = f._emit(
    "GEOMETRICALLY_BOUNDED_SURFACE_SHAPE_REPRESENTATION",
    [geom_set], geom_ctx, name="auxiliary_construction",
)

# Tie the two representations together as representations of the SAME shape.
f._emit(
    "SHAPE_REPRESENTATION_RELATIONSHIP",
    "auxiliary construction geometry", main_rep, aux_rep,
    name="main solid + auxiliary set",
)

f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M202.stp")
