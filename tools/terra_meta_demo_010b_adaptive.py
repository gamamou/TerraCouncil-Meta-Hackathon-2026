"""DEMO-010B: adaptive model-selected FAITH research, scientific coverage gates.
No Python rehabilitation matching or rankings. No silent retries of Meta calls.
"""
import argparse, hashlib, json, os, re
from pathlib import Path
from council import meta_call, SPARK, WONDER
from terra_demo_001_faith_gateway import Gateway, invoke, load
from tools.terra_demo_003_preflight import preflight
from tools.terra_meta_demo_009_autonomous import extract_action, RULES

ALLOWED=("PilotCandidate","MiningPermit","RehabilitationSolution","PermitSpatialContext","SiteRehabilitationRecommendation")
def coverage(data,observations,question):
    read={o["action"].get("entity") for o in observations if o["action"]["tool"] in ("query_faith_data","get_faith_record") and o["result"]}
    required={"MiningPermit","PilotCandidate"}
    if any(s in question.lower() for s in ("rehabilit","réhabilit","intervention","solution")):
        required.add("RehabilitationSolution")
    available={x for x in required if data.get(x)}
    return {"required_available":sorted(available),"consulted":sorted(read),
            "missing_required":sorted(available-read),
            "unavailable_sources":sorted(x for x in ALLOWED if not data.get(x)),
            "is_complete":not bool(available-read)}

def parse_decision(raw):
    # JSON object may include stop with explanation; strict authorization for tool calls
    if isinstance(raw,str):
        try:return extract_action(raw)
        except ValueError:
            i=raw.find("{")
            if i<0:raise
            obj,_=json.JSONDecoder().raw_decode(raw[i:])
    elif isinstance(raw,dict):obj=raw
    else:raise ValueError("Invalid tool-choice format")
    if isinstance(obj,dict) and obj.get("tool")=="finish_research" and isinstance(obj.get("reason"),str):
        return {"tool":"finish_research","reason":obj["reason"][:500]}
    raise ValueError("Unsupported tool or finish decision")

