"""Tsh187 — BRepBuilderAPI_Sewing.AnalysisNearestEdges section-bound-lookup gate.

Catalog claim: Section-edge bound tracking initializes lookup structures but may
not enumerate all section edges during analysis. Near-gap multi-shell geometries
trigger incomplete edge-distance evaluation, producing unmatched or skipped
candidates suitable for sewing.

Mechanism IS the shell structure: TWO SEPARATE OPEN_SHELLs, each a single
ADVANCED_FACE (unit square), placed with a NEAR-GAP between them IS the defect
trigger. The gap IS small enough that the sewing tolerance should permit merging.
AnalysisNearestEdges IS the defect path: it initializes aMapMultiConnectEdges
and section-bound tracking structures, but fails to enumerate the facing section
edges of both shells during analysis. The facing edges (right edge of shell_a
and left edge of shell_b) ARE the sewing candidates that go unmatched. The
shells remain disjoint despite tolerance permitting merge — IS the defect.

Tier-3 assertion: shape_null == True

live oracle: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh187",
    defect=(
        "TWO SEPARATE OPEN_SHELLs with NEAR-GAP IS the AnalysisNearestEdges defect trigger; "
        "shell_a IS unit square (0,0,0)-(1,0,0)-(1,1,0)-(0,1,0) — IS the first shell; "
        "shell_b IS unit square (1.0005,0,0)-(2.0005,0,0)-(2.0005,1,0)-(1.0005,1,0) — IS the second shell; "
        "gap of 0.0005 between shells IS smaller than sewing tolerance — IS the near-gap; "
        "AnalysisNearestEdges initializes section-bound tracking — IS the defect path entry; "
        "section edges of shell_a right boundary and shell_b left boundary ARE the sewing candidates; "
        "bound-lookup gate skips incomplete section enumeration — IS the defect; "
        "shells remain disjoint despite tolerance permitting merge — IS the model impact; "
        "fix: AnalysisNearestEdges must exhaustively enumerate all section boundary edges; "
        "emit E_SEWING_BOUND_INCOMPLETE when section edge enumeration is partial"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# shell_a: unit square (0,0,0) to (1,1,0)
pa00 = cp(0, 0, 0); va00 = f.vertex_point(pa00)
pa10 = cp(1, 0, 0); va10 = f.vertex_point(pa10)
pa11 = cp(1, 1, 0); va11 = f.vertex_point(pa11)
pa01 = cp(0, 1, 0); va01 = f.vertex_point(pa01)

ea_bot = led(va00, va10, pa00,  1, 0, 0)   # bottom
ea_rgt = led(va10, va11, pa10,  0, 1, 0)   # right — IS the section edge candidate
ea_top = led(va11, va01, pa11, -1, 0, 0)   # top
ea_lft = led(va01, va00, pa01,  0,-1, 0)   # left

loop_a = f.edge_loop([
    f.oriented_edge(ea_bot, True),
    f.oriented_edge(ea_rgt, True),
    f.oriented_edge(ea_top, True),
    f.oriented_edge(ea_lft, True),
])
plane_a = f.plane(f.axis2_placement_3d(pa00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], plane_a, same_sense=True)
shell_a = f.open_shell([face_a])

# shell_b: unit square (1.0005,0,0) to (2.0005,1,0) — gap of 0.0005 from shell_a
pb00 = cp(1.0005, 0, 0); vb00 = f.vertex_point(pb00)
pb10 = cp(2.0005, 0, 0); vb10 = f.vertex_point(pb10)
pb11 = cp(2.0005, 1, 0); vb11 = f.vertex_point(pb11)
pb01 = cp(1.0005, 1, 0); vb01 = f.vertex_point(pb01)

eb_bot = led(vb00, vb10, pb00,  1, 0, 0)
eb_rgt = led(vb10, vb11, pb10,  0, 1, 0)
eb_top = led(vb11, vb01, pb11, -1, 0, 0)
eb_lft = led(vb01, vb00, pb01,  0,-1, 0)  # left — IS the section edge candidate

loop_b = f.edge_loop([
    f.oriented_edge(eb_bot, True),
    f.oriented_edge(eb_rgt, True),
    f.oriented_edge(eb_top, True),
    f.oriented_edge(eb_lft, True),
])
plane_b = f.plane(f.axis2_placement_3d(pb00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], plane_b, same_sense=True)
shell_b = f.open_shell([face_b])

# Two separate OPEN_SHELLs in the same SBSM — IS the AnalysisNearestEdges defect mechanism
sbsm = f.shell_based_surface_model([shell_a, shell_b])
f.add_product_chain(sbsm)
