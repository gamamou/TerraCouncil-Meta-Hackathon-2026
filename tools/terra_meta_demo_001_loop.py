"""DEMO-001: Spark chooses FAITH reads; Wonder critiques; Spark revises.
Only model reasoning makes selections; Python validates cited IDs and logs actions.
Requires a locally exported, reviewed JSON snapshot (never uploads source to GitHub).
"""
import argparse,json,os,re
from pathlib import Path
from council import meta_call,SPARK,WONDER
from terra_demo_001_faith_gateway import Gateway,load,invoke
CHAIR="""You are Meta Muse Spark, chairing TerraCouncil. Respond to the USER question, not an
inventory of data. You may issue JSON actions, one per turn:
{"tool":"discover_faith_data"}
{"tool":"query_faith_data","entity":"PilotCandidate","limit":50}
{"tool":"get_faith_record","entity":"MiningPermit","identifier":"EXACT shape_uid"}
{"tool":"consult_scientific_agent","question":"specific scientific challenge","reason":"why independent critique adds value"}
{"tool":"final_answer","sites":[{"shape_uid":"EXACT ID","why":"grounded comparison","interventions":[{"solution_id":"EXACT ID","rationale":"conditional reasoning"}],"uncertainties":["..."]}],"answer":"direct response","review_of_critique":"how Wonder influenced answer"}
Supported entity names: PilotCandidate, MiningPermit, PermitSpatialContext,
SiteRehabilitationRecommendation, RehabilitationSolution.
Search data first. The user does not know the ranking. Do not invent values or joins.
A catalog solution is NOT a site-approved intervention. Rank ties must be explained. If many sites tie, clearly state that five selected are provisional and do not falsely claim objectively optimal five. No site-specific restoration diagnosis has been verified.
For this DEMO-004, you MUST consult Wonder after reviewing actual candidate and catalog data and BEFORE final_answer. Summarize and respond to Wonder in review_of_critique.
Only cite IDs you have actually retrieved. Missing evidence = conditional, not fact."""
CRITIC="""You are Meta Muse Wonder acting as independent mining restoration critic.
Inspect the chair's current candidate reasoning and available FAITH evidence.
Return strict JSON with keys "critique", "missing_evidence", "revision_suggestions":
all arrays of strings. Challenge causal leaps, tie-breaking, unsupported site joins,
and catalog solutions treated as proven interventions. No fabricated site data."""
class InvalidModelAction(ValueError):
 def __init__(self,raw,reason):
  self.preview=(raw[:1200] if isinstance(raw,str) else repr(raw)[:1200])
  super().__init__(reason)

def parse(raw):
 if isinstance(raw,dict):return raw
 if not isinstance(raw,str):raise InvalidModelAction(raw,"Model returned nontext action")
 value=raw.strip()
 if not value:raise InvalidModelAction(raw,"Meta returned an empty action")
 if value.startswith("```"):
  value=re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$","",value,flags=re.I).strip()
 try:
  parsed=json.loads(value)
 except json.JSONDecodeError:
  match=re.search(r"\{",value)
  if not match:raise InvalidModelAction(raw,"No JSON object found")
  try:parsed,_=json.JSONDecoder().raw_decode(value[match.start():])
  except json.JSONDecodeError as exc:raise InvalidModelAction(raw,"Malformed JSON: "+str(exc)) from None
 if not isinstance(parsed,dict):raise InvalidModelAction(raw,"Expected JSON action object")
 return parsed

