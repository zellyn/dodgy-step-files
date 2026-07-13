"""Gp185 — Pcurve winds MULTIPLE full periods of a closed surface
(degree-vs-radian confusion producing dozens of wraps), not just a
single-period shift (seq-xsalgo-pcurve-consistency subvariant (a),
missing from the class: prior fixtures Gs007/Gp023 are single-period
shifts, a different repair path than the multi-period span check).

Work packet D2, item `seq-xsalgo-pcurve-consistency` (PARTIAL, missing 1
of 3), problem_id `seq-xsalgo-pcurve-consistency`, subvariant (a):
"pcurve spanning multiple surface periods (unit/angle confusion)"
(XSAlgo_AlgoContainer::CheckPCurve, XSAlgo_AlgoContainer.cxx:326-342 --
multi-period pcurve span check; drops the pcurve).

Mechanism: A genuine unit-radius CYLINDRICAL_SURFACE (u is the angular
direction, natural period 2*pi). A single self-closed full-circle
EDGE_CURVE (start==end vertex, exactly the Gp182/Gp013 "healthy rim"
idiom) whose 3D CIRCLE is a correct, single physical revolution -- but
whose PCURVE is a 2D LINE in UV that runs from u=0 to u=40*pi (20 full
periods) instead of the correct single period [0, 2*pi]. This is exactly
the "degree-vs-radian confusion" signature: e.g. an exporter that
multiplied an angle already in radians by a further factor intended for
degrees-to-radians conversion, producing a parametric span vastly larger
than the surface's actual angular domain. Distinct from Gs007/Gp023
(single-period shifts, e.g. pcurve offset by one whole 2*pi but still
spanning only one period) -- here the SPAN itself is the defect, not an
offset.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp185",
    defect=(
        "Unit-radius CYLINDRICAL_SURFACE; self-closed full-circle EDGE_CURVE "
        "(genuine single-revolution 3D CIRCLE) whose PCURVE 2D LINE spans u=[0, "
        "40*pi] -- 20 full periods of the surface's natural 2*pi angular period, "
        "not a single-period offset (contrast Gs007/Gp023); degree-vs-radian "
        "confusion signature -- dozens of wraps -- for XSAlgo_AlgoContainer::"
        "CheckPCurve's multi-period span check"
    ),
)

# CYLINDRICAL_SURFACE, radius 1, standard placement (axis Z, ref X).
c_orig = f.cartesian_point((0.0, 0.0, 0.0))
c_axis = f.direction((0.0, 0.0, 1.0))
c_ref = f.direction((1.0, 0.0, 0.0))
c_plc = f.axis2_placement_3d(c_orig, c_axis, c_ref)
cyl = f.cylindrical_surface(c_plc, 1.0)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Self-closed full circle at z=0: physical point (1,0,0), single vertex.
p_rim = f.cartesian_point((1.0, 0.0, 0.0))
v_rim = f.vertex_point(p_rim)

rim_circle = f.circle(c_plc, 1.0)

# THE DEFECT: pcurve LINE spans u=[0, 40*pi] -- 20 periods -- instead of
# the correct single period [0, 2*pi].
pc_start = f.cartesian_point((0.0, 0.0))
pc_dir = f.direction((1.0, 0.0))
pc_vec = f.vector(pc_dir, 40.0 * math.pi)
pc_line = f._emit_raw(f"LINE('multi_period_pcurve',#{pc_start.eid},#{pc_vec.eid})")
pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp185_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gp185_uv',#{cyl.eid},#{pc_def.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gp185_sc',#{rim_circle.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('gp185_rim',#{v_rim.eid},#{v_rim.eid},#{surface_curve.eid},.T.)"
)
oe = f.oriented_edge(edge, True)
loop = f.edge_loop([oe])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
