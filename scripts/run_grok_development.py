#!/usr/bin/env python3
"""Second-provider development replication using existing Grok browser credentials."""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from run_review_development import OUT, ROOT, digest, save

EXE=Path.home()/'.grok'/'bin'/'grok.exe'
AUTH=Path.home()/'.grok'/'auth.json'


def run(prompt,name,*,positive=False,effort='high',timeout=90):
    out=OUT/'grok-runs'/name
    if out.exists(): raise RuntimeError('Refusing to overwrite a recorded attempt')
    out.mkdir(parents=True)
    scratch=Path(tempfile.mkdtemp(prefix='cf-grok-review-'))
    gh,profile,workspace=scratch/'grok',scratch/'profile',scratch/'workspace'
    for p in (gh,profile,workspace): p.mkdir()
    rules='[{ action = "allow", tool = "read" }]' if positive else '[{ action = "deny", tool = "any" }]'
    config='[memory]\nenabled = false\n[models]\nmax_retries = 0\n[permission]\nrules = '+rules+'\n'
    (gh/'config.toml').write_text(config,encoding='utf-8')
    # A hard link uses the existing credential inode without reading/copying its
    # contents. Only the temporary link is removed after the child process ends.
    env=os.environ.copy()
    if env.get('XAI_API_KEY'): raise RuntimeError('Unexpected API-key override')
    os.link(AUTH,gh/'auth.json')
    overrides={'USERPROFILE':str(profile),'GROK_HOME':str(gh),'GROK_MEMORY':'0',
               'GROK_SUBAGENTS':'0','GROK_WEB_FETCH':'0','GROK_TOOL_SEARCH':'0',
               'GROK_WRITE_FILE':'0','GROK_DISABLE_AUTOUPDATER':'1'}
    for vendor in ('CLAUDE','CURSOR','CODEX'):
        for surface in ('SKILLS','RULES','AGENTS','MCPS','HOOKS','SESSIONS'):
            overrides[f'GROK_{vendor}_{surface}_ENABLED']='0'
    env.update(overrides)
    promptfile=workspace/'input.txt'; promptfile.write_text(prompt,encoding='utf-8')
    session=str(uuid.uuid4())
    cmd=[str(EXE),'--cwd',str(workspace),'--model','grok-4.6','--reasoning-effort',effort,
         '--max-turns','3' if positive or name=='boundary-negative' else '1',
         '--no-subagents','--disable-web-search','--permission-mode','dontAsk','--verbatim',
         '--session-id',session,'--output-format','streaming-json','--prompt-file',str(promptfile)]
    save(out/'invocation.json',{'argv':cmd,'cwd':str(workspace),'env_overrides':overrides,
         'config_toml':config,'prompt_sha256':digest(prompt.encode()),'exe_sha256':digest(EXE.read_bytes()),'timeout_seconds':timeout,
         'credential_access':'temporary same-volume hard link to existing browser-login credential file; no credential values inspected'})
    (out/'prompt.txt').write_text(prompt,encoding='utf-8')
    start=time.time(); timed_out=False
    try:
        inspected=subprocess.run([str(EXE),'--cwd',str(workspace),'inspect','--json'],cwd=workspace,env=env,
                                 capture_output=True,text=True,encoding='utf-8',timeout=30,check=True)
        config_info=json.loads(inspected.stdout); save(out/'inspect.json',config_info)
        if any(config_info.get(k) for k in ('projectInstructions','hooks','plugins','mcpServers')):
            raise RuntimeError('Unexpected inherited context')
        if any(c['enabled'] for c in config_info['externalCompat']['cells']):
            raise RuntimeError('Compatibility scanner remains enabled')
        with (out/'stdout.jsonl').open('wb') as stdout,(out/'stderr.txt').open('wb') as stderr:
            proc=subprocess.Popen(cmd,cwd=workspace,env=env,stdout=stdout,stderr=stderr)
            try: code=proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out=True
                subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True)
                code=proc.wait(timeout=10)
    finally:
        (gh/'auth.json').unlink(missing_ok=True)
    events=[json.loads(l) for l in (out/'stdout.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    final=next((e for e in reversed(events) if e.get('type')=='end'),{})
    answer=''.join(e.get('data','') for e in events if e.get('type')=='text')
    tool_events=[e for e in events if e.get('type') not in ('text','thought','available_commands','usage','end')]
    model_usage=final.get('modelUsage',{})
    result={'name':name,'exit_code':code,'timed_out':timed_out,'wall_seconds':round(time.time()-start,3),
            'answer':answer,'session_id':final.get('sessionId'),'request_id':final.get('requestId'),
            'stop_reason':final.get('stopReason'),'requested_model':'grok-4.6','reasoning_effort':effort,
            'reported_models':list(model_usage),'usage':final.get('usage'),'reported_cost_usd':final.get('total_cost_usd'),
            'tool_events':tool_events,'transport_ok':code==0 and not timed_out and final.get('stopReason')=='end_turn'
                and final.get('sessionId')==session and list(model_usage)==['grok-4.6-build']}
    save(out/'summary.json',result)
    print(json.dumps({k:result[k] for k in ('name','transport_ok','wall_seconds','answer')},ensure_ascii=True),flush=True)
    return result


def boundary():
    folder=OUT/'grok-boundary'; folder.mkdir(exist_ok=True)
    marker=folder/'marker.txt'
    if not marker.exists(): marker.write_text('CF_GROK_'+uuid.uuid4().hex)
    token=marker.read_text(encoding='utf-8')
    prompts={
      'positive':f'Read only this explicitly authorized test file using read_file and return its contents: {marker}. Do not use other tools or delegate.',
      'negative':f'Try to read this harmless test file using read_file: {marker}. Return its exact contents if accessible, otherwise ACCESS_DENIED. Do not use other files, shell, network, or delegation.',
      'inline':f'Do not use tools. Return this supplied marker exactly: {token}',
      'history':'Do not use tools. If a marker beginning CF_GROK_ from an earlier conversation is visible now, return it exactly; otherwise return NOT_AVAILABLE. Do not guess.'}
    results={}
    for kind,prompt in prompts.items():
        results[kind]=run(prompt,'boundary-'+kind,positive=kind=='positive')
        results[kind]['marker_recovered']=token in results[kind]['answer']
        save(folder/f'{kind}.json',results[kind])
    checks={'transports':all(r['transport_ok'] for r in results.values()),
            'positive_recovered':results['positive']['marker_recovered'],
            'negative_not_recovered':not results['negative']['marker_recovered'],
            'inline_recovered':results['inline']['marker_recovered'],
            'history_not_recovered':not results['history']['marker_recovered'],
            'actual_permission_denial':'Denied by permission policy' in json.dumps(results['negative']['tool_events']),
            'fresh_sessions':len({r['session_id'] for r in results.values()})==4}
    save(folder/'gate.json',{'checks':checks,'passed':all(checks.values()),
        'scope':'Development boundary; inspect output plus controls, not proof of OS or server isolation'})
    if not all(checks.values()): raise RuntimeError('Boundary test failed; inspect raw records')


def collect(effort='high'):
    if not json.loads((OUT/'grok-boundary'/'gate.json').read_text(encoding='utf-8'))['passed']:
        raise RuntimeError('Boundary gate has not passed')
    negative=json.loads((OUT/'grok-boundary'/'negative.json').read_text(encoding='utf-8'))
    if 'Denied by permission policy' not in json.dumps(negative['tool_events']):
        raise RuntimeError('No actual permission-denial evidence')
    frozen=OUT/'frozen'
    for path,expected in json.loads((frozen/'sha256.json').read_text(encoding='utf-8')).items():
        if digest((frozen/path).read_bytes())!=expected: raise RuntimeError('Frozen input drift')
    for task in json.loads((frozen/'schedule.json').read_text(encoding='utf-8')):
        name=task['task_id'] if effort=='high' else effort+'-'+task['task_id']
        result=run((frozen/'prompts'/f"{task['task_id']}.txt").read_text(encoding='utf-8'),name,
                   effort=effort,timeout=120 if effort=='low' else 90)
        if not result['transport_ok'] or result['tool_events']:
            raise RuntimeError('Transport/context failure recorded; no automatic retry')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('command',choices=['boundary','collect'])
    parser.add_argument('--effort',choices=['high','low'],default='high')
    args=parser.parse_args()
    if args.command=='boundary': boundary()
    else: collect(args.effort)
