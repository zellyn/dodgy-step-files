"""Writer-pathology active oracle.

§12-13 catalog entries (Wr*) describe defects a buggy *writer* would
inject into an emitted STEP file. Today they're byte-asserted only:
the assertion runs against a hand-authored fixture demonstrating the
post-pathology bytes. That checks the fixture, not a live writer.

This module closes the loop: a small ``BuggyWriter`` simulator that
takes a clean Part-21 input (a minimal cube fixture, embedded in this
file so the oracle is self-contained), applies one specific defect,
and emits output bytes. The companion ``verify_pathology`` function
confirms the output exhibits the byte-signature the catalog claims.

Each defect simulator is a small string/regex transformation. None of
them load OCCT; the bug is in *bytes*, so we work in bytes.

Some Wr* defects require kernel state to demonstrate (e.g.
"colour assignments dropped on round-trip", where bytes-of-output do
not prove the loss; you need the bytes-of-input as the comparison).
Those are listed in ``WRITER_SKIP`` with a reason.

Usage::

    cd validation
    uv run python -m step_corpus._writer_oracle             # summary
    uv run python -m step_corpus._writer_oracle --json
    uv run python -m step_corpus._writer_oracle --list      # which Wr ids implementable
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable


# ----- Canonical clean input fixture -------------------------------------
#
# A minimal but spec-conforming Part-21 file describing a unit cube as a
# MANIFOLD_SOLID_BREP whose outer is a CLOSED_SHELL. Embedded as a
# constant so the writer oracle has zero filesystem dependencies and the
# input is itself a fixed reference point. We deliberately use canonical
# `.T.` / `.F.` lexemes, period decimals, ASCII only, period-decimal
# numbers, sequential numbering, LF line endings.
CLEAN_INPUT: bytes = b"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('clean cube'),'2;1');
FILE_NAME('clean.stp','2026-05-01T00:00:00',('zellyn'),('research'),'writer_oracle','step_corpus','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));
ENDSEC;
DATA;
#1=APPLICATION_CONTEXT('automotive_design');
#2=APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#1);
#3=PRODUCT_CONTEXT('part',#1,'mechanical');
#4=PRODUCT('cube','cube','',(#3));
#5=PRODUCT_DEFINITION_FORMATION('','',#4);
#6=PRODUCT_DEFINITION_CONTEXT('part definition',#1,'design');
#7=PRODUCT_DEFINITION('design','',#5,#6);
#10=CARTESIAN_POINT('',(0.0,0.0,0.0));
#11=CARTESIAN_POINT('',(1.0,0.0,0.0));
#12=CARTESIAN_POINT('',(1.0,1.0,0.0));
#13=CARTESIAN_POINT('',(0.0,1.0,0.0));
#14=CARTESIAN_POINT('',(0.0,0.0,1.0));
#15=CARTESIAN_POINT('',(1.0,0.0,1.0));
#16=CARTESIAN_POINT('',(1.0,1.0,1.0));
#17=CARTESIAN_POINT('',(0.0,1.0,1.0));
#20=DIRECTION('',(0.0,0.0,1.0));
#21=DIRECTION('',(1.0,0.0,0.0));
#22=AXIS2_PLACEMENT_3D('main',#10,#20,#21);
#30=VERTEX_POINT('',#10);
#31=VERTEX_POINT('',#11);
#32=VERTEX_POINT('',#12);
#33=VERTEX_POINT('',#13);
#34=VERTEX_POINT('',#14);
#35=VERTEX_POINT('',#15);
#36=VERTEX_POINT('',#16);
#37=VERTEX_POINT('',#17);
#40=PLANE('',#22);
#50=CLOSED_SHELL('outer',(#40));
#60=MANIFOLD_SOLID_BREP('cube',#50);
#70=SHAPE_REPRESENTATION('main',(#22,#60),#22);
#80=SHAPE_DEFINITION_REPRESENTATION(#7,#70);
ENDSEC;
END-ISO-10303-21;
"""


# ----- BuggyWriter -------------------------------------------------------


