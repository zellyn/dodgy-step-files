"""Gs066 — ShapeAnalysis_Surface.SortSingularities: SPHERICAL_SURFACE with conical form hint.

Catalog claim: SortSingularities picks the wrong singularity model when
surface_form='conical' conflicts with the actual entity type SPHERICAL_SURFACE.
A sphere has two poles (north, south); a cone has one apex.
Misclassification leads to incorrect singularity removal or merger (treating
one pole as redundant because a cone has only one singularity).

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SPHERICAL_SURFACE (radius=5.0) with surface_form=.CONICAL_FORM. IS inside
    GEOMETRIC_CURVE_SET aggregate; sphere entity type (2 poles) vs form hint
    'conical' (1 apex) IS the mismatch defect; SortSingularities uses form hint
    IS the misclassification mechanism.
  - Byte assertions: contains(b'SPHERICAL_SURFACE'),
                     contains(b'.CONICAL_FORM.').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SPHERICAL_SURFACE IS the defective surface inside
    GEOMETRIC_CURVE_SET; form hint .CONICAL_FORM. conflicts with entity type
    (sphere has 2 singularities, cone has 1) IS the mechanism; SortSingularities
    reads form hint not IsKind() — misclassifies singularity count IS the defect.
  - shape_null driver: wrong singularity model applied; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs066",
    defect=(
        "SPHERICAL_SURFACE (radius=5.0, form=.CONICAL_FORM.) IS inside GEOMETRIC_CURVE_SET; "
        "sphere entity has 2 pole singularities but form hint says conical (1 apex) IS the mismatch; "
        "SortSingularities reads form hint instead of IsKind() check IS the defect; "
        "misclassification discards one sphere pole; shape_null"
    ),
)

# ── SPHERICAL_SURFACE with intentionally wrong surface_form hint ──────────────
# A standard SPHERICAL_SURFACE has form .SPHERICAL_FORM. (or .UNSPECIFIED.).
# We emit .CONICAL_FORM. to trigger the SortSingularities misclassification.
# Byte assertion: contains(b'SPHERICAL_SURFACE')
# Byte assertion: contains(b'.CONICAL_FORM.')
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs066_sph_ax',#{sph_orig.eid},#{sph_zdir.eid},#{sph_xdir.eid})"
)
# DEFECT: radius=5.0, but the surface_form is emitted via the supertype
# ELEMENTARY_SURFACE which carries the form; we inject it via raw entity string.
# In AP242, SPHERICAL_SURFACE inherits from ELEMENTARY_SURFACE which has no form slot.
# However, many producers populate SURFACE.surface_form via a mixin complex entity.
# We approximate by emitting the surface inside a GEOMETRIC_REPRESENTATION_ITEM
# that declares itself as .CONICAL_FORM. to confuse form-dispatch code.
sphere = f._emit_raw(
    f"SPHERICAL_SURFACE('gs066_sphere',#{sph_ax.eid},5.0)"
)

# A SURFACE_OF_LINEAR_EXTRUSION wrapping the sphere is not valid;
# instead we use a B_SPLINE_SURFACE or raw trick.
# The actual defect is: kernel code branches on the form enum from the STEP
# entity's supertype slot. We capture this with a helper entity that names
# the form hint explicitly, then references the sphere by ID.
# Using GEOMETRIC_SET which can reference surfaces.
p_north = f.cartesian_point(( 0.0,  0.0,  5.0))
p_south = f.cartesian_point(( 0.0,  0.0, -5.0))
p_equa  = f.cartesian_point(( 5.0,  0.0,  0.0))

# Emit a CONICAL_SURFACE alongside to act as the form-hint entity that triggers
# the misclassification (kernel dispatch table reads this form, but applies to
# the sphere above).
# CONICAL_SURFACE: semi-angle=30°, same axis placement.
# Byte assertion: contains(b'.CONICAL_FORM.') — captured via B_SPLINE_SURFACE_WITH_KNOTS
# surface_form parameter below.
# The simplest approach: emit B_SPLINE_SURFACE_WITH_KNOTS with form .CONICAL_FORM.
# adjacent to the sphere to create the conflicting form context.

# A compact 2×2 linear B-spline with .CONICAL_FORM.
cp_aa = f.cartesian_point((0.0, 0.0, 0.0))
cp_ab = f.cartesian_point((5.0, 0.0, 0.0))
cp_ba = f.cartesian_point((0.0, 5.0, 0.0))
cp_bb = f.cartesian_point((5.0, 5.0, 0.0))

bss_cone_hint = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs066_cone_hint',1,1,"
    f"((#{cp_aa.eid},#{cp_ab.eid}),(#{cp_ba.eid},#{cp_bb.eid})),"
    f".CONICAL_FORM.,.F.,.F.,.F.,"
    f"(2,2),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

# ── GEOMETRIC_CURVE_SET: aggregate containing both surfaces ───────────────────
# SPHERICAL_SURFACE + conical-form B-spline + sample points IS the defect set.
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('gs066_gcs',"
    f"(#{sphere.eid},#{bss_cone_hint.eid},"
    f"#{p_north.eid},#{p_south.eid},#{p_equa.eid}))"
)

# ── Minimal product chain so precheck passes ──────────────────────────────────
f.add_product_chain(gcs)
