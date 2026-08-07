"""Multi-tier validator for a single STEP fixture.

Runs the file through several independent oracles and emits structured output:
- byte-level signatures (BOM, line endings, NUL bytes, file size)
- ifcopenshell strict Part-21 parse (rejects malformed)
- OCCT load, reader-default mode (`STEPControl_Reader::TransferRoots`)
- OCCT load, alternate reader mode

  NOTE on what these two actually are, because the names oversell them.
  They are not a healing on/off toggle. The only thing separating them is
  `read.surfacecurve.mode` (0 = prefer the file's pcurves, 3 = ignore them
  and rebuild from the 3D curve) plus a few precision tunables. Real
  healing (ShapeFix/ShapeProcess) is not toggled here at all.

  Measured 2026-08-01 across all 2530 STEP fixtures with the settings
  genuinely applied: the two modes produce an IDENTICAL summary token for
  EVERY fixture. So `occt=X/Y` always has Y == X today, and the second
  token carries no information. It is retained because it costs nothing
  and would become informative if the alternate branch were ever pointed
  at a real healing sequence -- which is the open design question in
  BACKLOG (G). Do not read `occt=shape(1)/shape(1)` as evidence that a
  fixture survives with healing disabled; nothing in this corpus tests
  that yet.
- gmsh load with `Geometry.OCCAutoFix=0` (alternate OCC build, healing disabled)
- entity-graph summary (entity-type counts)

Usage:
    uv run python -m step_corpus.validate <file.stp> [--json]
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import sys
import tempfile
import traceback
from pathlib import Path


class _CaptureFDs:
    """Redirect OS-level fd 1 (stdout) and/or fd 2 (stderr) to a tempfile.

    Needed because OCCT writes diagnostics directly to C++ stdout/stderr (some
    via colored stdout, some via stderr); Python's `contextlib.redirect_*` only
    catches `sys.stdout`/`sys.stderr` writes. Captures both by default.
    Python's own stdout buffer (where we write our JSON) is restored on exit.
    """

    def __init__(self, capture_stdout: bool = True, capture_stderr: bool = True):
        self.cap1 = capture_stdout
        self.cap2 = capture_stderr

    def __enter__(self):
        # Flush both Python-level and C-stdio buffers before redirecting OS fds.
        try:
            sys.stdout.flush()
            sys.stderr.flush()
            self._libc.fflush(None)  # flush all C stdio streams
        except Exception:
            pass
        self.old1 = os.dup(1) if self.cap1 else None
        self.old2 = os.dup(2) if self.cap2 else None
        self.tmp = tempfile.NamedTemporaryFile(mode="w+b", delete=False)
        if self.cap1:
            os.dup2(self.tmp.fileno(), 1)
        if self.cap2:
            os.dup2(self.tmp.fileno(), 2)
        return self

    def __exit__(self, *a):
        # Flush before restoring so OCCT's buffered output lands in our tmpfile.
        try:
            self._libc.fflush(None)
        except Exception:
            pass
        if self.cap1 and self.old1 is not None:
            os.dup2(self.old1, 1)
            os.close(self.old1)
        if self.cap2 and self.old2 is not None:
            os.dup2(self.old2, 2)
            os.close(self.old2)
        self.tmp.seek(0)
        self.captured = self.tmp.read()
        self.tmp.close()
        try:
            os.unlink(self.tmp.name)
        except FileNotFoundError:
            pass

    # Lazy libc handle, set up once.
    @classmethod
    def _get_libc(cls):
        import ctypes
        return ctypes.CDLL(None, use_errno=True)


_CaptureFDs._libc = _CaptureFDs._get_libc()


# Backward-compatible alias for the old name (in case any code references it).
_CaptureFD2 = _CaptureFDs


def byte_signature(path: Path) -> dict:
    data = path.read_bytes()
    sig = {
        "size": len(data),
        "bom_utf8": data[:3] == b"\xef\xbb\xbf",
        "bom_utf16le": data[:2] == b"\xff\xfe",
        "bom_utf16be": data[:2] == b"\xfe\xff",
        "starts_with_iso_token": data.lstrip().startswith(b"ISO-10303-21"),
        "ends_with_close_token": data.rstrip().endswith(b"END-ISO-10303-21;"),
        "has_crlf": b"\r\n" in data,
        "has_lone_cr": (b"\r" in data) and (b"\r\n" not in data.replace(b"\r\n", b"")),
        "has_nul": b"\x00" in data,
        "has_form_feed": b"\f" in data,
        "high_bit_byte_count": sum(1 for b in data if b >= 0x80),
    }
    # Quick header field sniff (best-effort)
    try:
        head = data[:8192].decode("latin-1", errors="replace")
        m = re.search(r"FILE_SCHEMA\s*\(\s*\(\s*'([^']+)'", head)
        sig["file_schema"] = m.group(1) if m else None
    except Exception:
        sig["file_schema"] = None
    return sig


def entity_summary(path: Path) -> dict:
    """Cheap entity-type histogram from regex over the DATA section."""
    text = path.read_text(encoding="latin-1", errors="replace")
    # Entries look like #N=ENTITY(...);  but also `( ENTITY1() ENTITY2() )` for complex.
    types: dict[str, int] = {}
    for m in re.finditer(r"#\d+\s*=\s*([A-Z][A-Z0-9_]*)\s*\(", text):
        types[m.group(1)] = types.get(m.group(1), 0) + 1
    # Complex entity components
    for m in re.finditer(r"#\d+\s*=\s*\(\s*([A-Z][A-Z0-9_]*)\s*\(", text):
        types["__complex_first:" + m.group(1)] = types.get("__complex_first:" + m.group(1), 0) + 1
    return {
        "total_entity_definitions": sum(v for k, v in types.items() if not k.startswith("__")),
        "distinct_types": len([k for k in types if not k.startswith("__")]),
        "top_types": dict(sorted(
            [(k, v) for k, v in types.items() if not k.startswith("__")],
            key=lambda kv: -kv[1],
        )[:15]),
    }


def parse_ifcopenshell(path: Path) -> dict:
    """ifcopenshell ships a strict Part-21 parser shared with IFC.

    For non-IFC schema files (AUTOMOTIVE_DESIGN, AP242), the schema lookup fails
    BEFORE Part-21 grammar checking, so a generic "Unsupported schema" reject tells
    us nothing about the file's syntactic validity. We tag this case distinctly.

    For IFC schema files, a real parse-level reject is meaningful.
    """
    try:
        import ifcopenshell  # type: ignore
        try:
            f = ifcopenshell.open(str(path))
            return {"status": "accept", "schema": f.schema, "n_entities": len(list(f))}
        except Exception as e:
            msg = str(e)
            low = msg.lower()
            # Schema-class reject: "Unsupported schema", "No schema XYZ", etc.
            # This is BEFORE grammar checking; says nothing about Part-21 syntactic validity.
            if any(s in low for s in ["unsupported schema", "no schema", "schema not", "unknown schema"]):
                return {"status": "schema_class_reject", "error": msg[:300]}
            # "Unable to parse IFC SPF header" or similar grammar-level error.
            return {"status": "reject", "error": msg[:500]}
    except ImportError as e:
        return {"status": "tool_missing", "error": str(e)}


def parse_occt(path: Path, healing: bool = True) -> dict:
    """OCCT via OCP. healing=False sets precision tunables to off-band values.

    Captures C++ stderr (where OCCT writes diagnostics) so the caller can see
    "ERR StepFile : Undefined Parsing" messages. Distinguishes:
      - reject_at_read: ReadFile returned non-RetDone
      - accept: Read succeeded AND TransferRoots produced a non-null shape with content
      - accept_silent: Read succeeded BUT n_roots=0 or shape is null (silent corruption)
      - exception: Python exception during processing
    """
    try:
        from OCP.STEPControl import (  # type: ignore
            STEPControl_Controller,
            STEPControl_Reader,
        )
        from OCP.IFSelect import IFSelect_RetDone  # type: ignore
        from OCP.Interface import Interface_Static  # type: ignore

        # Registers the read.* parameters. Until this runs, every
        # Interface_Static.Set* below silently returns False and stores
        # nothing. See the fuller note in _oracle_workers.oracle_occt.
        STEPControl_Controller.Init_s()

        if not healing:
            Interface_Static.SetIVal_s("read.precision.mode", 0)
            Interface_Static.SetRVal_s("read.precision.val", 1.0e-7)
            Interface_Static.SetRVal_s("read.maxprecision.val", 1.0e-7)
            Interface_Static.SetIVal_s("read.maxprecision.mode", 1)
            Interface_Static.SetIVal_s("read.stdsameparameter.mode", 1)
            Interface_Static.SetIVal_s("read.surfacecurve.mode", 0)
        else:
            Interface_Static.SetIVal_s("read.precision.mode", 0)
            Interface_Static.SetIVal_s("read.surfacecurve.mode", 3)

        with _CaptureFD2() as cap:
            try:
                reader = STEPControl_Reader()
                status = reader.ReadFile(str(path))
                read_status = str(status)
                read_ok = (status == IFSelect_RetDone)
                if read_ok:
                    n_roots = reader.TransferRoots()
                    shape = reader.OneShape()
                    shape_null = shape.IsNull()
                    from OCP.TopExp import TopExp_Explorer  # type: ignore
                    from OCP.TopAbs import (  # type: ignore
                        TopAbs_VERTEX, TopAbs_EDGE, TopAbs_WIRE,
                        TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID, TopAbs_COMPOUND,
                    )
                    counts = {}
                    for label, t in [
                        ("vertex", TopAbs_VERTEX), ("edge", TopAbs_EDGE),
                        ("wire", TopAbs_WIRE), ("face", TopAbs_FACE),
                        ("shell", TopAbs_SHELL), ("solid", TopAbs_SOLID),
                        ("compound", TopAbs_COMPOUND),
                    ]:
                        if shape_null:
                            counts[label] = 0
                        else:
                            exp = TopExp_Explorer(shape, t)
                            c = 0
                            while exp.More():
                                c += 1
                                exp.Next()
                            counts[label] = c
                else:
                    n_roots = 0
                    shape_null = True
                    counts = {}
            except Exception as e:
                stderr_msg = cap.captured.decode("utf-8", errors="replace")[-2000:] if hasattr(cap, "captured") else ""
                return {
                    "status": "exception",
                    "error": str(e)[:400],
                    "stderr": stderr_msg,
                    "traceback": traceback.format_exc()[-500:],
                }

        # Strip ANSI color codes for cleanliness
        stderr_raw = cap.captured.decode("utf-8", errors="replace")
        stderr_clean = re.sub(r"\x1b\[[0-9;]*m", "", stderr_raw)
        # Extract the most informative error/warning lines
        diag_lines = [l.strip() for l in stderr_clean.splitlines()
                      if l.strip() and ("ERR" in l or "WARN" in l or "Warning" in l or "Error" in l)]

        if not read_ok:
            return {
                "status": "reject_at_read",
                "ret_status": read_status,
                "occt_diagnostics": diag_lines[:20],
            }

        # Read succeeded; but did we get a usable shape?
        if shape_null or n_roots == 0:
            return {
                "status": "accept_silent",
                "n_roots": n_roots,
                "shape_null": shape_null,
                "shape_counts": counts,
                "occt_diagnostics": diag_lines[:20],
                "note": "parser accepted but transfer produced no shape; silent corruption signal",
            }
        return {
            "status": "accept",
            "n_roots": n_roots,
            "shape_null": shape_null,
            "shape_counts": counts,
            "occt_diagnostics": diag_lines[:20],
        }
    except Exception as e:
        return {"status": "exception_outer", "error": str(e)[:400],
                "traceback": traceback.format_exc()[-500:]}


def parse_gmsh(path: Path, autofix: bool = True) -> dict:
    """gmsh via the OCC pipeline. autofix=False disables Geometry.OCCAutoFix."""
    try:
        import gmsh  # type: ignore
        gmsh.initialize([], False)
        try:
            gmsh.option.setNumber("Geometry.OCCAutoFix", 1 if autofix else 0)
            gmsh.option.setNumber("General.Terminal", 0)
            try:
                gmsh.model.occ.importShapes(str(path))
                gmsh.model.occ.synchronize()
                ents = gmsh.model.getEntities()
                by_dim = {0: 0, 1: 0, 2: 0, 3: 0}
                for d, _ in ents:
                    by_dim[d] = by_dim.get(d, 0) + 1
                return {
                    "status": "accept",
                    "by_dim": by_dim,
                    "total_entities": len(ents),
                }
            except Exception as e:
                return {"status": "reject", "error": str(e)[:400]}
        finally:
            try:
                gmsh.clear()
            except Exception:
                pass
            gmsh.finalize()
    except ImportError as e:
        return {"status": "tool_missing", "error": str(e)}


def derive_summary(per_oracle: dict) -> dict:
    """Boil oracle outputs down to a one-liner verdict per oracle.

    For OCCT:
      - reject = ReadFile failed (clean rejection by parser)
      - empty  = ReadFile OK but TransferRoots gave nothing (silent corruption)
      - shape  = ReadFile OK and a non-null shape was produced
      - except = Python exception was raised
    For ifcopenshell:
      - reject = grammar-level reject
      - schema = schema-class reject (says nothing about syntax)
      - accept = parse OK
    For gmsh: reject / accept (with content count).
    """
    s = {}
    for oracle in ["occt_heal_on", "occt_heal_off"]:
        d = per_oracle.get(oracle, {})
        if d.get("status") == "reject_at_read":
            s[oracle] = "reject"
        elif d.get("status") == "accept_silent":
            s[oracle] = "empty"
        elif d.get("status") == "accept":
            s[oracle] = "shape"
        elif d.get("status") in ("exception", "exception_outer"):
            s[oracle] = "except"
        else:
            s[oracle] = d.get("status", "unknown")
    for oracle in ["gmsh_autofix_on", "gmsh_autofix_off"]:
        d = per_oracle.get(oracle, {})
        if d.get("status") == "accept":
            n = d.get("total_entities", 0)
            s[oracle] = f"shape({n})" if n else "empty"
        elif d.get("status") == "reject":
            s[oracle] = "reject"
        else:
            s[oracle] = d.get("status", "unknown")
    d = per_oracle.get("ifcopenshell_strict", {})
    if d.get("status") == "reject":
        s["ifcopenshell"] = "reject"
    elif d.get("status") == "schema_class_reject":
        s["ifcopenshell"] = "schema_n/a"
    elif d.get("status") == "accept":
        s["ifcopenshell"] = f"accept({d.get('n_entities')})"
    else:
        s["ifcopenshell"] = d.get("status", "unknown")
    return s


def validate(path: Path) -> dict:
    per = {
        "byte_signature": byte_signature(path),
        "entity_summary": entity_summary(path),
        "ifcopenshell_strict": parse_ifcopenshell(path),
        "occt_heal_on": parse_occt(path, healing=True),
        "occt_heal_off": parse_occt(path, healing=False),
        "gmsh_autofix_on": parse_gmsh(path, autofix=True),
        "gmsh_autofix_off": parse_gmsh(path, autofix=False),
    }
    return {
        "file": str(path),
        "summary": derive_summary(per),
        **per,
    }


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: validate.py <file.stp> [--json]", file=sys.stderr)
        return 2
    path = Path(argv[0])
    as_json = "--json" in argv[1:]
    result = validate(path)
    if as_json:
        json.dump(result, sys.stdout, indent=2, default=str)
    else:
        from rich.console import Console
        from rich.pretty import Pretty
        Console().print(Pretty(result, expand_all=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
