"""DEMO-009 — Meta Spark chooses read-only FAITH tools before Wonder critique.
Bounded 5 Meta calls: Spark plan + two tool-choice turns + Wonder + Spark revision.
Each response is checkpointed; no automatic retry after interruption.
"""
import argparse, json, os, hashlib, re
from pathlib import Path
from council import meta_call, SPARK, WONDER
from terra_demo_001_faith_gateway import Gateway, load, invoke
from tools.terra_demo_003_preflight import preflight

TOOLS = """Allowed JSON action: {"tool":"discover_faith_data"} or
{"tool":"query_faith_data","entity":"MiningPermit","limit":50} or
{"tool":"get_faith_record","entity":"MiningPermit","identifier":"GUIDSHAPE:..."}.
Allowed entities: PilotCandidate, MiningPermit, PermitSpatialContext,
RehabilitationSolution, SiteRehabilitationRecommendation.
You choose tools according to the user question; no Python scientific ranking.
Return exactly one JSON object and nothing else."""
RULES = """You are TerraCouncil using FAITH screened information, not field-validated facts.
Never invent site-level degradation, geolocation, overlap, or water distances.
A screening score is not confidence of damage. Thirty sites share score 100.
Catalog solutions are not site prescriptions. All recommendations provisional.
Respond in French; cite exact shape_uid and solution_id when relevant."""
def extract_action(raw):
 if isinstance(raw,dict): obj=raw
 elif isinstance(raw,str):
  text=raw.strip()
  try: obj=json.loads(text)
  except json.JSONDecodeError:
   start=text.find("{")
   if start<0:raise ValueError("Model produced no JSON action")
   try:obj,_=json.JSONDecoder().raw_decode(text[start:])
   except json.JSONDecodeError:raise ValueError("Invalid JSON action") from None
 else:raise ValueError("Unexpected model output")
 if not isinstance(obj,dict) or obj.get("tool") not in ("discover_faith_data","query_faith_data","get_faith_record"):
  raise ValueError("Unauthorized or malformed tool action")
 return obj

def run(data,question,key,path,caller=meta_call):
 if preflight(data)["status"]!="READY_FOR_EXPLORATORY_MUSE_DEMO":
  raise ValueError("FAITH preflight failed")
 gateway=Gateway(data)
 state={"status":"STARTED_DO_NOT_AUTORETRY","question":question,"steps":[]}
 def save():path.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf8")
 save()
 def call(label,model,instruction,payload):
  state["pending"]=label;save()
  answer=caller(model,instruction,payload,key)
  if not isinstance(answer,str) or not answer.strip():raise ValueError("Empty Meta response")
  state["steps"].append({"stage":label,"model":model,"response":answer})
  state.pop("pending",None);save()
  return answer
 try:
  agenda=call("SPARK_RESEARCH_PLAN",SPARK,RULES+" Identify in prose which FAITH sources you need and why. Do not decide the final five yet.",
              {"question":question,"discovery":gateway.discover_faith_data()})
  observations=[]
  for n in range(2):
   raw=call("SPARK_TOOL_CHOICE_"+str(n+1),SPARK,RULES+" "+TOOLS,
            {"question":question,"plan":agenda,"past_observations":observations,
             "instruction":"Choose one FAITH read-only tool."})
   action=extract_action(raw)
   result=invoke(gateway,action)
   observations.append({"action":action,"result":result})
   state["steps"].append({"stage":"FAITH_TOOL_RESULT_"+str(n+1),"action":action,"result":result});save()
  critique=call("WONDER_CRITIQUE",WONDER,RULES+" Evaluate research coverage, selection risks, and admissible catalog recommendations. Do not invent data.",
                {"question":question,"spark_plan":agenda,"faith_observations":observations})
  revision=call("SPARK_REVISION",SPARK,RULES+" Provide direct, substantively reasoned answer. Address Wonder critique. State if five cannot be distinguished scientifically.",
                {"question":question,"spark_plan":agenda,"faith_observations":observations,"wonder_critique":critique})
  valid_ids={r.get("shape_uid") for e in ("PilotCandidate","MiningPermit") for r in data.get(e,[])}
  valid_solutions={r.get("solution_id") for r in data.get("RehabilitationSolution",[])}
  cited_sites=set(re.findall(r"GUIDSHAPE:[A-Z0-9-]+",revision))
  cited_solutions=set(re.findall(r"SOL-CAT-[0-9]{5}",revision))
  state["citation_check"]={"unknown_site_ids":sorted(cited_sites-valid_ids),
                           "unknown_solution_ids":sorted(cited_solutions-valid_solutions)}
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
 p.add_argument("--output",required=True);p.add_argument("--execute",action="store_true")
 args=p.parse_args(); data=load(args.snapshot)
 if not args.execute:
  print(json.dumps({"status":"PREVIEW_NO_CALLS","preflight":preflight(data)["status"],
   "planned_model_calls":5,"available":Gateway(data).discover_faith_data()},ensure_ascii=False,indent=2))
  return
 if not os.environ.get("MODEL_API_KEY"):raise SystemExit("MODEL_API_KEY missing")
 target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():raise SystemExit("Refusing overwrite of previous run")
 target.write_text('{"status":"RESERVED_DO_NOT_AUTORETRY"}',encoding="utf8")
 state=run(data,args.question,os.environ["MODEL_API_KEY"],target)
 print(json.dumps({"status":state["status"],"steps":len(state["steps"]),"output":str(target)},ensure_ascii=False))
 if state["status"]!="GENERATED_NEEDS_SCIENTIFIC_REVIEW":raise SystemExit(2)
if __name__=="__main__":main()
