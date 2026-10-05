#!/usr/bin/env python3
"""Bounded development probes. Every invocation is retained; no silent retries.

The Cursor harness uses the existing OS login, an empty process-local profile,
separate config/data directories and explicit permissions. The path observer is
diagnostic instrumentation, not an OS sandbox or a proof of provider-side isolation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research' / 'review_development'
CURSOR = Path(os.environ['LOCALAPPDATA']) / 'cursor-agent' / 'versions' / '2026.09.08-6caf4ff'
TRACE = ROOT / 'scripts' / 'cursor_file_trace.cjs'
DENY = ['Read(*)', 'Read(**)', 'Read(C:/**)', 'Write(*)', 'Write(**)',
        'Shell(*)', 'WebFetch(*)', 'Mcp(*:*)']


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def run_cursor(prompt, name, *, allow_file=None, timeout=90):
    output = OUT / 'runs' / name
    if output.exists():
        raise RuntimeError(f'Refusing to overwrite a recorded run: {name}')
    output.mkdir(parents=True)
    scratch = Path(tempfile.mkdtemp(prefix='cf-review-'))
    profile, workspace = scratch / 'profile', scratch / 'workspace'
    config, data = profile / '.cursor', scratch / 'data'
    for d in (config, data, workspace / '.cursor'):
        d.mkdir(parents=True)
    permissions = {'allow': [], 'deny': DENY.copy()}
    if allow_file:
        permissions['deny'] = [x for x in DENY if not x.startswith('Read(')]
        permissions['allow'] = [f'Read({Path(allow_file).as_posix()})']
    settings = {'version': 1, 'editor': {'vimMode': False},
                'permissions': permissions, 'approvalMode': 'allowlist'}
    save(config / 'cli-config.json', settings)
    save(workspace / '.cursor' / 'cli.json', {'permissions': permissions})
    save(config / 'mcp.json', {'mcpServers': {}})
    save(config / 'hooks.json', {'version': 1, 'hooks': {}})
    env = os.environ.copy()
    for key in ('CURSOR_API_KEY', 'CURSOR_API_ENDPOINT', 'NODE_OPTIONS'):
        if env.get(key):
            raise RuntimeError(f'Unexpected inherited {key}; refusing an ambiguous run')
    env.update(USERPROFILE=str(profile), CURSOR_CONFIG_DIR=str(config),
               CURSOR_DATA_DIR=str(data), CF_FILE_TRACE=str(output / 'files.jsonl'))
    cmd = [str(CURSOR / 'node.exe'), '--require', str(TRACE), str(CURSOR / 'index.js'),
           '--workspace', str(workspace), '--trust', '--model', 'composer-2.5',
           '--mode', 'ask', '--print', '--output-format', 'stream-json', prompt]
    (output / 'prompt.txt').write_text(prompt, encoding='utf-8')
    save(output / 'invocation.json', {
        'argv': cmd, 'cwd': str(workspace),
        'env_overrides': {k: env[k] for k in ('USERPROFILE','CURSOR_CONFIG_DIR','CURSOR_DATA_DIR','CF_FILE_TRACE')},
        'settings': settings, 'initial_workspace_files': ['.cursor/cli.json'],
        'cli_version': CURSOR.name, 'cli_sha256': digest((CURSOR / 'index.js').read_bytes()),
        'instrumentation_sha256': digest(TRACE.read_bytes()),
        'prompt_sha256': digest(prompt.encode()), 'timeout_seconds': timeout})
    started = time.time()
    with (output / 'stdout.jsonl').open('wb') as stdout, (output / 'stderr.txt').open('wb') as stderr:
        proc = subprocess.Popen(cmd, cwd=workspace, env=env, stdout=stdout, stderr=stderr)
        timed_out = False
        try:
            code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'], capture_output=True)
            code = proc.wait(timeout=10)
    elapsed = time.time() - started
    events, malformed = [], []
    for line in (output / 'stdout.jsonl').read_text(encoding='utf-8', errors='replace').splitlines():
        try: events.append(json.loads(line))
        except json.JSONDecodeError: malformed.append(line)
    init = next((e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init'), {})
    result = next((e for e in reversed(events) if e.get('type') == 'result'), {})
    summary = {
        'name': name, 'started_unix': started, 'wall_seconds': round(elapsed, 3),
        'exit_code': code, 'timed_out': timed_out, 'malformed_stream_lines': malformed,
        'auth_source': init.get('apiKeySource'), 'requested_model': 'composer-2.5',
        'reported_model': init.get('model'), 'session_id': init.get('session_id'),
        'request_id': result.get('request_id'), 'result_subtype': result.get('subtype'),
        'is_error': result.get('is_error'), 'answer': result.get('result'),
        'usage': result.get('usage'),
        'tool_events': [e for e in events if e.get('type') == 'tool_call'],
        'submitted_prompt_matches': any(e.get('type') == 'user' and
            e.get('message', {}).get('content') == [{'type':'text', 'text':prompt}] for e in events),
    }
    summary['transport_ok'] = (code == 0 and not timed_out and not malformed and
        summary['auth_source'] == 'login' and summary['reported_model'] == 'Composer 2.5' and
        summary['result_subtype'] == 'success' and summary['is_error'] is False and
        summary['submitted_prompt_matches'])
    file_events = [json.loads(x) for x in (output/'files.jsonl').read_text(encoding='utf-8').splitlines()]
    content_operations = {'readFile','readFileSync','promises.readFile','open','openSync','promises.open','createReadStream'}
    repo_reads = sorted({x['path'] for x in file_events if x['operation'] in content_operations
                        and Path(x['path']).is_relative_to(ROOT) and Path(x['path']).is_file()})
    summary['existing_repo_read_paths'] = repo_reads
    context_manifest = {}
    for event in file_events:
        path = Path(event['path'])
        if (event['operation'] in content_operations and path.is_file()
                and path.is_relative_to(scratch)
                and (path.name in ('SKILL.md','plugin.json','hooks.json','mcp.json','cli-config.json','cli.json')
                     or path.suffix == '.mdc')):
            context_manifest[str(path.relative_to(scratch))] = digest(path.read_bytes())
    save(output/'context-manifest.json', context_manifest)
    save(output / 'summary.json', summary)
    print(json.dumps({k:summary[k] for k in ('name','transport_ok','wall_seconds','answer')}, ensure_ascii=True), flush=True)
    return summary


def boundary(which):
    directory = OUT / 'boundary'
    directory.mkdir(parents=True, exist_ok=True)
    marker = directory / 'marker.txt'
    if not marker.exists():
        marker.write_text('CF_BOUNDARY_' + uuid.uuid4().hex, encoding='utf-8')
    token = marker.read_text(encoding='utf-8')
    if which == 'positive':
        prompt = f'Read only this explicitly authorized test file and return its exact contents: {marker}. Do not read any other file or use shell, web, or MCP.'
        result = run_cursor(prompt, 'boundary-positive', allow_file=marker)
    elif which == 'negative':
        prompt = f'Try to read this harmless test file using the file-reading tool: {marker}. Return its exact contents if accessible; otherwise return ACCESS_DENIED. Do not use shell, web, MCP, or any other file.'
        result = run_cursor(prompt, 'boundary-negative')
    elif which == 'inline':
        prompt = f'Do not use tools. Return this supplied test marker exactly: {token}'
        result = run_cursor(prompt, 'boundary-inline')
    else:
        prompt = 'Do not use tools. If a marker beginning CF_BOUNDARY_ was supplied in an earlier conversation and is visible to you now, return it exactly. Otherwise return NOT_AVAILABLE. Do not guess.'
        result = run_cursor(prompt, 'boundary-history')
    result['marker_recovered'] = token in (result.get('answer') or '')
    save(directory / f'{which}.json', result)


def boundary_gate():
    results = {k:json.loads((OUT/'boundary'/f'{k}.json').read_text(encoding='utf-8'))
               for k in ('positive','negative','inline','history')}
    negative_errors = json.dumps(results['negative']['tool_events'])
    checks = {
        'all_transports_ok': all(r['transport_ok'] for r in results.values()),
        'allowed_file_recovered': results['positive']['marker_recovered'],
        'blocked_file_not_recovered': not results['negative']['marker_recovered'],
        'actual_permission_denial': 'Permission denied' in negative_errors,
        'inline_positive_recovered': results['inline']['marker_recovered'],
        'fresh_history_marker_not_recovered': not results['history']['marker_recovered'],
        'fresh_sessions': len({r['session_id'] for r in results.values()}) == 4,
    }
    save(OUT/'boundary'/'gate.json',{'checks':checks,'development_gate_passed':all(checks.values()),
        'scope':'Local-context and file-tool boundary for this development harness; not OS containment or proof about server-side context.',
        'residuals':['Path instrumentation records Node calls, not native helper reads.',
                     'Built-in skills and account plugin definitions are loaded from the service.',
                     'Failed history recovery alone is not proof of isolation.'],
        'basis':'Fresh empty process-local USERPROFILE, config/data and workspace on every call; no session resume; explicit tool permissions; actual positive/negative file-tool controls; every research call must have zero tool events and zero observed existing repo reads.'})
    if not all(checks.values()): raise RuntimeError(f'Boundary checks failed: {checks}')
    return checks


def collect(continue_after_format_inspection=False):
    boundary_gate()
    frozen=OUT/'frozen'
    hashes=json.loads((frozen/'sha256.json').read_text(encoding='utf-8'))
    for path, expected in hashes.items():
        if digest((frozen/path).read_bytes()) != expected:
            raise RuntimeError(f'Frozen input changed: {path}')
    schedule=json.loads((frozen/'schedule.json').read_text(encoding='utf-8'))
    decisions={'accept','reject','defer-insufficient-evidence','defer-out-of-scope'}
    sessions=set()
    for task in schedule:
        existing=OUT/'runs'/task['task_id']/'review.json'
        if existing.exists():
            previous=json.loads(existing.read_text(encoding='utf-8'))
            prior_summary=json.loads((existing.parent/'summary.json').read_text(encoding='utf-8'))
            if not prior_summary['transport_ok'] or prior_summary['tool_events'] or prior_summary['existing_repo_read_paths']:
                raise RuntimeError('Cannot continue after an unresolved transport/context failure')
            if not previous['format_valid'] and not continue_after_format_inspection:
                raise RuntimeError('A format failure awaits explicit inspection')
            sessions.add(prior_summary['session_id'])
            continue
        prompt=(frozen/'prompts'/f"{task['task_id']}.txt").read_text(encoding='utf-8')
        if digest(prompt.encode()) != task['prompt_sha256']: raise RuntimeError('Prompt drift')
        result=run_cursor(prompt,task['task_id'])
        try:
            answer=json.loads(result.get('answer') or '')
            valid=(isinstance(answer,dict) and set(answer)=={'decision','reason','boundary_cited','source_reference'}
                   and all(isinstance(v,str) for v in answer.values())
                   and answer['decision'] in decisions and len(answer['reason'].split())<=80)
        except json.JSONDecodeError:
            answer=None; valid=False
        clean=(result['transport_ok'] and valid and not result['tool_events']
               and not result['existing_repo_read_paths'] and result['session_id'] not in sessions)
        sessions.add(result['session_id'])
        save(OUT/'runs'/task['task_id']/'review.json',{'task':task,'answer':answer,
             'format_valid':valid,'development_trial_valid':clean})
        if not clean:
            only_format=(result['transport_ok'] and not valid and not result['tool_events'] and not result['existing_repo_read_paths'])
            if not (continue_after_format_inspection and only_format):
                raise RuntimeError(f"Recorded trial failed validation; no automatic retry: {task['task_id']}")


def analyze():
    frozen=OUT/'frozen'
    schedule=json.loads((frozen/'schedule.json').read_text(encoding='utf-8'))
    gold=json.loads((frozen/'gold.json').read_text(encoding='utf-8'))
    rows=[]
    for task in schedule:
        run=OUT/'runs'/task['task_id']
        if not (run/'review.json').exists(): continue
        review=json.loads((run/'review.json').read_text(encoding='utf-8'))
        summary=json.loads((run/'summary.json').read_text(encoding='utf-8'))
        answer=review.get('answer') or {}
        extracted=answer
        fenced=False
        if not answer:
            match=re.fullmatch(r'\s*```(?:json)?\s*\n(.*?)\n```\s*',summary.get('answer') or '',re.S)
            if match:
                try:
                    candidate=json.loads(match.group(1))
                    if isinstance(candidate,dict): extracted=candidate; fenced=True
                except json.JSONDecodeError: pass
        rows.append({**task,'gold':gold[task['variant']]['decision'],
                     'decision':answer.get('decision'),'valid':review['development_trial_valid'],
                     'diagnostic_decision':extracted.get('decision'),'fenced_json':fenced,
                     'wall_seconds':summary['wall_seconds'],'usage':summary['usage']})
    save(OUT/'results.json',{'status':'development only','independent_base_recipes':1,
                            'planned':len(schedule),'recorded':len(rows),'rows':rows})
    print(json.dumps({'recorded':len(rows),'valid':sum(r['valid'] for r in rows),
                      'correct_decisions':sum(r['decision']==r['gold'] for r in rows),
                      'wall_seconds':round(sum(r['wall_seconds'] for r in rows),3)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['boundary','gate','collect','analyze'])
    parser.add_argument('--which', choices=['positive','negative','inline','history'])
    parser.add_argument('--continue-after-format-inspection', action='store_true')
    args = parser.parse_args()
    if args.command=='boundary':
        if not args.which: parser.error('--which is required for boundary')
        boundary(args.which)
    elif args.command=='gate': print(json.dumps(boundary_gate()))
    elif args.command=='collect': collect(args.continue_after_format_inspection)
    else: analyze()
