# PdfCraft for AROS

An AROS port of [PdfCraft](https://github.com/storytold/pdfcraft), a PDF viewer and editor. It provides text search, zoom, page rotation and saving, with command-line tools for extracting text and rendering pages.

## Download and run

[Download v0.9.0-test4](https://github.com/tomaszstaniak/aros-pdfcraft/releases/tag/v0.9.0-test4) for **AROS x86_64 ABIv11**, or install `pdfcraft` from the apkg catalogue. The download includes PdfCraft and `pdfcraft-cli`.

These builds are experimental and not optimised. They use CPU rendering and can be slow, especially in large windows.

Unpack the archive into a drawer and double-click the PdfCraft icon. From a Shell, run `Stack 4000000` before starting `PdfCraft`.

Test 4 fixes a crash after closing PdfCraft when it was started from Workbench: on exit the program could release its starting drawer twice.

## Known limitations

OCR, printing, signing and image clipboard exchange are unavailable. Very large, encrypted or damaged PDFs may not open.

## Build from source

This repository contains source revisions, AROS patches and build scripts. See [Building](docs/development.md), [Patch workflow](docs/patching.md) and [Source revisions](upstreams.json). `main` and the tag `v0.9.0-test4` hold the recipe test 4 was built from; release packages are made with `scripts/package_release.py`.

The repository stores build recipes rather than a full upstream source tree. Licenses and author notices are included in the source and application archives.
