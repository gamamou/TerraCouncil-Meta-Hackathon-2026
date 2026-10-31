"""TERRA-META-023 — Jury-ready local interface built on proven TERRA-META-020.
Reuse existing execution engine; no new scientific or billing logic.
"""
import argparse,html,json,webbrowser
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
from tools import terra_meta_020_end_to_end as core

def esc(x):return html.escape(str(x if x is not None else ""))
def root_for(session):
    path=Path(session)
    return path.parent if path.name=="artifacts" else path
def audio_folders(root):
    return [root/"audio_generated",*sorted(root.glob("audio_retry_*"),reverse=True),
            *sorted(root.glob("audio_recovered_*"),reverse=True),
            *sorted(root.glob("audio_revised_*"),reverse=True)]
def audio_for_session(session):
    root=root_for(session)
    candidates=[x for x in audio_folders(root) if (x/"audio_manifest.json").exists()]
    verified=[]
    for folder in candidates:
        try:
            data=core.read_json(folder/"audio_manifest.json")
            if data.get("status")!="AUDIO_GENERATED_UNREVIEWED":continue
            tracks=data.get("audio_segments",[])
            if tracks and all((folder/t["file"]).is_file() for t in tracks):verified.append(folder)
        except (ValueError,KeyError,OSError):continue
    if verified:return max(verified,key=lambda p:p.stat().st_mtime)
    return None
def current_audio():
    folder=Path(core.STATE["audio"]) if core.STATE.get("audio") else audio_for_session(core.STATE["session"])
    return folder if folder and folder.exists() else None
def actions_html():
    f=Path(core.STATE["session"])/"03_investigation_plan.json"
    if not f.exists():return "<p>Plan d'investigation non disponible.</p>"
    d=core.read_json(f);tasks=d.get("tasks",[])
    rows="".join("<tr><td>"+esc(t.get("task_id"))+"</td><td>"+esc(t.get("action") or t.get("title") or t.get("description"))+
        "</td><td>"+esc(t.get("status"))+"</td></tr>" for t in tasks)
    return "<p>Investigations proposées, non autorisées automatiquement.</p><table><thead><tr><th>ID</th><th>Action</th><th>Statut</th></tr></thead><tbody>"+rows+"</tbody></table>"
def passport_html():
    f=Path(core.STATE["session"])/"04_passport_preview.json"
    if not f.exists():return "<p>Passport indisponible.</p>"
    d=core.read_json(f)
    audio=current_audio()
    link=root_for(core.STATE["session"])/"audio_passport_link.json"
    return ("<dl><dt>Session</dt><dd>"+esc(d.get("session_id"))+"</dd>"
        "<dt>Statut</dt><dd>"+esc(d.get("passport_status"))+"</dd>"
        "<dt>Maturité</dt><dd>"+esc(d.get("scientific_readiness"))+"</dd>"
        "<dt>Trace SHA-256</dt><dd><code>"+esc(d.get("trace_sha256"))+"</code></dd>"
        "<dt>Révision humaine</dt><dd>"+esc((d.get("human_review") or {}).get("status"))+"</dd>"
        "<dt>Audio</dt><dd>"+("Généré, non revu" if audio else "Non disponible")+"</dd></dl>"
        "<p><a href='/passport.json'>Exporter le Passport JSON</a></p>")
