#!/usr/bin/env python3
"""Exercise cache hits, damaged objects and changed SDK identity without modifying caches."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pdfc

cfg = pdfc.pdfconfig.load(['aros_gcc', 'aros_ar', 'aros_sdk', 'aros_src', 'build_root'])
root = Path(cfg['build_root'])
cache, record = pdfc.build_pthread(cfg, root)
with tempfile.TemporaryDirectory(prefix='pdfc-cache-test-') as tmp:
    tmp = Path(tmp)
    copied = tmp / cache.name
    shutil.copytree(cache, copied)
    assert pdfc.build_pthread(cfg, tmp)[1] == record
    obj = copied / 'pthread.o'
    original = obj.read_bytes()
    obj.write_bytes(original + b'changed')
    try:
        pdfc.build_pthread(cfg, tmp)
    except pdfc.Failure as error:
        assert 'changed pthread cache' in str(error)
    else:
        raise AssertionError('damaged object was trusted')
    obj.write_bytes(original)
    real_hash, real_run = pdfc.sha256_file, pdfc.run
    def changed_hash(path):
        return '0' * 64 if Path(path) == Path(cfg['aros_sdk']) / 'lib/libpthread.a' else real_hash(path)
    class RebuildRequired(Exception):
        pass
    def forbid_build(command, **kwargs):
        if str(command[0]) == 'git':
            raise RebuildRequired()
        return real_run(command, **kwargs)
    with patch.object(pdfc, 'sha256_file', changed_hash), patch.object(pdfc, 'run', forbid_build):
        try:
            pdfc.build_pthread(cfg, tmp)
        except RebuildRequired:
            pass
        else:
            raise AssertionError('changed SDK reused cached objects')
print(json.dumps({'cache': cache.name, 'cache_hit': True, 'damaged_object_rejected': True, 'changed_sdk_requires_rebuild': True}))
