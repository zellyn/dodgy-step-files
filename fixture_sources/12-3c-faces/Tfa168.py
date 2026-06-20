"""Tfa168 — ShapeFix_Face.FixOrientation degenerate-edge-only.

Catalog claim: Face whose outer wire consists exclusively of degenerate edges
(all edges collapse to a single point). FixOrientation attempts to extract
direction from edge vectors; with no valid edge directions available, the
direction vector remains undefined or zero, making orientation correction
impossible.

Mechanism: GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a PLANE. The
outer wire is an EDGE_LOOP with four DEGENERATE_PCURVE-backed edges, each
starting and ending at the same single vertex (the degenerate point). All
edges collapse to the point (5, 5, 0). FixOrientation extracts tangent
vectors from edge geometry but all are zero-length (degenerate), leaving the
orientation direction undefined.

OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'DEGENERATE_PCURVE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa168",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on PLANE; "
        "outer wire: 4 degenerate edges all collapsing to single point (5,5,0); "
        "each edge: start_vertex == end_vertex == degenerate point; "
        "DEGENERATE_PCURVE used as edge geometry (all zero-length); "
        "FixOrientation extracts zero tangent vectors from all edges; "
        "direction remains undefined/zero — orientation correction impossible; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Plane surface ─────────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Single degenerate point ───────────────────────────────────────────────────
deg_pt = f.cartesian_point((5.0, 5.0, 0.0))
deg_v  = f._emit_raw(f"VERTEX_POINT('deg_pt',#{deg_pt.eid})")

# ── Degenerate pcurve: a 2D point at (0,0) in the plane's parameter space ─────
# PCURVE references a surface and a definitional representation (2D point curve)
# We build a minimal 2D point as a degenerate pcurve

# 2D origin for the pcurve parameter-space location
pcurve_pt2d = f._emit_raw("CARTESIAN_POINT('',(0.,0.))")
# A zero-length 2D line direction
pcurve_d2d  = f._emit_raw("DIRECTION('',(1.,0.))")
pcurve_v2d  = f._emit_raw(f"VECTOR('',#{pcurve_d2d.eid},0.)")
pcurve_ln2d = f._emit_raw(f"LINE('',#{pcurve_pt2d.eid},#{pcurve_v2d.eid})")

# Geometric representation context (2D)
geom_ctx = f._emit_raw(
    "GEOMETRIC_REPRESENTATION_CONTEXT(2)"
)
# Representation using the 2D line
pcurve_rep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{pcurve_ln2d.eid}),#{geom_ctx.eid})"
)

# ── Four degenerate edges all at the same point ────────────────────────────────
# DEGENERATE_PCURVE as edge geometry: both endpoints are the same vertex
deg_pcurve = f._emit_raw(
    f"DEGENERATE_PCURVE('',#{plane.eid},#{pcurve_rep.eid})"
)

# All four edges start and end at the same degenerate vertex
ec0 = f._emit_raw(f"EDGE_CURVE('degen0',#{deg_v.eid},#{deg_v.eid},#{deg_pcurve.eid},.T.)")
ec1 = f._emit_raw(f"EDGE_CURVE('degen1',#{deg_v.eid},#{deg_v.eid},#{deg_pcurve.eid},.T.)")
ec2 = f._emit_raw(f"EDGE_CURVE('degen2',#{deg_v.eid},#{deg_v.eid},#{deg_pcurve.eid},.T.)")
ec3 = f._emit_raw(f"EDGE_CURVE('degen3',#{deg_v.eid},#{deg_v.eid},#{deg_pcurve.eid},.T.)")

oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('degen_only_loop',"
    f"(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
af  = f._emit_raw(f"ADVANCED_FACE('degen_edge_only_face',(#{fob.eid}),#{plane.eid},.T.)")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa168.stp")
