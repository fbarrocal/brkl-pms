#!/usr/bin/env python3
"""Mechanical checks for an assembled template.

    python tools/check.py fresh  --core core --out kb              # is the committed kb/ what the source builds?
    python tools/check.py fresh  --core vendor/kb/core --ext ext --out pms
    python tools/check.py forbid --dir kb --pattern '(?i)todoist'   # words that must not leak into a build

Exit code 0 = clean, 1 = findings. Standard library only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assemble import BuildError, assemble  # noqa: E402


def fresh(core: Path, ext: Path | None, out: Path) -> list[str]:
    """Compare the committed output folder with what the sources assemble to."""
    try:
        built = assemble(core, ext)
    except BuildError as e:
        return [f"build failed: {e}"]
    on_disk = {p.relative_to(out).as_posix(): p.read_bytes() for p in out.rglob("*") if p.is_file()} if out.exists() else {}
    problems = []
    for rel in sorted(set(built) | set(on_disk)):
        if rel not in on_disk:
            problems.append(f"missing from {out}: {rel}")
        elif rel not in built:
            problems.append(f"in {out} but not produced by the build (hand-added?): {rel}")
        elif built[rel] != on_disk[rel]:
            problems.append(f"stale or hand-edited: {out}/{rel}")
    return problems


def forbid(folder: Path, patterns: list[str]) -> list[str]:
    problems = []
    regexes = [re.compile(p) for p in patterns]
    for p in sorted(folder.rglob("*")):
        if not p.is_file():
            continue
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for n, line in enumerate(lines, 1):
            for rx in regexes:
                m = rx.search(line)
                if m:
                    problems.append(f"{p.relative_to(folder).as_posix()}:{n}: '{m.group(0)}' — {line.strip()[:100]}")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fresh")
    f.add_argument("--core", required=True, type=Path)
    f.add_argument("--ext", type=Path)
    f.add_argument("--out", required=True, type=Path)
    b = sub.add_parser("forbid")
    b.add_argument("--dir", required=True, type=Path)
    b.add_argument("--pattern", action="append", required=True)
    a = ap.parse_args(argv)
    problems = fresh(a.core, a.ext, a.out) if a.cmd == "fresh" else forbid(a.dir, a.pattern)
    for p in problems:
        print(p)
    print(f"{a.cmd}: {'clean' if not problems else f'{len(problems)} finding(s)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
