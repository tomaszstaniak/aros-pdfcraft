---
type: guide
updated: 2026-11-23
---

# Building PdfCraft for AROS

The pinned source is PdfCraft 0.22.0 (tag `v0.22.0`), with the patch series in
`patches/pdfcraft/`. It builds the viewer and editor (`PdfCraft`) and the command line
(`pdfcraft-cli`, including the MCP server over stdio).

Targets, named as `<system>-<arch>-<abi>-<platform>`:

| Target | System |
|---|---|
| `aros-x86_64-abiv11-pc` | ABIv11 distributions (AROS One), x86_64 PC |
| `aros-x86_64-abiv1-pc` | mainline AROS, x86_64 PC |
| `aros-aarch64-abiv1-raspi` | native AROS on Raspberry Pi, AArch64 |

A binary built for one target does not run on another. Each target has its own toolchain,
SDK, Cargo home (`deps/<target>/`) and build directory (`build/<target>/`). This document
describes how to build; it does not record build or test results for any target.

The build, packaging and update tools are shared by the Craft ports and live in egui-aros under
`tools/craft`. `scripts/craft.py` runs the snapshot of them that `scripts/tooling.json` pins (a
commit and the content hash of that directory), prepared in the ignored `build/tooling/`; it
takes the commit from the egui-aros checkout named in the local file, or from the URL in
`tooling.json` when there is none. The app's names are in `scripts/port.json` (environment
prefix `PDFCRAFT`; packages `pdfcraft-aros` for `PdfCraft` and `pdfcraft-cli`). The tools'
README describes the pin, how to change it, and `update-check`, which tries the patch series on a
newer upstream commit without changing this repository.

## What you need

- Python 3.11 or later, Git, rustup.
- Rust nightly `nightly-2026-09-01` (it reports `rustc 1.100.0-nightly (0dfb098f3 2026-08-31)`)
  with `rust-src`, and one private toolchain alias per target whose sysroot holds the AROS
  standard library source for that target, made with the rust-aros std patch tooling.
- Per target, an AROS C toolchain and the SDK it was made for. The C glue, the pthread objects
  and the Rust link must all use the same SDK: ABIv1 and ABIv11 pass `SysBase` differently, and
  a mismatch crashes inside the first system call instead of failing to build.
  - ABIv11: x86_64 AROS GCC 10.5 and the ABIv11 SDK, plus a deadwood2/AROS checkout that
    contains commit `5376f09bc1ed0c36a12fbb096406013f8a046e89` (its `compiler/pthread` is
    rebuilt with `patches/aros-pthread`: a thread detached after it finished no longer keeps the
    program from exiting, and a detached thread's exit code stays loaded until the thread has
    left it).
  - mainline ABIv1: x86_64 AROS GCC 10.5 and the mainline Developer SDK.
  - Raspberry Pi: the AROS-patched Clang 20.1 for `aarch64-unknown-aros` with compiler-rt, the
    Raspberry Pi Developer SDK (its `libpthread.a` is used unchanged: `"pthread": "sdk"` in the
    local file), and a pomaros-hosted checkout at
    `3bc9359d439f9fb5655cf48924413ffe670931cc` (the C bridge of the AArch64 standard
    library). The shared tools build that bridge with their own `aros-glue` patch.
