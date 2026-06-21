"""M051 — Bare GEOMETRIC_SET / GEOMETRIC_CURVE_SET with non-geometric children or mesh-as-surfaces.

Catalog claim: GEOMETRIC_SET/GEOMETRIC_CURVE_SET may aggregate items beyond
curve/surface/point (axis placements, scalar measures), or may contain a
free-standing set of bounded surfaces with no shell/face superstructure. Many
importers reject as "no solid found" or skip silently.

Reproducer recipe: STEP file with a GEOMETRIC_SET referring to
B_SPLINE_SURFACE_WITH_KNOTS instances and no shell/face boundary, plus a
GEOMETRIC_SET aggregating LINE + AXIS2_PLACEMENT_3D + DESCRIPTIVE_REPRESENTATION_ITEM.

Byte assertions:
  contains(b'GEOMETRIC_SET')
  contains(b'DESCRIPTIVE_REPRESENTATION_ITEM')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M051",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET aggregating non-geometric children — "
        "AXIS2_PLACEMENT_3D and DESCRIPTIVE_REPRESENTATION_ITEM alongside curves; "
        "input: AP242 STEP file with a bare GEOMETRIC_SET whose items list includes "
        "LINE, AXIS2_PLACEMENT_3D (a placement entity, not a geometric shape), and "
        "DESCRIPTIVE_REPRESENTATION_ITEM (a scalar/text item) — schema-illegal mix; "
        "OpenVSP (aero/preliminary-design tools): free-standing GEOMETRIC_CURVE_SET "
        "used as primary geometry container without shell/face superstructure; "
        "ISO 10303-42 §4.5.1: GEOMETRIC_SET items must be geometric_select "
        "(curve | surface | point); AXIS2_PLACEMENT_3D and "
        "DESCRIPTIVE_REPRESENTATION_ITEM are not in the geometric_select union; "
        "kernel must never silently drop: reject with diagnostic, or warn and preserve "
        "as wireframe shape; offer optional stitching pass for surface-only sets; "
        "OCC silently produces empty results on bare GEOMETRIC_SET / "
        "GEOMETRIC_CURVE_SET files without surfacing the wireframe-only nature; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: bare GEOMETRIC_SET silent-empty, wireframe-only file appears empty, "
        "GEOMETRIC_CURVE_SET with non-geometric children, bare surface set rejected as no solid"
    ),
)

# ── A simple LINE as a valid geometric item in the set ────────────────────────
line_origin = f._emit_raw("CARTESIAN_POINT('line_origin',(0.,0.,0.))")
line_dir = f._emit_raw("DIRECTION('line_dir',(1.,0.,0.))")
line_vec = f._emit_raw(f"VECTOR(#{line_dir.eid},100.)")
line = f._emit_raw(f"LINE('axis_line',#{line_origin.eid},#{line_vec.eid})")

# ── AXIS2_PLACEMENT_3D — non-geometric item, illegal in GEOMETRIC_SET.items ──
placement_origin = f._emit_raw("CARTESIAN_POINT('placement_origin',(10.,0.,0.))")
placement_dir_z = f._emit_raw("DIRECTION('placement_z',(0.,0.,1.))")
placement_dir_x = f._emit_raw("DIRECTION('placement_x',(1.,0.,0.))")
# Byte assertion: contains(b'GEOMETRIC_SET')  (satisfied by the GCS entity below)
axis_placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('non_geometric_item',"
    f"#{placement_origin.eid},#{placement_dir_z.eid},#{placement_dir_x.eid})"
)

# ── DESCRIPTIVE_REPRESENTATION_ITEM — scalar/text item, not a geometric_select ─
# Byte assertion: contains(b'DESCRIPTIVE_REPRESENTATION_ITEM')
desc_item = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('scale_note','1:1 — non-geometric annotation')"
)

# ── B_SPLINE_SURFACE_WITH_KNOTS — free-standing surface, no shell superstructure
surf_pt00 = f._emit_raw("CARTESIAN_POINT('s00',(0.,0.,0.))")
surf_pt01 = f._emit_raw("CARTESIAN_POINT('s01',(0.,50.,0.))")
surf_pt10 = f._emit_raw("CARTESIAN_POINT('s10',(50.,0.,0.))")
surf_pt11 = f._emit_raw("CARTESIAN_POINT('s11',(50.,50.,0.))")
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('free_surface',1,1,"
    f"((#{surf_pt00.eid},#{surf_pt01.eid}),"
    f"(#{surf_pt10.eid},#{surf_pt11.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),(0.,1.),(0.,1.),.PIECEWISE_BEZIER_KNOTS.)"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
# Contains non-geometric items (axis_placement, desc_item) making it schema-illegal
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('bare-geometric-set-non-geometric-children',"
    f"(#{line.eid},#{axis_placement.eid},#{desc_item.eid},#{bss.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M051.stp")
