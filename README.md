# PdfCraft for AROS

An AROS port of [PdfCraft](https://github.com/storytold/pdfcraft), a PDF viewer and editor. It shows, searches and annotates PDF documents, fills forms, organises pages, signs documents and exports pictures and text, with a command-line program for the same work.

## Download and run

[Download 0.22.0](https://github.com/tomaszstaniak/aros-pdfcraft/releases/tag/v0.22.0) for one of these systems, or install `pdfcraft` with arospkg:

| Package | System |
|---|---|
| `PdfCraft-0.22.0-aros-x86_64-abiv11-pc.zip` | AROS x86_64, ABIv11 distributions |
| `PdfCraft-0.22.0-aros-x86_64-abiv1-pc.zip` | AROS x86_64, mainline ABIv1 (nightly 2026-11-06 or later) |
| `PdfCraft-0.22.0-aros-aarch64-abiv1-raspi.zip` | AROS on Raspberry Pi, AArch64 ABIv1 (mainline nightly 2026-11-06 or later) |

Each package runs only on the system it was built for and includes PdfCraft and `pdfcraft-cli`. Unpack the archive anywhere writable and double-click the PdfCraft icon; from a Shell, run `PdfCraft [file]`. The program takes the stack it needs itself. `ReadMe.txt` in the drawer describes installation, the command line, the clipboard and the interface renderer.

## Known limitations

There is no printing and no text recognition (OCR). Changes of the whole window, such as scrolling and zooming, redraw all of it and follow with a delay on slow machines and in emulators. The Raspberry Pi build was tested only in an emulator. The [release notes](docs/releases/v0.22.0.md) list the rest.

## Build from source

This repository contains source revisions, AROS patches and build scripts. See [Building](docs/development.md), [Patch workflow](docs/patching.md) and [Source revisions](upstreams.json). The window, clipboard, file requesters and start-up code use [egui-aros](https://github.com/tomaszstaniak/egui-aros), pinned in `upstreams.json`, which also holds the build tools shared by the Craft ports; the Rust standard library for AROS comes from [rust-aros](https://github.com/tomaszstaniak/rust-aros).

The repository holds the build recipe and patches; the source archive of each release adds the pinned upstream inputs. Licenses and author notices are in the source and application archives.
