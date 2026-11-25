# PdfCraft 0.22.0 for AROS, revision 1

The AROS port of PdfCraft 0.22.0, a PDF viewer and editor. It is built from the PdfCraft 0.22.0 release (tag `v0.22.0`), for three AROS systems.

## Downloads

| File | System |
|---|---|
| `PdfCraft-0.22.0-aros-x86_64-abiv11-pc.zip` | AROS x86_64, ABIv11 distributions (unchanged, from the 0.22.0 release) |
| `PdfCraft-0.22.0-r1-aros-x86_64-abiv1-pc.zip` | AROS x86_64, mainline ABIv1 (nightly 2026-11-24 or later) |
| `PdfCraft-0.22.0-r1-aros-aarch64-abiv1-raspi.zip` | AROS on Raspberry Pi, AArch64 ABIv1 (mainline nightly 2026-11-24 or later) |
| `PdfCraft-0.22.0-r1-source.zip` | Port sources, patches, pinned inputs and build recipe |

Each package runs only on the system it was built for. `SHA256SUMS` lists the checksums. The packages can also be installed with the AROS package manager: `apkg install pdfcraft`.

## What is new in revision 1

Revision 1 is a rebuild of the mainline x86_64 and Raspberry Pi packages for AROS nightly builds from 2026-11-24 on. The programs have no other changes. `PdfCraft --version` prints `0.22.0-r1`.

- The nightly of 2026-11-24 changed a system structure that programs are built against. Packages built before it do not start on that nightly or a later one, and these packages do not start on an earlier one.
- On a nightly before 2026-11-24, keep PdfCraft 0.22.0.
- The ABIv11 package is not affected and stays at 0.22.0.

With the package manager: `apkg upgrade pdfcraft`. Settings and data in `PdfCraftData` are kept.

Checked for this revision on the mainline x86_64 nightly of 2026-11-24, in an emulator: installation and verification with the package manager and a start from Workbench. The Raspberry Pi package was built the same way and not run for this revision.

## What was new in 0.22.0

This release moves from PdfCraft 0.9.0 (test 4) to PdfCraft 0.22.0. For the changes in the program itself, see the release notes of PdfCraft upstream. On the AROS side:

- Packages for mainline x86_64 and the Raspberry Pi, besides ABIv11 distributions.
- The window runs on the same engine as the other Craft programs: only the parts that changed are drawn again, and in the emulators used for testing a typical frame takes about 0.02 s.
- OpenGL can draw the window. The `GUI_RENDERER` ToolType in the icon, or `--gui-renderer` in a Shell, chooses `AUTO` (the default), `CPU` or `GPU`. `AUTO` uses OpenGL only when it is not Mesa's software renderer.
- Every file choice (Open, Save As, export folders, pictures, digital IDs) uses the standard file requester.
- The program takes the stack it needs itself; `Stack` is no longer needed before a Shell start, and the archive has a Workbench icon.
- Settings, AutoRecover data and the log file `PdfCraft.log` are kept in `PdfCraftData` in the program drawer. At its first start PdfCraft takes over the settings of 0.9.0 from `ENVARC:PdfCraft`.

With the package manager: `apkg upgrade pdfcraft`.

## Installation

Unpack the archive for your system anywhere writable and double-click PdfCraft. From a Shell, run `PdfCraft [--gui-renderer CPU|AUTO|GPU] [file]`. To upgrade by hand, unpack the new version to a new place and move `PdfCraftData` into it. Leave `PdfCraft.portable` in the drawer: it keeps the settings there. The archive also holds a `.arospkg` drawer with the arospkg description; after unpacking by hand it can be deleted.

`PdfCraft --version` and the first line of `PdfCraft.log` name the build (`0.22.0` and the target); please include them when you report a problem.

## Known limitations

- No printing: export to PDF or to pictures instead.
- No text recognition (OCR): its recognition models are not in the package.
- The interface is in English only.
- Changes of the whole window (scrolling, zooming, opening a dialog) redraw all of it; on slow machines and in emulators these follow with a delay.
- Fonts for Japanese, Korean and Chinese are not built in. Text in these scripts is shown as boxes unless the document embeds its own font.
- Files dropped on the window are not opened. File lists and formatted (HTML) text are not exchanged through the clipboard.
- Digital signatures, the clipboard, keyboard layouts other than the US one and a start from Workbench have not been tested on AROS in this release.
- No automatic updates: install new versions with the AROS package manager or by unpacking the new archive. The MCP server (`pdfcraft-cli mcp`) has been tested only for its handshake and tool list on AROS.
- ABIv11: AROS One 1.3 has only Mesa's software renderer, so `AUTO` uses the CPU there. `GPU` works with it but draws a frame in seconds.
- Mainline x86_64: `AUTO` uses the CPU, because a program that has opened OpenGL there leaves its log file in use after it ends and the Shell it ran in stops redirecting output (seen on nightly 2026-11-10). `GPU` still opens OpenGL; with VirGL in an emulator it drew correctly at about half a second a frame. Hardware OpenGL drivers have not been tested.
- Mainline x86_64: run one PdfCraft at a time. AutoRecover cannot tell that another PdfCraft is running and may take over its recovery data.
- Raspberry Pi: tested in an emulator only. OpenGL has not been tested on Pi hardware, so `AUTO` uses the CPU; save your work before you try `GPU`.

Licences and notices for PdfCraft, the fonts built into it and everything else linked into it are in the `Licenses` drawer of each package.
