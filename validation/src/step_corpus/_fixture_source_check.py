"""CI invariant: every ``fixture_sources/<section>/<ID>.py`` must
regenerate byte-identical with ``step-examples/<section>/<ID>.stp``.

This catches drift between the Python source (canonical going forward)
and the checked-in STEP file (canonical for consumers). Run as part
of CI; nonzero exit on any mismatch.

Usage:

    cd validation
    uv run python -m step_corpus._fixture_source_check          # check
    uv run python -m step_corpus._fixture_source_check --fix    # rewrite .stp
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from step_corpus._build_catalog_json import RESEARCH_ROOT


def _regenerate(src_path: Path) -> tuple[str, str | None]:
    """Run a fixture source and return (rendered_text, error_msg).

    On success, error_msg is None and rendered_text is the .stp content.
    On error, rendered_text is empty and error_msg explains why.
    """
    ns: dict[str, Any] = {
        "__file__": str(src_path),
        "__name__": "__fixture__",
    }
    try:
        exec(compile(src_path.read_text(), str(src_path), "exec"), ns)
    except Exception as e:
        return "", f"exec error: {type(e).__name__}: {e}"
    f = ns.get("f")
    if f is None or not hasattr(f, "render"):
        return "", "source must define top-level `f` as StepFile"
    try:
        return f.render(), None
    except Exception as e:
        return "", f"render error: {type(e).__name__}: {e}"


def _print_first_diff_lines(current: str, rendered: str, out_path: Path, n: int = 5) -> None:
    """Print up to n line-level mismatches for diagnosing CI-only drift."""
    cur_lines = current.splitlines()
    new_lines = rendered.splitlines()
    shown = 0
    for i, (a, b) in enumerate(zip(cur_lines, new_lines), 1):
        if a != b:
            print(f"  line {i}: on-disk  : {a[:160]}")
            print(f"          regen    : {b[:160]}")
            shown += 1
            if shown >= n:
                break
    if shown == 0 and len(cur_lines) != len(new_lines):
        print(f"  length differs: on-disk={len(cur_lines)} lines, regen={len(new_lines)} lines")
    print(f"  byte-length: on-disk={len(current)} regen={len(rendered)}")


def _expected_stp_path(src_path: Path) -> Path | None:
    """Map ``fixture_sources/<section>/<ID>.py`` to
    ``step-examples/<section>/<ID>.stp``.
    """
    parts = src_path.parts
    try:
        idx = parts.index("fixture_sources")
    except ValueError:
        return None
    section = parts[idx + 1]
    fixture_id = src_path.stem
    return RESEARCH_ROOT / "step-examples" / section / f"{fixture_id}.stp"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix", action="store_true",
                        help="rewrite .stp files instead of checking")
    parser.add_argument("--quiet", action="store_true",
                        help="only print summary line")
    args = parser.parse_args(argv)

    src_root = RESEARCH_ROOT / "fixture_sources"
    if not src_root.is_dir():
        print(f"no fixture_sources/ at {src_root}", file=sys.stderr)
        return 2

    sources = sorted(src_root.rglob("*.py"))
    if not sources:
        print(f"no .py files under {src_root}", file=sys.stderr)
        return 0

    mismatched: list[Path] = []
    errored: list[tuple[Path, str]] = []
    ok = 0

    for src in sources:
        if src.name.startswith("_") or src.name == "__init__.py":
            continue
        out_path = _expected_stp_path(src)
        if out_path is None:
            errored.append((src, "no fixture_sources/ ancestor"))
            continue
        rendered, err = _regenerate(src)
        if err is not None:
            errored.append((src, err))
            continue
        if args.fix:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            current = out_path.read_text() if out_path.is_file() else None
            if current != rendered:
                out_path.write_text(rendered)
                if not args.quiet:
                    print(f"REWRITE {out_path.relative_to(RESEARCH_ROOT)}")
            ok += 1
            continue
        if not out_path.is_file():
            mismatched.append(out_path)
            if not args.quiet:
                print(f"MISSING {out_path.relative_to(RESEARCH_ROOT)}")
            continue
        current = out_path.read_text()
        if current != rendered:
            mismatched.append(out_path)
            if not args.quiet:
                print(f"DRIFT   {out_path.relative_to(RESEARCH_ROOT)}")
                _print_first_diff_lines(current, rendered, out_path)
            continue
        ok += 1

    total = len(sources)
    print(f"\nfixture_sources check: {ok}/{total} ok, "
          f"{len(mismatched)} drift, {len(errored)} error")
    for src, err in errored[:10]:
        print(f"  ERR {src.relative_to(RESEARCH_ROOT)}: {err}")
    if not mismatched and not errored:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
