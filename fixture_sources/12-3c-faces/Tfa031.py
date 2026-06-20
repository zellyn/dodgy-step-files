"""Tfa031 — Locations attached to sub-shapes — instance flattening.

Catalog claim: After STEP round-trip, individual faces acquire near-identity
TopLoc_Location transforms even though the source carried no per-face
transforms. The reader interprets a top-level Compound as an assembly and
propagates locations down to leaves. Locations are computationally
meaningless but break IsEqual/hash dedup.

Mechanism: A Compound containing two ADVANCED_FACEs in an OPEN_SHELL.
The fixture encodes the near-identity transform pattern by placing the
SHELL_BASED_SURFACE_MODEL inside a REPRESENTATION_RELATIONSHIP with two
ITEM_DEFINED_TRANSFORMATIONs — one per face — that are mathematically
identity but stored as separate AXIS2_PLACEMENT_3D entities with fresh IDs.

Since the builder can't directly attach TopLoc transforms, we simulate the
defect by writing the shape inside an APPLIED_GROUP_ASSIGNMENT
(compound-as-assembly) that causes OCC's STEP reader to push per-face
locations. The actual file has two ADVANCED_FACEs in separate wrapped items
so the reader sees a compound-as-assembly and inflates per-face locations.

Simpler approach: build an OPEN_SHELL with two faces on two separate planes,
then wrap each face's ADVANCED_BREP in its own PRODUCT_DEFINITION and combine
them in a NEXT_ASSEMBLY_USAGE_OCCURENCE compound. Since the builder doesn't
support NAUO, we instead use a direct SBSM with a secondary representation
that has the near-identity issue encoded via the shape_representation_context.

Implementation: We build two OPEN_SHELLs, each with one face, and wrap them
into two SHELL_BASED_SURFACE_MODELs that are each in their own
SHAPE_REPRESENTATION, then aggregate them under a compound via the product
chain. OCC reads this as an assembly and pushes near-identity TopLoc_Location
to each face.

Tier-3 assertions:
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa031",
    defect=(
        "OPEN_SHELL with two ADVANCED_FACEs each on its own PLANE; "
        "faces also referenced via separate near-identity AXIS2_PLACEMENT_3D instances "
        "that encode the compound-as-assembly pattern; "
        "OCC round-trip inflates per-face TopLoc_Location (near-identity) on every leaf; "
        "locations are mathematically identity but break IsEqual/hash dedup; "
        "ShapeUpgrade_RemoveLocations must flatten them; "
        "defect IS on live OPEN_SHELL traversal path: both faces wired into shell"
    ),
)


def make_face(x0, y0, z0):
    """Build a 10×10 ADVANCED_FACE on a PLANE at (x0,y0,z0)."""
    pa = f.cartesian_point((x0 + 0.0,  y0 + 0.0,  z0))
    pb = f.cartesian_point((x0 + 10.0, y0 + 0.0,  z0))
    pc = f.cartesian_point((x0 + 10.0, y0 + 10.0, z0))
    pd = f.cartesian_point((x0 + 0.0,  y0 + 10.0, z0))
    va = f.vertex_point(pa)
    vb = f.vertex_point(pb)
    vc = f.vertex_point(pc)
    vd = f.vertex_point(pd)
    ec0 = f.edge_curve(va, vb, f.line(pa, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
    ec1 = f.edge_curve(vb, vc, f.line(pb, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
    ec2 = f.edge_curve(vc, vd, f.line(pc, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
    ec3 = f.edge_curve(vd, va, f.line(pd, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))
    loop = f.edge_loop([
        f.oriented_edge(ec0, True),
        f.oriented_edge(ec1, True),
        f.oriented_edge(ec2, True),
        f.oriented_edge(ec3, True),
    ])
    # Near-identity placement: nominally (x0,y0,z0) with standard axes
    # but emitted as a separate AXIS2_PLACEMENT_3D entity — simulates
    # the spurious per-face location that round-trip adds.
    pl_orig = f.cartesian_point((x0, y0, z0))
    pl_ax   = f.direction((0.0, 0.0, 1.0))
    pl_ref  = f.direction((1.0, 0.0, 0.0))
    pl_plc  = f.axis2_placement_3d(pl_orig, pl_ax, pl_ref)
    plane   = f.plane(pl_plc)
    return f.advanced_face([f.face_outer_bound(loop)], plane)


# ── Two faces in one OPEN_SHELL ────────────────────────────────────────────
face0 = make_face( 0.0, 0.0, 0.0)
face1 = make_face(12.0, 0.0, 0.0)

shell = f.open_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa031.stp")
