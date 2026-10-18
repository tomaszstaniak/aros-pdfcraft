#!/usr/bin/env python3
"""Build a test-only widened pthread epilogue from the selected private series."""
import argparse
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'scripts'))
import pdfc

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('run', help='fresh output/run label using letters, digits or hyphens')
args = parser.parse_args()
if not args.run or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-' for c in args.run):
    parser.error('invalid run label')
cfg = pdfc.pdfconfig.load(['aros_src', 'aros_gcc', 'aros_sdk', 'aros_ar', 'build_root'])
out = Path(cfg['build_root']) / ('pthread-tail-' + args.run)
out.mkdir(exist_ok=False)
commit = cfg['aros_src_commit']
archive = pdfc.run(['git', '-C', cfg['aros_src'], 'archive', '--format=tar', commit, 'compiler/pthread']).stdout
patches = [pdfc.PTHREAD_DIR / name for name in (pdfc.PTHREAD_DIR / 'series').read_text().split()]
with tempfile.TemporaryDirectory() as tmp:
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(tmp, filter='data')
    src = Path(tmp) / 'compiler/pthread'
    for patch in patches:
        pdfc.run(['patch', '--quiet', '-p3', '-i', patch], cwd=src)
    source = src / 'pthread_create.c'
    text = source.read_text()
    marker = '        ReleaseSemaphore(&thread_sem);\n    }\n}\n\nint pthread_create('
    if text.count(marker) != 1:
        raise ValueError('review pthread tail before injecting the test hook')
    text = text.replace(marker, '        ReleaseSemaphore(&thread_sem);\n'
                        '        extern void pdfc_test_thread_tail(void);\n'
                        '        pdfc_test_thread_tail();\n    }\n}\n\nint pthread_create(')
    source.write_text(text)
    for name in ['pthread', 'pthread_create']:
        pdfc.run([cfg['aros_gcc'], f"--sysroot={cfg['aros_sdk']}", *pdfc.PTHREAD_CFLAGS,
                  '-I', src, '-c', src / (name + '.c'), '-o', out / (name + '.o')])
    pdfc.run([cfg['aros_gcc'], f"--sysroot={cfg['aros_sdk']}", *pdfc.PTHREAD_CFLAGS,
              REPO / 'tests/pthread-exit/probe.c', out / 'pthread.o', out / 'pthread_create.o',
              '-lpthread', '-o', out / 'pthread-tail-probe'])
(out / 'run-tail').write_text(
    f'FailAt 21\nProtect RAM:pdfc/pthread-tail-probe +e\n'
    f'RAM:pdfc/pthread-tail-probe >RESULTS:pdfc-tail-{args.run}.txt\n'
    f'Echo $RC >RESULTS:pdfc-tail-{args.run}.rc\n'
    f'Echo done >RESULTS:pdfc-tail-{args.run}.done\n')
(out / 'build.json').write_text(json.dumps({
    'abi': 'x86_64 ABIv11', 'source': commit, 'test_only_instrumentation': True,
    'patches': {p.name: pdfc.sha256_file(p) for p in patches},
    'probe_source_sha256': pdfc.sha256_file(REPO / 'tests/pthread-exit/probe.c'),
    'probe_binary_sha256': pdfc.sha256_file(out / 'pthread-tail-probe'),
    'sdk_archive_sha256': pdfc.sha256_file(Path(cfg['aros_sdk']) / 'lib/libpthread.a'),
}, indent=2) + '\n')
print(out)
