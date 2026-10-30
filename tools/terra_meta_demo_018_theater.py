"""DEMO-018 Council Theater: replay original council exchanges and link reviewed audio.
No synthesis, paraphrasing, approvals or artificial scientific conclusions.
"""
import argparse, html, json
from pathlib import Path

STAGES=(("SPARK_RESEARCH_PLAN","Spark — Plan de recherche"),
        ("WONDER_CRITIQUE","Wonder — Examen contradictoire"),
        ("SPARK_REVISION","Spark — Réponse révisée"))

def build(session):
    root=Path(session)
    trace=json.loads((root/"01_trace.json").read_text(encoding="utf-8-sig"))
    brief=json.loads((root/"05_scientific_brief.json").read_text(encoding="utf-8-sig"))
    passport=json.loads((root/"04_passport_preview.json").read_text(encoding="utf-8-sig"))
    recorded={s.get("stage"):s for s in trace.get("steps",[])}
    panels=[{"stage":stage,"speaker":speaker,"text":recorded[stage].get("response",""),
             "model":recorded[stage].get("model")} for stage,speaker in STAGES if stage in recorded]
    return {"schema_version":"DEMO-018","session_id":passport.get("session_id"),
        "question":trace.get("question"),"family":brief.get("family"),
        "scientific_readiness":brief.get("executive_brief",{}).get("scientific_readiness"),
        "interventions":panels,
        "audio":{"status":"NOT_GENERATED","tracks":[]},
        "passport_status":passport.get("passport_status"),
        "investigations":brief.get("follow_up",{}).get("proposed_investigations",[]),
        "scientific_integrity":"Unedited model text; debate sequence is a transcript replay, not generated speech."}

def render(theater):
    esc=lambda value:html.escape(str(value if value is not None else ""))
    parts=[]
    for i,item in enumerate(theater["interventions"]):
        parts.append('<section class="speech"><div class="speaker">'+esc(item["speaker"])+
          '</div><div class="source">'+esc(item.get("model"))+' · '+esc(item["stage"])+
          '</div><details'+(" open" if i==0 else "")+'><summary>Lire l’intervention originale</summary><pre>'+
          esc(item["text"])+'</pre></details></section>')
    actions="".join('<li>'+esc(a.get("action"))+' <small>('+esc(a.get("status"))+')</small></li>'
                    for a in theater["investigations"])
    return """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TerraCouncil — Council Theater</title><style>
body{margin:0;background:#edf2f6;color:#1b3444;font:16px/1.55 system-ui,sans-serif}
main{max-width:1050px;margin:32px auto;padding:0 20px}
header{background:#11384c;color:#fff;border-radius:16px;padding:28px}
h1{margin:0 0 10px}section{border:1px solid #d5e1e8;background:#fff;border-radius:12px;
padding:22px;margin:16px 0} .speaker{font-size:20px;font-weight:750}
.source,small{color:#597385;font-size:12px}summary{cursor:pointer;font-weight:650;margin-top:12px}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}
.tag{display:inline-block;background:#e3edf3;border-radius:99px;padding:6px 12px;font-size:12px}
.notice{border-left:4px solid #c18631}
@media print{body{background:#fff}details{display:block}details>summary{display:none}details>pre{display:block!important}}
</style></head><body><main><header><h1>Council Theater</h1><p>"""+esc(theater["question"])+"""</p>
<p>Délibération scientifique · Transcription originale des modèles</p></header>
<section class="notice"><strong>Audio : NON GÉNÉRÉ</strong>
<p>Cette vue présente une transcription vérifiable. Elle ne simule pas un fichier audio inexistant.</p>
<span class="tag">Passport : """+esc(theater["passport_status"])+"""</span>
<span class="tag">Maturité : """+esc(theater["scientific_readiness"])+"""</span></section>
<h2>Interventions du Conseil</h2>"""+"".join(parts)+"""
<section><h2>Investigations proposées</h2><ul>"""+actions+"""</ul>
<p>Ces actions ne sont ni approuvées ni assignées.</p></section>
<section><h2>TerraCouncil Passport</h2><p>Session : """+esc(theater["session_id"])+
"""</p><p>État : """+esc(theater["passport_status"])+"""</p></section>
</main></body></html>"""

def main():
    p=argparse.ArgumentParser();p.add_argument("--session",required=True)
    p.add_argument("--output-dir",required=True);args=p.parse_args()
    root=Path(args.output_dir)
    if root.exists():raise SystemExit("Output already exists; refusing overwrite")
    theater=build(args.session);root.mkdir(parents=True)
    (root/"council_theater.json").write_text(json.dumps(theater,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (root/"council_theater.html").write_text(render(theater),encoding="utf8")
    print(json.dumps({"html":str(root/"council_theater.html"),
        "interventions":len(theater["interventions"]),"audio":theater["audio"]["status"]},ensure_ascii=False))
if __name__=="__main__":main()
