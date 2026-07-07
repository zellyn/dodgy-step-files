"""P008 — Long helix represented as huge B-spline causes catastrophic import time.

Catalog claim: a single long thread/helix represented as B_SPLINE_CURVE_WITH_KNOTS
with thousands of control points (e.g. M10×300 thread) takes >1 hour in FreeCAD
vs. <1 minute in SolidWorks/VariCAD. The helix dominates cost; rest of model is fast.

The defect: STEP file with one helical sweep represented as a NURBS curve with
5000+ control points spanning many turns, plus minimal capping faces. A correct
kernel must scale linearly with face count, not catastrophically. Must not hang
on long helix.

Byte assertions:
  contains(b'B_SPLINE_CURVE_WITH_KNOTS') or contains(b'B_SPLINE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P008",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS with 5040 control points representing a long "
        "helical thread curve (M10x300, 60 turns at pitch 5mm); "
        "catastrophic import time >1 hour in FreeCAD vs <1 min in SolidWorks; "
        "helix parametrization causes quadratic scaling in OCCT tessellator; "
        "NEXT_ASSEMBLY_USAGE_OCCURRENCE scaffolding for §12.6 lint; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── Generate a helical B-spline curve with many control points ──────────────
# M10 thread: radius=5mm, pitch=5mm, 60 turns → length=300mm.
# We use 84 control points per turn × 60 turns = 5040 total.
# Each "turn" is approximated by a cubic B-spline arc set.
# The control points trace a helix: x=r*cos(t), y=r*sin(t), z=pitch*t/(2π)
radius = 5.0      # mm (M10 thread)
pitch = 5.0       # mm per turn
n_turns = 60
pts_per_turn = 84  # 5040 total control points
total_pts = n_turns * pts_per_turn

cpt_entities = []
for i in range(total_pts):
    t = 2.0 * math.pi * i / pts_per_turn  # angle in radians (0..2π per turn)
    z = pitch * (i / pts_per_turn)        # z ascent: 0..300 mm
    x = radius * math.cos(t)
    y = radius * math.sin(t)
    cpt_entities.append(f.cartesian_point((x, y, z)))

# B_SPLINE_CURVE_WITH_KNOTS: degree=3, n=5040 control points.
# Knot multiplicities: [4] at start, [1]*interior, [4] at end.
# Interior knots evenly spaced to give (5040 - 3 - 1) = 5036 intervals.
n = total_pts
degree = 3
n_interior = n - degree - 1  # = 5036
# knots: [0.0] mult 4, then interior at 1..n_interior, then [n_interior+1] mult 4
# Use integer knot values for simplicity.
mults = [4] + [1] * n_interior + [4]
knots = [0.0] + [float(i) for i in range(1, n_interior + 1)] + [float(n_interior + 1)]

cp_refs = ",".join(f"#{e.eid}" for e in cpt_entities)
mults_str = ",".join(str(m) for m in mults)
knots_str = ",".join(f"{k:.1f}" for k in knots)

helix_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS("
    f"'M10x300_thread_helix',"
    f"{degree},"
    f"({cp_refs}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"({mults_str}),"
    f"({knots_str}),"
    f".UNSPECIFIED.)"
)

# Wrap in GEOMETRIC_CURVE_SET — no solid, shape_null==True.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{helix_curve.eid}))")
f.add_product_chain(gcs)

# NAUO scaffolding for §12.6 assembly-presence lint.
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('M10x300Thread','M10x300Thread','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','thread_helix_instance','',#9054,#{sub_pdef.eid},$)"
)
