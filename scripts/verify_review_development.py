#!/usr/bin/env python3
"""Offline checks of frozen inputs, exact Lean label bindings and the output parser."""
import json
import os
import subprocess
import tempfile
from pathlib import Path
from run_review_development import OUT, ROOT, digest
from prepare_review_development import SOURCE, ledger
from analyze_review_development import parse_answer


def main():
    frozen=OUT/'frozen'
    hashes=json.loads((frozen/'sha256.json').read_text(encoding='utf-8'))
    for file,expected in hashes.items():
        assert digest((frozen/file).read_bytes())==expected,file
    schedule=json.loads((frozen/'schedule.json').read_text(encoding='utf-8'))
    assert len(schedule)==12 and len({t['task_id'] for t in schedule})==12
    assert len({(t['presentation'],t['condition'],t['variant']) for t in schedule})==12
    gold=json.loads((frozen/'gold.json').read_text(encoding='utf-8'))
    assert sorted(g['decision'] for g in gold.values())==['accept','reject']
    env=os.environ.copy(); env['ELAN_TOOLCHAIN']=(ROOT/'formal'/'lean'/'lean-toolchain').read_text(encoding='utf-8').strip()
    lean=Path.home()/'.elan'/'bin'/'lean.exe'
    for variant,g in gold.items():
        directory=frozen/'variants'/variant
        source=(directory/'Artifact.lean').read_text(encoding='utf-8')
        receipt=json.loads((directory/'receipt.json').read_text(encoding='utf-8'))
        assert source==SOURCE.format(cutoff=g['cutoff'])
        assert receipt['source_sha256']==digest(source.encode()) and receipt['exit_code']==0
        assert ledger(source)==json.loads((directory/'ledger.json').read_text(encoding='utf-8'))
        assert ledger(source)['fields'][2]['value']==(1 if g['decision']=='accept' else 0)
        work=Path(tempfile.mkdtemp(prefix='cf-verify-label-'))
        for name in ('Artifact.lean','Witness.lean'):
            (work/name).write_bytes((directory/name).read_bytes())
        local_env={**env,'LEAN_PATH':str(work)}
        target=g['target_proposition']
        term='ReviewArtifact.target_witness' if g['decision']=='accept' else 'ReviewArtifact.target_negation'
        statement=target if g['decision']=='accept' else 'Not ('+target+')'
        (work/'Binding.lean').write_text('import Witness\nexample : '+statement+' := '+term+'\n',encoding='utf-8')
        for args in (['-o','Artifact.olean','Artifact.lean'],['-o','Witness.olean','Witness.lean'],['Binding.lean']):
            p=subprocess.run([str(lean),*args],cwd=work,env=local_env,capture_output=True,text=True,timeout=60)
            assert p.returncode==0,p.stdout+p.stderr
            assert 'sorry' not in (p.stdout+p.stderr).lower()
    try: ledger(SOURCE.format(cutoff=5).replace('4 <=','3 <='))
    except ValueError: pass
    else: raise AssertionError('Unsupported source grammar accepted')
    obj={'decision':'accept','reason':'A source witness exists.','boundary_cited':'domain','source_reference':'Artifact.lean:6'}
    text=json.dumps(obj)
    assert parse_answer(text)==(obj,True,False)
    assert parse_answer('```json\n'+text+'\n```')==(obj,False,True)
    for invalid in ('Preamble\n'+text,text+'\n'+text,json.dumps({**obj,'decision':'maybe'}),json.dumps({**obj,'reason':'word '*81})):
        assert parse_answer(invalid)==(None,False,False)
    print('PASS: frozen hashes; balanced 12-task schedule; two exact Lean target/negation bindings; paired ledgers; unsupported-grammar rejection; strict/fenced/malformed output handling.')


if __name__=='__main__': main()