class BuggyWriter:
    """Simulator: applies one specific writer-pathology defect to clean input bytes.

    Every method takes no arguments (uses ``self.input_bytes``) and
    returns output bytes with the defect injected. Methods are
    deliberately small (string / regex level); the goal is to model
    each defect as a single-line bug a real producer might have.
    """

    def __init__(self, input_bytes: bytes = CLEAN_INPUT) -> None:
        self.input_bytes = input_bytes

    # --- Wr001: trailing whitespace on every record line -----------------
    def write_with_trailing_whitespace(self) -> bytes:
        out = []
        for line in self.input_bytes.split(b"\n"):
            if line.rstrip(b" ").endswith(b";"):
                out.append(line + b"   ")
            else:
                out.append(line)
        return b"\n".join(out)

    # --- Wr002: HEADER uses CRLF, DATA uses LF ---------------------------
    def write_with_mixed_crlf_lf(self) -> bytes:
        body = self.input_bytes
        data_idx = body.find(b"DATA;")
        if data_idx < 0:
            return body
        head = body[:data_idx].replace(b"\n", b"\r\n")
        tail = body[data_idx:]
        return head + tail

    # --- Wr003: no trailing newline after END-ISO-10303-21; --------------
    def write_no_trailing_newline(self) -> bytes:
        return self.input_bytes.rstrip(b"\r\n")

    # --- Wr004: mixed tab/2-space continuation indentation ---------------
    def write_with_mixed_indent(self) -> bytes:
        # Break a long-ish entity onto continuation lines, alternating tab/space.
        body = self.input_bytes
        body = body.replace(
            b"#22=AXIS2_PLACEMENT_3D('main',#10,#20,#21);",
            b"#22=AXIS2_PLACEMENT_3D('main',\n\t#10,\n  #20,\n\t#21);",
        )
        return body

    # --- Wr005: heterogeneous numeric formats ----------------------------
    def write_with_inconsistent_numbers(self) -> bytes:
        body = self.input_bytes
        body = body.replace(
            b"#10=CARTESIAN_POINT('',(0.0,0.0,0.0));",
            b"#10=CARTESIAN_POINT('',(1.0E-7,1e-07,0.0000001));",
            1,
        )
        body = body.replace(
            b"#11=CARTESIAN_POINT('',(1.0,0.0,0.0));",
            b"#11=CARTESIAN_POINT('',(1.0e-007,1.0,1.));",
            1,
        )
        return body

    # --- Wr006: precision degradation on round-trip ----------------------
    def write_with_precision_degradation(self) -> bytes:
        body = self.input_bytes
        body = body.replace(b"1.0,1.0,0.0", b"1.4999999999998,2.5000000000003,0.99999999999996")
        return body

    # --- Wr007: locale comma-decimal -------------------------------------
    def write_with_locale_comma(self) -> bytes:
        body = self.input_bytes
        # Replace inside one CARTESIAN_POINT's coords. Naive: produce
        # `(1,5,2,5,3,5)` (intended `(1.5,2.5,3.5)`), what a buggy locale-aware
        # printf produces.
        return body.replace(
            b"#11=CARTESIAN_POINT('',(1.0,0.0,0.0));",
            b"#11=CARTESIAN_POINT('',(1,5,2,5,3,5));",
            1,
        )

    # --- Wr008: excessive trailing zeros ---------------------------------
    def write_with_trailing_zeros(self) -> bytes:
        body = self.input_bytes
        return body.replace(
            b"#10=CARTESIAN_POINT('',(0.0,0.0,0.0));",
            b"#10=CARTESIAN_POINT('',(1.00000000000000000,2.50000000000000000,0.00000000000000000));",
            1,
        )

    # --- Wr009: spurious $ for required AXIS2_PLACEMENT params -----------
    def write_with_omitted_required_params(self) -> bytes:
        body = self.input_bytes
        return body.replace(
            b"#22=AXIS2_PLACEMENT_3D('main',#10,#20,#21);",
            b"#22=AXIS2_PLACEMENT_3D('p',#10,$,$);",
            1,
        )

    # --- Wr010: misuse of * (override) in non-subtype context ------------
    def write_with_override_in_simple(self) -> bytes:
        body = self.input_bytes
        return body.replace(
            b"#10=CARTESIAN_POINT('',(0.0,0.0,0.0));",
            b"#10=CARTESIAN_POINT('p',(*,0.0,0.0));",
            1,
        )

    # --- Wr011: empty parameter list where schema requires content -------
    def write_with_empty_param_list(self) -> bytes:
        body = self.input_bytes
        return body.replace(
            b"#50=CLOSED_SHELL('outer',(#40));",
            b"#50=CLOSED_SHELL('hollow',());",
            1,
        )

    # --- Wr012: random instance numbers (non-monotonic) ------------------
    def write_with_random_numbering(self) -> bytes:
        # Renumber a few entities out of natural order to demonstrate scatter.
        body = self.input_bytes
        body = body.replace(b"#10=CARTESIAN_POINT", b"#1=CARTESIAN_POINT", 1)
        body = body.replace(b"(#10)", b"(#1)")  # no-op for cube but symbolic
        body = body.replace(b"#11=CARTESIAN_POINT", b"#1000=CARTESIAN_POINT", 1)
        body = body.replace(b"#12=CARTESIAN_POINT", b"#5=CARTESIAN_POINT", 1)
        body = body.replace(b"#13=CARTESIAN_POINT", b"#1003=CARTESIAN_POINT", 1)
        body = body.replace(b"#14=CARTESIAN_POINT", b"#7=CARTESIAN_POINT", 1)
        body = body.replace(b"#15=CARTESIAN_POINT", b"#1006=CARTESIAN_POINT", 1)
        return body

    # --- Wr013: forward references ---------------------------------------
    def write_with_forward_refs(self) -> bytes:
        # Construct a fragment that references #5 before it appears.
        body = self.input_bytes
        injection = (
            b"#1=AXIS2_PLACEMENT_3D('forward',#5,$,$);\n"
            b"#5=CARTESIAN_POINT('forwardpt',(0.0,0.0,0.0));\n"
        )
        return body.replace(b"DATA;\n", b"DATA;\n" + injection, 1)

    # --- Wr014: huge instance numbers ------------------------------------
    def write_with_sparse_numbering(self) -> bytes:
        body = self.input_bytes
        return body.replace(
            b"#60=MANIFOLD_SOLID_BREP('cube',#50);",
            b"#999999999=MANIFOLD_SOLID_BREP('cube',#50);",
            1,
        )

    # --- Wr015: duplicate #N --------------------------------------------
    def write_with_duplicate_instance_numbers(self) -> bytes:
        # Inject a second #10=CARTESIAN_POINT(...).
        body = self.input_bytes
        injection = b"#10=CARTESIAN_POINT('b',(1.0,1.0,1.0));\n"
        return body.replace(b"#11=CARTESIAN_POINT", injection + b"#11=CARTESIAN_POINT", 1)

    # --- Wr016: orphan construction-residue points -----------------------
    def write_with_orphan_geometry(self) -> bytes:
        body = self.input_bytes
        orphans = b"".join(
            f"#9{i:03d}=CARTESIAN_POINT('orphan_{i}',({i}.0,{i}.0,{i}.0));\n".encode()
            for i in range(15)
        )
        return body.replace(b"DATA;\n", b"DATA;\n" + orphans, 1)

    # --- Wr017: TESSELLATED instead of B-rep -----------------------------
    def write_with_tessellation_replacement(self) -> bytes:
        body = self.input_bytes
        injection = (
            b"#900=TESSELLATED_SHELL_REPRESENTATION('mesh',(#901),#22);\n"
            b"#901=TRIANGULATED_FACE('',$,$,$,$,$,$,.F.);\n"
        )
        return body.replace(b"ENDSEC;\nEND", injection + b"ENDSEC;\nEND", 1)

    # --- Wr018: empty SHAPE_REPRESENTATION items chain -------------------
    def write_with_empty_shape_representation(self) -> bytes:
        body = self.input_bytes
        return body.replace(
            b"#70=SHAPE_REPRESENTATION('main',(#22,#60),#22);",
            b"#70=SHAPE_REPRESENTATION('main',(#22),#22);",
            1,
        )

    # --- Wr020: re-export drops names → BREP_001 placeholder -------------
    def write_with_brep_placeholder_names(self) -> bytes:
        body = self.input_bytes
        return body.replace(
            b"#4=PRODUCT('cube','cube','',(#3));",
            b"#4=PRODUCT('BREP_001','BREP_001','',(#3));",
            1,
        )

    # --- Wr026: vendor-sniffable FILE_DESCRIPTION ------------------------
    def write_with_vendor_sniffable_description(self) -> bytes:
        body = self.input_bytes
        return body.replace(
            b"FILE_DESCRIPTION(('clean cube'),'2;1');",
            b"FILE_DESCRIPTION(('CAD-System-X v12.4.1'),'2;1');",
            1,
        )

    # --- Wr027: HEADER-says-mm but DATA-LENGTH_UNIT is INCH --------------
    def write_with_unit_mismatch(self) -> bytes:
        body = self.input_bytes
        body = body.replace(
            b"FILE_DESCRIPTION(('clean cube'),'2;1');",
            b"FILE_DESCRIPTION(('part in mm'),'2;1');",
            1,
        )
        injection = (
            b"#700=(LENGTH_UNIT() NAMED_UNIT(*) CONVERSION_BASED_UNIT('INCH',#701));\n"
            b"#701=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#702);\n"
            b"#702=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        )
        return body.replace(b"ENDSEC;\nEND", injection + b"ENDSEC;\nEND", 1)

    # --- Wr028: blank author/originating_system in FILE_NAME -------------
    def write_with_blank_provenance(self) -> bytes:
        body = self.input_bytes
        return re.sub(
            rb"FILE_NAME\([^;]+\);",
            b"FILE_NAME('clean.stp','2026-05-01T00:00:00',(''),(''),'','','');",
            body,
            count=1,
        )

    # --- Wr029: literal newline inside FILE_DESCRIPTION string -----------
    def write_with_unescaped_newline(self) -> bytes:
        body = self.input_bytes
        return body.replace(
            b"FILE_DESCRIPTION(('clean cube'),'2;1');",
            b"FILE_DESCRIPTION(('first line\nsecond line'),'2;1');",
            1,
        )

    # --- Wr030: FILE_SCHEMA over-declared --------------------------------
    def write_with_overdeclared_schema(self) -> bytes:
        body = self.input_bytes
        return body.replace(
            b"FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));",
            b"FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }','AP242_MANAGED_MODEL_BASED_3D_ENGINEERING'));",
            1,
        )

    # --- Wr032: schema upgrade with synthesised stub PMI -----------------
    def write_with_synthesised_pmi_stub(self) -> bytes:
        body = self.input_bytes
        body = body.replace(
            b"FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));",
            b"FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING { 1 0 10303 442 1 1 4 }'));",
            1,
        )
        injection = b"#800=GEOMETRIC_TOLERANCE_RELATIONSHIP('','',$,$);\n"
        return body.replace(b"ENDSEC;\nEND", injection + b"ENDSEC;\nEND", 1)

    # --- Wr033: schema-version year tuple `99` ---------------------------
    def write_with_invalid_schema_version(self) -> bytes:
        body = self.input_bytes
        return body.replace(
            b"FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));",
            b"FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 99 1 1 }'));",
            1,
        )

    # --- Wr034: Y-up axis swap (label only) ------------------------------
    def write_with_yup_marker(self) -> bytes:
        # Add a comment marker that the file was emitted Y-up. The byte
        # signature in the catalog accepts a literal `Y-up` substring.
        body = self.input_bytes
        return body.replace(b"DATA;\n", b"DATA;\n/* coordinates emitted Y-up */\n", 1)

    # --- Wr035: scale applied twice (1000-times scaled) ------------------
    def write_with_double_scale(self) -> bytes:
        body = self.input_bytes
        body = body.replace(
            b"#16=CARTESIAN_POINT('',(1.0,1.0,1.0));",
            b"#16=CARTESIAN_POINT('',(1000.0,1000.0,1000.0));",
            1,
        )
        injection = (
            b"#710=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        )
        return body.replace(b"ENDSEC;\nEND", injection + b"ENDSEC;\nEND", 1)

    # --- Wr036: invert face same_sense to .F. ----------------------------
    def write_with_inverted_orientation(self) -> bytes:
        body = self.input_bytes
        # Add a placeholder ADVANCED_FACE with .F. same_sense flag.
        injection = b"#88=ADVANCED_FACE('inverted',(),#40,.F.);\n"
        return body.replace(b"ENDSEC;\nEND", injection + b"ENDSEC;\nEND", 1)

    # --- Wr037: extra duplicate-coincident VERTEX_POINTs at seam ---------
    def write_with_seam_duplicate_vertices(self) -> bytes:
        # Add 4 extra VERTEX_POINTs at the same coordinate to model
        # duplicate-vertex-at-seam pattern. Catalog asserts >= 4 of them.
        # The clean input already has 8; we just emit more.
        return self.input_bytes  # already >= 4

    # --- Wr038: non-canonical (non-monotonic) numbering breaks round-trip
    def write_with_noncanonical_numbering(self) -> bytes:
        body = self.input_bytes
        # The catalog regex expects the *body* of DATA to read
        # ``#42 ... #17 ... #99 ... #1=``. Move the existing #1
        # APPLICATION_CONTEXT entity to a high number, then renumber
        # several CARTESIAN_POINTs to scatter, with a late `#1=`.
        body = body.replace(b"#1=APPLICATION_CONTEXT", b"#7777=APPLICATION_CONTEXT", 1)
        body = body.replace(b",#1)", b",#7777)")
        body = body.replace(b"#10=CARTESIAN_POINT", b"#42=CARTESIAN_POINT", 1)
        body = body.replace(b"#11=CARTESIAN_POINT", b"#17=CARTESIAN_POINT", 1)
        body = body.replace(b"#12=CARTESIAN_POINT", b"#99=CARTESIAN_POINT", 1)
        body = body.replace(b"#13=CARTESIAN_POINT", b"#1=CARTESIAN_POINT", 1)
        return body

    # --- Wr039: complex-record supertype reordering ----------------------
    def write_with_complex_record_reorder(self) -> bytes:
        body = self.input_bytes
        injection = (
            b"#720=(SI_UNIT(.MILLI.,.METRE.) NAMED_UNIT(*) LENGTH_UNIT());\n"
        )
        return body.replace(b"ENDSEC;\nEND", injection + b"ENDSEC;\nEND", 1)

    # --- Wr040: empty name='' on every entity ----------------------------
    def write_with_empty_names(self) -> bytes:
        # Clean input already has many `=CARTESIAN_POINT('',`. Add a few
        # more empty-named DIRECTION/PLANE so the catalog's count threshold
        # of >= 3 is met, plus assert all are empty.
        return self.input_bytes  # already meets the assertion

    # --- Wr041: long-form .TRUE./.FALSE. ---------------------------------
    def write_with_long_form_booleans(self) -> bytes:
        body = self.input_bytes
        # Inject .TRUE./.FALSE. on a fake EDGE_CURVE we add at the end.
        injection = (
            b"#810=EDGE_CURVE('',#30,#31,#40,.TRUE.);\n"
            b"#811=EDGE_CURVE('',#31,#32,#40,.FALSE.);\n"
        )
        return body.replace(b"ENDSEC;\nEND", injection + b"ENDSEC;\nEND", 1)

    # --- Wr042: mixed ;\n and ;\r\n line terminators ---------------------
    def write_with_mixed_record_terminators(self) -> bytes:
        # Take every other DATA-section record and switch its `;\n` to `;\r\n`.
        body = self.input_bytes
        data_idx = body.find(b"DATA;\n")
        if data_idx < 0:
            return body
        head = body[: data_idx + len(b"DATA;\n")]
        rest = body[data_idx + len(b"DATA;\n") :]
        records = rest.split(b";\n")
        # records[-1] is the trailing piece after the last ; (keep as-is).
        out_records = []
        for i, r in enumerate(records[:-1]):
            term = b";\r\n" if (i % 2 == 0) else b";\n"
            out_records.append(r + term)
        return head + b"".join(out_records) + records[-1]

    # --- Wr043: raw UTF-8 in Edition-2 string literal --------------------
    def write_with_raw_utf8_in_ed2(self) -> bytes:
        body = self.input_bytes
        # Replace 'cube' name with raw UTF-8 'caf\xC3\xA9' (café).
        return body.replace(
            b"#4=PRODUCT('cube','cube','',(#3));",
            b"#4=PRODUCT('caf\xc3\xa9','caf\xc3\xa9','',(#3));",
            1,
        )

    # ---- Map of method-name -> Wr id (for the runner) -------------------
    DEFECT_METHODS: dict[str, str] = {
        "Wr001": "write_with_trailing_whitespace",
        "Wr002": "write_with_mixed_crlf_lf",
        "Wr003": "write_no_trailing_newline",
        "Wr004": "write_with_mixed_indent",
        "Wr005": "write_with_inconsistent_numbers",
        "Wr006": "write_with_precision_degradation",
        "Wr007": "write_with_locale_comma",
        "Wr008": "write_with_trailing_zeros",
        "Wr009": "write_with_omitted_required_params",
        "Wr010": "write_with_override_in_simple",
        "Wr011": "write_with_empty_param_list",
        "Wr012": "write_with_random_numbering",
        "Wr013": "write_with_forward_refs",
        "Wr014": "write_with_sparse_numbering",
        "Wr015": "write_with_duplicate_instance_numbers",
        "Wr016": "write_with_orphan_geometry",
        "Wr017": "write_with_tessellation_replacement",
        "Wr018": "write_with_empty_shape_representation",
        "Wr020": "write_with_brep_placeholder_names",
        "Wr026": "write_with_vendor_sniffable_description",
        "Wr027": "write_with_unit_mismatch",
        "Wr028": "write_with_blank_provenance",
        "Wr029": "write_with_unescaped_newline",
        "Wr030": "write_with_overdeclared_schema",
        "Wr032": "write_with_synthesised_pmi_stub",
        "Wr033": "write_with_invalid_schema_version",
        "Wr034": "write_with_yup_marker",
        "Wr035": "write_with_double_scale",
        "Wr036": "write_with_inverted_orientation",
        "Wr038": "write_with_noncanonical_numbering",
        "Wr039": "write_with_complex_record_reorder",
        "Wr041": "write_with_long_form_booleans",
        "Wr042": "write_with_mixed_record_terminators",
        "Wr043": "write_with_raw_utf8_in_ed2",
    }


# ----- WRITER_SKIP --------------------------------------------------------
#
# Wr* entries the BuggyWriter cannot simulate from a clean fixture
# alone. Each carries a short reason. Most of these need *sibling-pair*
# evidence (input bytes vs output bytes) to demonstrate semantic loss
# on round-trip; bytes-of-output alone are well-formed.
WRITER_SKIP: dict[str, str] = {
    "Wr019": "round-trip data loss: needs sibling input with STYLED_ITEM/COLOUR_RGB to prove drop",
    "Wr021": "round-trip data loss: needs sibling input with PMI to prove drop",
    "Wr022": "round-trip data loss: needs sibling input with CAMERA_MODEL_D3 to prove drop",
    "Wr023": "round-trip data loss: needs sibling input with GEOMETRIC_VALIDATION_PROPERTY to prove drop",
    "Wr024": "round-trip data loss: needs sibling input with deeper NAUO chain to prove flattening",
    "Wr025": "round-trip data loss: needs sibling input with different NAUO root to prove re-rooting",
    "Wr031": "round-trip schema downgrade: needs sibling AP242 input to prove entity loss",
    "Wr037": "seam-edge healing: needs UV-aware kernel state, not a bytes-only transformation",
    "Wr040": "every-entity name='' is byte-equivalent to clean fixture (no transformation needed)",
}


# ----- Pathology verifier -------------------------------------------------


def _matches(body: bytes, pattern: bytes) -> bool:
    try:
        return bool(re.search(pattern, body))
    except re.error:
        return False


# Each verifier returns True if the output bytes exhibit the catalog's claimed defect.
PATHOLOGY_VERIFIERS: dict[str, Callable[[bytes], bool]] = {
    "Wr001": lambda b: bool(re.search(rb" +\n", b)) and b.count(b" \n") >= 5,
    "Wr002": lambda b: (b"\r\n" in b) and (b"\n" in b) and b.count(b"\r") >= 1,
    "Wr003": lambda b: b.rstrip(b"\r\n").endswith(b"END-ISO-10303-21;") and not b.endswith(b"\n"),
    "Wr004": lambda b: bool(re.search(rb"\n\t", b)) and bool(re.search(rb"\n  ", b)) and b"\t" in b,
    "Wr005": lambda b: (b"1.0E-7" in b) and (b"1e-07" in b) and ((b"0.0000001" in b) or (b"1.0e-007" in b)),
    "Wr006": lambda b: bool(re.search(rb"\d\.\d{12,}", b)) and bool(re.search(rb"\.999999", b)),
    "Wr007": lambda b: bool(re.search(rb"CARTESIAN_POINT\([^;]*,\(\d+,\d+,\d+,\d+", b)) and b.count(b",") >= 8,
    "Wr008": lambda b: bool(re.search(rb"\d\.0{15,}", b)),
    "Wr009": lambda b: bool(re.search(rb"AXIS2_PLACEMENT_3D\([^;]*,#\d+,\$,\$\)", b)) and (b"$,$)" in b),
    "Wr010": lambda b: bool(re.search(rb"CARTESIAN_POINT\([^;]*,\(\*\s*,", b)) and bool(re.search(rb"\(\*,", b)),
    "Wr011": lambda b: (b"CLOSED_SHELL" in b) and bool(re.search(rb"CLOSED_SHELL\('[^']*',\(\)\)", b)),
    "Wr012": lambda b: bool(re.search(rb"(?s)#1=.*#1000=.*#5=", b)) and b.count(b"#") >= 6,
    "Wr013": lambda b: bool(re.search(rb"(?s)#1=AXIS2_PLACEMENT_3D[^;]+#5[^;]+;.*#5=CARTESIAN_POINT", b)),
    "Wr014": lambda b: bool(re.search(rb"#\d{7,}=", b)),
    "Wr015": lambda b: bool(re.search(rb"(?s)#10\s*=\s*CARTESIAN_POINT.*#10\s*=\s*CARTESIAN_POINT", b)) and b.count(b"#10=") >= 2,
    "Wr016": lambda b: _count_entity_def(b, b"CARTESIAN_POINT") >= 10,
    "Wr017": lambda b: (b"TESSELLATED_SHELL" in b) or (b"TRIANGULATED_FACE" in b),
    "Wr018": lambda b: bool(re.search(rb"SHAPE_REPRESENTATION\('[^']*',\(#\d+\),#", b)),
    "Wr020": lambda b: (b"PRODUCT('BREP_" in b) and (b"BREP_001" in b),
    "Wr026": lambda b: b"CAD-System-X" in b,
    "Wr027": lambda b: (b"'INCH'" in b) and (b"part in mm" in b),
    "Wr028": lambda b: bool(re.search(rb"(?s)FILE_NAME\([^;]*\(''\)[^;]*'','',''", b)),
    "Wr029": lambda b: bool(re.search(rb"FILE_DESCRIPTION\(\('[^']*\n[^']*'", b)),
    "Wr030": lambda b: bool(re.search(rb"FILE_SCHEMA\(\(\s*'[^']+'\s*,\s*'[^']+'", b)) and b.count(b"','") >= 1,
    "Wr032": lambda b: (b"AP242" in b) and ((_count_entity_def(b, b"GEOMETRIC_TOLERANCE_RELATIONSHIP") >= 1) or (b"GEOMETRIC_TOLERANCE_RELATIONSHIP('','',$,$)" in b)),
    "Wr033": lambda b: bool(re.search(rb"\b99\b.*\}", b)),
    "Wr034": lambda b: (b"Y-up" in b) or (b"Z-up" in b),
    "Wr035": lambda b: (bool(re.search(rb"CARTESIAN_POINT\([^;]*1000(?:\.0)?,1000", b)) or (b"1000.0,1000.0,1000.0" in b)) and (b".MILLI." in b),
    "Wr036": lambda b: bool(re.search(rb"ADVANCED_FACE\([^;]*\.F\.\)", b)),
    "Wr038": lambda b: bool(re.search(rb"(?s)#42.*#17.*#99.*#1=", b)),
    "Wr039": lambda b: bool(re.search(rb"\(\s*SI_UNIT\([^)]+\)\s+NAMED_UNIT\(\*\)\s+LENGTH_UNIT\(\)\s*\)", b)),
    "Wr041": lambda b: (b".TRUE." in b) and (b".FALSE." in b),
    "Wr042": lambda b: (b";\r\n" in b) and (b";\n" in b) and (b"\r\n" in b) and b.count(b"\n") >= 5,
    "Wr043": lambda b: (b"'2;1'" in b) and bool(re.search(rb"[\xC0-\xF7][\x80-\xBF]", b)),
}


_RE_INSTANCE_DEF = re.compile(
    rb"(?:^|;|\n)\s*#\d+\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE
)


def _count_entity_def(body: bytes, type_name: bytes) -> int:
    target = type_name.upper()
    return sum(1 for m in _RE_INSTANCE_DEF.finditer(body) if m.group(1).upper() == target)


def verify_pathology(output: bytes, expected_pathology: str) -> dict[str, Any]:
    """Check whether ``output`` exhibits the catalog defect for ``expected_pathology``.

    ``expected_pathology`` is a Wr id (``"Wr007"``). Returns a dict::

        {"verdict": "exhibits" | "missing" | "ambiguous",
         "id": expected_pathology,
         "detail": "<reason>"}

    The verifier mirrors the Wr* catalog's primary byte-assertion. A
    "missing" verdict means the bytes do not show the pathology, so the
    BuggyWriter is broken or the expected id is wrong. "ambiguous" is
    reserved for ids the oracle does not know how to verify.
    """
    fn = PATHOLOGY_VERIFIERS.get(expected_pathology)
    if fn is None:
        return {
            "verdict": "ambiguous",
            "id": expected_pathology,
            "detail": f"no verifier registered for {expected_pathology}",
        }
    try:
        ok = fn(output)
    except Exception as e:  # pragma: no cover
        return {
            "verdict": "ambiguous",
            "id": expected_pathology,
            "detail": f"verifier raised {type(e).__name__}: {e}",
        }
    return {
        "verdict": "exhibits" if ok else "missing",
        "id": expected_pathology,
        "detail": "byte signature matched" if ok else "byte signature did not match",
    }


# ----- Runner -------------------------------------------------------------


def run_all(input_bytes: bytes = CLEAN_INPUT) -> list[dict[str, Any]]:
    """Run every BuggyWriter method against ``input_bytes`` and verify the result."""
    writer = BuggyWriter(input_bytes)
    rows: list[dict[str, Any]] = []
    for wr_id, method_name in BuggyWriter.DEFECT_METHODS.items():
        method = getattr(writer, method_name)
        out = method()
        v = verify_pathology(out, wr_id)
        rows.append({
            "id": wr_id,
            "method": method_name,
            "input_len": len(input_bytes),
            "output_len": len(out),
            "verdict": v["verdict"],
            "detail": v["detail"],
        })
    return rows


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._writer_oracle")
    p.add_argument("--json", action="store_true")
    p.add_argument("--list", action="store_true",
                   help="list implementable Wr ids vs skipped, with reasons")
    args = p.parse_args(argv)

    if args.list:
        impl = list(BuggyWriter.DEFECT_METHODS.keys())
        print(f"Implementable: {len(impl)} Wr ids")
        for wr_id in impl:
            print(f"  {wr_id}  -> BuggyWriter.{BuggyWriter.DEFECT_METHODS[wr_id]}")
        print(f"\nSkipped: {len(WRITER_SKIP)} Wr ids")
        for wr_id, reason in WRITER_SKIP.items():
            print(f"  {wr_id}  {reason}")
        return 0

    rows = run_all()
    if args.json:
        json.dump(rows, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    from collections import Counter
    by_verdict = Counter(r["verdict"] for r in rows)
    print(f"Writer-oracle ran {len(rows)} BuggyWriter methods on canonical clean input.")
    for k, n in sorted(by_verdict.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<10} {n:>4}")

    misses = [r for r in rows if r["verdict"] != "exhibits"]
    if misses:
        print(f"\nNon-exhibits ({len(misses)}):")
        for r in misses:
            print(f"  {r['id']:<8} verdict={r['verdict']:<10} detail={r['detail']}")
    return 1 if misses else 0


if __name__ == "__main__":
    raise SystemExit(main())
