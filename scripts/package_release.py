#!/usr/bin/env python3
"""Package a PdfCraft release from two `pdfc.py build` outputs.

    package_release.py --gui GUI_BUILD --cli CLI_BUILD --label LABEL [--dist DIR]

LABEL names packaging/LABEL/README.txt and the release (test4: PdfCraft 0.9.0 test 4).
Writes into DIR (default: dist/):

    PdfCraft-0.9.0-LABEL.x86_64-aros-v11.zip   PdfCraft.info and the PdfCraft drawer:
        PdfCraft, PdfCraft.info (tool icon with the stack), pdfcraft-cli, README.txt,
        BUILD.json, SHA256SUMS (the drawer's files), licences and notices
    PdfCraft-0.9.0-LABEL-source.zip            this repository at HEAD (recipe and patches)
    SHA256SUMS                                 both archives, appended

The programs are stripped of unneeded symbols (--strip-unneeded --remove-section .comment) and
must then fit the package manager's 64 MiB limit on one file.

Refuses: a build that is not finished, not built with --lto fat, not from a clean committed work copy, not built with
the SDK -nix startup, built with the diagnostic allocator or a label, whose binaries differ
from their manifest or contain this computer's home directory; a dirty repository; a series
that differs from the one the builds used; and any file that already exists in DIR.
"""
import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import time
import tomllib
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pdfconfig  # noqa: E402

REPO = pdfconfig.REPO
WORK = REPO / "work" / "pdfcraft"
STACK = 4_000_000
# apkg (arospkg 0.5) refuses an archive with a member over 64 MiB unpacked, or a download over 64 MiB.
MEMBER_LIMIT = 64 << 20
NOTICES = ["LICENSE-MIT", "LICENSE-APACHE", "NOTICE", "ATTRIBUTION.md", "ATTRIBUTION.toml"]
LICENSE_PREFIXES = ("LICENSE", "LICENCE", "COPYING", "NOTICE", "OFL")


class Failure(Exception):
    pass


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git(*args, cwd=REPO):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True).stdout.decode().strip()


def check_build(out, binary, series):
    m = json.loads((out / "manifest.json").read_text())
    if m.get("status") not in ("built-not-run", "accepted") or m.get("returncode") != 0:
        raise Failure(f"{out}: not a finished build")
    if m["work_dirty"] or m["source"] != "committed HEAD":
        raise Failure(f"{out}: built from a dirty or uncommitted work copy")
    if m["path_mode"] != "SDK -nix startup":
        raise Failure(f"{out}: not built with --nix-paths (file names from the command line need it)")
    if m.get("label") or any("diag-alloc" in str(c) for c in m["command"]):
        raise Failure(f"{out}: a labelled or diagnostic build is not a release build")
    if 'profile.release.lto="fat"' not in m["command"]:
        raise Failure(f"{out}: not built with --lto fat")
    if m["series"] != series:
        raise Failure(f"{out}: built with another patch series")
    data = (out / binary).read_bytes()
    if sha256(data) != m["binaries"][binary]["sha256"] or m["binaries"][binary]["undefined_symbols"]:
        raise Failure(f"{out / binary}: bytes differ from the manifest or symbols are undefined")
    if os.path.expanduser("~").encode() in data:
        raise Failure(f"{out / binary}: contains this computer's home directory")
    return m, data


def strip(data, tool, name):
    """The program with unneeded symbols and .comment removed: the form verified to load on AROS
    (a full strip loses the relocations AROS applies at load time)."""
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp) / "in", Path(tmp) / "out"
        src.write_bytes(data)
        subprocess.run([tool, "--strip-unneeded", "--remove-section", ".comment", "-o", str(dst), str(src)], check=True)
        out = dst.read_bytes()
    if len(out) > MEMBER_LIMIT:
        raise Failure(f"{name} is {len(out)} bytes after stripping, over the 64 MiB package limit")
    return out


