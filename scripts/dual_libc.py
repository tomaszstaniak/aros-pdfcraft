"""Combine the pinned AROS backend with unchanged host libc sources.

Cargo patch selection is global, including host build dependencies. Only AROS
may use the SDK bindings/C glue; host tools must retain their own ABI.
"""
import hashlib
import shutil
import tarfile
from pathlib import Path

VERSION = "0.2.189"
CHECKSUM = "3eaf3ede3fee6db1a4c2ee091bf8a8b4dccdc6d17f656fb07896ee72867612f2"


def add_host_support(aros, cargo_home):
    archives = list(cargo_home.glob(f"registry/cache/*/libc-{VERSION}.crate"))
    if len(archives) != 1 or hashlib.sha256(archives[0].read_bytes()).hexdigest() != CHECKSUM:
        raise ValueError("missing or changed checksum-pinned upstream libc archive")
    # The caller supplies a fresh staging directory, never a shared cache source.
    host = aros / "host-source"
    with tarfile.open(archives[0]) as archive:
        archive.extractall(host, filter="data")
    host = host / f"libc-{VERSION}"
    original = (aros / "src/lib.rs").read_text()
    # Root-level no_core/feature selection stays with the upstream crate root.
    lines = original.splitlines(keepends=True)
    lines = [line for line in lines if not line.startswith(("#![no_std]", "#![cfg_attr"))]
    (aros / "src/aros.rs").write_text("".join(lines))
    root = (host / "src/lib.rs").read_text()
    marker = '    if #[cfg(windows)] {'
    if root.count(marker) != 1:
        raise ValueError("review libc platform dispatch before changing its base")
    root = root.replace("mod new;", '#[cfg(not(target_os = "aros"))]\nmod new;').replace("pub use new::*;", '#[cfg(not(target_os = "aros"))]\npub use new::*;')
    root = root.replace(marker, '    if #[cfg(target_os = "aros")] {\n        mod aros;\n        pub use aros::*;\n    } else if #[cfg(windows)] {')
    # Preserve the upstream crate's modules, metadata and host build script.
    for path in (host / "src").iterdir():
        if path.name == "lib.rs":
            continue
        dest = aros / "src" / path.name
        if path.is_dir():
            shutil.copytree(path, dest)
        else:
            shutil.copy2(path, dest)
    (aros / "src/lib.rs").write_text(root)
    shutil.copy2(host / "Cargo.toml", aros / "Cargo.toml")
    shutil.copy2(aros / "build.rs", aros / "aros_build.rs")
    build = (host / "build.rs").read_text()
    marker = 'fn main() {'
    if build.count(marker) != 1:
        raise ValueError("review libc build dispatch before changing its base")
    build = build.replace('fn main() {', 'fn main() {\n    println!(\"cargo:rustc-check-cfg=cfg(target_os, values(\\\"aros\\\"))\");', 1)
    build = build.replace(marker, 'mod aros_build;\n\nfn main() {\n    if std::env::var("CARGO_CFG_TARGET_OS").as_deref() == Ok("aros") {\n        aros_build::compile();\n        return;\n    }')
    (aros / "build.rs").write_text(build)
    p = aros / "aros_build.rs"
    p.write_text(p.read_text().replace('fn main() {', 'pub fn compile() {', 1))
    for name in ("LICENSE-APACHE", "LICENSE-MIT", "LICENSE", "README.md"):
        if (host / name).exists():
            shutil.copy2(host / name, aros / ("host-" + name))
    shutil.rmtree(aros / "host-source")
