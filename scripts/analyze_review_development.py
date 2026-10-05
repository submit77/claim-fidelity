#!/usr/bin/env python3
"""Report strict format outcomes separately from uniformly extracted decisions."""
import json
import re
import statistics
from run_review_development import OUT, digest, save

DECISIONS={'accept','reject','defer-insufficient-evidence','defer-out-of-scope'}
FIELDS={'decision','reason','boundary_cited','source_reference'}


def parse_answer(text):
    fenced=False
    try: answer=json.loads(text)
    except json.JSONDecodeError:
        match=re.fullmatch(r'\s*```(?:json)?\s*\n(.*?)\n```\s*',text,re.S)
        if not match: return None,False,False
        try: answer=json.loads(match.group(1)); fenced=True
        except json.JSONDecodeError: return None,False,False
    valid=(isinstance(answer,dict) and set(answer)==FIELDS and all(isinstance(x,str) for x in answer.values())
           and answer['decision'] in DECISIONS and len(answer['reason'].split())<=80)
    return answer if valid else None,valid and not fenced,valid and fenced


def main():
    frozen=OUT/'frozen'
    for path,expected in json.loads((frozen/'sha256.json').read_text(encoding='utf-8')).items():
        if digest((frozen/path).read_bytes())!=expected: raise RuntimeError('Frozen input drift')
    schedule=json.loads((frozen/'schedule.json').read_text(encoding='utf-8'))
    gold=json.loads((frozen/'gold.json').read_text(encoding='utf-8'))
    rows=[]; totals={}
    for vendor,folder,prefix in [('Cursor Composer 2.5','runs',''),('Grok Build 4.6 high (stopped)','grok-runs',''),('Grok Build 4.6 low','grok-runs','low-')]:
        for task in schedule:
            record=OUT/folder/(prefix+task['task_id'])/'summary.json'
            if not record.exists(): continue
            result=json.loads(record.read_text(encoding='utf-8'))
            answer,strict,fenced=parse_answer(result.get('answer') or '')
            boundary_ok=not result['tool_events'] and not result.get('existing_repo_read_paths',[])
            rows.append({**task,'vendor':vendor,'gold':gold[task['variant']]['decision'],
                 'decision':answer['decision'] if answer else None,'reason':answer['reason'] if answer else None,
                 'strict_format_valid':strict,'fenced_json_valid':fenced,
                 'transport_ok':result['transport_ok'],'observed_boundary_ok':boundary_ok,
                 'wall_seconds':result['wall_seconds'],'session_id':result['session_id'],
                 'usage':result['usage'],'reported_cost_usd':result.get('reported_cost_usd'),
                 'record':str(record.relative_to(OUT))})
        group=[r for r in rows if r['vendor']==vendor]
        if not group: continue
        answered=[r for r in group if r['transport_ok'] and r['decision'] is not None]
        warranted=[r for r in answered if r['gold']=='accept']; unsupported=[r for r in answered if r['gold']=='reject']
        totals[vendor]={'recorded':len(group),'planned':12,
            'transport_success':sum(r['transport_ok'] for r in group),
            'observed_boundary_pass':sum(r['observed_boundary_ok'] for r in group),
            'strict_format_valid':sum(r['strict_format_valid'] for r in group),
            'fenced_json_valid':sum(r['fenced_json_valid'] for r in group),
            'unscored_attempts':len(group)-len(answered),
            'diagnostic_correct_decisions':sum(r['decision']==r['gold'] for r in group),
            'warranted_accepted':sum(r['decision']=='accept' for r in warranted),'warranted_n':len(warranted),
            'unsupported_accepted':sum(r['decision']=='accept' for r in unsupported),'unsupported_n':len(unsupported),
            'wall_seconds_total':round(sum(r['wall_seconds'] for r in group),3),
            'wall_seconds_median':statistics.median(r['wall_seconds'] for r in group),
            'wall_seconds_min':min(r['wall_seconds'] for r in group),'wall_seconds_max':max(r['wall_seconds'] for r in group),
            'reported_cost_usd':sum(r['reported_cost_usd'] for r in group if r['reported_cost_usd'] is not None)
                if any(r['reported_cost_usd'] is not None for r in group) else None}
    known_sessions=[r['session_id'] for r in rows if r['session_id']]
    if len(set(known_sessions))!=len(known_sessions): raise RuntimeError('Repeated session')
    save(OUT/'results.json',{'status':'development-only; one independent construction',
        'strict_endpoint':'Every fenced JSON response fails the original format contract.',
        'diagnostic_endpoint':'Uniform exact outer-fence removal, added after first development response; separate from strict compliance.',
        'independent_base_recipes':1,'totals':totals,'rows':rows})
    lines=['# Development results','',
       'These are development observations from one constructed mathematical pair, presented in short and longer packets. They are not held-out estimates, independent replications across tasks, or evidence of general prevalence.','',
       'The decision table uses the separately disclosed diagnostic parser. Strict JSON compliance is reported below; removing an outer Markdown fence does not turn a format failure into a strict success.','',
       '| System | Presentation | Condition | Warranted claim | Unsupported claim |',
       '|---|---|---|---|---|']
    for vendor in totals:
        if '(stopped)' in vendor: continue
        for presentation in ('atomic','embedded'):
            for condition in 'ABC':
                group=[r for r in rows if r['vendor']==vendor and r['presentation']==presentation and r['condition']==condition]
                decisions={r['gold']:r['decision'] or 'unparseable' for r in group}
                lines.append(f"| {vendor} | {presentation} | {condition} | {decisions.get('accept','pending')} | {decisions.get('reject','pending')} |")
    lines+=['','A = ordinary review; B = explicit checklist; C = checklist plus source-derived ledger. Each cell contains one response.','',
            '| System | Transport | Strict JSON | Fenced JSON | Warranted accepted | Unsupported accepted | Median seconds |',
            '|---|---|---|---|---|---|---|']
    for vendor,t in totals.items():
        warranted=f"{t['warranted_accepted']}/{t['warranted_n']}" if t['warranted_n'] else 'no scored answers'
        unsupported=f"{t['unsupported_accepted']}/{t['unsupported_n']}" if t['unsupported_n'] else 'no scored answers'
        lines.append(f"| {vendor} | {t['transport_success']}/{t['recorded']} | {t['strict_format_valid']}/{t['recorded']} | {t['fenced_json_valid']}/{t['recorded']} | {warranted} | {unsupported} | {t['wall_seconds_median']:.1f} |")
    lines+=['','## Nonmatching diagnostic decisions','']
    for r in rows:
        if r['decision'] is not None and r['decision']!=r['gold']:
            lines.append(f"- {r['vendor']}, {r['presentation']}, {r['condition']}, `{r['task_id']}`: expected {r['gold']}; returned {r['decision']}. Raw record: `{r['record']}`. Reason: {r['reason']}")
    lines+=['','## Interpretation limits','',
       '- Treat repeated conditions and the two presentations as observations of one recipe, not new independent cases.',
       '- No confidence interval or general treatment-effect estimate is warranted from this unit.',
       '- The longer packet adds framing as well as length; this is not a pure length intervention.',
       '- Labels have Lean witnesses or negations and restricted prose bindings, but no independent human audit has occurred.',
       '- Boundary evidence covers fresh local contexts, permission controls, and observed calls. It does not certify an OS sandbox or reveal provider-side prompts and routing.',
       '- Cursor loads built-in skills and account plugin definitions. These inputs are part of the evaluated harness; observed context-file hashes are retained.',
       '- Grok and Cursor use different harnesses and controls. Their difference cannot be attributed solely to base-model weights.',
       '- Provider labels are recorded interface identities, not immutable weight snapshots.',
       '- Runtime accounting is not independently verified billing; a short burst does not establish sustained quota.',
       '- All attempts remain recorded. The first formatting failure stopped collection; the documented amendment allowed the remaining unchanged prompts, without retries.','']
    lines+=['The initial Grok high-reasoning attempt timed out at 90 seconds without a final answer. It is unscored and remains in the transport table. The separately labelled low-reasoning series uses all 12 frozen prompts and a uniform 120-second limit. Thought-stream fragments are never substituted for final answers.','']
    (OUT/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(totals,indent=2))


if __name__=='__main__': main()
