#!/usr/bin/env python3
"""Assemble a template from the KB core, optionally with one extension.

    python tools/assemble.py --core core --out kb --clean
    python vendor/kb/tools/assemble.py --core vendor/kb/core --ext ext --out pms --clean

Standard library only. The contract it enforces is documented in docs/SLOTS.md.

Core files may contain SLOTS, in either form:

    block   a line that is exactly  <!-- slot:NAME -->  ... a line that is exactly  <!-- /slot:NAME -->
            The marker lines vanish; the lines between them are the default content.
            <!-- slot:NAME /--> alone on a line is an empty block slot.
    inline  <!-- slot:NAME -->default text<!-- /slot:NAME -->  anywhere inside a line (or across lines).
            The characters between the markers are the default content.

An extension fills slots from ext/fills/<same relative path as the core file>, using the same
two forms with `fill` instead of `slot`. Text outside fill blocks is ignored. A filled slot is
replaced by the fill; an unfilled one by its default. ext/files/ adds whole files that the core
does not have. {{VAR}} placeholders are replaced everywhere from core.json, then extension.json.

The build fails, rather than guessing, when: a fill names a slot the core file doesn't have, a fill
file has no core file, an extension file would overwrite a core file, a placeholder is unknown,
the extension needs a different core version, or any marker survives into the output.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

NAME = r"[a-z0-9][a-z0-9.-]*"
OPEN = re.compile(r"<!-- (slot|fill):(" + NAME + r") -->")
SELF = re.compile(r"<!-- (slot|fill):(" + NAME + r") /-->")
VAR = re.compile(r"\{\{([A-Za-z_]+)\}\}")
LEFTOVER = re.compile(r"<!-- /?(slot|fill):|\{\{[A-Za-z_]+\}\}")
# Instance folders whose content must never be wiped by --clean.
CONTENT_DIRS = ("knowledge", "raw", "tasks")


class BuildError(Exception):
    pass


def _alone(text: str, start: int, end: int) -> bool:
    """True if text[start:end] occupies a whole line by itself."""
    line_start = start == 0 or text[start - 1] == "\n"
    line_end = end == len(text) or text[end] == "\n"
    return line_start and line_end


def parse(text: str, kind: str, where: str):
    """Split text into a list of literal strings and (name, content, block) tuples."""
    parts, pos = [], 0
    while True:
        m_open, m_self = OPEN.search(text, pos), SELF.search(text, pos)
        cands = [m for m in (m_open, m_self) if m and m.group(1) == kind]
        others = [m for m in (m_open, m_self) if m and m.group(1) != kind]
        if others and (not cands or others[0].start() < min(c.start() for c in cands)):
            raise BuildError(f"{where}: found a `{others[0].group(1)}` marker where only `{kind}` markers belong")
        if not cands:
            parts.append(text[pos:])
            return parts
        m = min(cands, key=lambda c: c.start())
        name = m.group(2)
        if m.re is SELF:
            block = _alone(text, m.start(), m.end())
            cut_end = m.end() + 1 if block and m.end() < len(text) else m.end()
            parts.append(text[pos:m.start()])
            parts.append((name, "", block))
            pos = cut_end
            continue
        close = f"<!-- /{kind}:{name} -->"
        c = text.find(close, m.end())
        if c < 0:
            raise BuildError(f"{where}: `{kind}:{name}` is never closed")
        inner = text[m.end():c]
        if OPEN.search(inner) or SELF.search(inner):
            raise BuildError(f"{where}: `{kind}:{name}` contains another marker (no nesting)")
        open_alone = _alone(text, m.start(), m.end())
        close_alone = _alone(text, c, c + len(close))
        if open_alone != close_alone:
            raise BuildError(f"{where}: `{kind}:{name}` mixes block and inline form — put both markers alone on their lines, or both inline")
        if open_alone:
            content = inner[1:]  # drop the newline that ends the opening marker line
            cut_end = c + len(close) + (1 if c + len(close) < len(text) else 0)
            parts.append(text[pos:m.start()])
            parts.append((name, content, True))
            pos = cut_end
        else:
            parts.append(text[pos:m.start()])
            parts.append((name, inner, False))
            pos = c + len(close)


def read_fills(path: Path) -> dict:
    fills = {}
    for part in parse(path.read_text(encoding="utf-8"), "fill", str(path)):
        if isinstance(part, tuple):
            name, content, block = part
            if name in fills:
                raise BuildError(f"{path}: fill `{name}` appears twice")
            fills[name] = (content, block)
    return fills


def slot_names(text: str, where: str) -> list[str]:
    return [p[0] for p in parse(text, "slot", where) if isinstance(p, tuple)]


def render(text: str, fills: dict, where: str, used: set) -> str:
    out, seen = [], set()
    for part in parse(text, "slot", where):
        if isinstance(part, str):
            out.append(part)
            continue
        name, default, block = part
        if name in seen:
            raise BuildError(f"{where}: slot `{name}` appears twice")
        seen.add(name)
        if name in fills:
            content, fill_block = fills[name]
            if block and content and not content.endswith("\n"):
                raise BuildError(f"{where}: slot `{name}` is a block slot; its fill must be block form too")
            if not block and fill_block and content:
                raise BuildError(f"{where}: slot `{name}` is an inline slot; its fill must be inline too")
            out.append(content)
            used.add(name)
        else:
            out.append(default)
    return "".join(out)


def substitute(text: str, vars_: dict, where: str) -> str:
    def rep(m):
        key = m.group(1)
        if key not in vars_:
            raise BuildError(f"{where}: unknown placeholder {{{{{key}}}}}")
        return str(vars_[key])
    return VAR.sub(rep, text)


def version_tuple(v: str):
    return tuple(int(x) for x in v.split("."))


def check_requires(req: str, core_version: str):
    """Supports '^X.Y.Z': same major, and at least X.Y.Z."""
    if not req.startswith("^"):
        raise BuildError(f"extension.json: unsupported requires_core '{req}' (use ^X.Y.Z)")
    need, have = version_tuple(req[1:]), version_tuple(core_version)
    if have[0] != need[0] or have < need:
        raise BuildError(f"extension needs core {req}, but the core is {core_version}")


def is_text(path: Path) -> bool:
    try:
        path.read_bytes().decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def assemble(core: Path, ext: Path | None, unfilled: list | None = None) -> dict:
    """Return {relative path: bytes} for the assembled template.

    If `unfilled` is a list and an extension is given, it receives "file: slot" for every core
    slot the extension leaves at its default — the list to read after bumping the core.
    """
    meta = json.loads((core.parent / "core.json").read_text(encoding="utf-8"))
    vars_ = dict(meta.get("vars", {}))
    vars_["VERSION"] = meta["version"]
    vars_["CORE_VERSION"] = meta["version"]
    fills_root = files_root = None
    if ext is not None:
        emeta = json.loads((ext / "extension.json").read_text(encoding="utf-8"))
        check_requires(emeta["requires_core"], meta["version"])
        vars_.update(emeta.get("vars", {}))
        vars_["VERSION"] = emeta["version"]
        fills_root, files_root = ext / "fills", ext / "files"

    out = {}
    core_files = sorted(p for p in core.rglob("*") if p.is_file())
    core_rel = {p.relative_to(core).as_posix() for p in core_files}

    if fills_root and fills_root.exists():
        for f in fills_root.rglob("*"):
            if f.is_file() and f.relative_to(fills_root).as_posix() not in core_rel:
                raise BuildError(f"{f}: fills a core file that does not exist ({f.relative_to(fills_root).as_posix()})")

    for p in core_files:
        rel = p.relative_to(core).as_posix()
        if not is_text(p):
            out[rel] = p.read_bytes()
            continue
        fills, used = {}, set()
        fpath = fills_root / rel if fills_root else None
        if fpath and fpath.exists():
            fills = read_fills(fpath)
        source = p.read_text(encoding="utf-8")
        text = render(source, fills, f"core/{rel}", used)
        if ext is not None and unfilled is not None:
            unfilled.extend(f"{rel}: {n}" for n in slot_names(source, f"core/{rel}") if n not in used)
        unused = set(fills) - used
        if unused:
            raise BuildError(f"ext/fills/{rel}: fills slots the core file does not have: {', '.join(sorted(unused))} — renamed or removed in the core?")
        out[rel] = substitute(text, vars_, rel).encode("utf-8")

    if files_root and files_root.exists():
        for p in sorted(files_root.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(files_root).as_posix()
            if rel in out:
                raise BuildError(f"ext/files/{rel}: would overwrite a core file — fill a slot instead")
            out[rel] = substitute(p.read_text(encoding="utf-8"), vars_, rel).encode("utf-8") if is_text(p) else p.read_bytes()

    for rel, data in out.items():
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        m = LEFTOVER.search(text)
        if m:
            line = text.count("\n", 0, m.start()) + 1
            raise BuildError(f"{rel}:{line}: marker or placeholder left in the output: {m.group(0)}")
    return out


def write(out: dict, dest: Path, clean: bool):
    if dest.exists():
        if not clean:
            raise BuildError(f"{dest} exists; pass --clean to replace it")
        for d in CONTENT_DIRS:
            for f in (dest / d).rglob("*") if (dest / d).exists() else []:
                if f.is_file() and f.name != ".gitkeep":
                    raise BuildError(f"refusing to clean {dest}: {f} looks like real content, not a template")
        shutil.rmtree(dest)
    for rel, data in sorted(out.items()):
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--core", required=True, type=Path, help="core template source (its parent holds core.json)")
    ap.add_argument("--ext", type=Path, help="extension folder (holds extension.json, fills/, files/)")
    ap.add_argument("--out", required=True, type=Path, help="where to write the assembled template")
    ap.add_argument("--clean", action="store_true", help="replace --out if it exists")
    a = ap.parse_args(argv)
    try:
        out = assemble(a.core, a.ext)
        write(out, a.out, a.clean)
    except BuildError as e:
        print(f"build failed: {e}", file=sys.stderr)
        return 1
    print(f"assembled {len(out)} files into {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
