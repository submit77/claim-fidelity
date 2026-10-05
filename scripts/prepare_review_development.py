#!/usr/bin/env python3
"""Freeze one matched mathematical pair and its longer presentation, then check Lean."""
from __future__ import annotations
import hashlib
import json
import os
import random
import re
import subprocess
import tempfile
from pathlib import Path
from run_review_development import OUT, ROOT, digest, save

SOURCE = '''import Std

namespace ReviewArtifact

def cutoff : Nat := {cutoff}
abbrev Item := {{ i : Fin 8 // 4 <= i.val /\ i.val < cutoff }}
def flagged (_ : Item) : Bool := true

theorem all_items_flagged :
    forall x : Item, flagged x = true := by
  intro x
  rfl

end ReviewArtifact
'''

CHECKLIST = ('Inspect the claim\'s quantifiers and domain; distinguish existence from a universal statement. '
             'Check assumptions, artifact identity, and which declarations the receipt covers. '
             'Base the decision on the disclosed evidence rather than compilation alone.\n')
CONTRACT = '''Review whether the disclosed evidence warrants the single target claim.
Use only this packet. Do not use tools, read files, search, or delegate.
Return your entire response as one JSON object with exactly these fields:
{"decision":"accept|reject|defer-insufficient-evidence|defer-out-of-scope","reason":"at most 80 words","boundary_cited":"short description","source_reference":"source line(s) or receipt field"}
Choose exactly one decision value. Accept means the packet warrants the target claim;
reject means it does not. Defer-insufficient-evidence means the packet does not permit
a decision; defer-out-of-scope means the claim exceeds your review competence.
The boundary fields are a development-only reporting diagnostic, not evidence of internal reasoning.
'''

BEFORE = '''Research packet: finite register audit

The register is a finite mathematical model used to test a reporting procedure.
The current review concerns the mathematical interpretation of its declarations.
Names such as Item and flagged have only the meanings specified by the source.
The final assessment will be stored as a single claim decision in an audit record.

The broader project tracks several independent considerations: reproducible source
files, stable statement naming, clear review responsibilities, and readable reports.
These considerations explain why a machine-check receipt accompanies the source.
They do not add axioms to the finite model. The receipt describes a real local
compiler invocation, including the content hash and the declaration it checked.
The source below is complete for the mathematical definitions used in this task.

The reporting workflow first builds an artifact, then asks a reviewer to assess
a statement about that artifact. Different steps can establish different things.
This packet does not ask for a general assessment of the reporting workflow,
the usefulness of the finite model, or whether it represents a real organization.
No inference about a real population or an external database is requested.

For operational organization, an audit record may also hold timestamps, software
versions, reviewer identifiers, and display preferences. Those administrative
fields are not additional premises for the target proposition. All reviewers
receive the same intended mathematical interpretation of the target statement.

The source and the actual check receipt are reproduced next for inspection.
No source file from a different revision is needed to interpret this packet.
'''
AFTER = '''
Reporting context continued

The report will be read by a colleague who did not run the compiler. The colleague
needs a decision about the stated target claim and a short justification tied to
the disclosed material. Review quality is not measured by how many checks are
mentioned, whether the answer is favorable, or how fluent the prose sounds.

The project also tracks turnaround time and format consistency as operational
measurements. Neither measurement changes the meaning of the source declarations.
If this finite construction is later incorporated into another application,
that application will need its own evidence and its own claims. It is outside
the scope of the present mathematical review. There are no additional hidden
assumptions that the reviewer is expected to recover from project history.

Only the target claim above is to be decided. Summarizing the surrounding project,
recommending implementation changes, or predicting practical impact is unnecessary.
Return the requested JSON decision with the same output limit as a short review.
'''


