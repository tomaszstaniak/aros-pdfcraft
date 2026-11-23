PdfCraft @VERSION@ for AROS
=========================

PdfCraft is a PDF viewer and editor. It shows, searches and annotates PDF
documents, fills and creates forms, organises pages (rotate, delete,
insert, extract, combine, split), edits text and pictures, signs documents
and exports them to pictures, text and other formats. This is its AROS
port, based on PdfCraft @UPSTREAM_VERSION@.

This package is for: @SYSTEM@.
It does not run on other AROS systems; use the package made for yours.

The drawer holds two programs:

  PdfCraft       the PDF viewer and editor
  pdfcraft-cli   the command-line program: shows a document's details and
                 text, renders pages to pictures, rotates, deletes, moves,
                 extracts and combines pages, checks documents and serves
                 an MCP automation interface over standard input and output

PdfCraft.portable keeps the settings in the program drawer (see Settings
and log); leave it there.

Installation
------------

Unpack the archive anywhere writable, for example to Work:. It creates the
drawer PdfCraft and its icon. Both programs use only libraries that come
with AROS; nothing in the system is replaced or added.

To upgrade, unpack the new version to a new place (not over the old drawer),
then move the drawer PdfCraftData from the old PdfCraft drawer into the new
one to keep your settings, recent files and AutoRecover data.

Starting
--------

Workbench: double-click PdfCraft. The program takes the stack it needs
itself; it also works from a Shell with the default stack.

Shell:

  PdfCraft [--gui-renderer CPU|AUTO|GPU] [--window WxH] [file ...]

Files named on the command line are opened at start. Open, Save As and the
other file choices use the standard file requester. To close PdfCraft, use
the window's close gadget; with unsaved changes it asks whether to save
them. Documents left unsaved when PdfCraft stopped unexpectedly are offered
again at the next start (AutoRecover).

  pdfcraft-cli info report.pdf
  pdfcraft-cli text report.pdf --page 1
  pdfcraft-cli render report.pdf --page 1 --dpi 96 --out page1.png
  pdfcraft-cli edit report.pdf --out rotated.pdf --rotate 1:90
  pdfcraft-cli combine a.pdf b.pdf --out both.pdf
  pdfcraft-cli --help

pdfcraft-cli mcp runs an MCP server on standard input and output for a
client that starts it as a child process. It works on its own documents,
not on the ones open in the PdfCraft window.

Settings and log
----------------

Settings, recent files, AutoRecover data and the log file PdfCraft.log are
kept in the drawer PdfCraftData inside the PdfCraft drawer; it is created at
the first start. At its first start this version also takes over the
settings of PdfCraft 0.9.0 for AROS (ENVARC:PdfCraft/ui.json), which it
leaves in place. The variable PDFCRAFT_LOG names another log file.

Clipboard
---------

Text is exchanged with other programs through the system clipboard.
Pictures are copied to and pasted from the clipboard as ILBM. The clipboard
has not been tested in this release.

Interface renderer
------------------

The ToolType GUI_RENDERER in the program's icon, or the Shell argument
--gui-renderer, chooses how the interface is drawn. A Shell argument takes
priority; the icon is not read when the program is started from the Shell.
Values ignore letter case.

  AUTO  OpenGL if it opens and is not Mesa's software renderer, otherwise
        CPU; the reason is written to PdfCraft.log (default)
  CPU   the processor draws the interface; OpenGL is not opened
  GPU   OpenGL (the software renderer too), or the program stops with an
        error

Known limitations
-----------------

@LIMITATIONS@

Licences
--------

PdfCraft is available under the MIT license or the Apache License 2.0, at
your option. The texts, the licences of the fonts built into the programs,
and the licences of everything linked into the programs are in the Licenses
drawer. BUILD.txt identifies this build.

PdfCraft: https://github.com/storytold/pdfcraft
AROS port: https://github.com/tomaszstaniak/aros-pdfcraft
