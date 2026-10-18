#!/usr/bin/env python3
"""Prepare one immutable CLI smoke payload. Run through the guarded VM pool."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import uuid
from make_fixture import make_pdf


def stage(build, output):
    manifest = json.loads((build / 'manifest.json').read_text())
    binary = build / 'pdfcraft-cli'
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    if manifest['status'] != 'built-not-run' or manifest['binaries']['pdfcraft-cli']['sha256'] != digest:
        raise ValueError('require a complete matching build manifest')
    output.mkdir(parents=True, exist_ok=False)
    run = 'pdfc-' + uuid.uuid4().hex[:12]
    shutil.copy2(binary, output / binary.name)
    (output / binary.name).chmod(0o755)
    (output / 'fixture.pdf').write_bytes(make_pdf())
    (output / 'mcp.txt').write_text(''.join(json.dumps(m) + '\n' for m in [
        {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'aros-smoke','version':'1'}}},
        {'jsonrpc':'2.0','method':'notifications/initialized'},
        {'jsonrpc':'2.0','id':2,'method':'ping'},
        {'jsonrpc':'2.0','id':3,'method':'tools/list'},
        {'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'doc_open','arguments':{'path':'RAM:pdfc/fixture.pdf'}}},
        {'jsonrpc':'2.0','id':5,'method':'tools/call','params':{'name':'doc_open','arguments':{'path':'RAM:pdfc/file with spaces.pdf'}}},
        {'jsonrpc':'2.0','id':6,'method':'tools/call','params':{'name':'doc_open','arguments':{'path':'../pdfc-outside.pdf'}}},
        {'jsonrpc':'2.0','id':7,'method':'tools/call','params':{'name':'doc_open','arguments':{'path':'RAM:pdfc-outside.pdf'}}},
        {'jsonrpc':'2.0','id':8,'method':'tools/call','params':{'name':'doc_open','arguments':{'path':'/RAM/pdfc-outside.pdf'}}},
        {'jsonrpc':'2.0','id':9,'method':'tools/call','params':{'name':'doc_save','arguments':{'doc':1,'path':'saved-mcp.pdf'}}},
        {'jsonrpc':'2.0','id':10,'method':'tools/call','params':{'name':'doc_save','arguments':{'doc':1,'path':'RAM:pdfc-outside-write.pdf'}}},
        {'jsonrpc':'2.0','id':11,'method':'tools/call','params':{'name':'doc_open','arguments':{'path':'fixture.pdf'}}},
        {'jsonrpc':'2.0','id':12,'method':'tools/call','params':{'name':'doc_info','arguments':{'doc':1}}},
    ]))
    commands = [
        ('version','--version'),
        ('info','info RAM:pdfc/fixture.pdf'),
        ('text','text RAM:pdfc/fixture.pdf'),
        ('render','render RAM:pdfc/fixture.pdf --page 1 --dpi 72 --out RAM:pdfc/page.png'),
        ('edit','edit RAM:pdfc/fixture.pdf --out RAM:pdfc/edited.pdf --rotate 1:90 --title "AROS saved"'),
        ('overwrite','edit RAM:pdfc/edited.pdf --out RAM:pdfc/edited.pdf --title "AROS saved twice"'),
        ('reopen','info RAM:pdfc/edited.pdf'),
        ('invalid','render RAM:pdfc/fixture.pdf --page 0 --out RAM:pdfc/invalid.png'),
        ('missing','info RAM:pdfc/missing.pdf'),
        ('mcp','mcp --root RAM:pdfc <RAM:pdfc/mcp.txt'),
        ('mcposix','mcp --root /RAM/pdfc <RAM:pdfc/mcp.txt'),
    ]
    lines=['FailAt 21',f'If EXISTS RESULTS:{run}-start.txt','Echo "Refusing stale run"','Quit 20','EndIf',
           'Protect RAM:pdfc/pdfcraft-cli +e',f'Echo "{run} {manifest["build_id"]}" >RESULTS:{run}-start.txt',
           f'List RAM:pdfc >RESULTS:{run}-list.txt',
           'Copy RAM:pdfc/fixture.pdf "RAM:pdfc/file with spaces.pdf"',
           'Copy RAM:pdfc/fixture.pdf RAM:pdfc-outside.pdf']
    for name,args in commands:
        lines += [f'RAM:pdfc/pdfcraft-cli {args} >RESULTS:{run}-{name}.txt',f'Echo $RC >RESULTS:{run}-{name}.rc']
    for name in ['page.png','edited.pdf','saved-mcp.pdf']:
        lines += [f'If EXISTS RAM:pdfc/{name}',f'Copy RAM:pdfc/{name} RESULTS:{run}-{name}','EndIf']
    lines += [f'Echo "{run} {manifest["build_id"]}" >RESULTS:{run}-done.txt']
    (output/'run-cli').write_text('\n'.join(lines)+'\n')
    record={'run_id':run,'build_id':manifest['build_id'],'binary_sha256':digest,'commands':commands,
            'expected_rc':{n:(1 if n in ('invalid','missing') else 0) for n,_ in commands},
            'expected_title':'AROS saved twice',
            'mcp_ids':list(range(1,13)), 'mcp_denied_ids':[6,7,8,10]}
    (output/'smoke.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'run_id':run,'payload':str(output)},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    stage(args.build.resolve(),args.output.resolve())