def frontpage():
    state=core.STATE.copy()
    root=Path(state["session"])
    brief=root/"05_scientific_brief.json"
    question=""
    level="Non disponible";investigations="—"
    if brief.is_file():
        b=core.read_json(brief);question=b.get("question") or ""
        level=(b.get("executive_brief") or {}).get("scientific_readiness","—")
        investigations=str(len((b.get("follow_up") or {}).get("proposed_investigations",[])))
    audio=current_audio()
    tracks=[]
    if audio:
        try:tracks=core.read_json(audio/"audio_manifest.json").get("audio_segments",[])
        except (ValueError,OSError):pass
    players="".join("<div class='player'><audio controls preload='metadata' src='/audio?i="+str(i)+"'></audio></div>"
          for i,_ in enumerate(tracks))
    if not players:players="<p class='muted'>Aucun audio disponible pour cette session.</p>"
    oral=root_for(state["session"])/"oral"/"internal_oral_script.json"
    revised=list(root_for(state["session"]).glob("oral_revised_*/internal_oral_script.json"))
    retry=bool(oral.is_file() or revised)
    # Do not automatically rerun Meta if only revised script is present.
    if not audio and retry and not state["busy"]:
        players+="<form method='post' action='/resume-audio' onsubmit=\"return confirm('Reprendre ElevenLabs uniquement ? Cet appel est payant.')\"><button>Reprendre la génération audio</button></form>"
    items=core.sessions(core.ARGS.storage)
    history="".join("<li><a href='/select?session="+esc(x.parent.name)+"'>"+esc(x.parent.name)+"</a></li>" for x in items)
    busy=bool(state["busy"])
    return """<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>TerraCouncil · Decision Intelligence</title>
<style>
:root{font:15px/1.55 system-ui,Segoe UI,sans-serif;color:#163348;background:#eef4f7}*{box-sizing:border-box}body{margin:0}
main{max-width:1120px;margin:auto;padding:26px 18px}header{padding:30px;border-radius:20px;background:linear-gradient(115deg,#0f394f,#16616d);color:white}
header h1{font-size:34px;margin:8px 0}.eyebrow{font-size:12px;letter-spacing:.15em;opacity:.8}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.panel{border:1px solid #d5e3ec;background:white;border-radius:16px;padding:23px;margin-top:18px}
h2{margin:0 0 12px;font-size:21px}h3{margin:0;font-size:17px}.muted{color:#617a88}
textarea{width:100%;min-height:120px;border-radius:10px;padding:12px;font:inherit;border:1px solid #b6cad6}
button{background:#12647d;color:white;border:0;border-radius:10px;padding:11px 17px;cursor:pointer;margin-top:10px}
button:disabled{opacity:.55}a{color:#09647a}audio{width:100%}.player{margin:14px 0}
.stat{font-size:21px;font-weight:750;overflow-wrap:anywhere}dt{font-weight:700;margin-top:12px}dd{margin:3px 0;overflow-wrap:anywhere}
table{border-collapse:collapse;width:100%}td,th{padding:9px;border-bottom:1px solid #d9e4eb;text-align:left}
#status{padding:13px;border-radius:10px;background:#edf4f7}nav{display:flex;gap:16px;flex-wrap:wrap;margin-top:14px}
nav a{color:white}li{padding:3px}small{color:#617a88}
@media(max-width:750px){.grid{display:block}header h1{font-size:28px}}@media print{form,nav,audio{display:none}}
</style></head><body><main><header><div class="eyebrow">SUSTAINAFRICA · FAITH · TERRACOUNCIL</div>
<h1>Scientific Decision Intelligence</h1><p>De la question aux preuves, aux recommandations et au débat oral.</p>
<nav><a href="#question">Nouvelle question</a><a href="#brief">Rapport</a><a href="#audio">Council Theater</a>
<a href="#passport">Passport</a><a href="#actions">Suivi</a></nav></header>
<section class="panel" id="question"><h2>Question scientifique</h2>
<form action="/start" method="post" onsubmit="return confirm('Démarrer une nouvelle délibération Meta ? Les appels API peuvent être facturés.')">
<textarea name="question" required>"""+esc(question or "Identifiez cinq sites miniers en Guinée prioritaires pour un programme pilote de réhabilitation.")+"""</textarea>
<label><input type="checkbox" name="audio" value="yes" checked> Générer le débat oral ElevenLabs v4</label>
<p><button """+("disabled" if busy else "")+""">Lancer le Conseil</button></p></form>
<div id="status" role="status" aria-live="polite"><strong>Étape :</strong> """+esc(state["phase"])+""" · """+esc(state["message"])+"""</div></section>
<div class="grid"><section class="panel" id="brief"><h2>Executive Brief</h2><p class="muted">Maturité scientifique</p>
<div class="stat">"""+esc(level)+"""</div><p>Investigations : """+investigations+"""</p><a href="/brief">Ouvrir le rapport</a></section>
<section class="panel" id="passport"><h2>Decision Passport</h2>"""+passport_html()+"""</section></div>
<section class="panel" id="audio"><h2>Council Theater</h2>"""+players+"""</section>
<section class="panel" id="actions"><h2>Actions & suivi</h2>"""+actions_html()+"""</section>
<section class="panel"><h2>Historique des sessions</h2><ul>"""+history+"""</ul></section>
<p><small>Les résultats conservent leurs réserves scientifiques. Toute validation humaine est enregistrée séparément.</small></p>
</main><script>
const previous="""+json.dumps({"phase":state["phase"],"busy":busy},ensure_ascii=False)+""";
async function poll(){try{
 const r=await fetch('/status');const s=await r.json();
 if(s.busy){document.getElementById('status').textContent='Étape : '+s.phase+' · '+s.message;}
 if(previous.busy && !s.busy){location.reload();}
}catch(e){}}
setInterval(poll,3000);
</script></body></html>"""

class Handler(core.Handler):
    def do_GET(self):
        route=urlparse(self.path)
        if route.path=="/":return self.send(200,frontpage().encode("utf8"),"text/html; charset=utf-8")
        if route.path=="/status":
            s={k:core.STATE.get(k) for k in ("phase","message","busy")}
            return self.send(200,json.dumps(s,ensure_ascii=False).encode("utf8"),"application/json")
        if route.path=="/passport.json":
            f=Path(core.STATE["session"])/"04_passport_preview.json"
            if f.is_file():return self.send(200,f.read_bytes(),"application/json")
        if route.path=="/audio":
            folder=current_audio()
            if folder:
                try:
                    tracks=core.read_json(folder/"audio_manifest.json")["audio_segments"]
                    index=int(parse_qs(route.query).get("i",["0"])[0])
                    if 0<=index<len(tracks):
                        f=folder/tracks[index]["file"]
                        if f.is_file():return self.send(200,f.read_bytes(),"audio/mpeg")
                except (ValueError,KeyError,IndexError,OSError):pass
            return self.send(404,b"Audio unavailable","text/plain")
        return super().do_GET()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--snapshot",required=True)
    parser.add_argument("--session",default=str(core.PILOT))
    parser.add_argument("--storage",type=Path,default=core.HOME/"Sessions-UNIFIED020")
    parser.add_argument("--port",type=int,default=8767)
    args=parser.parse_args()
    core.ARGS=args
    core.STATE.update(session=args.session,audio=str(audio_for_session(args.session)) if audio_for_session(args.session) else None)
    server=ThreadingHTTPServer(("127.0.0.1",args.port),Handler)
    url="http://127.0.0.1:"+str(args.port)
    print("TerraCouncil 023: "+url,flush=True)
    webbrowser.open(url);server.serve_forever()
if __name__=="__main__":main()
