#!/usr/bin/env python3
"""Prepare a fresh native GUI smoke; completion must include its PNG and actual exit code."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import uuid
from make_fixture import make_pdf

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('build', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
manifest = json.loads((args.build / 'manifest.json').read_text())
binary = args.build / 'PdfCraft'
digest = hashlib.sha256(binary.read_bytes()).hexdigest()
if manifest['status'] != 'built-not-run' or manifest['binaries']['PdfCraft']['sha256'] != digest:
    raise ValueError('require a complete matching GUI build')
args.output.mkdir(parents=True, exist_ok=False)
shutil.copy2(binary, args.output / binary.name)
(args.output / 'fixture.pdf').write_bytes(make_pdf())
run = 'pdfc-gui-' + uuid.uuid4().hex[:12]
identity = run + ' ' + manifest['build_id']
script = f'''FailAt 21
If EXISTS RESULTS:{run}-start.txt
Quit 20
EndIf
Protect RAM:pdfc/PdfCraft +e
SetEnv PDFCRAFT_NO_PREFS 1
SetEnv PDFCRAFT_SYSTEM_FONTS 0
SetEnv PDFCRAFT_LOG RESULTS:{run}-log.txt
Echo "{identity}" >RESULTS:{run}-start.txt
RAM:pdfc/PdfCraft --window 800x600 --screenshot RAM:pdfc/ui.png --screenshot-frames 8 RAM:pdfc/fixture.pdf
Echo $RC >RESULTS:{run}-exit.rc
If EXISTS RAM:pdfc/ui.png
Copy RAM:pdfc/ui.png RESULTS:{run}-ui.png
EndIf
Echo "{identity}" >RESULTS:{run}-done.txt
'''
(args.output / 'run-gui').write_text(script)
(args.output / 'smoke.json').write_text(json.dumps({'run_id':run, 'build_id':manifest['build_id'], 'binary_sha256':digest}, indent=2)+'\n')
print(json.dumps({'run_id':run,'payload':str(args.output.resolve())}))
