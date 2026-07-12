"""Minimal Python builder for Part-21 STEP fixtures.

Each fixture source lives at ``fixture_sources/<section>/<ID>.py`` and
constructs a ``StepFile`` object via the convenience methods below. The
CLI (``python -m step_corpus.step_builder <source.py>``) runs the
source and writes the corresponding ``step-examples/<section>/<ID>.stp``.

The builder takes responsibility for **correct-by-construction Part-21
syntax**: entity-ID allocation, paren balance, REAL formatting with
decimals, FILE_DESCRIPTION arity, the ``ISO-10303-21;`` ↔
``END-ISO-10303-21;`` bookends, and the canonical PRODUCT chain.

Fixture authors (humans or LLMs) write the *intent* of the defect; the
builder ensures the output is syntactically valid Part-21 — eliminating
the entire class of bugs the Part-21 validator catches today.

Design choices:

- One entity type per method. The method name lower-cases the entity:
  ``f.cartesian_point((0, 0, 0))`` emits ``#N=CARTESIAN_POINT('',
  (0.0, 0.0, 0.0));``.
- ``Entity`` objects carry their assigned ID and serialize themselves
  to ``#N`` when referenced from another entity's arg list.
- Lists of entities serialize as ``(#a,#b,#c)``.
- The PRODUCT chain is opt-in (``f.add_product_chain(model_entity)``)
  because not every fixture needs OCCT reachability.
- Defect demonstration is explicit: the *malformed* shape is what the
  fixture author writes — the builder doesn't refuse to construct
  invalid topology (e.g. ``manifold_solid_brep`` accepts an
  ``open_shell`` outer because some defect classes need exactly that).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
import sys


# ----- Entity model -----

@dataclass
class Entity:
    """A Part-21 entity instance: ``#N=TYPE_NAME(arg1, arg2, ...);``."""

    eid: int
    type_name: str
    args: list[Any] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"#{self.eid}"

    def ref(self) -> str:
        return f"#{self.eid}"

    def part21(self) -> str:
        return f"#{self.eid}={self.type_name}({_format_arglist(self.args)});"


def _format_real(v: float) -> str:
    """Format a float as a Part-21 REAL (must contain a decimal point).

    Rounds to 12 significant digits to make output platform-deterministic
    (libm's ``math.cos``/``sin`` etc. can differ in the last few bits
    between macOS and Linux, which broke fixture-source round-trip
    checks on CI). 12 digits is more than enough precision for CAD
    fixtures while eliminating libm divergence.

    Also snaps any value with magnitude < 1e-14 to exactly 0.0. CAD
    geometric precision is at most ~1e-9; values smaller than 1e-14
    are libm round-off noise (e.g. ``math.sin(math.pi)`` evaluates to
    ~1.22e-16, with the exact ULP varying between macOS and Linux).
    Snapping suppresses the cross-platform divergence.
    """
    v = float(v)
    if abs(v) < 1e-14:
        v = 0.0
    # Round to 12 significant digits; preserves identity of nice values
    # like 0.5 / -1.0 / 1e-7 and trims libm-divergent trailing bits.
    s = f"{v:.12g}"
    # Ensure a decimal point exists (Part-21 §6.4 requires REAL to have one)
    if "e" in s or "E" in s:
        mantissa, exp = (s.split("e") if "e" in s else s.split("E"))
        if "." not in mantissa:
            mantissa += ".0"
        return f"{mantissa}E{exp}"
    if "." not in s:
        s += ".0"
    return s


def _format_arg(a: Any) -> str:
    if a is None:
        return "$"
    if a is True:
        return ".T."
    if a is False:
        return ".F."
    if isinstance(a, (Entity, DanglingRef)):
        return a.ref()
    if isinstance(a, Enum):
        return f".{a.value}."
    if isinstance(a, (list, tuple)):
        return f"({','.join(_format_arg(x) for x in a)})"
    if isinstance(a, str):
        # Escape apostrophes by doubling
        return "'" + a.replace("'", "''") + "'"
    if isinstance(a, bool):  # must come before int; bool subclasses int
        return ".T." if a else ".F."
    if isinstance(a, int):
        return str(a)
    if isinstance(a, float):
        return _format_real(a)
    raise TypeError(f"cannot format arg of type {type(a).__name__}: {a!r}")