def licences(packages):
    """{archive path: bytes} of every linked package's licence and notice files."""
    out = {}
    for manifest_path in sorted(set(packages.values())):
        directory = Path(manifest_path).parent
        meta = tomllib.loads((directory / "Cargo.toml").read_text()).get("package", {})
        version = meta.get("version", "workspace")
        version = "0.9.0" if isinstance(version, dict) else version
        crate = meta.get("name", directory.name)
        # Classic FFS names stop at 30 characters; long crate names are shortened, version kept.
        ident = f"{crate[:30 - len(str(version)) - 1]}-{version}"
        for p in sorted(directory.rglob("*")):
            rel = p.relative_to(directory)
            if not p.is_file() or {"target", ".git", "node_modules"} & set(rel.parts):
                continue
            if p.name.upper().startswith(LICENSE_PREFIXES):
                try:
                    p.read_text()
                except (UnicodeError, OSError):
                    continue
                out[f"Licenses/{ident}/{rel.as_posix()}"] = p.read_bytes()
    for p in sorted((WORK / "assets").rglob("*")):
        if p.is_file() and p.name.startswith(("LICENSE", "OFL")):
            out[f"Licenses/pdfcraft-assets/{p.relative_to(WORK / 'assets').as_posix()}"] = p.read_bytes()
    return out