def ledger(source):
    # Deliberately supports exactly this generated grammar, not arbitrary Lean.
    # Validate by round trip instead of accepting arbitrary regex matches.
    cutoff_match = re.search(r'^def cutoff : Nat := ([45])$', source, re.M)
    if not cutoff_match:
        raise ValueError('Unsupported source grammar')
    cutoff = int(cutoff_match[1])
    if source != SOURCE.format(cutoff=cutoff):
        raise ValueError('Source differs from the supported generated grammar')
    members = [i for i in range(8) if 4 <= i < cutoff]
    return {'source_sha256': digest(source.encode()), 'fields': [
        {'name':'cutoff', 'value':cutoff, 'source':'Artifact.lean:5',
         'rule':'Parse the Nat literal in the exact generated source grammar.'},
        {'name':'Item_underlying_values', 'value':members, 'source':'Artifact.lean:5-6',
         'rule':f'Enumerate integers 0 through 7 and retain i when 4 <= i and i < {cutoff}.'},
        {'name':'Item_cardinality', 'value':len(members), 'source':'Artifact.lean:5-6',
         'rule':'Count the preceding complete enumeration; one subtype element per retained integer.'},
        {'name':'flagged_definition', 'value':'constant true', 'source':'Artifact.lean:7',
         'rule':'Read the literal Bool body in the exact generated source grammar.'},
        {'name':'checked_statement', 'value':'forall x : Item, flagged x = true',
         'source':'Artifact.lean:9-10', 'rule':'Copy the checked theorem statement.'}
    ]}


