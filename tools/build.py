#!/usr/bin/env python3
"""Build the PMS template: the vendored KB core plus ext/, into pms/.

    python tools/build.py          # verify the vendored core, rebuild pms/, list core slots ext/ leaves unfilled
    python tools/build.py --check  # change nothing; fail if the vendored core was edited or pms/ is stale

Run from the repository root. Standard library only. The assembler itself comes from the
vendored core (vendor/kb/tools/), so the PMS is always built by the tool its core version ships.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "vendor" / "kb" / "tools"))
from vendor_kb import verify  # noqa: E402
from assemble import BuildError, assemble, write  # noqa: E402
from check import fresh  # noqa: E402

CORE, EXT, OUT = ROOT / "vendor" / "kb" / "core", ROOT / "ext", ROOT / "pms"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)

    problems = verify()
    if a.check:
        problems += fresh(CORE, EXT, OUT)
    elif not problems:
        unfilled = []
        try:
            out = assemble(CORE, EXT, unfilled)
            write(out, OUT, clean=True)
            print(f"built {len(out)} files into pms/")
        except BuildError as e:
            print(f"build failed: {e}", file=sys.stderr)
            return 1
        if unfilled:
            print(f"core slots left at their KB default ({len(unfilled)}) — read them in pms/ before committing:")
            for u in unfilled:
                print(f"  {u}")
    for p in problems:
        print(p)
    print("clean" if not problems else f"{len(problems)} finding(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
