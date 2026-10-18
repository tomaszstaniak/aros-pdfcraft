#!/usr/bin/env python3
"""Contributor-original deterministic two-page PDF, no embedded external assets."""
from pathlib import Path
import sys


def make_pdf():
    streams = [b"0 0 1 rg 20 20 60 40 re f\nBT /F1 18 Tf 20 100 Td (AROS PdfCraft page one) Tj ET\n",
               b"1 0 0 rg 40 30 50 60 re f\nBT /F1 18 Tf 20 110 Td (AROS PdfCraft page two) Tj ET\n"]
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>"]
    for content in (6, 7):
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 240 160] /Resources << /Font << /F1 5 0 R >> >> /Contents {content} 0 R >>".encode())
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for stream in streams:
        objects.append(f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"endstream")
    out = bytearray(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, obj in enumerate(objects, 1):
        offsets.append(len(out))
        out.extend(f"{i} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets:
        out.extend(f"{offset:010d} 00000 n \n".encode())
    out.extend(f"trailer\n<< /Root 1 0 R /Size {len(objects)+1} >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return out


if __name__ == "__main__":
    Path(sys.argv[1]).write_bytes(make_pdf())