def run(data,question,key,path,caller=meta_call,max_lookups=5):
    if not 1<=max_lookups<=8:raise ValueError("max_lookups must be 1..8")
    pf=preflight(data)
    if pf["status"]!="READY_FOR_EXPLORATORY_MUSE_DEMO":raise ValueError("FAITH preflight failed")
    gateway=Gateway(data)
    digest=hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    state={"schema_version":"010B","status":"STARTED_DO_NOT_AUTORETRY",
           "snapshot_sha256":digest,"question":question,"max_lookups":max_lookups,"steps":[]}
    def save():path.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf8")
    def call(stage,model,instruction,payload):
        state["pending"]=stage;save()
        answer=caller(model,instruction,payload,key)
        if not isinstance(answer,str) or not answer.strip():raise ValueError("Empty model reply")
        state["steps"].append({"stage":stage,"model":model,"response":answer})
        state.pop("pending",None);save()
        return answer
    save()
    try:
        plan=call("SPARK_RESEARCH_PLAN",SPARK,
          RULES+" Plan essential FAITH entities for this question. Do not choose final sites yet.",
          {"question":question,"available":gateway.discover_faith_data()})
        observations=[];seen=set()
        for n in range(max_lookups):
            cov=coverage(data,observations,question)
            instruction=(RULES+
             '\nRespond with ONLY a JSON tool decision. Options: {"tool":"query_faith_data","entity":"MiningPermit","limit":50}; '
             '{"tool":"get_faith_record","entity":"MiningPermit","identifier":"GUIDSHAPE:..."}; '
             '{"tool":"discover_faith_data"}; {"tool":"finish_research","reason":"..."} . '
             "Other allowed entities: PilotCandidate, RehabilitationSolution, PermitSpatialContext, SiteRehabilitationRecommendation. "
             "Do not request an already completed query. Read available essential source entities before finishing. "
             "Never claim unavailable evidence exists.")
            raw=call("SPARK_TOOL_CHOICE_"+str(n+1),SPARK,instruction,
             {"question":question,"plan":plan,"coverage":cov,
              "previous_actions":[o["action"] for o in observations],
              "previous_results":observations})
            action=parse_decision(raw)
            if action["tool"]=="finish_research":
                if cov["missing_required"] and n<max_lookups-1:
                    state["steps"].append({"stage":"COVERAGE_GATE_REJECTED_STOP",
                      "reason":"available required entities unconsulted","missing":cov["missing_required"]});save()
                    continue
                state["steps"].append({"stage":"RESEARCH_STOP","reason":action["reason"]});save()
                break
            if action.get("entity") and action["entity"] not in ALLOWED:raise ValueError("Disallowed entity")
            signature=json.dumps(action,sort_keys=True)
            if signature in seen:
                state["steps"].append({"stage":"DUPLICATE_TOOL_REQUEST_BLOCKED","action":action});save()
                continue
            seen.add(signature)
            result=invoke(gateway,action)
            observations.append({"action":action,"result":result})
            state["steps"].append({"stage":"FAITH_TOOL_RESULT_"+str(len(observations)),
                                  "action":action,"result":result});save()
        cov=coverage(data,observations,question)
        state["coverage"]=cov;save()
        critique=call("WONDER_CRITIQUE",WONDER,RULES+
          " Critically review tool results, coverage gaps, top-five selection bias, and site-vs-catalog evidence. No invented facts.",
          {"question":question,"plan":plan,"observations":observations,"coverage":cov})
        final=call("SPARK_REVISION",SPARK,RULES+
          " Answer the user's request while addressing Wonder; decline unsupported final priorities. "
          "Make conditional investigation recommendations only; avoid presenting catalog items as site-specific prescriptions.",
          {"question":question,"plan":plan,"observations":observations,
           "coverage":cov,"wonder":critique})
        sites={r.get("shape_uid") for t in ("MiningPermit","PilotCandidate") for r in data.get(t,[])}
        sols={r.get("solution_id") for r in data.get("RehabilitationSolution",[])}
        site_refs=set(re.findall(r"GUIDSHAPE:[A-Z0-9-]+",final))
        sol_refs=set(re.findall(r"SOL-CAT-[0-9]{5}",final))
        state["citation_check"]={"unknown_site_ids":sorted(site_refs-sites),
          "unknown_solution_ids":sorted(sol_refs-sols),
          "site_ids_cited":len(site_refs),"solution_ids_cited":len(sol_refs)}
        state["status"]="GENERATED_NEEDS_SCIENTIFIC_REVIEW"
        save()
    except Exception as exc:
        state["status"]="INTERRUPTED_DO_NOT_AUTORETRY"
        state["error_type"]=type(exc).__name__
        state["error_message"]=str(exc)[:300]
        save()
    return state

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--snapshot",required=True);p.add_argument("--question",required=True)
    p.add_argument("--output",required=True);p.add_argument("--max-lookups",type=int,default=5)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args();data=load(a.snapshot)
    if not a.execute:
        print(json.dumps({"mode":"PREVIEW_NO_META_CALLS","preflight":preflight(data)["status"],
          "maximum_calls":a.max_lookups+3,"starting_coverage":coverage(data,[],a.question)},
          ensure_ascii=False,indent=2));return
    if not os.environ.get("MODEL_API_KEY"):raise SystemExit("MODEL_API_KEY missing")
    target=Path(a.output);target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():raise SystemExit("Refusing to overwrite existing trace")
    target.write_text('{"status":"RESERVED_DO_NOT_AUTORETRY"}',encoding="utf8")
    result=run(data,a.question,os.environ["MODEL_API_KEY"],target,max_lookups=a.max_lookups)
    print(json.dumps({"status":result["status"],"coverage":result.get("coverage"),
      "citation_check":result.get("citation_check"),"output":str(target)},ensure_ascii=False))
    if result["status"]!="GENERATED_NEEDS_SCIENTIFIC_REVIEW":raise SystemExit(2)
if __name__=="__main__":main()
