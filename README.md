# PdfCraft for AROS

An experimental AROS x86_64 ABIv11 port of [PdfCraft](https://github.com/storytold/pdfcraft), a PDF viewer and editor.

This diagnostic build investigates a desktop crash or freeze after closing PdfCraft. Opening a disk drawer afterwards may trigger the failure. The cause remains under investigation; this build does not fix it.

Each Rust allocation is checked separately. Guard areas, checks of freed blocks and double-free detection can report memory damage. Findings appear as alerts and are written to `RAM:PdfCraft-diag.txt`. Detection may happen after the offending write.

The archive contains the GUI and the `grubpatch` helper with its source. Enabling system memory checks changes the boot configuration and requires a restart. The helper accepts only the boot-menu layout it recognises and saves the original as `SYS:boot/grub/grub.cfg.orig`. Follow the included instructions and use `grubpatch RESTORE` afterwards, then restart.

Repeat the original steps: start PdfCraft, close its window, then open a disk drawer. Photograph any alert and its “More...” page. Copy `RAM:PdfCraft-diag.txt` to disk before restarting. Report the result even if no alert appears.

This build uses more memory and runs more slowly than the normal application. OCR is unavailable.

## Sources and build

This repository contains the pinned source revisions, AROS patches and build scripts. See [development](docs/development.md), [patching](docs/patching.md) and [upstreams.json](upstreams.json).

Upstream sources and generated build outputs are fetched or created locally. They are not included in the repository. Mainline ABIv1 is a separate target; these binaries require ABIv11.

Upstream and dependency licenses and author notices are retained in the application archives and pinned sources.