def _format_arglist(args: list[Any]) -> str:
    return ",".join(_format_arg(a) for a in args)


class Enum:
    """Wrap an enumeration value so it serializes as ``.VALUE.``."""

    def __init__(self, value: str):
        self.value = value

    def __repr__(self) -> str:
        return f".{self.value}."


@dataclass
class DanglingRef:
    """An intentional unresolved ``#N`` reference. Used by fixtures that
    demonstrate parser behavior on dangling refs (e.g. Tfa098). The
    builder doesn't add a corresponding entity, so the resulting file
    has a real unresolved-reference defect.
    """
    eid: int

    def ref(self) -> str:
        return f"#{self.eid}"


# ----- StepFile -----

class StepFile:
    """A Part-21 STEP fixture under construction.

    Args:
        catalog_id: fixture id, e.g. ``"Tsh020"``. Used in FILE_NAME
            and as the FILE_DESCRIPTION text.
        defect: one-line description of the defect being demonstrated.
            Goes into the leading ``/* */`` comment block.
        timestamp: ISO-8601 timestamp for FILE_NAME; default
            ``"2026-06-17T00:00:00"``.
    """

    def __init__(self, catalog_id: str, defect: str,
                 timestamp: str = "2026-06-17T00:00:00",
                 schema: str = "AP214"):
        self.catalog_id = catalog_id
        self.defect = defect
        self.timestamp = timestamp
        # ``schema`` may be "AP214" (default) or "AP242". AP242 entities
        # like PROJECTED_ZONE_DEFINITION, TRIANGULATED_FACE etc. require
        # AP242 — using them under AP214 trips schema_oracle test.
        self.schema = schema
        self.entities: list[Entity] = []
        self._next_id = 1
        # Entity-ID 9000-9023 reserved for PRODUCT chain (set by add_product_chain).
        self._reserved_high = 9000

    def _emit(self, type_name: str, *args, name: str = "") -> Entity:
        """Allocate next ID, append entity, return it.

        ``name`` is the first arg if the entity type takes a name slot
        (most do); pass empty string to omit visually but keep slot.
        """
        eid = self._next_id
        self._next_id += 1
        # Skip the reserved high range for PRODUCT chain.
        if eid >= self._reserved_high:
            eid = max(eid, self._reserved_high + 50)
            self._next_id = eid + 1
        if name == "_no_name":
            full_args = list(args)
        else:
            full_args = [name] + list(args)
        ent = Entity(eid, type_name, full_args)
        self.entities.append(ent)
        return ent

    # ----- Geometry primitives -----

    def cartesian_point(self, coords: tuple[float, float, float], name: str = "") -> Entity:
        return self._emit("CARTESIAN_POINT", list(coords), name=name)

    def direction(self, ratios: tuple[float, float, float], name: str = "") -> Entity:
        return self._emit("DIRECTION", list(ratios), name=name)

    def vector(self, dir: Entity, magnitude: float, name: str = "") -> Entity:
        return self._emit("VECTOR", dir, float(magnitude), name=name)

    def line(self, pnt: Entity, vec: Entity, name: str = "") -> Entity:
        return self._emit("LINE", pnt, vec, name=name)

    def circle(self, placement: Entity, radius: float, name: str = "") -> Entity:
        return self._emit("CIRCLE", placement, float(radius), name=name)

    def axis2_placement_3d(self, location: Entity, axis: Entity, ref_direction: Entity,
                            name: str = "") -> Entity:
        return self._emit("AXIS2_PLACEMENT_3D", location, axis, ref_direction, name=name)

    # ----- Topology -----

    def vertex_point(self, pnt: Entity, name: str = "") -> Entity:
        return self._emit("VERTEX_POINT", pnt, name=name)

    def edge_curve(self, v1: Entity, v2: Entity, curve: Entity,
                   same_sense: bool = True, name: str = "") -> Entity:
        return self._emit("EDGE_CURVE", v1, v2, curve, same_sense, name=name)

    def oriented_edge(self, edge: Entity, orientation: bool = True, name: str = "") -> Entity:
        # ORIENTED_EDGE takes (name, *, *, edge_element, orientation) with stars for unused.
        # We omit using None ($).
        return self._emit("ORIENTED_EDGE", None, None, edge, orientation, name=name)

    def edge_loop(self, oriented_edges: list[Entity], name: str = "") -> Entity:
        return self._emit("EDGE_LOOP", list(oriented_edges), name=name)

    def face_outer_bound(self, edge_loop: Entity, orientation: bool = True,
                          name: str = "") -> Entity:
        return self._emit("FACE_OUTER_BOUND", edge_loop, orientation, name=name)

    def face_bound(self, edge_loop: Entity, orientation: bool = True,
                    name: str = "") -> Entity:
        return self._emit("FACE_BOUND", edge_loop, orientation, name=name)

    def advanced_face(self, bounds: list[Entity], surface: Entity,
                       same_sense: bool = True, name: str = "") -> Entity:
        return self._emit("ADVANCED_FACE", list(bounds), surface, same_sense, name=name)

    def plane(self, placement: Entity, name: str = "") -> Entity:
        return self._emit("PLANE", placement, name=name)

    def cylindrical_surface(self, placement: Entity, radius: float, name: str = "") -> Entity:
        return self._emit("CYLINDRICAL_SURFACE", placement, float(radius), name=name)

    def conical_surface(self, placement: Entity, radius: float, semi_angle: float,
                        name: str = "") -> Entity:
        return self._emit("CONICAL_SURFACE", placement, float(radius), float(semi_angle), name=name)

    def spherical_surface(self, placement: Entity, radius: float, name: str = "") -> Entity:
        return self._emit("SPHERICAL_SURFACE", placement, float(radius), name=name)

    def toroidal_surface(self, placement: Entity, major_radius: float, minor_radius: float,
                         name: str = "") -> Entity:
        return self._emit("TOROIDAL_SURFACE", placement, float(major_radius),
                          float(minor_radius), name=name)

    def open_shell(self, faces: list[Entity], name: str = "") -> Entity:
        return self._emit("OPEN_SHELL", list(faces), name=name)

    def closed_shell(self, faces: list[Entity], name: str = "") -> Entity:
        return self._emit("CLOSED_SHELL", list(faces), name=name)

    def manifold_solid_brep(self, outer: Entity, name: str = "") -> Entity:
        """The DEFECT-DEMONSTRATION HOOK: outer should be CLOSED_SHELL per
        spec, but we accept OPEN_SHELL too for fixtures that demonstrate
        that exact malformation. Builder warns but doesn't refuse."""
        if hasattr(outer, "type_name") and outer.type_name == "OPEN_SHELL":
            # Intentional: many fixtures demonstrate this exact bug. Emit a
            # comment in the serialized form, but proceed.
            ent = self._emit("MANIFOLD_SOLID_BREP", outer, name=name)
            ent._note = "outer is OPEN_SHELL (intentional defect)"
            return ent
        return self._emit("MANIFOLD_SOLID_BREP", outer, name=name)

    def shell_based_surface_model(self, shells: list[Entity], name: str = "") -> Entity:
        return self._emit("SHELL_BASED_SURFACE_MODEL", list(shells), name=name)

    # ----- B-spline + trimmed surfaces (the most common _emit_raw use cases) -----

    def rational_b_spline_curve_with_knots(self, degree: int,
                                            control_points: list[Entity],
                                            weights: list[float],
                                            knot_multiplicities: list[int],
                                            knots: list[float],
                                            *,
                                            curve_form: str = "UNSPECIFIED",
                                            closed: bool = False,
                                            self_intersect: bool = False,
                                            knot_spec: str = "UNSPECIFIED",
                                            name: str = "") -> Entity:
        """Rational (NURBS) B-spline curve as a complex instance combining
        BOUNDED_CURVE + B_SPLINE_CURVE + B_SPLINE_CURVE_WITH_KNOTS +
        CURVE + GEOMETRIC_REPRESENTATION_ITEM + RATIONAL_B_SPLINE_CURVE +
        REPRESENTATION_ITEM.

        Emitted as a complex-instance ``(B_SPLINE_CURVE_WITH_KNOTS(...)
        RATIONAL_B_SPLINE_CURVE(...))`` via _emit_raw, since these are
        the only entity types most readers expect for rational curves.

        ``len(weights)`` must equal ``len(control_points)``.
        """
        if len(weights) != len(control_points):
            raise ValueError(
                f"weights ({len(weights)}) must match control_points "
                f"({len(control_points)})")
        n = len(control_points)
        expected = n + degree + 1
        actual = sum(knot_multiplicities)
        if actual != expected:
            raise ValueError(
                f"knot-mult sum {actual} != n_poles({n}) + degree({degree}) + 1 = {expected}")
        if len(knots) != len(knot_multiplicities):
            raise ValueError("knots and knot_multiplicities must be parallel")
        cp_refs = ",".join(p.ref() for p in control_points)
        mults = ",".join(str(m) for m in knot_multiplicities)
        knts = ",".join(_format_real(k) for k in knots)
        wts = ",".join(_format_real(w) for w in weights)
        body = (
            f"(B_SPLINE_CURVE({degree},({cp_refs}),.{curve_form}.,"
            f".{'T' if closed else 'F'}.,.{'T' if self_intersect else 'F'}.)"
            f"B_SPLINE_CURVE_WITH_KNOTS(({mults}),({knts}),.{knot_spec}.)"
            f"BOUNDED_CURVE()CURVE()GEOMETRIC_REPRESENTATION_ITEM()"
            f"RATIONAL_B_SPLINE_CURVE(({wts}))"
            f"REPRESENTATION_ITEM('{name}'))"
        )
        return self._emit_raw(body)

    def rational_b_spline_surface_with_knots(self, u_degree: int, v_degree: int,
                                              control_points_grid: list[list[Entity]],
                                              weights_grid: list[list[float]],
                                              u_multiplicities: list[int],
                                              v_multiplicities: list[int],
                                              u_knots: list[float],
                                              v_knots: list[float],
                                              *,
                                              surface_form: str = "UNSPECIFIED",
                                              u_closed: bool = False,
                                              v_closed: bool = False,
                                              self_intersect: bool = False,
                                              knot_spec: str = "UNSPECIFIED",
                                              name: str = "") -> Entity:
        """Rational (NURBS) B-spline surface. weights_grid must be parallel
        to control_points_grid (same nu × nv shape)."""
        nu = len(control_points_grid)
        nv = len(control_points_grid[0]) if nu else 0
        if len(weights_grid) != nu or any(len(row) != nv for row in weights_grid):
            raise ValueError("weights_grid must have same shape as control_points_grid")
        if sum(u_multiplicities) != nu + u_degree + 1:
            raise ValueError("u-knot-mult sum wrong")
        if sum(v_multiplicities) != nv + v_degree + 1:
            raise ValueError("v-knot-mult sum wrong")
        cp_grid = ",".join(
            "(" + ",".join(p.ref() for p in row) + ")"
            for row in control_points_grid)
        wt_grid = ",".join(
            "(" + ",".join(_format_real(w) for w in row) + ")"
            for row in weights_grid)
        u_mults = ",".join(str(m) for m in u_multiplicities)
        v_mults = ",".join(str(m) for m in v_multiplicities)
        u_knts = ",".join(_format_real(k) for k in u_knots)
        v_knts = ",".join(_format_real(k) for k in v_knots)
        body = (
            f"(B_SPLINE_SURFACE({u_degree},{v_degree},({cp_grid}),.{surface_form}.,"
            f".{'T' if u_closed else 'F'}.,.{'T' if v_closed else 'F'}.,"
            f".{'T' if self_intersect else 'F'}.)"
            f"B_SPLINE_SURFACE_WITH_KNOTS(({u_mults}),({v_mults}),({u_knts}),({v_knts}),.{knot_spec}.)"
            f"BOUNDED_SURFACE()GEOMETRIC_REPRESENTATION_ITEM()"
            f"RATIONAL_B_SPLINE_SURFACE(({wt_grid}))"
            f"REPRESENTATION_ITEM('{name}')SURFACE())"
        )
        return self._emit_raw(body)

    def b_spline_curve_with_knots(self, degree: int,
                                   control_points: list[Entity],
                                   knot_multiplicities: list[int],
                                   knots: list[float],
                                   *,
                                   curve_form: str = "UNSPECIFIED",
                                   closed: bool = False,
                                   self_intersect: bool = False,
                                   knot_spec: str = "UNSPECIFIED",
                                   name: str = "") -> Entity:
        """B_SPLINE_CURVE_WITH_KNOTS per ISO 10303-42 §4.4.43.

        Invariant: ``sum(knot_multiplicities) == len(control_points) + degree + 1``.
        Builder raises ValueError on violation.
        """
        n = len(control_points)
        expected = n + degree + 1
        actual = sum(knot_multiplicities)
        if actual != expected:
            raise ValueError(
                f"B_SPLINE_CURVE_WITH_KNOTS knot-mult sum {actual} != "
                f"n_poles({n}) + degree({degree}) + 1 = {expected}")
        if len(knots) != len(knot_multiplicities):
            raise ValueError(
                f"knots ({len(knots)}) and knot_multiplicities "
                f"({len(knot_multiplicities)}) must be parallel lists")
        return self._emit(
            "B_SPLINE_CURVE_WITH_KNOTS",
            degree,
            list(control_points),
            Enum(curve_form),
            closed,
            self_intersect,
            list(knot_multiplicities),
            [float(k) for k in knots],
            Enum(knot_spec),
            name=name,
        )

    def b_spline_surface_with_knots(self, u_degree: int, v_degree: int,
                                     control_points_grid: list[list[Entity]],
                                     u_multiplicities: list[int],
                                     v_multiplicities: list[int],
                                     u_knots: list[float],
                                     v_knots: list[float],
                                     *,
                                     surface_form: str = "UNSPECIFIED",
                                     u_closed: bool = False,
                                     v_closed: bool = False,
                                     self_intersect: bool = False,
                                     knot_spec: str = "UNSPECIFIED",
                                     name: str = "") -> Entity:
        """B_SPLINE_SURFACE_WITH_KNOTS per ISO 10303-42 §4.4.49.

        ``control_points_grid`` is a 2-D list: outer dimension is U, inner V.
        Invariants:
          sum(u_multiplicities) == len(control_points_grid)   + u_degree + 1
          sum(v_multiplicities) == len(control_points_grid[0]) + v_degree + 1
        """
        if not control_points_grid or not control_points_grid[0]:
            raise ValueError("control_points_grid must be non-empty 2-D")
        nu = len(control_points_grid)
        nv = len(control_points_grid[0])
        if any(len(row) != nv for row in control_points_grid):
            raise ValueError("control_points_grid is not rectangular")
        u_expected = nu + u_degree + 1
        v_expected = nv + v_degree + 1
        if sum(u_multiplicities) != u_expected:
            raise ValueError(
                f"u-knot-mult sum {sum(u_multiplicities)} != "
                f"nu({nu}) + u_degree({u_degree}) + 1 = {u_expected}")
        if sum(v_multiplicities) != v_expected:
            raise ValueError(
                f"v-knot-mult sum {sum(v_multiplicities)} != "
                f"nv({nv}) + v_degree({v_degree}) + 1 = {v_expected}")
        return self._emit(
            "B_SPLINE_SURFACE_WITH_KNOTS",
            u_degree,
            v_degree,
            list(control_points_grid),
            Enum(surface_form),
            u_closed,
            v_closed,
            self_intersect,
            list(u_multiplicities),
            list(v_multiplicities),
            [float(k) for k in u_knots],
            [float(k) for k in v_knots],
            Enum(knot_spec),
            name=name,
        )

    def rectangular_trimmed_surface(self, basis_surface: Entity,
                                     u1: float, u2: float, v1: float, v2: float,
                                     *,
                                     usense: bool = True, vsense: bool = True,
                                     name: str = "") -> Entity:
        """RECTANGULAR_TRIMMED_SURFACE per ISO 10303-42 §4.4.21.

        Does NOT enforce u1 < u2 or v1 < v2 — fixtures often demonstrate
        defects via inverted bounds.
        """
        return self._emit(
            "RECTANGULAR_TRIMMED_SURFACE",
            basis_surface,
            float(u1), float(u2), float(v1), float(v2),
            usense, vsense,
            name=name,
        )

    # ----- Convenience composites -----

    def closed_polyline_loop(self, points: list[Entity]) -> Entity:
        """Build an EDGE_LOOP from a closed sequence of CARTESIAN_POINTs.

        Returns the EDGE_LOOP entity. Emits all intermediate VERTEX_POINTs,
        DIRECTIONs, VECTORs, LINEs, EDGE_CURVEs, ORIENTED_EDGEs.
        """
        if len(points) < 3:
            raise ValueError("closed_polyline_loop needs at least 3 points")
        verts = [self.vertex_point(p) for p in points]
        oriented = []
        for i in range(len(points)):
            v1 = verts[i]
            v2 = verts[(i + 1) % len(points)]
            p1, p2 = points[i], points[(i + 1) % len(points)]
            # Direction from p1 → p2
            dx = p2.args[1][0] - p1.args[1][0]  # args = [name, coords]
            dy = p2.args[1][1] - p1.args[1][1]
            dz = p2.args[1][2] - p1.args[1][2]
            length = (dx**2 + dy**2 + dz**2) ** 0.5
            if length == 0:
                raise ValueError(f"zero-length edge between {p1!r} and {p2!r}")
            dir_ent = self.direction((dx/length, dy/length, dz/length))
            vec_ent = self.vector(dir_ent, length)
            line_ent = self.line(p1, vec_ent)
            edge_curve = self.edge_curve(v1, v2, line_ent)
            oriented.append(self.oriented_edge(edge_curve))
        return self.edge_loop(oriented)

    # ----- Mandatory PRODUCT chain (canonical) -----

    def add_product_chain(self, model_entity: Entity, *,
                          product_id: str | None = None,
                          mode: str = "surface_shape",
                          uncertainty: float = 1.0E-7) -> Entity:
        """Add the canonical PRODUCT/PRODUCT_DEFINITION chain at fixed IDs
        #9000-#9023 referencing ``model_entity`` (usually a
        SHELL_BASED_SURFACE_MODEL or MANIFOLD_SOLID_BREP).

        Returns the SHAPE_DEFINITION_REPRESENTATION entity.

        ``mode`` controls the wrapper:
            - "surface_shape" → MANIFOLD_SURFACE_SHAPE_REPRESENTATION
                (for SHELL_BASED_SURFACE_MODEL)
            - "brep_shape" → ADVANCED_BREP_SHAPE_REPRESENTATION
                (for solid breps)

        ``uncertainty`` sets the global geom_ctx UNCERTAINTY_MEASURE
        (default 1.0E-7). Override for fixtures that need tight (e.g.,
        1.0E-15) or loose (e.g., 0.01) tolerances embedded in the
        geometric context.
        """
        if product_id is None:
            product_id = self.catalog_id
        # Force IDs 9000+
        block_start = max(9000, self._next_id)
        self._next_id = block_start

        app_ctx = Entity(self._next_id, "APPLICATION_CONTEXT", ["mechanical design"])
        self.entities.insert(0, app_ctx)  # insert near beginning
        self._next_id += 1

        product_ctx = self._emit("PRODUCT_CONTEXT", app_ctx, "mechanical", name="")
        product = self._emit("PRODUCT", product_id, product_id, "", [product_ctx], name="_no_name")
        prod_def_form = self._emit("PRODUCT_DEFINITION_FORMATION", "", "", product, name="_no_name")
        prod_def_ctx = self._emit("PRODUCT_DEFINITION_CONTEXT", app_ctx, "design", name="part definition")
        prod_def = self._emit("PRODUCT_DEFINITION", "", "", prod_def_form, prod_def_ctx, name="")
        prod_def_shape = self._emit("PRODUCT_DEFINITION_SHAPE", "", "", prod_def, name="")
        # Unit definitions (complex instances)
        length_unit = self._emit_raw(
            "(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))"
        )
        plane_angle_unit = self._emit_raw(
            "(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))"
        )
        solid_angle_unit = self._emit_raw(
            "(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())"
        )
        unc_literal = f"LENGTH_MEASURE({uncertainty:.6E})" if uncertainty != 1.0E-7 else "LENGTH_MEASURE(1.0E-7)"
        uncertainty_ent = self._emit(
            "UNCERTAINTY_MEASURE_WITH_UNIT",
            Enum_(unc_literal),
            length_unit, "distance_accuracy_value", "", name="_no_name",
        )
        geom_ctx = self._emit_raw(
            f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
            f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(({uncertainty_ent.ref()}))"
            f"GLOBAL_UNIT_ASSIGNED_CONTEXT(({length_unit.ref()},{plane_angle_unit.ref()},{solid_angle_unit.ref()}))"
            f"REPRESENTATION_CONTEXT('','3D'))"
        )

        if mode == "surface_shape":
            shape_rep = self._emit("MANIFOLD_SURFACE_SHAPE_REPRESENTATION",
                                    [model_entity], geom_ctx, name="")
        elif mode == "brep_shape":
            shape_rep = self._emit("ADVANCED_BREP_SHAPE_REPRESENTATION",
                                    [model_entity], geom_ctx, name="")
        else:
            raise ValueError(f"unknown mode: {mode}")
        sdr = self._emit("SHAPE_DEFINITION_REPRESENTATION", prod_def_shape, shape_rep, name="_no_name")
        return sdr

    def _emit_raw(self, body: str) -> Entity:
        """Emit a raw-text entity body (for complex instances). The body is
        the part between ``#N=`` and ``;``.
        """
        eid = self._next_id
        self._next_id += 1
        ent = Entity(eid, "__RAW__", [])
        ent._raw_body = body
        self.entities.append(ent)
        return ent

    # ----- Serialization -----

    def render(self) -> str:
        """Render the full Part-21 file as a string."""
        header = self._render_header()
        data_lines = []
        for e in self.entities:
            if e.type_name == "__RAW__":
                data_lines.append(f"#{e.eid}={e._raw_body};")
            else:
                data_lines.append(e.part21())
        data = "\n".join(data_lines)
        return f"ISO-10303-21;\n/* {self.catalog_id}: {self.defect} */\n{header}\nDATA;\n{data}\nENDSEC;\nEND-ISO-10303-21;\n"

    def _render_header(self) -> str:
        schema_lit = {
            "AP214": "AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }",
            "AP242": "AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 4 }",
        }[self.schema]
        return (
            "HEADER;\n"
            f"FILE_DESCRIPTION(('{self.catalog_id}'),'2;1');\n"
            f"FILE_NAME('{self.catalog_id}.stp','{self.timestamp}',(''),(''),"
            f"'cad-research-suite','','');\n"
            f"FILE_SCHEMA(('{schema_lit}'));\n"
            "ENDSEC;"
        )

    def write(self, path: str | Path) -> None:
        # write_bytes so fixtures with CRLF / NUL / non-ASCII payloads
        # (Le028's NUL+CRLF, Le032 UTF-16-BOM bodies, §-style symbols)
        # round-trip byte-stable. write_text would apply universal-newline
        # translation on some platforms.
        Path(path).write_bytes(self.render().encode("utf-8"))


