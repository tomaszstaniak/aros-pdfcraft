---
type: reference
updated: 2026-10-18
---

# Build tooling origin

scripts/pdfc.py and scripts/pdfconfig.py derive from the WordCraft AROS port scripts/wc.py and wcconfig.py (local sibling snapshot 2026-10-18). Preserve their source/patch reconstruction checks and private libc/pthread construction. The PdfCraft version selects pdfcraft-cli and the native PdfCraft GUI (package pdfcraft-aros). The GUI shell derives from WordCraft source02628f1ca3f0a5577aa3601b7e5f390bab398fc8; original PdfCraftApp still owns document logic and UI. Dependency patches retain original PhotoCraft provenance headers. Runtime source is pinned to rust-aros fd6e4c4c61220eba008029aee886654a3a16fe40; installed toolchain and SDK are separate explicit local settings. No global installation is changed. Private pthread caches key SDK archive/header hashes, compiler/archiver identity and flags, and verify object hashes on reuse. Libc sources are reconstructed and compared on every build.
