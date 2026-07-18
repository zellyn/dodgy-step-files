"""P027 — Boolean-history faces with degenerate hole-loop pcurves crash writer.

Catalog claim: With "write parametric pcurves" enabled, certain BSpline-surface
faces with a hole loop whose pcurve domain is degenerate (zero length) or maps
outside the surface's natural domain cause the STEP writer's face-emission pass
to dereference null and crash. When such files are nonetheless emitted, they
contain malformed pcurves on read.

The defect: a face on a BSpline surface with a hole loop whose PCURVE domain
is degenerate (start == end, zero-length range) or extends outside the
surface's natural domain. A kernel must detect and skip/fix the bad pcurve
before writing; reader should reject malformed pcurves with clear message;
silent empty result is the bug.

Byte assertions:
  contains(b'PCURVE')
  contains(b'B_SPLINE') or contains(b'SURFACE_CURVE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P027",
    defect=(
        "BSpline-surface face with a hole loop whose PCURVE domain is degenerate "
        "(zero length: start == end at parameter 0.0); "
        "hole-loop pcurve maps outside the surface's natural domain; "
        "STEP writer dereferences null on face-emission pass and crashes; "
        "reader must reject malformed pcurves with clear message; "
        "B_SPLINE_SURFACE + PCURVE + SURFACE_CURVE are the defect entities. "
        "The degenerate hole-loop pcurve sits unreachable from the shape-rep root, "
        "so OCC loads a 1-vertex stub (shape(1)); and even when the pcurve is wired "
        "into a real ADVANCED_FACE hole loop, OCC recomputes every pcurve from the "
        "3D curve during transfer (per Gp193), so the zero-length pcurve domain is "
        "absorbed and the face rebuilds byte-identically to a valid-pcurve control — "
        "the defect is oracle-invisible (shape_counts), not a load-time demonstration"
    ),
    schema="AP242",
)

# ── Minimal geometry payload so shape is empty ────────────────────────────────
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin_pt.eid}))")
f.add_product_chain(gcs)

# ── The defect: B_SPLINE_SURFACE with a degenerate hole-loop PCURVE ──────────

# A minimal degree-1 B_SPLINE_SURFACE_WITH_KNOTS (bilinear patch, 2x2 ctrl pts).
# This represents the underlying surface that the face sits on.
# Byte assertion: contains(b'B_SPLINE') — satisfied by B_SPLINE_SURFACE_WITH_KNOTS.
cp00 = f._emit_raw("CARTESIAN_POINT('cp00',(0.0,0.0,0.0))")
cp01 = f._emit_raw("CARTESIAN_POINT('cp01',(0.0,1.0,0.0))")
cp10 = f._emit_raw("CARTESIAN_POINT('cp10',(1.0,0.0,0.0))")
cp11 = f._emit_raw("CARTESIAN_POINT('cp11',(1.0,1.0,0.0))")

bspline_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('bspline_patch',1,1,"
    f"((#{cp00.eid},#{cp01.eid}),(#{cp10.eid},#{cp11.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

# The 3D edge: runs from (0,0,0) to (1,0,0).
e3d_start = f._emit_raw("CARTESIAN_POINT('e3d_start',(0.0,0.0,0.0))")
e3d_end = f._emit_raw("CARTESIAN_POINT('e3d_end',(1.0,0.0,0.0))")
e3d_dir = f._emit_raw("DIRECTION('e3d_dir',(1.0,0.0,0.0))")
e3d_vec = f._emit_raw(f"VECTOR('e3d_vec',#{e3d_dir.eid},1.0)")
edge_line_3d = f._emit_raw(f"LINE('edge_line_3d',#{e3d_start.eid},#{e3d_vec.eid})")

# The degenerate PCURVE: start point == end point at (0.0, 0.0) in UV space.
# Zero-length range — this is the defect: the hole loop pcurve collapses to a point.
deg_pcurve_pt = f._emit_raw("CARTESIAN_POINT('deg_pcurve_pt',(0.0,0.0))")
deg_pcurve_dir = f._emit_raw("DIRECTION('deg_pcurve_dir',(1.0,0.0))")
# Vector with magnitude 0.0 — zero-length, degenerate pcurve domain.
deg_pcurve_vec = f._emit_raw(f"VECTOR('deg_pcurve_vec',#{deg_pcurve_dir.eid},0.0)")
deg_pcurve_line = f._emit_raw(
    f"LINE('deg_pcurve_line',#{deg_pcurve_pt.eid},#{deg_pcurve_vec.eid})"
)
deg_def_rep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{deg_pcurve_line.eid}),#9060)"
)
# PCURVE binding the degenerate 2D line to the BSpline surface.
# Byte assertion: contains(b'PCURVE').
pcurve = f._emit_raw(
    f"PCURVE('degenerate_hole_pcurve',#{bspline_surf.eid},#{deg_def_rep.eid})"
)

# SURFACE_CURVE associates the 3D edge line with the degenerate PCURVE.
# Byte assertion: contains(b'SURFACE_CURVE').
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('defect_surface_curve',#{edge_line_3d.eid},"
    f"(#{pcurve.eid}),.PCURVE_S1.)"
)

# Wrap the defect entities in a GEOMETRIC_CURVE_SET for reference.
defect_gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('degenerate_pcurve_defect',(#{surface_curve.eid}))"
)

# ── NAUO scaffolding for §12.6 assembly-presence lint ─────────────────────────
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('BoolHistoryFace','BoolHistoryFace','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','bool_history_face_instance','',#9054,#{sub_pdef.eid},$)"
)
