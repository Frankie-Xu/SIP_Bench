"""Run a deterministic end-to-end medical SIP-Bench demonstration."""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path
from sip_bench.adapters.medical import MedicalAdapter

def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('--cases',default='benchmarks/medical/cases.json'); ap.add_argument('--out',default='results/medical_demo'); a=ap.parse_args()
    adapter=MedicalAdapter(); tasks=adapter.discover_tasks(a.cases)
    m=adapter.build_manifest(tasks,replay_count=2,adapt_count=2,heldout_count=2,drift_count=2,seed=7); adapter.validate_manifest(m)
    by_id={t.task_id: t.metadata.get('clinical', {}) for t in tasks}; learned=set(); runs=[]
    def predict(case, phase):
        s=set(case.get('symptoms', []))
        if s & {'chest_pain','stroke_signs','severe_bleeding'}: return 'emergency' if 'chest_pain' in s or 'severe_bleeding' in s else 'urgent'
        if phase != 'T0' and case.get('diagnosis') in learned: return case['diagnosis']
        return 'unknown'
    for phase in ('T0','T1','T2'):
      if phase=='T1': learned.update(by_id[t.task_id]['diagnosis'] for t in m.adapt)
      for split in ('replay','adapt','heldout','drift'):
       for t in getattr(m,split):
        c=by_id[t.task_id]; pred=predict(c,phase); safe,reason=adapter.safety_gate(c,pred); success=pred==c['diagnosis'] and safe
        if split=='drift' and phase=='T2': success = success and c['diagnosis'] in learned
        runs.append({'schema_version':'0.1.0','run_id':f'medical::{phase}::{split}::{t.task_id}','benchmark_name':adapter.benchmark_name,'benchmark_version':'synthetic-v1','benchmark_split':split,'phase':phase,'path_type':'external','model_name':'deterministic-baseline','agent_name':'medical-rule-agent','agent_version':'0.1','task_id':t.task_id,'attempt_index':0,'score':1.0 if success else 0.0,'success':success,'token_input':120,'token_output':20,'token_total':140,'tool_calls_total':0,'memory_reads':1 if phase!='T0' else 0,'memory_writes':1 if split=='adapt' and phase=='T1' else 0,'wall_clock_seconds':0.01,'human_interventions':0,'seed':7,'started_at':datetime.now(timezone.utc).isoformat(),'finished_at':datetime.now(timezone.utc).isoformat(),'metadata':{'prediction':pred,'safety_gate_passed':safe,'failure_reason':reason or (None if success else 'wrong_or_unknown'),'patient_id':t.metadata.get('patient_id')}})
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True); (out/'runs.jsonl').write_text('\n'.join(json.dumps(r) for r in runs)+'\n'); (out/'manifest.json').write_text(json.dumps(m.to_dict(),indent=2)); print(f'wrote {len(runs)} runs to {out}')
if __name__=='__main__': main()