# Re-export Enum for fixture source files
Enum_ = Enum


# ----- CLI -----

def main(argv: list[str] | None = None) -> int:
    """Run a fixture source file and emit the corresponding .stp.

    The source must define a top-level variable ``f`` that is a StepFile
    instance. Output goes to ``step-examples/<section>/<ID>.stp``
    relative to the repo root.

    Repo root inferred from the source's path:
    ``fixture_sources/<section>/<ID>.py`` →
    ``step-examples/<section>/<ID>.stp``.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("usage: python -m step_corpus.step_builder <fixture_source.py> [<source>...]",
              file=sys.stderr)
        return 2
    rc = 0
    for src in args:
        src_path = Path(src).resolve()
        if not src_path.is_file():
            print(f"no such file: {src}", file=sys.stderr)
            rc = 2
            continue
        # Find fixture_sources in path
        parts = src_path.parts
        try:
            idx = parts.index("fixture_sources")
        except ValueError:
            print(f"path must contain fixture_sources/: {src}", file=sys.stderr)
            rc = 2
            continue
        # repo_root = parent of fixture_sources
        repo_root = Path(*parts[:idx])
        section = parts[idx + 1]
        fixture_id = src_path.stem
        out_path = repo_root / "step-examples" / section / f"{fixture_id}.stp"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Execute the source
        ns: dict[str, Any] = {}
        ns["__file__"] = str(src_path)
        ns["__name__"] = "__fixture__"
        src_text = src_path.read_text()
        try:
            exec(compile(src_text, str(src_path), "exec"), ns)
        except Exception as e:
            print(f"{src}: error executing: {e}", file=sys.stderr)
            rc = 1
            continue
        f = ns.get("f")
        # Duck-type: StepFile defines `render()` and `write()`. Avoid
        # isinstance because `python -m step_corpus.step_builder` runs
        # this module as __main__, and the source's `from step_corpus.step_builder
        # import StepFile` imports a separate copy of the class.
        if f is None or not (hasattr(f, "render") and hasattr(f, "write")):
            print(f"{src}: source must define top-level variable `f` as StepFile",
                  file=sys.stderr)
            rc = 1
            continue
        f.write(out_path)
        print(f"{src_path.name} → {out_path}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
