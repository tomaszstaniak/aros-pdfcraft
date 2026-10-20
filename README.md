# PdfCraft for AROS

An AROS port of [PdfCraft](https://github.com/storytold/pdfcraft), a PDF viewer and editor. It provides text search, zoom, page rotation and saving, with command-line tools for extracting text and rendering pages.

## Download and run

[Download v0.9.0-test2-r2](https://github.com/tomaszstaniak/aros-pdfcraft/releases/tag/v0.9.0-test2-r2) for **AROS x86_64 ABIv11**, or find `pdfcraft` in the apkg catalogue. The download includes PdfCraft and `pdfcraft-cli`.

These builds are experimental and not optimised. They use CPU rendering and can be slow, especially in large windows.

Unpack into a writable drawer, open a Shell and `CD` to it. Run `Protect PdfCraft +e` and `Protect pdfcraft-cli +e`, then start `PdfCraft`. This release has no Workbench icon.

## Known limitations

A desktop crash or freeze after closing PdfCraft has been reported. The cause remains unresolved. OCR, printing, signing and image clipboard exchange are unavailable. Very large, encrypted or damaged PDFs may not open.

## Build from source

This repository contains source revisions, AROS patches and build scripts. See [Building](docs/development.md), [Patch workflow](docs/patching.md) and [Source revisions](upstreams.json). **For test2-r2, use the source archive attached to the release.** The recipe on `main` is for the separate test3-diag diagnostic build; its instructions do not apply to test2-r2.

The repository stores build recipes rather than a full upstream source tree. Licenses and author notices are included in the source and application archives.