def zip_entry(z, name, data, mode, date):
    info = zipfile.ZipInfo(name, date_time=date)
    info.create_system = 3
    info.external_attr = (mode & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(info, data, compresslevel=9)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--gui", type=Path, required=True)
    p.add_argument("--cli", type=Path, required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--dist", type=Path, default=REPO / "dist")
    a = p.parse_args()
    try:
        cfg = pdfconfig.load(["aros_src", "aros_strip"])
        if git("status", "--porcelain"):
            raise Failure("commit this repository first: the source archive is made from HEAD")
        series_dir = REPO / "patches" / "pdfcraft"
        series = {n: sha256((series_dir / n).read_bytes()) for n in (series_dir / "series").read_text().split()}
        gui, gui_data = check_build(a.gui.resolve(), "PdfCraft", series)
        cli, cli_data = check_build(a.cli.resolve(), "pdfcraft-cli", series)
        if len(gui_data) == 0:
            raise Failure("empty GUI binary")
        if gui["work_head"] != cli["work_head"]:
            raise Failure("the GUI and CLI builds come from different work-copy commits")
        readme = REPO / "packaging" / a.label / "README.txt"
        version = tomllib.loads((WORK / "Cargo.toml").read_text())["workspace"]["package"]["version"]
        name = f"PdfCraft-{version}-{a.label}"
        archive, source = a.dist / f"{name}.x86_64-aros-v11.zip", a.dist / f"{name}-source.zip"
        a.dist.mkdir(parents=True, exist_ok=True)
        for f in (archive, source):
            if f.exists():
                raise Failure(f"{f} exists; a delivered file is never replaced")
        head = git("rev-parse", "HEAD")
        date = time.gmtime(int(git("log", "-1", "--format=%ct")))[:6]
        upstream = json.loads((REPO / "upstreams.json").read_text())["repositories"]["pdfcraft"]

        gui_stripped = strip(gui_data, cfg["aros_strip"], "PdfCraft")
        cli_stripped = strip(cli_data, cfg["aros_strip"], "pdfcraft-cli")
        drawer = {"PdfCraft": (gui_stripped, 0o100755), "pdfcraft-cli": (cli_stripped, 0o100755),
                  "README.txt": (readme.read_bytes(), 0o100644)}
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([sys.executable, str(REPO / "scripts" / "icons.py"),
                            str(WORK / "assets/app-icon/hicolor/64x64/apps/ai.storyteller.pdfcraft.png"), tmp, "PdfCraft", str(STACK)], check=True)
            drawer["PdfCraft.info"] = ((Path(tmp) / "PdfCraft" / "PdfCraft.info").read_bytes(), 0o100644)
            drawer_icon = (Path(tmp) / "PdfCraft.info").read_bytes()
        for n in NOTICES:
            drawer[n] = ((WORK / n).read_bytes(), 0o100644)
        packages = {**gui["linked_packages"], **cli["linked_packages"]}
        for rel, data in licences(packages).items():
            drawer[rel] = (data, 0o100644)
        pthread_c = Path(cfg["aros_src"]) / "compiler/pthread/pthread_create.c"
        notice = pthread_c.read_text().split("*/", 1)[0] + "*/\n"
        notice += f"The pthread link library is built from deadwood2/AROS {gui['pthread']['aros_src_commit']} with the patches in patches/aros-pthread.\n"
        drawer["Licenses/AROS-pthread-NOTICE.txt"] = (notice.encode(), 0o100644)
        record = lambda m: {k: m[k] for k in ("build_id", "date", "abi", "path_mode", "features", "work_head", "snapshot_sha256",
                                               "cargo_lock_sha256", "cargo_lock_build_sha256", "binaries", "libc_aros")} | {
            "toolchain": {k: m["toolchain"][k] for k in ("name", "rustc", "gcc", "panic")},
            "pthread": {k: m["pthread"][k] for k in ("aros_src_commit", "patches", "objects", "sdk_archive_sha256")}}
        build = {"package": name, "abi": "x86_64 ABIv11", "upstream": upstream["url"], "upstream_commit": upstream["commit"],
                 "port": "https://github.com/tomaszstaniak/aros-pdfcraft", "port_commit": head,
                 "series": series, "builds": {"PdfCraft": record(gui), "pdfcraft-cli": record(cli)},
                 "packaged": {"strip": "--strip-unneeded --remove-section .comment",
                              "PdfCraft": sha256(gui_stripped), "pdfcraft-cli": sha256(cli_stripped)},
                 "unsupported": ["OCR", "printing", "AROS mainline (ABIv1)"]}
        drawer["BUILD.json"] = ((json.dumps(build, indent=2) + "\n").encode(), 0o100644)
        sums = "".join(f"{sha256(d)}  {n}\n" for n, (d, _) in sorted(drawer.items()))
        drawer["SHA256SUMS"] = (sums.encode(), 0o100644)
        for n in drawer:
            if any(len(part) > 30 for part in n.split("/")):
                raise Failure(f"name longer than 30 characters: {n}")
            if b"/Users/" in drawer[n][0] and not n.startswith("Licenses/"):
                raise Failure(f"{n} contains a home directory path")

        files = {f"PdfCraft/{n}": v for n, v in drawer.items()} | {"PdfCraft.info": (drawer_icon, 0o100644)}
        partial = archive.with_name(archive.name + ".partial")
        with zipfile.ZipFile(partial, "x") as z:
            dirs = sorted({"/".join(n.split("/")[:i]) for n in files for i in range(1, n.count("/") + 1)})
            for d in dirs:
                zip_entry(z, d + "/", b"", 0o40755, date)
            for n in sorted(files):
                zip_entry(z, n, files[n][0], files[n][1], date)
        with zipfile.ZipFile(partial) as z:
            if z.testzip() is not None:
                raise Failure("the archive does not read back")
            for line in z.read("PdfCraft/SHA256SUMS").decode().splitlines():
                digest, member = line.split("  ", 1)
                if sha256(z.read(f"PdfCraft/{member}")) != digest:
                    raise Failure(f"{member}: checksum mismatch in the archive")
            for b in ("PdfCraft", "pdfcraft-cli"):
                if not (z.getinfo(f"PdfCraft/{b}").external_attr >> 16) & stat.S_IXUSR:
                    raise Failure(f"{b} is not executable in the archive")
        partial.rename(archive)
        subprocess.run(["git", "-C", str(REPO), "archive", "--format=zip", f"--prefix={name}-source/", "-o", str(source), "HEAD",
                        "--", ".", ":(exclude)AGENTS.md", ":(exclude)CLAUDE.md"], check=True)
        sums_file = a.dist / "SHA256SUMS"
        existing = sums_file.read_text().splitlines() if sums_file.exists() else []
        sums_file.write_text("\n".join(existing + [f"{sha256(f.read_bytes())}  {f.name}" for f in (archive, source)]) + "\n")
        print(json.dumps({"archive": str(archive), "sha256": sha256(archive.read_bytes()), "bytes": archive.stat().st_size,
                          "source": str(source), "source_sha256": sha256(source.read_bytes()), "port_commit": head,
                          "files": len(files)}, indent=2))
    except Failure as e:
        sys.exit(f"package_release: {e}")


if __name__ == "__main__":
    main()
