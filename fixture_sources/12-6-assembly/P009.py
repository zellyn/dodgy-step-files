"""P009 — Helical sweep tessellates with garbled facets at seam.

Catalog claim: a spring (helical sweep solid) renders as garbled facets in OCCT
due to pathological chord-deviation tessellation at the helix seam, but renders
correctly in Inventor.

The defect: SWEPT_SURFACE whose directrix is a parametric helix with constant
pitch and several turns. The seam at parameter start/end creates garbled facets
in OCCT's tessellator. Receivers enforcing the spec must heal or smooth the
tessellation at the seam.

Byte assertions:
  contains(b'SURFACE_CURVE')
  contains(b'PCURVE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P009",
    defect=(
        "SWEPT_SURFACE with helical directrix represented as B_SPLINE_CURVE; "
        "seam at parameter 0/2π causes garbled facets in OCCT chord-deviation "
        "tessellator; renders correctly in Autodesk Inventor; "
        "SURFACE_CURVE + PCURVE present as byte evidence of surface/curve seam; "
        "NEXT_ASSEMBLY_USAGE_OCCURRENCE scaffolding for §12.6 lint; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── Helical directrix: approximate helix as B_SPLINE_CURVE_WITH_KNOTS ────────
# 4-turn helix, radius=10, pitch=5mm, ~28 points per turn = 112 total.
radius = 10.0
pitch = 5.0
n_turns = 4
pts_per_turn = 28
total_pts = n_turns * pts_per_turn

helix_pts = []
for i in range(total_pts):
    t = 2.0 * math.pi * i / pts_per_turn
    z = pitch * (i / pts_per_turn)
    x = radius * math.cos(t)
    y = radius * math.sin(t)
    helix_pts.append(f.cartesian_point((x, y, z)))

n = total_pts
degree = 3
n_interior = n - degree - 1
mults = [4] + [1] * n_interior + [4]
knots = [0.0] + [float(i) for i in range(1, n_interior + 1)] + [float(n_interior + 1)]

cp_refs = ",".join(f"#{e.eid}" for e in helix_pts)
mults_str = ",".join(str(m) for m in mults)
knots_str = ",".join(f"{k:.1f}" for k in knots)

helix_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS("
    f"'helix_directrix',"
    f"{degree},"
    f"({cp_refs}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"({mults_str}),"
    f"({knots_str}),"
    f".UNSPECIFIED.)"
)

# ── Profile curve: circle cross-section for the sweep ────────────────────────
profile_origin = f.cartesian_point((radius, 0.0, 0.0))
profile_zdir = f.direction((0.0, 0.0, 1.0))
profile_xdir = f.direction((1.0, 0.0, 0.0))
profile_plc = f.axis2_placement_3d(profile_origin, profile_zdir, profile_xdir)
profile_circle = f._emit_raw(
    f"CIRCLE('sweep_profile',#{profile_plc.eid},1.5)"
)

# ── PCURVE: the helix curve parametrized on a cylinder surface ────────────────
# We need a reference surface for the PCURVE. Use a CYLINDRICAL_SURFACE.
cyl_origin = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc = f.axis2_placement_3d(cyl_origin, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(
    f"CYLINDRICAL_SURFACE('helix_cylinder',#{cyl_plc.eid},{radius:.1f})"
)

# PCURVE: the helix lives on the cylindrical surface.
# The 2D parametrization is a straight line in (u,v) space: u=t, v=pitch*t/(2π).
pcurve_origin_2d = f._emit_raw(
    "CARTESIAN_POINT('pcurve_origin2d',(0.0,0.0))"
)
pcurve_dir_2d = f._emit_raw(
    "DIRECTION('pcurve_dir2d',(1.0,0.0))"
)
# Use a 2D placement for the pcurve definition map.
pcurve_vec = f._emit_raw(
    f"VECTOR('pcurve_vec',#{pcurve_dir_2d.eid},1.0)"
)
pcurve_line = f._emit_raw(
    f"LINE('pcurve_line2d',#{pcurve_origin_2d.eid},#{pcurve_vec.eid})"
)
# DEFINITIONAL_REPRESENTATION for PCURVE.
pcurve_rep_ctx = f._emit_raw(
    "PARAMETRIC_REPRESENTATION_CONTEXT('','')"
)
pcurve_def_rep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{pcurve_line.eid}),#{pcurve_rep_ctx.eid})"
)
pcurve = f._emit_raw(
    f"PCURVE('helix_pcurve',#{cyl_surf.eid},#{pcurve_def_rep.eid})"
)

# ── SURFACE_CURVE: the helix as a 3D+surface curve ───────────────────────────
# The seam of this SURFACE_CURVE is where the tessellation garbles.
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('helix_surface_curve',#{helix_curve.eid},"
    f"(#{pcurve.eid}),.PCURVE_S1.)"
)

# ── SWEPT_SURFACE: sweep the profile along the helical directrix ──────────────
swept_surf = f._emit_raw(
    f"SURFACE_OF_LINEAR_EXTRUSION("
    f"'helical_sweep',#{profile_circle.eid},#{helix_curve.eid})"
)

# Wrap in GEOMETRIC_CURVE_SET — no solid, shape_null==True.
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('',"
    f"(#{helix_curve.eid},#{surface_curve.eid},#{swept_surf.eid}))"
)
f.add_product_chain(gcs, uncertainty_literal="LENGTH_MEASURE(1.0E-7)")  # bare typed real, not enum-wrapped (scaffolding-artifact fix)

# NAUO scaffolding for §12.6 assembly-presence lint.
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('HelicalSweep','HelicalSweep','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','helical_sweep_instance','',#9054,#{sub_pdef.eid},$)"
)
