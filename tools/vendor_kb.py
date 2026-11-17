#!/usr/bin/env python3
"""Pin the KB core that the PMS is built on.

    python tools/vendor_kb.py --from ../brkl-kb --tag v1.2.0     # copy core/, core.json, tools/ from that tag
    python tools/vendor_kb.py --verify                           # vendor/kb/ still matches its pin

The copy comes from the tag through `git archive`, not from the KB repo's working tree, so
uncommitted KB edits can't slip in. vendor/kb/VENDOR.json records the tag, the commit and a
sha256 per file; --verify fails on any file that was edited, added or removed since.
Never edit vendor/kb/ by hand: change brkl-kb, release it, and vendor the new tag.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor" / "kb"
MANIFEST = VENDOR / "VENDOR.json"
PATHS = ["core", "core.json", "tools"]
REPOSITORY = "https://github.com/fbarrocal/brkl-kb"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(src: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(src), *args], check=True, capture_output=True).stdout


def vendor(src: Path, tag: str):
    commit = git(src, "rev-parse", f"{tag}^{{commit}}").decode().strip()
    archive = git(src, "archive", "--format=tar", tag, *PATHS)
    files = {}
    with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
        for m in tf.getmembers():
            if m.isfile():
                files[m.name] = tf.extractfile(m).read()
    version = json.loads(files["core.json"])["version"]
    if tag.lstrip("v") != version:
        raise SystemExit(f"tag {tag} carries core.json version {version}; refusing a mismatched pin")
    if VENDOR.exists():
        shutil.rmtree(VENDOR)
    for name, data in files.items():
        target = VENDOR / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    manifest = {
        "repository": REPOSITORY,
        "tag": tag,
        "commit": commit,
        "version": version,
        "files": {name: sha(data) for name, data in sorted(files.items())},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"vendored brkl-kb {tag} ({commit[:7]}): {len(files)} files into vendor/kb/")


def verify() -> list[str]:
    if not MANIFEST.exists():
        return ["vendor/kb/VENDOR.json is missing — run tools/vendor_kb.py --from <brkl-kb> --tag <tag>"]
    pinned = json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]
    on_disk = {
        p.relative_to(VENDOR).as_posix(): p.read_bytes()
        for p in VENDOR.rglob("*")
        if p.is_file() and p != MANIFEST and "__pycache__" not in p.parts
    }
    problems = []
    for name in sorted(set(pinned) | set(on_disk)):
        if name not in on_disk:
            problems.append(f"vendor/kb/{name}: missing")
        elif name not in pinned:
            problems.append(f"vendor/kb/{name}: not in the pin (added by hand?)")
        elif sha(on_disk[name]) != pinned[name]:
            problems.append(f"vendor/kb/{name}: edited since it was vendored — change brkl-kb instead")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--from", dest="src", type=Path, help="a local clone of brkl-kb")
    ap.add_argument("--tag", help="the brkl-kb tag to pin, e.g. v1.2.0")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    if a.verify:
        problems = verify()
        for p in problems:
            print(p)
        print("vendor: clean" if not problems else f"vendor: {len(problems)} finding(s)")
        return 1 if problems else 0
    if not (a.src and a.tag):
        ap.error("--from and --tag are required (or use --verify)")
    vendor(a.src, a.tag)
    return 0


if __name__ == "__main__":
    sys.exit(main())
