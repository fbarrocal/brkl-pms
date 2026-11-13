#!/usr/bin/env python3
"""Build the KB-only template from core/ into kb/, or check that kb/ is current.

    python tools/build.py               # rebuild kb/ from core/, then run the leak check
    python tools/build.py --check       # change nothing; fail if kb/ is stale or leaks
    python tools/build.py --list-slots  # print every slot in core/ (the contract with extensions)

Run from the repository root. Standard library only.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from assemble import BuildError, assemble, slot_names, write  # noqa: E402
from check import forbid, fresh  # noqa: E402

CORE, OUT = ROOT / "core", ROOT / "kb"

# Words that mean an extension's concept leaked into the bare KB through a slot default or
# through core text that should have been a slot. The KB build must contain none of them.
LEAKS = [
    r"(?i)\btasks?\b",
    r"(?i)todoist",
    r"\bPMS\b",
    r"(?i)skills/(capture|plan|sync)",
    r"(?i)action items?",
    r"(?i)\bconventions\b",
]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--list-slots", action="store_true")
    a = ap.parse_args(argv)

    if a.list_slots:
        total = 0
        for p in sorted(CORE.rglob("*.md")):
            names = slot_names(p.read_text(encoding="utf-8"), str(p))
            if names:
                total += len(names)
                print(f"{p.relative_to(CORE).as_posix()} ({len(names)})")
                for n in names:
                    print(f"  {n}")
        print(f"{total} slots")
        return 0

    problems = []
    if a.check:
        problems += fresh(CORE, None, OUT)
    else:
        try:
            out = assemble(CORE, None)
            write(out, OUT, clean=True)
            print(f"built {len(out)} files into kb/")
        except BuildError as e:
            print(f"build failed: {e}", file=sys.stderr)
            return 1
    problems += [f"leak: {p}" for p in forbid(OUT, LEAKS)]
    for p in problems:
        print(p)
    print("clean" if not problems else f"{len(problems)} finding(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
