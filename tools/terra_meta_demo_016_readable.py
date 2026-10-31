"""DEMO-016: readable scientific brief + immutable proposed action tracker.
Renders the exact Meta recommendation and critique; no Python science decisions.
"""
import argparse,html,json
from pathlib import Path
def render(brief):
    e=brief["executive_brief"]
    esc=lambda x:html.escape(str(x or ""))
    tasks=brief.get("follow_up",{}).get("proposed_investigations",[])
    rows="".join("<tr><td>"+esc(t.get("task_id"))+"</td><td>"+esc(t.get("action"))+
      "</td><td>"+esc(t.get("proposed_owner_role"))+"</td><td>"+esc(t.get("status"))+"</td></tr>" for t in tasks)
    limitations="".join("<li>"+esc(x)+"</li>" for x in e.get("evidence_limitations",[]))
    return """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TerraCouncil Scientific Brief</title><style>
body{font:16px/1.6 system-ui,Arial,sans-serif;color:#1e293b;background:#f5f7fa;margin:0}
main{max-width:980px;margin:36px auto;padding:24px}
header{background:#102f43;color:white;padding:30px;border-radius:14px}
section{background:white;border:1px solid #d8e1e7;border-radius:12px;padding:24px;margin:18px 0}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}
table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;text-align:left;padding:10px}
small{color:#64748b}@media print{body{background:white}main{margin:0;padding:0}section{break-inside:avoid}}
</style></head><body><main><header><h1>TerraCouncil — Scientific Brief</h1><p>""" +esc(brief.get("question"))+"""</p></header>
<section><h2>Statut scientifique</h2><p>"""+esc(e.get("scientific_readiness"))+"""</p>
<p>Ce rapport est un brouillon soumis à révision scientifique humaine.</p></section>
<section><h2>Conclusions et recommandations de Spark — texte original</h2><pre>"""+esc(e.get("council_recommendations_verbatim"))+"""</pre></section>
<section><h2>Examen critique de Wonder — texte original</h2><pre>"""+esc(e.get("critic_assessment_verbatim"))+"""</pre></section>
<section><h2>Limites des preuves</h2><ul>"""+limitations+"""</ul></section>
<section><h2>Investigations proposées (non autorisées)</h2><table><thead>
<tr><th>ID</th><th>Action</th><th>Responsable proposé</th><th>État</th></tr></thead><tbody>"""+rows+"""</tbody></table></section>
<section><h2>Passport et audio</h2><p>Passport : """+esc(brief.get("passport",{}).get("status"))+""" · Audio : """+esc(brief.get("audio",{}).get("status"))+"""</p></section>
<small>Les affirmations des modèles n'ont pas été vérifiées individuellement. Aucune décision n'est approuvée automatiquement.</small>
</main></body></html>"""

def tracker(brief):
    return {"schema_version":"DEMO-016-TRACKER","status":"DRAFT_UNAUTHORIZED",
        "passport_session":brief.get("passport",{}).get("session_id"),
        "tasks":[{"task_id":x.get("task_id"),"action":x.get("action"),
          "owner_role_suggested":x.get("proposed_owner_role"),"owner_assigned":None,
          "due_date":None,"status":"PROPOSED_NOT_AUTHORIZED","evidence_refs":[],
          "human_approval":None} for x in brief.get("follow_up",{}).get("proposed_investigations",[])]}

def main():
    p=argparse.ArgumentParser();p.add_argument("--brief",required=True);p.add_argument("--output-dir",required=True)
    a=p.parse_args();root=Path(a.output_dir)
    if root.exists():raise SystemExit("Output directory exists; refusing overwrite")
    b=json.loads(Path(a.brief).read_text(encoding="utf-8-sig"))
    root.mkdir(parents=True)
    (root/"scientific_brief.html").write_text(render(b),encoding="utf8")
    (root/"action_tracker.json").write_text(json.dumps(tracker(b),ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"html":str(root/"scientific_brief.html"),"tracker":str(root/"action_tracker.json"),"tasks":len(tracker(b)["tasks"])},ensure_ascii=False))
if __name__=="__main__":main()
