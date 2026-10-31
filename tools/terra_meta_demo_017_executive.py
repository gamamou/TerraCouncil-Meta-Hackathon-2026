"""DEMO-017 — Decision-facing HTML, no model-generated scientific reinterpretation.
Existing Meta conclusions remain verbatim; summary is only administrative metadata.
"""
import argparse,html,json
from pathlib import Path
from tools.terra_meta_demo_016_readable import tracker

def render(brief):
    if brief.get("schema_version")!="DEMO-015":raise ValueError("Expected DEMO-015 brief")
    esc=lambda x:html.escape(str(x if x is not None else ""))
    e=brief["executive_brief"];cov=e.get("research_coverage") or {}
    tasks=brief.get("follow_up",{}).get("proposed_investigations",[])
    missing=cov.get("missing_required",[])
    limitations=e.get("evidence_limitations") or []
    status=e.get("scientific_readiness","UNKNOWN")
    note=("Les consultations indispensables disponibles ne sont pas toutes achevées."
          if not cov.get("is_complete",False) else
          "Les consultations requises ont été couvertes ; cela ne valide pas les résultats scientifiques.")
    rows="".join("<tr><td>"+esc(t.get("task_id"))+"</td><td>"+esc(t.get("action"))+
         "</td><td>"+esc(t.get("proposed_owner_role"))+"</td><td>"+esc(t.get("status"))+"</td></tr>"
         for t in tasks)
    li=lambda items:"".join("<li>"+esc(x)+"</li>" for x in items)
    spark=esc(e.get("council_recommendations_verbatim",""))
    wonder=esc(e.get("critic_assessment_verbatim",""))
    return """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TerraCouncil — Executive Decision Brief</title>
<style>
:root{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;color:#203244;background:#f3f6fa}
*{box-sizing:border-box}body{margin:0}main{max-width:1100px;margin:auto;padding:30px 18px}
.hero{background:#12394c;color:white;padding:32px;border-radius:18px}
.eyebrow{font-size:12px;letter-spacing:.12em;text-transform:uppercase;opacity:.8}
h1{font-size:30px;line-height:1.2;margin:8px 0}h2{margin:0 0 12px;font-size:20px}
.subtitle{max-width:850px;line-height:1.6}.cols{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:18px}
.panel{background:white;border:1px solid #dae3ed;border-radius:14px;padding:22px;margin-top:16px}
.stat{font-size:22px;font-weight:750;overflow-wrap:anywhere}.muted{color:#587083}
.warning{border-left:5px solid #bd8028}.tag{display:inline-block;background:#e7edf4;border-radius:20px;padding:5px 12px;font-size:12px}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:12px;text-align:left;border-bottom:1px solid #e2e8f0}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit;line-height:1.65}details summary{cursor:pointer;font-weight:700;padding:12px 0}
li{margin-bottom:7px}.small{font-size:13px;color:#5d7286}
@media(max-width:700px){.cols{grid-template-columns:1fr}.panel{overflow-x:auto}}
@media print{body{background:white}details{display:block}details>summary{display:none}details>div{display:block!important}}
</style></head><body><main>
<header class="hero"><div class="eyebrow">SustainAfrica · FAITH · TerraCouncil</div>
<h1>Executive Decision Brief</h1><p class="subtitle">"""+esc(brief.get("question"))+"""</p>
<p>Compte rendu de conseil scientifique — brouillon soumis à validation humaine</p></header>
<div class="cols">
<div class="panel"><div class="small">Maturité scientifique</div><div class="stat">"""+esc(status)+"""</div></div>
<div class="panel"><div class="small">Sources essentielles non consultées</div><div class="stat">"""+str(len(missing))+"""</div></div>
<div class="panel"><div class="small">Investigations proposées</div><div class="stat">"""+str(len(tasks))+"""</div></div>
</div>
<section class="panel warning"><h2>Lecture exécutive · état des preuves</h2>
<p>"""+esc(note)+"""</p><p>Ce panneau affiche des métadonnées contrôlées ; il ne résume pas ni ne remplace le raisonnement Meta.</p>
<p><strong>Autorisation automatique :</strong> aucune.</p></section>
<section class="panel"><h2>Couverture de la recherche FAITH</h2>
<p><strong>Sources consultées :</strong> """+esc(", ".join(cov.get("consulted",[])) or "Aucune source enregistrée")+"""</p>
<p><strong>Sources essentielles manquantes :</strong> """+esc(", ".join(missing) or "Aucune source obligatoire manquante")+"""</p></section>
<section class="panel"><h2>Limites scientifiques documentées</h2><ul>"""+li(limitations)+"""</ul></section>
<section class="panel"><h2>Recommandations du conseil</h2>
<p class="small">Texte original de Muse Spark, non reformulé et non approuvé.</p>
<details><summary>Consulter les conclusions intégrales de Spark</summary><div><pre>"""+spark+"""</pre></div></details>
<details><summary>Consulter les objections intégrales de Wonder</summary><div><pre>"""+wonder+"""</pre></div></details></section>
<section class="panel"><h2>Action plan & suivi</h2>
<p class="small">Rôles suggérés uniquement ; aucune responsabilité ni échéance attribuée.</p>
<table><thead><tr><th>ID</th><th>Investigation</th><th>Rôle suggéré</th><th>Statut</th></tr></thead><tbody>"""+rows+"""</tbody></table></section>
<section class="panel"><h2>Passport · Council Theater</h2>
<p><span class="tag">Passport : """+esc(brief.get("passport",{}).get("status"))+"""</span>
<span class="tag">Audio : """+esc(brief.get("audio",{}).get("status"))+"""</span></p>
<p class="small">Le futur audio doit reprendre les conclusions et objections approuvées sans altérer leurs réserves.</p></section>
<footer class="small">Brouillon interne · Les affirmations scientifiques du modèle nécessitent un contrôle indépendant · Aucune approbation implicite.</footer>
</main></body></html>"""

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--brief",required=True);ap.add_argument("--output-dir",required=True)
    a=ap.parse_args();out=Path(a.output_dir)
    if out.exists():raise SystemExit("Refusing to overwrite directory")
    brief=json.loads(Path(a.brief).read_text(encoding="utf-8-sig"))
    html_text=render(brief);tasks=tracker(brief)
    out.mkdir(parents=True)
    (out/"executive_decision_brief.html").write_text(html_text,encoding="utf8")
    (out/"action_tracker.json").write_text(json.dumps(tasks,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"report":str(out/"executive_decision_brief.html"),
       "investigations":len(tasks["tasks"]),"review":"REQUIRED","audio":"NOT_GENERATED"},ensure_ascii=False))
if __name__=="__main__":main()
