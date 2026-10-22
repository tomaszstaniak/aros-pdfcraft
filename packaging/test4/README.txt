PdfCraft 0.9.0 for AROS - test 4
================================

PdfCraft is a PDF viewer and editor: view and search documents, zoom, rotate pages and save. The pdfcraft-cli command prints a document's details and text and renders pages to PNG.

This is an experimental build for AROS x86_64 ABIv11 (such as AROS One). It is not optimised: the window is drawn by the CPU and can be slow, especially when it is large. It is not a binary for AROS mainline (ABIv1).

STARTING
Double-click the PdfCraft icon. The icon gives the program the stack it needs. From a Shell:

  Stack 4000000
  Work:PdfCraft/PdfCraft
  Work:PdfCraft/PdfCraft "Work:Documents/example.pdf"

Open (Ctrl-O) uses the standard file requester. Work on copies of documents you care about. Preferences are kept in ENVARC:PdfCraft/ui.json; to leave them untouched for one Shell session, run SetEnv PDFCRAFT_NO_PREFS 1 first.

COMMAND LINE
  pdfcraft-cli --version
  pdfcraft-cli info "Work:Documents/example.pdf"
  pdfcraft-cli text "Work:Documents/example.pdf"
  pdfcraft-cli render "Work:Documents/example.pdf" --page 1 --dpi 72 --out RAM:page.png

CHANGES SINCE TEST 2
- Fixed a crash after closing PdfCraft when it was started from Workbench. On exit the program could release its starting drawer twice, which could damage memory and make the desktop crash or freeze afterwards.
- There is now a Workbench icon.

LIMITATIONS
Text recognition (OCR), printing, signing, and pictures or files through the clipboard are not available. Very large, encrypted or damaged PDF files may not open. If replacing a saved file fails after the old file has been removed, the new contents stay in a temporary file whose name the error message gives.

If something goes wrong, a log helps:
  SetEnv RUST_LOG debug
  SetEnv PDFCRAFT_LOG RAM:pdfcraft.log
  Work:PdfCraft/PdfCraft

BUILD AND LICENSES
BUILD.json names the exact sources, compiler and program checksums. SHA256SUMS covers the files in this drawer, excluding itself. NOTICE, ATTRIBUTION.* and Licenses keep the upstream and dependency notices. Upstream: https://github.com/storytold/pdfcraft Port: https://github.com/tomaszstaniak/aros-pdfcraft
