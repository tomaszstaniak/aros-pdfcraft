---
type: guide
updated: 2026-10-18
---

# Development preparation

Rust upstream requires edition 2024, Rust 1.95 and egui 0.36. Select an explicitly matched AROS Rust sysroot, compiler, archiver and SDK in local configuration before building. Keep ABI outputs separate and do not replace shared installations.

The CLI package is `pdfcraft-cli`; the original egui frontend runs through an AROS Intuition/CPU shell in package `pdfcraft-aros`. The private build entry point is `python3 scripts/pdfc.py build -p pdfcraft-cli --nix-paths --online` (jobs may be bounded with CARGO_BUILD_JOBS=2). Copy local.example.json to ignored local.json and select matching paths first. Builds alone do not establish runtime acceptance. Keep MCP as a separately tested capability; disabling it for an initial diagnostic does not establish parity.

Source preparation: clone the URL and full commit from `upstreams.json` into `upstream/pdfcraft`, then create a separate clone at `work/pdfcraft` at that revision. Apply each non-comment entry of `patches/pdfcraft/series` in order with `git am`. Never reset an existing work copy. Cargo.lock and the upstream vendor patches are part of the base; preserve the craft-libs Git pins and validate their availability before dependency resolution.

Before redistribution review upstream third-party notices and branding restrictions; the source license does not grant modified-fork use of ArtCraft marks.


## Verification commands

`python3 scripts/pdfc.py verify` reconstructs the source series and compares trees. `python3 scripts/pdfc.py crates` verifies archive checksums and patched dependency tree hashes. Builds produce fresh build/v11/out/<timestamp>-<id>/manifest.json and logs, with explicit source/runtime/SDK pins. A built-not-run status does not establish native behavior.

`tests/host-libc` is a small Cargo probe for host ABI and real jobserver acquire/release/available behavior. Run it with a separate CARGO_TARGET_DIR and a patch.crates-io.libc.path pointing to the generated dual-source libc. The host run must not need AROS_GCC/AROS_SDK. `rustc --edition 2021 --test tests/tempfile-adapter.rs` exercises the actual generated file adapter on a Unix host; it does not establish AROS filesystem behavior.

`python3 tests/stage_cli.py <successful-build-directory> <new-payload-directory>` creates fresh run markers and the contributor-original synthetic PDF. Use an exclusively reserved ABI-matched guest. Read its smoke.json for exact expected exit codes. Collect results only after guest writes finish and the machine stops. Verify actual PNG/PDF/MCP results as well as process return codes before acceptance.

AROS temporary files use exclusive std opens and no-clobber hard links. Filesystems that refuse hard links cause publication to fail rather than overwrite. Unnamed temporary files remain explicitly unsupported. AWS-LC is a local adaptation whose cryptographic/native acceptance must be recorded separately from compile/link success. See [build tooling provenance](build-tooling.md).


The selected CLI profile uses the existing SDK `-nix` startup: native volume paths still work, while Rust canonicalization and `.` need POSIX path mode. Native volume prefixes entering automation are converted before root joining; this is not permission to broaden the root. The optional `--nix-paths` flag currently requires one final target because it passes the startup option through cargo rustc. Without it, native-path compile probes do not establish automation/root support. No shared Rust default has been changed.


## Native GUI

Build with `CARGO_BUILD_JOBS=2 python3 scripts/pdfc.py build -p pdfcraft-aros --nix-paths --online`. The output binary is `PdfCraft`. It supports `--window 800x600`, file arguments (native volume or Unix paths), and diagnostic `--screenshot file.png --screenshot-frames 8`. `PDFCRAFT_NO_PREFS=1` disables preferences for isolated tests; default preferences are ENVARC:PdfCraft/ui.json, overridable with PDFCRAFT_PREFS. Logs may be directed to PDFCRAFT_LOG.

`tests/stage_gui.py <successful-build> <new-payload>` produces a fresh GUI smoke payload. Require matching run/build markers, actual zero exit, captured native PNG and inspected PDF content. Screenshot mode is diagnostic and does not exercise unsaved-close prompts. Normal close must be tested separately. ASL and clipboard callbacks belong to the GUI task; image/file-list clipboard operations remain unsupported.

OCR is unavailable on AROS: RTen retains a private static Rayon pool with no accepted shutdown path. The adapter refuses loading OCR before creating that pool. Printing, signing/TLS/update, interactive MCP pipe transport and full GUI feature parity remain separate gates. Current perf page counters inherited from the shell are placeholders, not PDF renderer measurements.

`python3 tests/cache-invalidation.py` checks the selected private pthread cache, copied into a temporary test root: valid hit, corrupted object rejection and changed SDK identity forcing reconstruction. Host checks do not replace native runtime testing.


## Detached pthread completion regression

The private pthread series also protects the detached epilogue from code unloading after its slot is cleared. `python3 tests/pthread-exit/build.py <fresh-label>` builds a deliberately widened, test-only epilogue; follow tests/pthread-exit/README.md for the native test. The hook is never linked into PdfCraft. Preserve the final scheduling protection and verify the selected SDK's ReleaseSemaphore implementation before transferring the patch. Shared Rust/SDK installations are not changed by this repository. Mainline v1 has a different completion protocol and needs separate assessment.

## Release packages

Release builds use the CPU renderer, the SDK `-nix` startup and no diagnostic allocator or label. Build them in a build root whose path names no user, so that the paths compiled into the programs (panic locations, the C library's assertions, the OCR model search path) reveal nothing about the build machine; the build remaps the build root to `/build` where the compiler allows it:

    export PDFCRAFT_BUILD_ROOT=/tmp/pdfcraft-release-build
    python3 scripts/pdfc.py build --online --nix-paths --lto fat -p pdfcraft-aros
    python3 scripts/pdfc.py build --nix-paths --lto fat -p pdfcraft-cli
    python3 scripts/package_release.py --gui <GUI build output> --cli <CLI build output> --label test4

Whole-program LTO (`--lto fat`) and stripping unneeded symbols when packaging keep the GUI under the 64 MiB that apkg accepts for one file; a full strip is not used, because AROS needs the relocations it removes. `package_release.py` refuses builds that do not meet these conditions, and writes the program archive (with Workbench icons), the source archive of this repository and `SHA256SUMS` into `dist/`.

`tests/workbench-cwd` checks that the GUI keeps ownership of its Workbench starting drawer when a worker thread changes directory (fixed in patch 0011); run it from a disk drawer, not RAM:.
