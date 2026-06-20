"""Gp069 — ShapeAnalysis_Edge.CheckOverlapping common-sub-pattern miss.

Catalog claim: two coplanar LINE edges share an interior segment (not
endpoints). CheckOverlapping looks for endpoint overlap or whole-curve
overlap and misses the interior sub-pattern.

Fixture (rebuilt 2026-06-19 per Sonnet rigor verify): one face with TWO
distinct EDGE_CURVEs in its wire — edge1 spans (0,0,0)→(3,0,0), edge2
spans (1,0,0)→(2,0,0). The 3D interval of edge2 is wholly inside
edge1's span. CheckOverlapping(edge1, edge2) must detect the interior
overlap; the cataloged bug is that it doesn't.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp069",
    defect=(
        "Two coplanar LINE edges where edge2 (1,0,0)→(2,0,0) "
        "shares its entire span with edge1's interior (0,0,0)→(3,0,0); "
        "CheckOverlapping false-negative misses the interior overlap"
    ),
)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)


def make_planar_edge(p_start_tup, p_end_tup, length, dir_tuple):
    """Build an EDGE_CURVE with SURFACE_CURVE + PCURVE on the host plane."""
    p_start = f.cartesian_point(p_start_tup)
    p_end = f.cartesian_point(p_end_tup)
    v_start = f.vertex_point(p_start)
    v_end = f.vertex_point(p_end)
    d = f.direction(dir_tuple); vec = f.vector(d, length)
    line_3d = f.line(p_start, vec)
    # Pcurve in UV: drop z (plane maps 1:1).
    pc_start = f.cartesian_point(p_start_tup[:2])
    pc_dir = f.direction((dir_tuple[0], dir_tuple[1]))
    pc_vec = f.vector(pc_dir, length)
    pc_line = f.line(pc_start, pc_vec)
    pc_def = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('pc_def',(#{pc_line.eid}),#{prc.eid})"
    )
    pcurve = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pc_def.eid})")
    sc = f._emit_raw(
        f"SURFACE_CURVE('sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
    )
    edge = f._emit_raw(
        f"EDGE_CURVE('edge',#{v_start.eid},#{v_end.eid},#{sc.eid},.T.)"
    )
    return edge, v_start, v_end


# Edge 1: 3D LINE (0,0,0) → (3,0,0)
edge1, v1_start, v1_end = make_planar_edge((0.0, 0.0, 0.0), (3.0, 0.0, 0.0), 3.0, (1.0, 0.0, 0.0))

# Edge 2: 3D LINE (1,0,0) → (2,0,0) — INTERIOR SUBSEGMENT of edge1
edge2, _, _ = make_planar_edge((1.0, 0.0, 0.0), (2.0, 0.0, 0.0), 1.0, (1.0, 0.0, 0.0))

# Closing edges for the outer loop.
e_right, _, v_tr = make_planar_edge((3.0, 0.0, 0.0), (3.0, 1.0, 0.0), 1.0, (0.0, 1.0, 0.0))
e_top, _, v_tl = make_planar_edge((3.0, 1.0, 0.0), (0.0, 1.0, 0.0), 3.0, (-1.0, 0.0, 0.0))
e_left, _, _ = make_planar_edge((0.0, 1.0, 0.0), (0.0, 0.0, 0.0), 1.0, (0.0, -1.0, 0.0))

outer_loop = f.edge_loop([
    f.oriented_edge(edge1, True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_left, True),
])
fob = f.face_outer_bound(outer_loop)

# Inner wire is edge2 alone — an interior overlap signal for CheckOverlapping.
edge2_loop = f.edge_loop([f.oriented_edge(edge2, True)])
inner_bound = f._emit_raw(
    f"FACE_BOUND('interior_overlap_wire',#{edge2_loop.eid},.T.)"
)

face = f._emit_raw(
    f"ADVANCED_FACE('face_with_overlapping_edges',"
    f"(#{fob.eid},#{inner_bound.eid}),#{surf.eid},.T.)"
)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