- The rust-aros files the build uses (target template, profiles, `libc-aros`, the std
  patches) at the commit in the local file (`rust_aros_commit`): a checkout of
  [rust-aros](https://github.com/tomaszstaniak/rust-aros).
- The craft-fonts checkout pinned in `upstreams.json` (fetched by `craft.py fetch`): the build
  embeds the fallback faces of its main manifest without the Japanese, Korean and Chinese ones,
  as `scripts/port.json` (`craft_fonts`) names them.
- An egui-aros checkout containing the commit pinned in `upstreams.json` (branch `egui-0.37`),
  with its upstream sources prepared by its own `python3 scripts/ea.py fetch`.

## Configuration

Copy `local.example.json` (an ABIv11 example) to one ignored local file per target and fill in
the paths: `local.json` (ABIv11, the default), for example `local.v1.json` and
`local.raspi.json` for the others, each with its `"target"`. Select a file with
`PDFCRAFT_LOCAL`:

```
PDFCRAFT_LOCAL=local.v1.json python3 scripts/craft.py config
```

`craft.py config` shows where every setting comes from; environment variables `PDFCRAFT_*`
override the file. Missing paths are reported, never guessed.

For the Raspberry Pi target, `aros_gcc` is the `aarch64-aros-clang` driver (with `aros_ar` and
`aros_strip` beside it), `pomaros_hosted` the pomaros-hosted checkout and `pthread` is `sdk`.
The mainline x86_64 target needs no `aros_src`.

## Steps

1. Fetch the pinned upstreams and create the work copy:

   ```
   python3 scripts/craft.py fetch
   python3 scripts/craft.py materialize
   python3 scripts/craft.py verify
   ```

2. Fetch the locked dependencies into the target's private Cargo home (once per target):

   ```
   PDFCRAFT_LOCAL=<file> python3 scripts/craft.py deps
   ```

3. Build both programs for a target:

   ```
   python3 scripts/craft.py build
   PDFCRAFT_LOCAL=local.v1.json python3 scripts/craft.py build
   PDFCRAFT_LOCAL=local.raspi.json python3 scripts/craft.py build
   ```

   Add `--online` if Cargo still has to download crates. Each build goes to a new
   `build/<target>/out/<date>-<id>/` with the unstripped binaries, `build.log`,
   `cargo-messages.jsonl` and `manifest.json`. The manifest records the work copy commit, the
   patch series, compiler and SDK hashes, the command, every linked package and the binary
   hashes, and checks that no symbol is left undefined. `--worktree` builds uncommitted files
   too and is recorded as such; such builds cannot be packaged. A build is not a runtime test.

   The build passes `release` from `packaging/release.json` to the programs as
   `PDFCRAFT_RELEASE`; `--version` and the log banner print it. Ambient `RUSTFLAGS`,
   `CARGO_TARGET_DIR` and similar overrides are refused. `PDFCRAFT_PANIC` selects the panic
   strategy instead of the target's default.

   What the build adds around the pinned source: `patches/crates/` (the shared set named in
   `crates.json` and this port's own `aws-lc-sys` and `tempfile` patches, checked against the
   Cargo.lock checksums and the recorded patched-tree hashes), the shared tools' `libc-aros` and `aros-glue` patches, `patches/aros-pthread/` (ABIv11 only) and the panic profile
   of the target. The window, input and renderer layer comes from egui-aros, prepared by its
   own `ea.py vendor`, which also supplies AROS versions of `rfd` (file dialogs as ASL
   requesters) and `arboard` (the clipboard) for the AROS build only.

4. Package a build. `scripts/package.py` forwards to `craft.py package`:

   ```
   export APKG_PACK=/path/to/arospkg/tools/apkg-pack
   python3 scripts/package.py binary build/<target>/out/<id>
   python3 scripts/package.py source build/<target>/out/<id> [build/<target>/out/<id> ...]
   ```

   The tools write `dist/PdfCraft-<release>[-rN]-<target>.zip` and
   `dist/PdfCraft-<release>[-rN]-source.zip` and add them to `dist/SHA256SUMS`. They refuse
   a dirty repository, a build from a dirty work copy, binaries that differ from the manifest
   and undefined symbols. A binary archive also needs a catalogue description per target in
   `packaging/catalogue/`, whose `requires_system` must match the C runtime libraries the
   programs open at start; The programs
   are stripped with `strip --strip-unneeded --remove-section .comment` only: a full strip
   removes relocations AROS applies when it loads a program. The program icon is generated from
   PdfCraft's 64x64 application icon with the stack and ToolTypes from `release.json`
   (stack 16 MiB, `GUI_RENDERER=AUTO`). `drawer_files` in `release.json` adds
   `PdfCraft.portable`, the marker that turns on PdfCraft's portable mode.

5. Check an archive on the host: unpack it into a new directory, compare the programs with the
   hashes recorded in the package and run the target's `nm -u` on them (it must print
   nothing). Then test the unpacked package on the target system itself.

## The viewer and editor on AROS

`apps/pdfcraft-aros` runs the desktop app's interface (`PdfCraftApp`, an `eframe::App`) with
egui-aros instead of eframe's own window: an Intuition window on the default public screen. The
renderer is chosen at run time with `--gui-renderer CPU|AUTO|GPU` or the `GUI_RENDERER`
ToolType. The program runs in the -nix path mode: requesters speak DOS names and are converted.
Every file choice goes through rfd, which on AROS is egui-aros' ASL version, with the desktop
app's filters as one pattern. The system clipboard carries text and pictures (ILBM). With
`PdfCraft.portable` beside the program, PdfCraft's portable mode keeps settings (`app.json`),
AutoRecover data, the OCR dictionary and `PdfCraft.log` in `PdfCraftData` in the program's
drawer; at the first start the settings of PdfCraft 0.9.0 for AROS
(`ENVARC:PdfCraft/ui.json`) are read if there are none. A start-up entry raises the program's
stack to 16 MiB. `pdfcraft-cli` runs its command on a thread with its own stack.

Not available on AROS, and reported as such: printing, OCR (the recognition models are not in
the package), the single-instance hand-off, the control file (`--control` is refused), file
lists and HTML on the clipboard, and the self-updater.

`PdfCraft --screenshot FILE.png [--screenshot-frames N]` writes the window's pixels after N
frames (20 by default) and quits. `--window WxH` sets the inner size. `--test-steps FILE.json`
drives the window through a scripted sequence of commands (`run`), opened files (`open`),
answers to the next file dialog (`pick`) and screenshots. `PDFCRAFT_LOG=file` names the log
file; `RUST_LOG=debug` raises the level and logs every frame.

## Guest scripts

`tests/guest/` holds AmigaDOS scripts. `run-smoke` is the release check: the CLI (version,
information, text, a page rendered to PNG, an edit saved twice to the same file, combine, the
MCP handshake), two unattended starts with `--screenshot`, and a scripted session (`steps.json`:
rotate a page, Save As, undo, redo, Save). `run-gpu` runs the screenshot start and the scripted
session with `--gui-renderer GPU`. `run-pkg`, `run-upgrade` and `run-use` install, upgrade, use
and remove the package with apkg from a local index. `tests/fixtures/two-pages.pdf`, written by
`tests/make_fixture.py`, is their input.

## Host checks

`python3 scripts/craft.py host test -p pdfcraft-platform` (or any other package) runs host tests
with the pinned egui-aros patched in.