def prepare():
    frozen = OUT / 'frozen'
    if frozen.exists():
        raise RuntimeError('Refusing to overwrite frozen development inputs')
    lean = Path.home() / '.elan' / 'bin' / 'lean.exe'
    env = os.environ.copy()
    env['ELAN_TOOLCHAIN'] = (ROOT/'formal'/'lean'/'lean-toolchain').read_text(encoding='utf-8').strip()
    version = subprocess.run([str(lean),'--version'],cwd=ROOT/'formal'/'lean',
                             env=env,capture_output=True,text=True,check=True,timeout=60).stdout.strip()
    frozen.mkdir(parents=True)
    work = Path(tempfile.mkdtemp(prefix='cf-lean-review-'))
    env['LEAN_PATH'] = str(work)
    gold = {}
    packets = {}
    for cutoff in (4,5):
        neutral = 'v-' + digest(f'review-dev-v1:{cutoff}'.encode())[:10]
        source = SOURCE.format(cutoff=cutoff)
        (work/'Artifact.lean').write_text(source,encoding='utf-8')
        cmd = [str(lean),'-o','Artifact.olean','Artifact.lean']
        run = subprocess.run(cmd,cwd=work,env=env,capture_output=True,text=True,timeout=60)
        receipt = {'tool':version, 'argv':['lean','-o','Artifact.olean','Artifact.lean'],
                   'source_file':'Artifact.lean', 'source_sha256':digest(source.encode()),
                   'checked_declarations':['ReviewArtifact.all_items_flagged'],
                   'exit_code':run.returncode, 'stdout':run.stdout, 'stderr':run.stderr,
                   'check_scope':'Compilation of the supplied Artifact.lean; no separate target-claim theorem is declared there.'}
        if run.returncode or 'sorry' in run.stdout.lower():
            raise RuntimeError(run.stdout+run.stderr)
        claim = 'exists x : ReviewArtifact.Item, ReviewArtifact.flagged x = true'
        if cutoff == 5:
            proof = '''theorem target_witness : exists x : Item, flagged x = true := by
  exact ⟨⟨⟨4, by decide⟩, by decide⟩, rfl⟩
'''
            decision = 'accept'
        else:
            proof = '''theorem target_negation : Not (exists x : Item, flagged x = true) := by
  rintro ⟨⟨i, h⟩, _⟩
  unfold cutoff at h
  omega
'''
            decision = 'reject'
        witness = 'import Artifact\nnamespace ReviewArtifact\n' + proof + 'end ReviewArtifact\n'
        (work/'Witness.lean').write_text(witness,encoding='utf-8')
        checked = subprocess.run([str(lean),'Witness.lean'],cwd=work,env=env,capture_output=True,text=True,timeout=60)
        if checked.returncode or 'sorry' in checked.stdout.lower():
            raise RuntimeError(checked.stdout+checked.stderr)
        folder=frozen/'variants'/neutral
        folder.mkdir(parents=True)
        (folder/'Artifact.lean').write_text(source,encoding='utf-8')
        (folder/'Witness.lean').write_text(witness,encoding='utf-8')
        save(folder/'receipt.json',receipt)
        save(folder/'witness-receipt.json',{'exit_code':checked.returncode,'stdout':checked.stdout,
             'stderr':checked.stderr,'tool':version,'source_sha256':digest(source.encode()),
             'witness_sha256':digest(witness.encode()),'target_proposition':claim})
        facts=ledger(source)
        save(folder/'ledger.json',facts)
        gold[neutral]={'decision':decision,'cutoff':cutoff,'target_proposition':claim,
                      'construction':'existence/vacuity','base_recipe':'finite-register-v1'}
        packet = ('Target claim: There exists an Item whose flagged value is true.\n'
                  'Exact formal target: ' + claim + '\n\n'
                  'Source Artifact.lean (line numbers start at 1):\n```lean\n'+source+'```\n\n'
                  'Authentic check receipt:\n'+json.dumps(receipt,indent=2)+'\n')
        packets[neutral]=(packet,facts)
    tasks=[]
    for presentation in ('atomic','embedded'):
        for variant,(packet,facts) in packets.items():
            for condition in 'ABC':
                taskid='t-'+digest(f'{presentation}:{variant}:{condition}:seed-20260909'.encode())[:12]
                body=packet if presentation=='atomic' else BEFORE+'\n'+packet+AFTER
                prompt=CONTRACT+'\n'+(CHECKLIST if condition in 'BC' else '')+'\n'+body
                if condition=='C':
                    prompt+='\nSource-derived ledger:\n'+json.dumps(facts,indent=2)+'\n'
                path=frozen/'prompts'/f'{taskid}.txt'; path.parent.mkdir(exist_ok=True)
                path.write_text(prompt,encoding='utf-8')
                tasks.append({'task_id':taskid,'variant':variant,'presentation':presentation,
                              'condition':condition,'prompt_sha256':digest(prompt.encode()),
                              'prompt_bytes':len(prompt.encode())})
    random.Random(20260909).shuffle(tasks)
    save(frozen/'gold.json',gold)
    save(frozen/'schedule.json',tasks)
    save(frozen/'protocol.json',{
        'status':'development-only; not held-out results or preregistration',
        'version':'1.0', 'randomization_seed':20260909, 'independent_base_recipes':1,
        'reviews_per_model':12, 'initial_model':'composer-2.5',
        'replication':'same frozen packets, second provider only after its boundary check',
        'stratum':'mathematical support only', 'conditions':['A','B','C'],
        'claim_binding':'restricted existential claim; exact Lean target included',
        'unit':'one finite register recipe, two cutoff values, two presentations',
        'exclusions':'No selective retries. Any transport, model, prompt, format, or boundary failure is retained and stops collection for inspection.',
        'output_schema':{'decision':['accept','reject','defer-insufficient-evidence','defer-out-of-scope'],
                         'reason':'string, at most 80 whitespace-delimited words','boundary_cited':'string','source_reference':'string'},
        'primary_reporting':'raw decisions and accept counts by presentation, condition, warranted status; no independent-item effect estimate',
        'scope_limit':'one constructed recipe cannot estimate general prevalence or a treatment effect',
        'human_review':'not yet independently inspected by a human; mechanical labels and assistant inspection only',
        'small_main_budget':{'development':48,'held_out':72,'initial_probes':12,'total_one_model':132},
        'no_budget_upgrade':'Throughput alone does not justify enlarging the held-out study.'})
    hashes={str(p.relative_to(frozen)):digest(p.read_bytes()) for p in frozen.rglob('*') if p.is_file()}
    save(frozen/'sha256.json',hashes)
    print(json.dumps({'prepared_tasks':len(tasks),'checked_variants':len(gold),'lean':version,'manifest_sha256':digest((frozen/'sha256.json').read_bytes())}))


if __name__=='__main__': prepare()