def run(question,gateway,key,caller=meta_call,max_steps=13):
 history=[];observed_ids=set();sol_ids=set();wonder=None;out=None
 for i in range(max_steps):
  prompt={"question":question,"history":history[-10:],
    "wonder_available":wonder is not None}
  action=parse(caller(SPARK,CHAIR,prompt,key))
  tool=action.get("tool")
  if tool in ("discover_faith_data","query_faith_data","get_faith_record"):
   data=invoke(gateway,action)
   for r in data:
    if isinstance(r,dict):
     if "shape_uid" in r:observed_ids.add(r["shape_uid"])
     if "solution_id" in r:sol_ids.add(r["solution_id"])
   result={"status":"DATA_RETURNED","data":data}
  elif tool=="consult_scientific_agent":
   if wonder is not None:
    result={"status":"REJECTED_ALREADY_CONSULTED"}
   else:
    critique=parse(caller(WONDER,CRITIC,{"question":question,"history":history[-10:],
                                       "challenge":action.get("question","")},key))
    if set(critique)!={"critique","missing_evidence","revision_suggestions"} or any(not isinstance(v,list) or any(not isinstance(z,str) for z in v) for v in critique.values()):
     raise ValueError("Wonder response schema invalid")
    wonder=critique
    result={"status":"SCIENTIFIC_CRITIQUE_RECEIVED","critique":critique}
  elif tool=="final_answer":
   sites=action.get("sites",[])
   if wonder is None:
    result={"status":"REJECTED_DEMO004_REQUIRES_WONDER_CRITIQUE"}
    history.append({"step":i+1,"actor":SPARK,"action":action,"result":result})
    continue
   if not isinstance(sites,list) or len(sites)!=5:
    result={"status":"REJECTED_EXPECT_FIVE_SITES"}
   elif any(not isinstance(s,dict) or s.get("shape_uid") not in observed_ids for s in sites):
    result={"status":"REJECTED_UNSEEN_SITE"}
   elif len({s["shape_uid"] for s in sites})!=5:
    result={"status":"REJECTED_DUPLICATE_SITE"}
   elif any(not isinstance(s.get("interventions",[]),list) or
            any(not isinstance(v,dict) or v.get("solution_id") not in sol_ids
                for v in s.get("interventions",[])) for s in sites):
    result={"status":"REJECTED_UNSEEN_SOLUTION"}
   elif wonder is not None and not str(action.get("review_of_critique","")).strip():
    result={"status":"REJECTED_NO_CRITIQUE_RESPONSE"}
   else:
    out=action;result={"status":"PROVISIONAL_ANSWER_ACCEPTED"}
  else:result={"status":"REJECTED_UNKNOWN_TOOL"}
  history.append({"step":i+1,"actor":SPARK,"action":action,"result":result})
  if out:break
 return {"status":"PROVISIONAL_HUMAN_REVIEW" if out else "INCOMPLETE",
         "question":question,"answer":out,"wonder_critique":wonder,"history":history,
         "validation":"ID_REFERENCES_ONLY_NO_SCIENTIFIC_VALIDATION"}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--snapshot",required=True);p.add_argument("--question",required=True)
 p.add_argument("--execute",action="store_true");p.add_argument("--output")
 a=p.parse_args();data=load(a.snapshot);g=Gateway(data)
 if not a.execute:
  print(json.dumps({"status":"PREVIEW_NO_CALLS","available":g.discover_faith_data()},
   ensure_ascii=False,indent=2));return
 if not a.output:raise SystemExit("--output mandatory")
 key=os.getenv("MODEL_API_KEY")
 if not key:raise SystemExit("MODEL_API_KEY missing")
 target=Path(a.output);target.parent.mkdir(parents=True,exist_ok=True)
 with target.open("x",encoding="utf8") as f:json.dump({"status":"STARTED_DO_NOT_AUTORETRY"},f)
 try:
  result=run(a.question,g,key)
  target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf8")
  print(json.dumps({"status":result["status"],"spark_steps":len(result["history"]),
   "wonder_called":bool(result["wonder_critique"]),"output":str(target)},ensure_ascii=False))
 except Exception as error:
  diagnostic={"status":"INTERRUPTED_DO_NOT_AUTORETRY",
   "error_type":type(error).__name__,"reason":str(error)[:400]}
  if isinstance(error,InvalidModelAction):diagnostic["model_response_excerpt"]=error.preview
  target.write_text(json.dumps(diagnostic,ensure_ascii=False,indent=2),encoding="utf8")
  raise
if __name__=="__main__":main()
