#!/usr/bin/env python3
"""Build the ABIv11 directory-ownership regression using pinned CRT headers."""
import json
from pathlib import Path
import struct
import subprocess
import sys
import zlib

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'scripts'))
import pdfconfig
cfg = pdfconfig.load(['aros_src', 'aros_gcc', 'aros_sdk', 'build_root'])
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=False)
for name in ['__crt_intbase.h', '__posixc_intbase.h']:
    data = subprocess.check_output(['git', '-C', cfg['aros_src'], 'show',
                                   cfg['aros_src_commit'] + ':compiler/crt/' + name])
    (out / name).write_bytes(data)
def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
def icon():
    # A small solid-color PNG tool icon. Include an adequate Workbench stack.
    tags = struct.pack('>IIII', 0x8000100F, 3, 0x80001009, 4000000)
    raw = (b'\0' + bytes([60, 100, 180, 255]) * 16) * 16
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 16, 16, 8, 6, 0, 0, 0))
           + chunk(b'icOn', tags) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))
    return png + png
for name, flags in [('lock-red', []), ('lock-green', ['-DPRIME'])]:
    subprocess.run([cfg['aros_gcc'], '--sysroot=' + cfg['aros_sdk'], '-I' + str(out),
                    '-O2', '-nix', *flags, str(Path(__file__).with_name('probe.c')),
                    '-lpthread', '-o', str(out / name)], check=True)
    (out / (name + '.info')).write_bytes(icon())
subprocess.run([cfg['aros_gcc'], '--sysroot=' + cfg['aros_sdk'], '-O2',
                str(Path(__file__).with_name('openwb.c')), '-o', str(out / 'openwb')], check=True)
(out / 'context.json').write_text(json.dumps({'crt_headers': cfg['aros_src_commit'],
    'sdk': cfg['aros_sdk'], 'compiler': cfg['aros_gcc'], 'abi': 'x86_64 ABIv11'}, indent=2) + '\n')
print(out)
