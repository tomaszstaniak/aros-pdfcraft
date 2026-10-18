#!/usr/bin/env python3
"""Strict validation of one completed native CLI run; failed gates are errors."""
import argparse
import hashlib
import json
from pathlib import Path
from check_png import decode


def check(payload, results):
    spec=json.loads((payload/'smoke.json').read_text())
    run=spec['run_id']
    manifest={line.split('  ',1)[1].removeprefix('./'):line.split('  ',1)[0]
              for line in (results/'COLLECT-MANIFEST.sha256').read_text().splitlines()}
    def read(suffix):
        p=results/(run+'-'+suffix)
        data=p.read_bytes()
        assert hashlib.sha256(data).hexdigest()==manifest[p.name], 'collection digest '+p.name
        return data
    identity=(run+' '+spec['build_id']+'\n').encode()
    assert read('start.txt')==identity and read('done.txt')==identity, 'fresh start/completion identity'
    assert hashlib.sha256((payload/'pdfcraft-cli').read_bytes()).hexdigest()==spec['binary_sha256']
    for name,code in spec['expected_rc'].items():
        actual=read(name+'.rc').decode().strip()
        assert actual==str(code), f'{name} returned {actual}, expected {code}'
    info=json.loads(read('info.txt'));assert info['pages']==2 and info['first_page_pt']==[240.0,160.0]
    text=read('text.txt').decode();assert 'AROS PdfCraft page one' in text and 'AROS PdfCraft page two' in text
    info=json.loads(read('reopen.txt'));assert info['pages']==2 and info['title']==spec.get('expected_title','AROS saved') and info['first_page_pt']==[160.0,240.0]
    assert read('edited.pdf').startswith((payload/'fixture.pdf').read_bytes()), 'original PDF bytes lost'
    read('page.png')
    width,height,pixel=decode(results/(run+'-page.png'))
    assert (width,height)==(240,160) and pixel(30,110)==(0,0,255) and pixel(200,140)==(255,255,255), 'render output'
    for command in [name for name in spec['expected_rc'] if name.startswith('mcp')]:
        replies=[json.loads(line) for line in read(command+'.txt').decode().splitlines()]
        assert [m.get('id') for m in replies]==spec.get('mcp_ids',[1,2,3,4]), 'MCP reply IDs'
        for reply in replies:
            assert 'error' not in reply, reply
            if reply['id']>=4:
                assert bool(reply['result'].get('isError'))==(reply['id'] in spec.get('mcp_denied_ids',[])), reply
    print(json.dumps({'run_id':run,'status':'accepted','commands':len(spec['expected_rc']),'render_size':[width,height]},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('payload',type=Path);parser.add_argument('results',type=Path)
    args=parser.parse_args();check(args.payload,args.results)
